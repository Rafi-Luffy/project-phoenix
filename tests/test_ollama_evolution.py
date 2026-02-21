"""
Comprehensive tests for Ollama integration and self-evolution system
"""

import pytest
import json
from datetime import datetime
import asyncio
from pathlib import Path

from autonomous_system.core.ollama_evolution import (
    OllamaEvolutionManager,
    OllamaIntegrationWithEvolution,
    get_ollama_evolution
)


class TestOllamaEvolutionManager:
    """Test cases for Ollama evolution manager"""
    
    @pytest.fixture
    def manager(self, tmp_path):
        """Create manager instance with temp directory"""
        manager = OllamaEvolutionManager()
        manager.learning_dir = tmp_path / "learning_data"
        manager.learning_dir.mkdir(exist_ok=True)
        manager._initialize_files()
        return manager
    
    def test_initialization(self, manager):
        """Test manager initialization"""
        assert manager.model_name == "mistral:latest"
        assert manager.learning_dir.exists()
        assert isinstance(manager.prompt_versions, dict)
        assert isinstance(manager.test_results, list)
        assert isinstance(manager.performance_metrics, dict)
        assert isinstance(manager.pattern_library, dict)
    
    def test_record_test_case(self, manager):
        """Test recording test cases"""
        manager.record_test_case(
            "test_error_analysis",
            "How to fix database timeout?",
            "expected_response",
            "actual_response",
            True,
            150.0
        )
        
        assert len(manager.test_results) == 1
        assert manager.test_results[0]["test_name"] == "test_error_analysis"
        assert manager.test_results[0]["success"] is True
    
    def test_calculate_confidence(self, manager):
        """Test confidence score calculation"""
        confidence1 = manager._calculate_confidence(
            "This is a test response",
            "This is a test response"
        )
        assert confidence1 == 1.0
        
        confidence2 = manager._calculate_confidence(
            "Different response text",
            "This is a test response"
        )
        assert 0 <= confidence2 < 1.0
        
        confidence3 = manager._calculate_confidence("", "test")
        assert confidence3 == 0.0
    
    def test_classify_prompt(self, manager):
        """Test prompt classification"""
        assert manager._classify_prompt("How to fix this error?") == "error_handling"
        assert manager._classify_prompt("Analyze the system") == "analysis"
        assert manager._classify_prompt("Optimize performance") == "optimization"
        assert manager._classify_prompt("Test the code") == "testing"
        assert manager._classify_prompt("Create a new feature") == "generation"
        assert manager._classify_prompt("Random topic") == "general"
    
    def test_learn_pattern(self, manager):
        """Test pattern learning"""
        manager._learn_pattern(
            "How to fix error X?",
            "Try solution A, B, and C"
        )
        
        assert "error_handling" in manager.pattern_library
        assert len(manager.pattern_library["error_handling"]["examples"]) > 0
        assert manager.pattern_library["error_handling"]["success_count"] == 1
    
    def test_record_performance_metric(self, manager):
        """Test performance metric recording"""
        manager.record_performance_metric("response_time_ms", 150.0)
        manager.record_performance_metric("response_time_ms", 200.0)
        manager.record_performance_metric("accuracy_score", 0.95)
        
        assert "response_time_ms" in manager.performance_metrics
        assert len(manager.performance_metrics["response_time_ms"]) == 2
        assert "accuracy_score" in manager.performance_metrics
    
    def test_get_learning_summary(self, manager):
        """Test learning summary generation"""
        manager.record_test_case(
            "test1",
            "prompt1",
            "expected1",
            "actual1",
            True,
            100.0
        )
        manager.record_test_case(
            "test2",
            "prompt2",
            "expected2",
            "actual2",
            False,
            150.0
        )
        
        summary = manager.get_learning_summary()
        
        assert summary["total_tests_recorded"] == 2
        assert summary["successful_tests"] == 1
        assert summary["success_rate"] == 0.5
        assert 0 <= summary["avg_confidence"] <= 1.0
    
    def test_get_top_patterns(self, manager):
        """Test top patterns retrieval"""
        # Add multiple patterns
        for i in range(5):
            manager._learn_pattern(
                f"Error handling test {i}",
                f"Solution {i}"
            )
        
        top = manager._get_top_patterns(limit=3)
        assert len(top) <= 3
        assert all("category" in p and "success_rate" in p for p in top)
    
    def test_generate_optimized_prompt(self, manager):
        """Test prompt optimization"""
        manager._learn_pattern(
            "Database connection timeout",
            "Increase connection pool size"
        )
        
        optimized = manager.generate_optimized_prompt(
            "error_handling",
            "How to fix database timeout?"
        )
        
        assert len(optimized) > len("How to fix database timeout?")
        assert "Context from successful" in optimized
    
    def test_export_learning_data(self, manager, tmp_path):
        """Test learning data export"""
        manager.record_test_case(
            "test1",
            "prompt1",
            "expected1",
            "actual1",
            True,
            100.0
        )
        
        export_path = str(tmp_path / "export.json")
        result = manager.export_learning_data(export_path)
        
        assert Path(result).exists()
        with open(result, 'r') as f:
            data = json.load(f)
            assert "summary" in data
            assert "model" in data
    
    def test_create_fine_tuning_dataset(self, manager):
        """Test fine-tuning dataset creation"""
        manager.record_test_case(
            "test1",
            "Good prompt",
            "expected",
            "actual",
            True,
            100.0
        )
        manager.record_test_case(
            "test2",
            "Bad prompt",
            "expected",
            "actual",
            False,
            100.0
        )
        
        dataset = manager.create_fine_tuning_dataset()
        # Should only include successful tests with high confidence
        assert isinstance(dataset, list)


class TestOllamaIntegrationWithEvolution:
    """Test cases for Ollama integration with evolution"""
    
    @pytest.fixture
    def integration(self):
        """Create integration instance"""
        return OllamaIntegrationWithEvolution(
            base_url="http://localhost:11434",
            model_name="mistral:latest"
        )
    
    def test_initialization(self, integration):
        """Test integration initialization"""
        assert integration.model_name == "mistral:latest"
        assert integration.evolution_manager is not None
        assert integration.session is not None
    
    @pytest.mark.asyncio
    async def test_analyze_error(self, integration):
        """Test error analysis"""
        result = await integration.analyze_error(
            "ConnectionTimeout",
            "Database connection timed out",
            "PostgreSQL service"
        )
        
        assert isinstance(result, dict)
        # May succeed or fail depending on Ollama availability
        # But should handle gracefully
    
    def test_get_evolution_status(self, integration):
        """Test evolution status retrieval"""
        status = integration.get_evolution_status()
        
        assert "model" in status
        assert "learning_status" in status
        assert "evolution_enabled" in status
        assert status["evolution_enabled"] is True


class TestOllamaEvolutionIntegration:
    """Integration tests for Ollama evolution system"""
    
    @pytest.fixture
    def manager(self, tmp_path):
        """Create manager with temp directory"""
        manager = OllamaEvolutionManager()
        manager.learning_dir = tmp_path / "learning_data"
        manager.learning_dir.mkdir(exist_ok=True)
        manager._initialize_files()
        return manager
    
    def test_full_learning_cycle(self, manager):
        """Test complete learning cycle"""
        # Record successful test cases
        test_cases = [
            ("error_fix_1", "How to fix database error?", "Check connection", True, 100),
            ("error_fix_2", "How to fix timeout?", "Increase timeout", True, 150),
            ("analysis_1", "Analyze system", "System is working", True, 120),
        ]
        
        for name, prompt, response, success, duration in test_cases:
            manager.record_test_case(name, prompt, response, response, success, float(duration))
        
        # Record metrics
        manager.record_performance_metric("response_time_ms", 110.0)
        manager.record_performance_metric("accuracy", 0.95)
        
        # Get summary
        summary = manager.get_learning_summary()
        
        assert summary["total_tests_recorded"] == 3
        assert summary["successful_tests"] == 3
        assert summary["success_rate"] == 1.0
        assert len(summary["pattern_categories"]) > 0
    
    def test_performance_metric_tracking(self, manager):
        """Test performance metric tracking"""
        metrics = [100, 150, 120, 110, 200, 90]
        
        for metric in metrics:
            manager.record_performance_metric("response_time_ms", float(metric))
        
        summary = manager.get_learning_summary()
        perf_data = summary["performance_metrics"]["response_time_ms"]
        
        assert perf_data["latest"] == 90  # Last value
        assert perf_data["min"] == 90
        assert perf_data["max"] == 200
        assert 120 < perf_data["avg"] < 140


class TestOllamaEvolutionConcurrency:
    """Test concurrent access to evolution system"""
    
    @pytest.fixture
    def manager(self, tmp_path):
        """Create manager with temp directory"""
        manager = OllamaEvolutionManager()
        manager.learning_dir = tmp_path / "learning_data"
        manager.learning_dir.mkdir(exist_ok=True)
        manager._initialize_files()
        return manager
    
    def test_concurrent_recording(self, manager):
        """Test concurrent test case recording"""
        import concurrent.futures
        
        def record_case(i):
            manager.record_test_case(
                f"test_{i}",
                f"prompt_{i}",
                f"expected_{i}",
                f"actual_{i}",
                True,
                100.0
            )
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(record_case, i) for i in range(10)]
            for future in concurrent.futures.as_completed(futures):
                future.result()
        
        assert len(manager.test_results) >= 10


class TestOllamaEvolutionEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.fixture
    def manager(self, tmp_path):
        """Create manager with temp directory"""
        manager = OllamaEvolutionManager()
        manager.learning_dir = tmp_path / "learning_data"
        manager.learning_dir.mkdir(exist_ok=True)
        manager._initialize_files()
        return manager
    
    def test_empty_prompt(self, manager):
        """Test handling of empty prompt"""
        manager.record_test_case(
            "empty_test",
            "",
            "expected",
            "actual",
            False,
            0.0
        )
        
        assert len(manager.test_results) == 1
        assert manager.test_results[0]["prompt"] == ""
    
    def test_very_long_prompt(self, manager):
        """Test handling of very long prompt"""
        long_prompt = "x" * 10000
        manager.record_test_case(
            "long_test",
            long_prompt,
            "expected",
            "actual",
            True,
            500.0
        )
        
        assert len(manager.test_results) == 1
    
    def test_special_characters(self, manager):
        """Test handling of special characters"""
        manager.record_test_case(
            "special_test",
            "Test with special: !@#$%^&*()_+-=[]{}|;':\",./<>?",
            "expected",
            "actual",
            True,
            100.0
        )
        
        assert len(manager.test_results) == 1
    
    def test_zero_metrics(self, manager):
        """Test recording zero values"""
        manager.record_performance_metric("zero_metric", 0.0)
        manager.record_performance_metric("zero_metric", 0.0)
        
        summary = manager.get_learning_summary()
        assert summary["performance_metrics"]["zero_metric"]["min"] == 0.0


# Global instance test
def test_global_ollama_evolution_instance():
    """Test global instance singleton pattern"""
    instance1 = get_ollama_evolution()
    instance2 = get_ollama_evolution()
    
    assert instance1 is instance2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
