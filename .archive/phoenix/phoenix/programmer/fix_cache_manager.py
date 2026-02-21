"""
Fix Caching System

Cache successful fixes and reuse them for identical failures.
Dramatically speeds up healing for repeated problems.

Optional module - enables solution reuse without affecting core healing.
Uses only standard library (json) - no external dependencies needed.
"""

import hashlib
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, asdict
import os
from pathlib import Path

from phoenix.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class CachedFix:
    """A cached fix solution."""
    failure_signature: str
    failure_type: str
    fix_code: str
    validation_tests: str
    created_at: str
    success_count: int = 0
    last_used_at: Optional[str] = None
    avg_application_time_ms: float = 0


class FixCacheManager:
    """
    Manages cache of successful fixes.
    
    When the same failure happens again, reuse the fix instead of
    generating a new one with LLM.
    
    Benefits:
    - 10-50x faster fix application
    - Consistent fixes for repeated issues
    - Reduced LLM API costs
    - Builds solution knowledge over time
    """
    
    def __init__(self, cache_file: str = "./phoenix_fix_cache.json"):
        """
        Initialize cache manager.
        
        Args:
            cache_file: Where to store cached fixes
        """
        self.cache_file = cache_file
        self.cache: Dict[str, CachedFix] = {}
        self.logger = get_logger(__name__)
        self._load_cache()
    
    def get_failure_signature(
        self,
        failure_type: str,
        error_message: str,
        stack_trace: str,
    ) -> str:
        """
        Create signature for a failure.
        
        Signature is deterministic hash so identical failures
        produce identical signatures.
        
        Args:
            failure_type: Type of failure
            error_message: Error message
            stack_trace: Stack trace (normalized)
        
        Returns:
            Failure signature hash
        """
        # Normalize stack trace (ignore line numbers)
        normalized_trace = self._normalize_stack_trace(stack_trace)
        
        # Create signature from type + message + normalized trace
        signature_input = f"{failure_type}||{error_message}||{normalized_trace}"
        
        signature = hashlib.sha256(signature_input.encode()).hexdigest()
        return signature[:16]  # Use first 16 chars
    
    def get_cached_fix(
        self,
        failure_signature: str,
    ) -> Optional[CachedFix]:
        """
        Get cached fix for a failure.
        
        Args:
            failure_signature: Failure signature
        
        Returns:
            CachedFix if found, None otherwise
        """
        if failure_signature in self.cache:
            cached = self.cache[failure_signature]
            
            # Update usage stats
            cached.success_count += 1
            cached.last_used_at = datetime.utcnow().isoformat()
            
            self.logger.info("cached_fix_reused", signature=failure_signature)
            self._save_cache()
            
            return cached
        
        return None
    
    def cache_fix(
        self,
        failure_signature: str,
        failure_type: str,
        fix_code: str,
        validation_tests: str,
        application_time_ms: float,
    ) -> CachedFix:
        """
        Cache a successful fix.
        
        Args:
            failure_signature: Failure signature
            failure_type: Type of failure
            fix_code: The fix code
            validation_tests: Tests for the fix
            application_time_ms: How long fix took to apply
        
        Returns:
            CachedFix
        """
        cached = CachedFix(
            failure_signature=failure_signature,
            failure_type=failure_type,
            fix_code=fix_code,
            validation_tests=validation_tests,
            created_at=datetime.utcnow().isoformat(),
            success_count=1,
            last_used_at=datetime.utcnow().isoformat(),
            avg_application_time_ms=application_time_ms,
        )
        
        self.cache[failure_signature] = cached
        self.logger.info("fix_cached", signature=failure_signature)
        
        self._save_cache()
        return cached
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_fixes = len(self.cache)
        total_reuses = sum(fix.success_count for fix in self.cache.values())
        
        # Calculate savings
        # Each LLM call costs time + money, reuse is free
        estimated_time_saved_ms = sum(
            fix.avg_application_time_ms * (fix.success_count - 1)
            for fix in self.cache.values()
        )
        
        return {
            "total_cached_fixes": total_fixes,
            "total_reuses": total_reuses,
            "avg_reuse_per_fix": (
                total_reuses / total_fixes if total_fixes > 0 else 0
            ),
            "estimated_time_saved_ms": estimated_time_saved_ms,
            "cache_file": self.cache_file,
        }
    
    def get_most_reused_fixes(self, top_n: int = 10) -> List[CachedFix]:
        """Get most frequently reused fixes."""
        fixes = list(self.cache.values())
        fixes.sort(key=lambda x: x.success_count, reverse=True)
        return fixes[:top_n]
    
    def export_cache_report(self) -> Dict[str, Any]:
        """Export cache report."""
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "stats": self.get_cache_stats(),
            "most_reused": [
                asdict(fix) for fix in self.get_most_reused_fixes()
            ],
        }
    
    def clear_old_fixes(self, max_age_days: int = 30):
        """Remove fixes not used in N days."""
        cutoff = datetime.utcnow().timestamp() - (max_age_days * 86400)
        
        to_remove = []
        for signature, cached_fix in self.cache.items():
            last_used = datetime.fromisoformat(
                cached_fix.last_used_at or cached_fix.created_at
            ).timestamp()
            
            if last_used < cutoff:
                to_remove.append(signature)
        
        for signature in to_remove:
            del self.cache[signature]
            self.logger.info("old_fix_removed", signature=signature)
        
        self._save_cache()
        return len(to_remove)
    
    def _normalize_stack_trace(self, trace: str) -> str:
        """Normalize stack trace for comparison."""
        # Remove line numbers, file paths vary
        lines = []
        for line in trace.split('\n'):
            # Keep only the function/method name part
            if ' at ' in line:
                lines.append(line.split(' at ')[0].strip())
            elif ' in ' in line:
                lines.append(line.split(' in ')[0].strip())
            else:
                lines.append(line.strip())
        
        return '\n'.join(lines[:10])  # Keep top 10 frames
    
    def _load_cache(self):
        """Load cache from file with recovery and validation."""
        if not os.path.exists(self.cache_file):
            return
        
        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
            
            # Validate structure
            if not isinstance(data, dict) or "fixes" not in data:
                self.logger.warning("cache_invalid_structure")
                return
            
            loaded_count = 0
            for signature, fix_data in data.get("fixes", {}).items():
                try:
                    # Validate required fields
                    if not isinstance(fix_data, dict):
                        continue
                    
                    required = ["failure_signature", "failure_type", "fix_code"]
                    if not all(k in fix_data for k in required):
                        continue
                    
                    self.cache[signature] = CachedFix(**fix_data)
                    loaded_count += 1
                except (TypeError, ValueError) as e:
                    # Skip corrupted entries
                    self.logger.debug("cache_entry_skipped", error=str(e))
                    continue
            
            self.logger.info("cache_loaded", count=loaded_count)
        
        except json.JSONDecodeError as e:
            # File corrupted - back it up
            backup_path = f"{self.cache_file}.corrupted"
            try:
                os.rename(self.cache_file, backup_path)
                self.logger.warning("cache_corrupted_backed_up", backup=backup_path)
            except Exception:
                pass
        
        except Exception as e:
            self.logger.warning("cache_load_failed", error=str(e))
    
    def _save_cache(self):
        """Save cache to file with atomic write and recovery."""
        try:
            # Create directory if needed
            Path(self.cache_file).parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "generated_at": datetime.utcnow().isoformat(),
                "fixes": {
                    sig: asdict(fix) for sig, fix in self.cache.items()
                },
            }
            
            # Write to temporary file first (atomic write)
            temp_path = f"{self.cache_file}.tmp"
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Verify temp file is valid
            with open(temp_path, 'r') as f:
                json.load(f)  # Raises exception if invalid
            
            # Backup existing file
            if os.path.exists(self.cache_file):
                backup_path = f"{self.cache_file}.backup"
                os.rename(self.cache_file, backup_path)
            
            # Atomic rename
            os.rename(temp_path, self.cache_file)
            
            # Clean up backup
            backup_path = f"{self.cache_file}.backup"
            if os.path.exists(backup_path):
                try:
                    os.remove(backup_path)
                except Exception:
                    pass
        
        except Exception as e:
            self.logger.warning("cache_save_failed", error=str(e))
            # Clean up temp file if it exists
            temp_path = f"{self.cache_file}.tmp"
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass


class CostOptimizer:
    """
    Routes fixes to cost-effective LLM models.
    
    Simple fixes -> cheap/fast models (Groq, Ollama)
    Complex fixes -> capable models (GPT-4, Claude)
    
    Saves money while maintaining quality.
    """
    
    def __init__(self):
        """Initialize optimizer."""
        self.logger = get_logger(__name__)
    
    def select_model_for_fix(
        self,
        failure_complexity: str,
        budget_tier: str = "standard",
    ) -> str:
        """
        Select best model for this fix.
        
        Args:
            failure_complexity: "simple", "medium", "complex"
            budget_tier: "budget", "standard", "premium"
        
        Returns:
            Model name to use
        """
        if failure_complexity == "simple":
            if budget_tier == "budget":
                return "groq/mixtral-8x7b"
            elif budget_tier == "standard":
                return "groq/llama-3-70b"
            else:
                return "openai/gpt-3.5-turbo"
        
        elif failure_complexity == "medium":
            if budget_tier == "budget":
                return "openai/gpt-3.5-turbo"
            elif budget_tier == "standard":
                return "anthropic/claude-3-sonnet"
            else:
                return "anthropic/claude-3-opus"
        
        else:  # complex
            if budget_tier == "budget":
                return "anthropic/claude-3-sonnet"
            elif budget_tier == "standard":
                return "anthropic/claude-3-opus"
            else:
                return "openai/gpt-4"
    
    def estimate_complexity(self, failure_type: str) -> str:
        """Estimate failure complexity."""
        simple_failures = {
            "null_pointer",
            "type_error",
            "syntax_error",
            "import_error",
            "division_by_zero",
        }
        
        complex_failures = {
            "agent_deadlock",
            "hallucination",
            "memory_corruption",
            "vector_search_failure",
            "distributed_consistency",
            "multi_agent_conflict",
        }
        
        if failure_type in simple_failures:
            return "simple"
        elif failure_type in complex_failures:
            return "complex"
        else:
            return "medium"
    
    def estimate_cost(
        self,
        model: str,
        estimated_tokens: int = 1000,
    ) -> Dict[str, Any]:
        """
        Estimate cost for using a model.
        
        Args:
            model: Model name
            estimated_tokens: Est. tokens for fix
        
        Returns:
            Cost estimate
        """
        # Approximate costs (in USD per 1M tokens)
        pricing = {
            "groq/mixtral-8x7b": 0.27,
            "groq/llama-3-70b": 0.59,
            "openai/gpt-3.5-turbo": 0.50,
            "anthropic/claude-3-sonnet": 3.00,
            "anthropic/claude-3-opus": 15.00,
            "openai/gpt-4": 30.00,
        }
        
        price_per_m = pricing.get(model, 5.00)
        estimated_cost = (estimated_tokens / 1_000_000) * price_per_m
        
        return {
            "model": model,
            "estimated_tokens": estimated_tokens,
            "price_per_1m_tokens": price_per_m,
            "estimated_cost_usd": estimated_cost,
        }
