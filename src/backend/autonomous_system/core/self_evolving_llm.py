"""
Self-Evolving LLM Engine for Project Phoenix
Continuous Learning & Optimization with Ollama Mistral 7B
"""

import json
import asyncio
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import hashlib
import aiohttp
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# SELF-EVOLVING LLM SYSTEM
# ============================================================================

class PromptQuality(Enum):
    """Quality levels for prompt performance"""
    EXCELLENT = 5
    GOOD = 4
    FAIR = 3
    POOR = 2
    CRITICAL = 1

@dataclass
class PromptPerformance:
    """Track how well a prompt performs"""
    prompt_id: str
    prompt: str
    category: str
    success_rate: float = 0.0
    avg_confidence: float = 0.0
    total_uses: int = 0
    successful_uses: int = 0
    avg_latency_ms: float = 0.0
    quality_score: float = 0.0
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def calculate_quality_score(self) -> float:
        """Calculate quality based on success rate and confidence"""
        if self.total_uses == 0:
            return 0.0
        
        success_weight = 0.6
        confidence_weight = 0.3
        latency_weight = 0.1
        
        # Normalize latency (faster is better, cap at 5 seconds)
        latency_score = max(0, 1 - (self.avg_latency_ms / 5000))
        
        quality = (
            (self.success_rate * success_weight) +
            (self.avg_confidence * confidence_weight) +
            (latency_score * latency_weight)
        )
        
        return quality

@dataclass
class PromptVariation:
    """A variation of a prompt template"""
    variation_id: str
    base_prompt_id: str
    prompt: str
    technique: str  # e.g., "few-shot", "chain-of-thought", "step-by-step"
    performance: PromptPerformance = field(default_factory=lambda: PromptPerformance("", "", ""))

class SelfEvolvingLLMEngine:
    """
    Self-evolving LLM engine that:
    1. Tests multiple prompt variations
    2. Learns which prompts work best
    3. Optimizes prompts based on feedback
    4. Continuously improves over time
    """
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "mistral"):
        self.ollama_url = ollama_url
        self.model = model
        
        # Prompt library
        self.prompts: Dict[str, PromptPerformance] = {}
        self.variations: Dict[str, List[PromptVariation]] = {}
        self.learning_history: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.performance_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_confidence": 0.0,
            "improvement_rate": 0.0,
        }
        
        self._init_prompts()
        
        logger.info(f"✅ Self-Evolving LLM Engine initialized")
        logger.info(f"   Model: {self.model}")
        logger.info(f"   Ollama URL: {self.ollama_url}")
    
    def _init_prompts(self):
        """Initialize core prompts with variations"""
        
        # ERROR ANALYSIS PROMPTS
        error_analysis_base = """You are an expert system failure analyst. Analyze the following error and provide:
1. Root cause (be specific)
2. Severity level (CRITICAL/HIGH/MEDIUM/LOW)
3. Confidence score (0-1)
4. Recommended actions

Error Type: {error_type}
Error Message: {error_message}
Context: {context}

Respond in JSON format with keys: root_cause, severity, confidence, actions"""

        self.prompts["error_analysis_base"] = PromptPerformance(
            "error_analysis_base",
            error_analysis_base,
            "error_analysis"
        )
        
        # ERROR ANALYSIS VARIATIONS
        self.variations["error_analysis_base"] = [
            PromptVariation(
                "error_analysis_cot",
                "error_analysis_base",
                """You are an expert system failure analyst. Let's think step by step.

First, understand the error:
- Error Type: {error_type}
- Error Message: {error_message}
- Context: {context}

Now analyze:
1. What are the potential root causes?
2. Which is most likely? Why?
3. What's the severity?
4. How confident are you?
5. What should we do?

Provide JSON response with: root_cause, severity, confidence, actions""",
                "chain-of-thought"
            ),
            PromptVariation(
                "error_analysis_few_shot",
                "error_analysis_base",
                """You are an expert system failure analyst.

Examples of similar errors:
Example 1: Timeout error -> Root cause: Database overload -> Severity: HIGH -> Action: Reduce load
Example 2: Memory error -> Root cause: Memory leak -> Severity: CRITICAL -> Action: Restart service

Now analyze this error:
Error Type: {error_type}
Error Message: {error_message}
Context: {context}

Provide JSON response with: root_cause, severity, confidence (0-1), actions (list)""",
                "few-shot"
            ),
        ]
        
        # PATTERN DETECTION PROMPTS
        pattern_detection_base = """Analyze error patterns from the provided error log.
Identify:
1. Most common error types
2. Recurring patterns
3. Root causes
4. Recommended prevention strategies

Log: {log_data}

Respond in JSON format with: patterns, common_errors, recommendations"""

        self.prompts["pattern_detection_base"] = PromptPerformance(
            "pattern_detection_base",
            pattern_detection_base,
            "pattern_detection"
        )
        
        # OPTIMIZATION PROMPTS
        optimization_base = """Given the current system configuration and recent errors, suggest optimizations.

Current Configuration: {config}
Recent Errors: {recent_errors}
Performance Metrics: {metrics}

Suggest optimizations for:
1. Performance
2. Reliability
3. Resource usage

Respond in JSON format with: performance_improvements, reliability_improvements, resource_improvements"""

        self.prompts["optimization_base"] = PromptPerformance(
            "optimization_base",
            optimization_base,
            "optimization"
        )
    
    async def query(
        self,
        prompt_key: str,
        inputs: Dict[str, Any],
        variations_to_test: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Query LLM with prompt, testing variations if enabled
        
        Args:
            prompt_key: Key of the prompt to use
            inputs: Input variables for the prompt
            variations_to_test: Number of variations to test (for learning)
        
        Returns:
            Best response and metadata
        """
        
        if prompt_key not in self.prompts:
            logger.warning(f"Prompt not found: {prompt_key}")
            return {"error": f"Prompt not found: {prompt_key}"}
        
        base_prompt = self.prompts[prompt_key]
        results = []
        
        # Always use base prompt
        response = await self._query_ollama(base_prompt.prompt, inputs)
        if response:
            results.append({
                "prompt_id": prompt_key,
                "prompt": base_prompt.prompt,
                "response": response,
                "is_variation": False
            })
        
        # Test variations if enabled
        if variations_to_test and prompt_key in self.variations:
            variations = self.variations[prompt_key][:variations_to_test]
            for variation in variations:
                response = await self._query_ollama(variation.prompt, inputs)
                if response:
                    results.append({
                        "prompt_id": variation.variation_id,
                        "prompt": variation.prompt,
                        "response": response,
                        "is_variation": True
                    })
        
        # Select best response and learn
        if results:
            best = self._select_best_response(results)
            await self._learn_from_response(best, inputs)
            return best
        
        return {"error": "No valid responses"}
    
    async def _query_ollama(self, prompt: str, inputs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Query Ollama with formatted prompt"""
        try:
            # Format prompt with inputs
            formatted_prompt = prompt.format(**inputs)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": formatted_prompt,
                        "stream": False,
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "top_k": 40,
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        response_text = data.get("response", "")
                        
                        latency_ms = data.get("total_duration", 0) / 1_000_000

                        # Try to parse JSON response (be tolerant of extra text)
                        parsed: Optional[Dict[str, Any]] = None
                        try:
                            parsed = json.loads(response_text)
                        except json.JSONDecodeError:
                            parsed = self._extract_json_object(response_text)

                        result: Dict[str, Any] = {
                            "raw": response_text,
                            "success": True,
                            "latency_ms": latency_ms,
                        }

                        if isinstance(parsed, dict):
                            result["parsed"] = parsed
                            extracted_conf = self._extract_confidence(parsed)
                            if extracted_conf is not None:
                                result["confidence"] = extracted_conf

                        return result
        except Exception as e:
            logger.error(f"Ollama query error: {e}")
            return None

    @staticmethod
    def _extract_json_object(text: str) -> Optional[Dict[str, Any]]:
        """Best-effort extraction of a JSON object from a model response."""
        if not text:
            return None

        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None

        candidate = text[start : end + 1]
        try:
            parsed = json.loads(candidate)
            return parsed if isinstance(parsed, dict) else None
        except Exception:
            return None

    @staticmethod
    def _extract_confidence(parsed: Dict[str, Any]) -> Optional[float]:
        """Extract a 0..1 confidence from a parsed JSON response."""
        if not isinstance(parsed, dict):
            return None

        value = parsed.get("confidence")
        if value is None:
            return None

        try:
            confidence = float(value)
        except Exception:
            return None

        if confidence != confidence:  # NaN
            return None

        return max(0.0, min(1.0, confidence))
    
    def _select_best_response(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select best response based on quality metrics"""
        # Score each response
        scored = []
        for result in results:
            score = self._score_response(result)
            scored.append((score, result))
        
        # Return highest scoring response
        best_score, best_result = max(scored, key=lambda x: x[0])
        best_result["selection_score"] = best_score
        return best_result
    
    def _score_response(self, result: Dict[str, Any]) -> float:
        """Score a response based on quality metrics"""
        if not result.get("success"):
            return 0.0
        
        score = 1.0
        
        # Penalize latency
        latency = result.get("response", {}).get("latency_ms", 0)
        if latency > 5000:
            score *= 0.5
        elif latency > 2000:
            score *= 0.8
        
        # Bonus for JSON parsing success
        if result["response"].get("parsed"):
            score *= 1.1

        # Prefer higher-confidence responses when provided by the model
        model_conf = result["response"].get("confidence")
        if model_conf is not None:
            try:
                score *= (0.6 + (float(model_conf) * 0.4))
            except Exception:
                pass
        
        # Bonus for variations (they're learning)
        if result.get("is_variation"):
            score *= 0.95  # Slight penalty to prefer base (but test variations)
        
        return score
    
    async def _learn_from_response(self, result: Dict[str, Any], inputs: Dict[str, Any]):
        """Learn from response to improve future prompts"""
        prompt_id = result["prompt_id"]
        
        # Update performance metrics
        if prompt_id in self.prompts:
            perf = self.prompts[prompt_id]
            
            # Update statistics
            perf.total_uses += 1
            perf.avg_latency_ms = (
                (perf.avg_latency_ms * (perf.total_uses - 1) + 
                 result["response"].get("latency_ms", 0)) / perf.total_uses
            )
            
            if result["response"].get("success"):
                perf.successful_uses += 1
            
            perf.success_rate = perf.successful_uses / perf.total_uses if perf.total_uses > 0 else 0
            perf.quality_score = perf.calculate_quality_score()
            perf.last_updated = datetime.now().isoformat()
            
            # Record learning event
            self.learning_history.append({
                "timestamp": datetime.now().isoformat(),
                "prompt_id": prompt_id,
                "success": result["response"].get("success"),
                "quality_score": perf.quality_score,
                "latency_ms": result["response"].get("latency_ms", 0)
            })
        
        # Update global stats
        self.performance_stats["total_requests"] += 1
        if result["response"].get("success"):
            self.performance_stats["successful_requests"] += 1
        else:
            self.performance_stats["failed_requests"] += 1
        
        # Calculate success rate
        if self.performance_stats["total_requests"] > 0:
            success_rate = (
                self.performance_stats["successful_requests"] / 
                self.performance_stats["total_requests"]
            )
            self.performance_stats["improvement_rate"] = success_rate
    
    def get_best_prompts(self, category: Optional[str] = None, top_k: int = 5) -> List[PromptPerformance]:
        """Get best performing prompts"""
        prompts = self.prompts.values()
        
        if category:
            prompts = [p for p in prompts if p.category == category]
        
        # Sort by quality score
        sorted_prompts = sorted(prompts, key=lambda p: p.quality_score, reverse=True)
        
        return sorted_prompts[:top_k]
    
    def get_learning_report(self) -> Dict[str, Any]:
        """Generate comprehensive learning report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "performance_stats": self.performance_stats,
            "best_prompts": [
                asdict(p) for p in self.get_best_prompts(top_k=10)
            ],
            "total_learning_events": len(self.learning_history),
            "model": self.model,
            "ollama_url": self.ollama_url,
        }
    
    def save_learning(self, filepath: str = "llm_learning.json"):
        """Save learning data for persistence"""
        data = {
            "prompts": {k: asdict(v) for k, v in self.prompts.items()},
            "variations": {
                k: [asdict(v) for v in vs] 
                for k, vs in self.variations.items()
            },
            "learning_history": self.learning_history[-1000:],  # Keep last 1000
            "performance_stats": self.performance_stats,
            "saved_at": datetime.now().isoformat(),
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"✅ Learning data saved to {filepath}")
    
    def load_learning(self, filepath: str = "llm_learning.json"):
        """Load saved learning data"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Load prompts
            for key, p_dict in data.get("prompts", {}).items():
                self.prompts[key] = PromptPerformance(**p_dict)
            
            # Load learning history
            self.learning_history = data.get("learning_history", [])
            self.performance_stats = data.get("performance_stats", self.performance_stats)
            
            logger.info(f"✅ Learning data loaded from {filepath}")
        except FileNotFoundError:
            logger.info(f"No previous learning data found at {filepath}")


# ============================================================================
# ASYNC WRAPPER FOR FASTAPI
# ============================================================================

# Global instance
_llm_engine: Optional[SelfEvolvingLLMEngine] = None

async def get_llm_engine() -> SelfEvolvingLLMEngine:
    """Get or create LLM engine instance"""
    global _llm_engine
    
    if _llm_engine is None:
        _llm_engine = SelfEvolvingLLMEngine(
            ollama_url=os.environ.get("OLLAMA_URL", "http://localhost:11434"),
            model=os.environ.get("OLLAMA_MODEL", "mistral")
        )
        
        # Load previous learning
        _llm_engine.load_learning()
    
    return _llm_engine

async def analyze_error_with_evolution(
    error_type: str,
    error_message: str,
    context: Dict[str, Any],
    test_variations: bool = False
) -> Dict[str, Any]:
    """
    Analyze error using self-evolving LLM
    
    Args:
        error_type: Type of error
        error_message: Error message
        context: Additional context
        test_variations: Whether to test prompt variations
    
    Returns:
        Analysis result with learning applied
    """
    engine = await get_llm_engine()
    
    result = await engine.query(
        "error_analysis_base",
        {
            "error_type": error_type,
            "error_message": error_message,
            "context": json.dumps(context)
        },
        variations_to_test=2 if test_variations else None
    )
    
    # Save learning periodically
    if engine.performance_stats["total_requests"] % 10 == 0:
        engine.save_learning()
    
    return result


if __name__ == "__main__":
    # Test the engine
    async def test():
        engine = SelfEvolvingLLMEngine()
        
        # Test error analysis
        result = await engine.query(
            "error_analysis_base",
            {
                "error_type": "TIMEOUT_ERROR",
                "error_message": "Database connection timeout after 30 seconds",
                "context": '{"service": "payment-api", "retries": 2}'
            },
            variations_to_test=2
        )
        
        print(json.dumps(engine.get_learning_report(), indent=2, default=str))
        engine.save_learning()
    
    asyncio.run(test())
