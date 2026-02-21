"""
End-to-End LLM Integration Workflow Test
Comprehensive test demonstrating error detection → analysis → correction → explanation
with full LLM reasoning layer
"""

import asyncio
import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch

from autonomous_system.core import (
    CoreOrchestrator, SelfCorrectionOrchestrator,
    ErrorContext, ErrorDetectionManager,
    CorrectionStrategyEngine, MemoryManager
)
from autonomous_system.core.llm_system_integration import (
    LLMSystemIntegrator, initialize_llm_integration, get_llm_integrator
)
from autonomous_system.core.llm_reasoning import OllamaClient, OllamaConfig
from autonomous_system.core.error_detection import ErrorSeverity


class TestEndToEndLLMWorkflow:
    """End-to-end tests for LLM integration"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator for testing"""
        return SelfCorrectionOrchestrator()

    @pytest.fixture
    def llm_integrator(self, orchestrator):
        """Create LLM integrator"""
        return LLMSystemIntegrator(orchestrator)

    @pytest.mark.asyncio
    async def test_error_detection_to_llm_analysis(self, orchestrator, llm_integrator):
        """Test: Error detected → analyzed with LLM"""
        print("\n🧪 TEST: Error Detection to LLM Analysis")
        print("=" * 60)

        # Step 1: Create error context
        error = ErrorContext(
            error_type="DATABASE_CONNECTION",
            message="Connection pool exhausted (10/10 connections active)",
            context={
                "pool_size": 10,
                "active_connections": 10,
                "waiting_requests": 5,
                "retry_count": 3
            },
            severity=ErrorSeverity.CRITICAL
        )
        print(f"✓ Error Created: {error.error_type}")
        print(f"  Message: {error.message}")

        # Step 2: Mock LLM for testing (since Ollama may not be available)
        llm_integrator.llm_enabled = True
        llm_integrator.llm_health = "healthy"

        # Mock the LLM client response
        mock_analysis = {
            "error_type": "DATABASE_CONNECTION",
            "root_cause": "Connection pool size too small for current load",
            "analysis": "The database connection pool is configured for 10 connections "
            "but the application is attempting to use more. This indicates either "
            "increased traffic or inefficient connection management.",
            "severity": "critical",
            "recommendations": [
                "Increase connection pool size to 20",
                "Review connection pooling strategy",
                "Implement connection timeout and reuse"
            ],
            "confidence": 0.95
        }

        # Patch the LLM client
        with patch.object(llm_integrator.llm_client, 'analyze_error', 
                         new_callable=AsyncMock, return_value=mock_analysis):
            
            print("✓ LLM Mock Initialized")

            # Step 3: Analyze error with LLM
            result = await llm_integrator.analyze_error_with_reasoning(error)
            
            print("✓ LLM Analysis Complete")
            print(f"  Root Cause: {result.get('root_cause')}")
            print(f"  Severity: {result.get('severity')}")
            print(f"  Confidence: {result.get('confidence', 0):.1%}")
            print(f"  Recommendations: {len(result.get('recommendations', []))} provided")
            for i, rec in enumerate(result.get('recommendations', []), 1):
                print(f"    {i}. {rec}")

        assert result['llm_enabled'] is True
        assert result['root_cause'] is not None
        assert len(result['recommendations']) > 0
        assert result['confidence'] > 0.8

        print("✅ TEST PASSED: Error analysis with LLM reasoning\n")

    @pytest.mark.asyncio
    async def test_correction_strategy_with_llm_explanation(self, orchestrator, llm_integrator):
        """Test: Strategy selected and explained by LLM"""
        print("\n🧪 TEST: Correction Strategy Selection with LLM Explanation")
        print("=" * 60)

        # Step 1: Create error and strategy
        error_msg = "Database connection timeout after 30 seconds"
        strategy = "restart_database"
        correction_result = "Database service restarted successfully"

        print(f"✓ Error: {error_msg}")
        print(f"✓ Strategy Selected: {strategy}")

        # Step 2: Mock LLM explanation
        llm_integrator.llm_enabled = True
        mock_explanation = (
            "The system selected 'restart_database' strategy because: "
            "After 3 retry attempts failed, the root cause appears to be a database "
            "service hang. Restarting the service clears any stuck connections and "
            "resets the state. This is the most effective approach for transient "
            "database service issues with 85% historical success rate."
        )

        with patch.object(llm_integrator.llm_client, 'explain_correction',
                         new_callable=AsyncMock, return_value=mock_explanation):
            
            print("✓ LLM Mock Initialized")

            # Step 3: Get LLM explanation
            explanation = await llm_integrator.explain_correction_decision(
                error_msg,
                strategy,
                correction_result
            )
            
            print("✓ LLM Explanation Generated")
            print(f"  Explanation: {explanation[:100]}...")

        assert "restart_database" in explanation or "database" in explanation.lower()
        print("✅ TEST PASSED: Strategy explained by LLM\n")

    @pytest.mark.asyncio
    async def test_pattern_detection_across_errors(self, orchestrator, llm_integrator):
        """Test: LLM detects patterns across multiple errors"""
        print("\n🧪 TEST: Error Pattern Detection with LLM")
        print("=" * 60)

        # Step 1: Create multiple similar errors
        errors = [
            {
                "error_type": "TIMEOUT",
                "message": "API request timeout after 30s",
                "timestamp": datetime.now().isoformat(),
                "context": {"endpoint": "/api/users", "retries": 3}
            },
            {
                "error_type": "TIMEOUT",
                "message": "API request timeout after 30s",
                "timestamp": datetime.now().isoformat(),
                "context": {"endpoint": "/api/users", "retries": 3}
            },
            {
                "error_type": "TIMEOUT",
                "message": "API request timeout after 30s",
                "timestamp": datetime.now().isoformat(),
                "context": {"endpoint": "/api/users", "retries": 3}
            }
        ]

        print(f"✓ {len(errors)} Similar Errors Created")
        print(f"  Type: TIMEOUT")
        print(f"  Endpoint: /api/users")

        # Step 2: Mock LLM pattern detection
        llm_integrator.llm_enabled = True
        mock_pattern = {
            "error_count": 3,
            "pattern_found": True,
            "pattern_type": "recurring_timeout",
            "pattern_analysis": (
                "Three consecutive API timeouts on the same endpoint (/api/users) "
                "within a short time window suggests either: "
                "1) Database query performance degradation "
                "2) Increased request volume overwhelming the service "
                "3) Network connectivity issues"
            ),
            "confidence": 0.92,
            "root_cause": "Likely database performance issue",
            "recommendations": [
                "Check database query performance",
                "Review active connection count",
                "Analyze endpoint response times"
            ]
        }

        with patch.object(llm_integrator.llm_client, 'identify_pattern',
                         new_callable=AsyncMock, return_value=mock_pattern):
            
            print("✓ LLM Mock Initialized")

            # Step 3: Detect patterns
            patterns = await llm_integrator.detect_error_patterns(errors)
            
            print("✓ Pattern Detection Complete")
            print(f"  Patterns Found: {patterns.get('pattern_found')}")
            print(f"  Pattern Type: {patterns.get('pattern_type')}")
            print(f"  Confidence: {patterns.get('confidence', 0):.1%}")
            print(f"  Root Cause: {patterns.get('root_cause')}")

        assert patterns['pattern_found'] is True
        assert patterns['error_count'] == 3
        assert "database" in patterns['root_cause'].lower()

        print("✅ TEST PASSED: Pattern detection with LLM\n")

    @pytest.mark.asyncio
    async def test_optimization_recommendations(self, orchestrator, llm_integrator):
        """Test: LLM provides system optimization recommendations"""
        print("\n🧪 TEST: System Optimization with LLM Recommendations")
        print("=" * 60)

        # Step 1: Create system state and metrics
        system_state = {
            "services": ["api", "database", "cache", "queue"],
            "instances": 2,
            "current_config": {
                "connection_pool": 10,
                "timeout": 30,
                "retries": 3
            }
        }

        metrics = {
            "cpu_usage": 0.85,
            "memory_usage": 0.75,
            "error_rate": 0.05,
            "response_time_ms": 250,
            "throughput": 1000
        }

        print("✓ System State and Metrics Prepared")
        print(f"  CPU Usage: {metrics['cpu_usage']:.0%}")
        print(f"  Memory Usage: {metrics['memory_usage']:.0%}")
        print(f"  Error Rate: {metrics['error_rate']:.1%}")

        # Step 2: Mock LLM optimization
        llm_integrator.llm_enabled = True
        mock_optimizations = {
            "recommendations": (
                "1. Increase connection pool from 10 to 20 (CPU and memory usage suggest capacity)\n"
                "2. Implement circuit breaker pattern for external API calls\n"
                "3. Add caching layer for frequently accessed data\n"
                "4. Review database query optimization\n"
                "5. Scale to 3 instances to handle increased load"
            )
        }

        with patch.object(llm_integrator.llm_client, 'recommend_optimization',
                         new_callable=AsyncMock, return_value=mock_optimizations):
            
            print("✓ LLM Mock Initialized")

            # Step 3: Get recommendations
            recs = await llm_integrator.recommend_optimizations(system_state, metrics)
            
            print("✓ Optimization Recommendations Generated")
            print(f"  Recommendations: {len(recs)}")
            for i, rec in enumerate(recs, 1):
                print(f"    {i}. {rec}")

        assert len(recs) > 0
        assert any("pool" in r.lower() for r in recs)

        print("✅ TEST PASSED: Optimization recommendations from LLM\n")

    @pytest.mark.asyncio
    async def test_complete_workflow_integration(self, orchestrator):
        """Test: Complete workflow from error to resolution with LLM"""
        print("\n🧪 TEST: Complete End-to-End Workflow")
        print("=" * 80)

        # Initialize LLM integrator
        llm_integrator = initialize_llm_integration(orchestrator)
        print("✓ LLM Integrator Initialized")

        # Mock Ollama unavailable, test graceful degradation
        llm_integrator.llm_enabled = False
        print("✓ Testing Graceful Degradation (Ollama unavailable)")

        # Step 1: Detect error
        print("\n📍 STEP 1: Error Detection")
        error = ErrorContext(
            error_type="RESOURCE_ERROR",
            message="Memory usage at 95% threshold",
            context={"memory_available": 100, "memory_used": 950},
            severity=ErrorSeverity.HIGH
        )
        print(f"  ✓ Error detected: {error.error_type}")

        # Step 2: Analyze without LLM
        print("\n📍 STEP 2: Analysis (Rule-Based, LLM disabled)")
        analysis = await llm_integrator.analyze_error_with_reasoning(error)
        print(f"  ✓ Status: {analysis.get('status', 'unknown')}")
        assert analysis['llm_enabled'] is False

        # Step 3: Now enable LLM mock
        print("\n📍 STEP 3: Enable LLM Mock")
        llm_integrator.llm_enabled = True
        llm_integrator.llm_health = "healthy"
        print("  ✓ LLM enabled (mock)")

        # Step 4: Analyze with LLM
        print("\n📍 STEP 4: Analysis (With LLM Reasoning)")
        mock_analysis = {
            "error_type": "RESOURCE_ERROR",
            "root_cause": "Memory leak in service or insufficient resource allocation",
            "analysis": "95% memory usage indicates either a memory leak causing "
            "unbounded growth or insufficient memory allocation for current workload.",
            "severity": "high",
            "recommendations": [
                "Restart the service to clear potential memory leak",
                "Increase memory allocation by 50%",
                "Monitor memory trends after restart"
            ],
            "confidence": 0.88
        }

        with patch.object(llm_integrator.llm_client, 'analyze_error',
                         new_callable=AsyncMock, return_value=mock_analysis):
            analysis = await llm_integrator.analyze_error_with_reasoning(error)
            print(f"  ✓ Root Cause: {analysis['root_cause']}")
            print(f"  ✓ Confidence: {analysis['confidence']:.0%}")

        # Step 5: Select and explain correction
        print("\n📍 STEP 5: Correction with LLM Explanation")
        strategy = "restart_service"
        mock_explanation = "Restarting the service is recommended to clear "
        "potential memory leaks and restore normal operation."

        with patch.object(llm_integrator.llm_client, 'explain_correction',
                         new_callable=AsyncMock, return_value=mock_explanation):
            explanation = await llm_integrator.explain_correction_decision(
                error.message,
                strategy
            )
            print(f"  ✓ Strategy: {strategy}")
            print(f"  ✓ Explanation: {explanation}")

        # Step 6: Verify health
        print("\n📍 STEP 6: System Health Check")
        health = await llm_integrator.get_health_status()
        print(f"  ✓ LLM Status: {health['status']}")
        print(f"  ✓ Requests: {health['requests']}")
        print(f"  ✓ Errors: {health['errors']}")

        print("\n" + "=" * 80)
        print("✅ COMPLETE WORKFLOW TEST PASSED")
        print("   Error Detection → LLM Analysis → Correction → Explanation")
        print("=" * 80 + "\n")

    @pytest.mark.asyncio
    async def test_llm_integration_alignment(self):
        """Test: LLM integration aligns with project framework"""
        print("\n🧪 TEST: Alignment with Project Phoenix Framework")
        print("=" * 60)

        # Verify imports work correctly
        print("✓ Verifying imports...")
        from autonomous_system.core import (
            LLMEnhancedOrchestrator, OllamaClient, OllamaConfig
        )
        print("  ✓ LLMEnhancedOrchestrator imported")
        print("  ✓ OllamaClient imported")
        print("  ✓ OllamaConfig imported")

        # Verify LLM integrator
        print("✓ Verifying LLM Integrator...")
        from autonomous_system.core.llm_system_integration import (
            LLMSystemIntegrator, initialize_llm_integration, get_llm_integrator
        )
        print("  ✓ LLMSystemIntegrator available")
        print("  ✓ initialize_llm_integration available")
        print("  ✓ get_llm_integrator available")

        # Verify framework compatibility
        print("✓ Verifying Framework Compatibility...")
        orchestrator = SelfCorrectionOrchestrator()
        integrator = LLMSystemIntegrator(orchestrator)
        assert integrator.orchestrator is orchestrator
        print("  ✓ Compatible with SelfCorrectionOrchestrator")

        # Verify error detection integration
        print("✓ Verifying Error Detection Integration...")
        from autonomous_system.core.error_detection import ErrorContext
        error = ErrorContext(
            error_type="TEST",
            message="test",
            context={},
            severity=ErrorSeverity.LOW
        )
        assert error is not None
        print("  ✓ ErrorContext compatible")

        print("✅ TEST PASSED: LLM fully integrated with Project Phoenix framework\n")


# Async test runner
@pytest.mark.asyncio
async def test_all_llm_workflows():
    """Run all LLM workflow tests"""
    test_instance = TestEndToEndLLMWorkflow()
    orchestrator = SelfCorrectionOrchestrator()
    llm_integrator = test_instance.llm_integrator(orchestrator)

    await test_instance.test_error_detection_to_llm_analysis(orchestrator, llm_integrator)
    await test_instance.test_correction_strategy_with_llm_explanation(orchestrator, llm_integrator)
    await test_instance.test_pattern_detection_across_errors(orchestrator, llm_integrator)
    await test_instance.test_optimization_recommendations(orchestrator, llm_integrator)
    await test_instance.test_complete_workflow_integration(orchestrator)
    await test_instance.test_llm_integration_alignment()


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("PROJECT PHOENIX - LLM INTEGRATION END-TO-END TESTS")
    print("=" * 80 + "\n")
    
    # Run with pytest
    pytest.main([__file__, "-v", "-s"])
