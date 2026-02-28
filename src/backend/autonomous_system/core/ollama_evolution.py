"""
Self-Evolving Ollama LLM System
Continuously learns and improves from test cases and user interactions
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class OllamaEvolutionManager:
    """Manages self-evolution of Ollama model through learning"""
    
    def __init__(self, model_name: str = "mistral:latest"):
        self.model_name = model_name
        self.learning_dir = Path("./ollama_learning_data")
        self.learning_dir.mkdir(exist_ok=True)
        
        # Learning data storage
        self.prompt_versions_file = self.learning_dir / "prompt_versions.json"
        self.test_results_file = self.learning_dir / "test_results.json"
        self.performance_metrics_file = self.learning_dir / "performance_metrics.json"
        self.pattern_library_file = self.learning_dir / "pattern_library.json"
        
        # Initialize files if they don't exist
        self._initialize_files()
        
        # Load existing data
        self.prompt_versions = self._load_json(self.prompt_versions_file)
        self.test_results = self._load_json(self.test_results_file)
        self.performance_metrics = self._load_json(self.performance_metrics_file)
        self.pattern_library = self._load_json(self.pattern_library_file)
    
    def _initialize_files(self):
        """Initialize learning data files"""
        files = [
            (self.prompt_versions_file, {}),
            (self.test_results_file, []),
            (self.performance_metrics_file, {}),
            (self.pattern_library_file, {})
        ]
        
        for file_path, default_content in files:
            if not file_path.exists():
                with open(file_path, 'w') as f:
                    json.dump(default_content, f, indent=2)
    
    def _load_json(self, file_path: Path) -> Any:
        """Load JSON file safely"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load {file_path}: {e}")
            return {} if 'versions' in str(file_path) or 'metrics' in str(file_path) or 'pattern' in str(file_path) else []
    
    def _save_json(self, file_path: Path, data: Any):
        """Save JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save {file_path}: {e}")
    
    def record_test_case(self, test_name: str, prompt: str, expected_response: str, 
                        actual_response: str, success: bool, duration_ms: float):
        """Record a test case for learning"""
        test_record = {
            "timestamp": datetime.now().isoformat(),
            "test_name": test_name,
            "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest(),
            "prompt": prompt,
            "expected": expected_response,
            "actual": actual_response,
            "success": success,
            "duration_ms": duration_ms,
            "confidence_score": self._calculate_confidence(actual_response, expected_response)
        }
        
        self.test_results.append(test_record)
        self._save_json(self.test_results_file, self.test_results)
        
        # Update pattern library
        if success:
            self._learn_pattern(prompt, actual_response)
        
        logger.info(f"Recorded test: {test_name} - Success: {success}")
    
    def _calculate_confidence(self, actual: str, expected: str) -> float:
        """Calculate confidence score based on response similarity"""
        if not actual or not expected:
            return 0.0
        
        actual_tokens = set(actual.lower().split())
        expected_tokens = set(expected.lower().split())
        
        if not expected_tokens:
            return 1.0
        
        overlap = len(actual_tokens.intersection(expected_tokens))
        confidence = overlap / len(expected_tokens)
        return min(1.0, confidence)
    
    def _learn_pattern(self, prompt: str, response: str):
        """Learn patterns from successful test cases"""
        prompt_type = self._classify_prompt(prompt)
        
        if prompt_type not in self.pattern_library:
            self.pattern_library[prompt_type] = {
                "examples": [],
                "success_count": 0,
                "total_count": 0,
                "avg_confidence": 0.0
            }
        
        pattern_data = self.pattern_library[prompt_type]
        
        # Add example
        confidence = self._calculate_confidence(response, response)
        pattern_data["examples"].append({
            "prompt": prompt[:500],  # Store first 500 chars
            "response": response[:500],
            "timestamp": datetime.now().isoformat(),
            "confidence": confidence
        })
        
        # Keep only top 10 examples
        if len(pattern_data["examples"]) > 10:
            pattern_data["examples"] = sorted(
                pattern_data["examples"],
                key=lambda x: x["confidence"],
                reverse=True
            )[:10]
        
        # Update stats
        pattern_data["success_count"] += 1
        pattern_data["total_count"] += 1
        pattern_data["avg_confidence"] = sum(
            e["confidence"] for e in pattern_data["examples"]
        ) / len(pattern_data["examples"])
        
        self._save_json(self.pattern_library_file, self.pattern_library)
    
    def _classify_prompt(self, prompt: str) -> str:
        """Classify prompt into categories"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["error", "fix", "repair", "heal", "crash"]):
            return "error_handling"
        elif any(word in prompt_lower for word in ["analyze", "diagnose", "understand", "explain"]):
            return "analysis"
        elif any(word in prompt_lower for word in ["optimize", "improve", "performance", "speed"]):
            return "optimization"
        elif any(word in prompt_lower for word in ["test", "verify", "check", "validate"]):
            return "testing"
        elif any(word in prompt_lower for word in ["create", "generate", "build", "make"]):
            return "generation"
        else:
            return "general"
    
    def record_performance_metric(self, metric_name: str, value: float, 
                                 timestamp: Optional[datetime] = None):
        """Record performance metric for learning"""
        if timestamp is None:
            timestamp = datetime.now()
        
        if metric_name not in self.performance_metrics:
            self.performance_metrics[metric_name] = []
        
        self.performance_metrics[metric_name].append({
            "timestamp": timestamp.isoformat(),
            "value": value
        })
        
        # Keep only last 1000 records per metric
        if len(self.performance_metrics[metric_name]) > 1000:
            self.performance_metrics[metric_name] = self.performance_metrics[metric_name][-1000:]
        
        self._save_json(self.performance_metrics_file, self.performance_metrics)
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of learning progress"""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for t in self.test_results if t.get("success", False))
        
        avg_confidence = 0.0
        if self.test_results:
            avg_confidence = sum(t.get("confidence_score", 0) for t in self.test_results) / total_tests
        
        return {
            "total_tests_recorded": total_tests,
            "successful_tests": successful_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "avg_confidence": avg_confidence,
            "patterns_learned": len(self.pattern_library),
            "pattern_categories": list(self.pattern_library.keys()),
            "top_patterns": self._get_top_patterns(),
            "performance_metrics": {
                name: {
                    "latest": values[-1]["value"] if values else None,
                    "avg": sum(v["value"] for v in values) / len(values) if values else None,
                    "min": min(v["value"] for v in values) if values else None,
                    "max": max(v["value"] for v in values) if values else None,
                }
                for name, values in self.performance_metrics.items()
            }
        }
    
    def _get_top_patterns(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top learned patterns"""
        patterns = [
            {
                "category": category,
                "success_count": data["success_count"],
                "success_rate": data["success_count"] / data["total_count"] if data["total_count"] > 0 else 0,
                "avg_confidence": data["avg_confidence"],
                "examples_count": len(data["examples"])
            }
            for category, data in self.pattern_library.items()
        ]
        
        return sorted(patterns, key=lambda x: x["success_rate"], reverse=True)[:limit]
    
    def generate_optimized_prompt(self, prompt_type: str, base_prompt: str) -> str:
        """Generate optimized prompt based on learned patterns"""
        if prompt_type not in self.pattern_library:
            return base_prompt
        
        pattern_data = self.pattern_library[prompt_type]
        
        if not pattern_data["examples"]:
            return base_prompt
        
        # Get best example for this category
        best_example = pattern_data["examples"][0]
        
        # Create optimized prompt with context from successful examples
        optimized = f"""{base_prompt}

Context from successful similar prompts:
- Pattern success rate: {pattern_data['success_count']}/{pattern_data['total_count']}
- Average confidence: {pattern_data['avg_confidence']:.2%}
- Example approach: {best_example['prompt'][:200]}...

Please provide a response following the pattern of successful similar requests."""
        
        return optimized
    
    def export_learning_data(self, export_path: Optional[str] = None) -> str:
        """Export learning data for analysis"""
        if export_path is None:
            export_path = f"ollama_learning_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "model": self.model_name,
            "summary": self.get_learning_summary(),
            "test_results": self.test_results[-100:],  # Last 100 tests
            "pattern_library": self.pattern_library,
            "performance_metrics": self.performance_metrics
        }
        
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Learning data exported to {export_path}")
        return export_path
    
    def create_fine_tuning_dataset(self) -> List[Dict[str, str]]:
        """Create dataset for fine-tuning based on learned patterns"""
        dataset = []
        
        for test in self.test_results:
            if test.get("success", False) and test.get("confidence_score", 0) > 0.8:
                dataset.append({
                    "input": test["prompt"],
                    "output": test["actual"]
                })
        
        return dataset


class OllamaIntegrationWithEvolution:
    """Ollama integration with self-evolution capabilities"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "mistral:latest"):
        self.base_url = base_url
        self.model_name = model_name
        self.evolution_manager = OllamaEvolutionManager(model_name)
        import requests
        self.session = requests.Session()
    
    async def analyze_error(self, error_type: str, error_message: str, 
                           context: str = "") -> Dict[str, Any]:
        """Analyze error with self-evolution"""
        prompt = f"""Analyze this error and provide a solution:
        
Error Type: {error_type}
Error Message: {error_message}
Context: {context}

Provide:
1. Root cause analysis
2. Immediate solution steps
3. Long-term prevention strategies"""
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result.get("response", "")
                
                # Record for learning
                self.evolution_manager.record_test_case(
                    "error_analysis",
                    prompt,
                    "error_analysis_response",
                    analysis,
                    True,
                    0.0
                )
                
                return {
                    "success": True,
                    "analysis": analysis,
                    "model": self.model_name
                }
        except Exception as e:
            logger.error(f"Error analysis failed: {e}")
        
        return {"success": False, "error": "Analysis failed"}
    
    def get_evolution_status(self) -> Dict[str, Any]:
        """Get current evolution status"""
        summary = self.evolution_manager.get_learning_summary()
        return {
            "model": self.model_name,
            "learning_status": summary,
            "evolution_enabled": True,
            "learning_data_location": str(self.evolution_manager.learning_dir)
        }


# Global instance
_ollama_evolution_instance: Optional[OllamaIntegrationWithEvolution] = None


def get_ollama_evolution() -> OllamaIntegrationWithEvolution:
    """Get or create global Ollama evolution instance"""
    global _ollama_evolution_instance
    if _ollama_evolution_instance is None:
        _ollama_evolution_instance = OllamaIntegrationWithEvolution()
    return _ollama_evolution_instance


if __name__ == "__main__":
    # Example usage
    manager = OllamaEvolutionManager()
    
    # Record test cases
    manager.record_test_case(
        "error_fix_test",
        "How to fix a database connection timeout?",
        "Check connection pool settings",
        "Verify connection pool size, increase timeout, check network connectivity",
        True,
        1500.0
    )
    
    # Record performance
    manager.record_performance_metric("llm_response_time_ms", 1500.0)
    manager.record_performance_metric("error_detection_accuracy", 0.95)
    
    # Get summary
    summary = manager.get_learning_summary()
    print(json.dumps(summary, indent=2))
    
    # Export data
    manager.export_learning_data()
