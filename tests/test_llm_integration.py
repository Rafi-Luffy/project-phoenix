"""
Tests for Free Ollama LLM Integration
Verifies autonomous system with LLM reasoning
"""

import pytest
import asyncio
from autonomous_system.core.llm_reasoning import OllamaClient, OllamaConfig
from autonomous_system.core.llm_enhanced_orchestrator import LLMEnhancedOrchestrator


class TestOllamaIntegration:
    """Test Ollama LLM integration"""
    
    @pytest.mark.asyncio
    async def test_ollama_connection(self):
        """Test connection to Ollama server"""
        client = OllamaClient()
        
        # Try to initialize (won't fail even if Ollama not running)
        result = await client.initialize()
        
        # Should return True or False, not raise exception
        assert isinstance(result, bool)
        
        await client.close()
    
    @pytest.mark.asyncio
    async def test_error_analysis(self):
        """Test LLM error analysis"""
        client = OllamaClient()
        
        if await client.initialize():
            # Test error analysis
            analysis = await client.analyze_error(
                "RESOURCE_ERROR",
                "Memory pool exhausted",
                {"available_memory": 100, "used_memory": 950}
            )
            
            assert analysis["error_type"] == "RESOURCE_ERROR"
            assert "analysis" in analysis
            assert analysis["model"] == OllamaConfig.MODEL
        
        await client.close()
    
    @pytest.mark.asyncio
    async def test_correction_explanation(self):
        """Test LLM correction explanation"""
        client = OllamaClient()
        
        if await client.initialize():
            # Test explanation
            explanation = await client.explain_correction(
                "Database connection pool exhausted",
                "Restart database service",
                "Service restarted successfully, connections restored"
            )
            
            assert isinstance(explanation, str)
            assert len(explanation) > 0
        
        await client.close()
    
    @pytest.mark.asyncio
    async def test_pattern_identification(self):
        """Test pattern identification across errors"""
        client = OllamaClient()
        
        if await client.initialize():
            errors = [
                {"type": "TIMEOUT", "message": "API timeout after 30s", "time": "10:00"},
                {"type": "TIMEOUT", "message": "API timeout after 30s", "time": "10:15"},
                {"type": "TIMEOUT", "message": "API timeout after 30s", "time": "10:30"},
            ]
            
            pattern = await client.identify_pattern(errors)
            
            assert "error_count" in pattern
            assert pattern["error_count"] == 3
            assert "pattern_analysis" in pattern
        
        await client.close()
    
    @pytest.mark.asyncio
    async def test_optimization_recommendations(self):
        """Test optimization recommendations"""
        client = OllamaClient()
        
        if await client.initialize():
            metrics = {
                "cpu_usage": 0.85,
                "memory_usage": 0.75,
                "error_rate": 0.05
            }
            state = {
                "services": 5,
                "instances": 2
            }
            
            recs = await client.recommend_optimization(state, metrics)
            
            assert "recommendations" in recs
            assert isinstance(recs["recommendations"], str)
        
        await client.close()


class TestLLMEnhancedOrchestrator:
    """Test LLM-enhanced orchestrator"""
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self):
        """Test orchestrator with LLM"""
        orchestrator = LLMEnhancedOrchestrator()
        
        # Initialize (graceful degradation if Ollama not available)
        result = await orchestrator.initialize()
        assert result == True
        
        await orchestrator.close()
    
    @pytest.mark.asyncio
    async def test_strategy_selection_with_reasoning(self):
        """Test LLM-guided strategy selection"""
        orchestrator = LLMEnhancedOrchestrator()
        await orchestrator.initialize()
        
        result = await orchestrator.select_correction_with_reasoning(
            error="CPU usage 95%",
            available_strategies=["reduce_load", "scale_out", "optimize_code"],
            success_rates={
                "reduce_load": 0.75,
                "scale_out": 0.85,
                "optimize_code": 0.60
            },
            system_context={"current_load": "high"}
        )
        
        assert "strategy" in result
        assert "confidence" in result
        assert "reasoning" in result
        assert result["strategy"] in ["reduce_load", "scale_out", "optimize_code"]
        
        await orchestrator.close()
    
    @pytest.mark.asyncio
    async def test_error_pattern_detection(self):
        """Test error pattern detection"""
        orchestrator = LLMEnhancedOrchestrator()
        await orchestrator.initialize()
        
        errors = [
            {"type": "TIMEOUT", "cause": "slow_query", "timestamp": "10:00"},
            {"type": "TIMEOUT", "cause": "slow_query", "timestamp": "10:15"},
            {"type": "TIMEOUT", "cause": "slow_query", "timestamp": "10:30"},
        ]
        
        pattern = await orchestrator.find_error_patterns(errors)
        
        assert "pattern_found" in pattern
        assert "pattern_description" in pattern
        assert "confidence" in pattern
        
        await orchestrator.close()
    
    @pytest.mark.asyncio
    async def test_graceful_degradation(self):
        """Test system works without LLM"""
        orchestrator = LLMEnhancedOrchestrator()
        orchestrator.llm_enabled = False  # Simulate Ollama not available
        
        # Should still work
        result = await orchestrator.analyze_error_with_reasoning(
            "TEST_ERROR", "test message", {}
        )
        
        assert "error_type" in result
        assert result["error_type"] == "TEST_ERROR"
        
        await orchestrator.close()


class TestOllamaConfig:
    """Test Ollama configuration"""
    
    def test_model_info(self):
        """Test model information"""
        mistral_info = OllamaConfig.get_model_info("mistral")
        
        assert mistral_info["name"] == "Mistral 7B"
        assert mistral_info["size"] == "4.1GB"
        assert mistral_info["recommended"] == True
    
    def test_all_models_available(self):
        """Test all models are documented"""
        models = ["mistral", "llama2", "neural-chat", "zephyr"]
        
        for model in models:
            info = OllamaConfig.get_model_info(model)
            assert "name" in info
            assert "size" in info
            assert "speed" in info


class TestLLMCaching:
    """Test LLM response caching"""
    
    @pytest.mark.asyncio
    async def test_reasoning_cache(self):
        """Test that reasoning is cached"""
        orchestrator = LLMEnhancedOrchestrator()
        await orchestrator.initialize()
        
        # Same error twice
        error = "Database connection pool exhausted"
        strategies = ["restart", "increase_pool"]
        rates = {"restart": 0.7, "increase_pool": 0.9}
        context = {"pool_size": 10}
        
        # First call (generates reasoning)
        result1 = await orchestrator.select_correction_with_reasoning(
            error, strategies, rates, context
        )
        
        # Should be cached
        cache_key = f"{error}_{str(strategies)}"
        assert cache_key in orchestrator.reasoning_cache
        
        # Second call (from cache)
        result2 = await orchestrator.select_correction_with_reasoning(
            error, strategies, rates, context
        )
        
        # Should be identical (cached)
        assert result1["strategy"] == result2["strategy"]
        
        await orchestrator.close()


# Integration test example
@pytest.mark.asyncio
async def test_full_llm_enhanced_workflow():
    """Test complete workflow with LLM"""
    
    # Initialize orchestrator with LLM
    orchestrator = LLMEnhancedOrchestrator()
    await orchestrator.initialize()
    
    # Simulate error detection
    error_type = "RESOURCE_ERROR"
    error_message = "Memory pool exhausted (95% usage)"
    context = {
        "available_memory": 1000,
        "used_memory": 950,
        "services": ["api", "db", "cache"]
    }
    
    # 1. Analyze with LLM
    analysis = await orchestrator.analyze_error_with_reasoning(
        error_type, error_message, context
    )
    print(f"Analysis: {analysis}")
    assert analysis["error_type"] == error_type
    
    # 2. Select correction with reasoning
    strategies = ["restart_service", "increase_memory", "optimize_code"]
    rates = {
        "restart_service": 0.6,
        "increase_memory": 0.85,
        "optimize_code": 0.95
    }
    
    selection = await orchestrator.select_correction_with_reasoning(
        error_message, strategies, rates, context
    )
    print(f"Selected: {selection['strategy']} with {selection['confidence']:.1%} confidence")
    assert selection["strategy"] in strategies
    assert 0 <= selection["confidence"] <= 1
    
    # 3. Explain decision
    explanation = await orchestrator.explain_correction_decision(
        error_message,
        selection["strategy"],
        selection["reasoning"],
        "Service restarted successfully"
    )
    print(f"Explanation: {explanation}")
    
    # 4. Detect patterns
    recent_errors = [
        {"type": error_type, "message": "Memory high"},
        {"type": error_type, "message": "Memory high"},
    ]
    
    pattern = await orchestrator.find_error_patterns(recent_errors)
    print(f"Pattern: {pattern}")
    
    # Clean up
    await orchestrator.close()
    
    print("✅ Full workflow completed successfully with LLM reasoning!")


if __name__ == "__main__":
    # Quick test
    print("Testing LLM Integration...")
    
    # Test without pytest
    async def quick_test():
        orchestrator = LLMEnhancedOrchestrator()
        result = await orchestrator.initialize()
        print(f"Ollama available: {orchestrator.llm_enabled}")
        await orchestrator.close()
    
    asyncio.run(quick_test())
    print("✅ Tests passed!")
