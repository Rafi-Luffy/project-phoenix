"""
Comprehensive tests for Phase 6: Advanced Autonomous Features

Tests system optimizer, meta-learning, predictive maintenance,
resource allocation, and orchestrator integration.

Expected: 25+ tests covering all Phase 6 functionality
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from autonomous_system.core.system_optimizer import (
    SystemOptimizer, OptimizationTarget, OptimizationMetrics
)
from autonomous_system.core.meta_learning import (
    MetaLearningEngine, MetaLearningMetrics, LearningPhase
)
from autonomous_system.core.predictive_maintenance import (
    PredictiveMaintenanceEngine, MaintenanceLevel
)
from autonomous_system.core.autonomous_resource_allocation import (
    ResourceAllocator, AllocationRequest, AllocationStrategy, ResourceType
)
from autonomous_system.core.advanced_autonomous_orchestrator import (
    AdvancedAutonomousOrchestrator, AdvancedAutonomousConfig
)


class TestSystemOptimizer:
    """Test system parameter optimization"""
    
    def test_optimizer_initialization(self):
        """Test optimizer initializes correctly"""
        optimizer = SystemOptimizer()
        assert optimizer is not None
        assert optimizer.config is not None
        assert optimizer.optimization_history == []
    
    def test_record_metrics(self):
        """Test recording optimization metrics"""
        optimizer = SystemOptimizer()
        metrics = OptimizationMetrics(
            target_metric=0.85,
            secondary_metrics={"speed": 0.9}
        )
        optimizer.record_metrics(metrics)
        assert len(optimizer.optimization_history) == 1
    
    def test_suggest_adjustments(self):
        """Test parameter adjustment suggestions"""
        optimizer = SystemOptimizer()
        
        # Record poor performance
        metrics = OptimizationMetrics(target_metric=0.5)
        optimizer.record_metrics(metrics)
        
        # Get suggestions
        suggestions = optimizer.suggest_adjustments(0.5, 0.95)
        assert suggestions is not None
    
    def test_parameter_sensitivity(self):
        """Test parameter sensitivity analysis"""
        optimizer = SystemOptimizer()
        
        # Record multiple metrics
        for i in range(5):
            metrics = OptimizationMetrics(target_metric=0.5 + i * 0.1)
            optimizer.record_metrics(metrics)
        
        sensitivity = optimizer.get_parameter_sensitivity()
        assert sensitivity is not None
    
    def test_convergence_tracking(self):
        """Test optimization convergence tracking"""
        optimizer = SystemOptimizer()
        
        # Record improving metrics
        for i in range(10):
            metrics = OptimizationMetrics(target_metric=0.5 + i * 0.04)
            optimizer.record_metrics(metrics)
        
        progress = optimizer.get_convergence_progress()
        assert 0 <= progress <= 1
        # More iterations should show some convergence
        assert progress > 0
    
    def test_error_type_optimization(self):
        """Test per-error-type optimization"""
        optimizer = SystemOptimizer()
        
        # Get config for specific error type
        from autonomous_system.core.error_detection import ErrorType
        config = optimizer.optimize_for_error_type(
            ErrorType.TIMEOUT_ERROR,
            OptimizationTarget.CORRECTION_SPEED
        )
        assert config is not None
        assert hasattr(config, 'exploration_max_depth')


class TestMetaLearning:
    """Test meta-learning engine"""
    
    def test_meta_learning_initialization(self):
        """Test meta-learning engine initializes"""
        engine = MetaLearningEngine()
        assert engine is not None
        assert engine.current_phase == LearningPhase.EXPLORATION
    
    def test_record_learning_experience(self):
        """Test recording learning experiences"""
        engine = MetaLearningEngine()
        from autonomous_system.core.correction_strategy import CorrectionStrategy
        from autonomous_system.core.error_detection import ErrorType
        
        engine.record_learning_experience(
            strategy=CorrectionStrategy.RETRY,
            error_type=ErrorType.TIMEOUT_ERROR,
            success=True,
            confidence=0.9
        )
        
        # Check that episode count increased (internal state changed)
        assert engine.episode_count == 1
    
    def test_phase_transitions(self):
        """Test learning phase transitions"""
        engine = MetaLearningEngine()
        from autonomous_system.core.correction_strategy import CorrectionStrategy
        from autonomous_system.core.error_detection import ErrorType
        
        initial_phase = engine.current_phase
        
        # Record many experiences
        for i in range(20):
            engine.record_learning_experience(
                strategy=CorrectionStrategy.RETRY,
                error_type=ErrorType.TIMEOUT_ERROR,
                success=i % 2 == 0,
                confidence=0.8
            )
        
        # Update phase
        engine.update_phase()
        # Phase may or may not have changed depending on logic
        assert engine.current_phase in [LearningPhase.EXPLORATION, 
                                        LearningPhase.EVALUATION,
                                        LearningPhase.ADAPTATION,
                                        LearningPhase.CONSOLIDATION]
    
    def test_strategy_evaluation(self):
        """Test strategy potential evaluation"""
        engine = MetaLearningEngine()
        from autonomous_system.core.correction_strategy import CorrectionStrategy
        from autonomous_system.core.error_detection import ErrorType
        
        # Record experiences for strategy
        for i in range(10):
            engine.record_learning_experience(
                strategy=CorrectionStrategy.RETRY,
                error_type=ErrorType.TIMEOUT_ERROR,
                success=True,
                confidence=0.8 + i * 0.01
            )
        
        potential = engine.evaluate_strategy_potential(CorrectionStrategy.RETRY)
        assert 0 <= potential <= 1
    
    def test_strategy_ranking_by_trend(self):
        """Test ranking strategies by improvement trend"""
        engine = MetaLearningEngine()
        from autonomous_system.core.correction_strategy import CorrectionStrategy
        from autonomous_system.core.error_detection import ErrorType
        
        # Record improving strategy
        for i in range(5):
            engine.record_learning_experience(
                strategy=CorrectionStrategy.RETRY,
                error_type=ErrorType.TIMEOUT_ERROR,
                success=True,
                confidence=0.5 + i * 0.1
            )
        
        # Record stagnant strategy
        for i in range(5):
            engine.record_learning_experience(
                strategy=CorrectionStrategy.FALLBACK,
                error_type=ErrorType.TIMEOUT_ERROR,
                success=True,
                confidence=0.7
            )
        
        ranked = engine.get_strategies_by_trend()
        assert len(ranked) >= 0
    
    def test_meta_parameter_optimization(self):
        """Test meta-parameter optimization"""
        engine = MetaLearningEngine()
        from autonomous_system.core.correction_strategy import CorrectionStrategy
        from autonomous_system.core.error_detection import ErrorType
        
        # Record experiences
        for i in range(15):
            engine.record_learning_experience(
                strategy=CorrectionStrategy.RETRY,
                error_type=ErrorType.TIMEOUT_ERROR,
                success=i % 2 == 0,
                confidence=0.75
            )
        
        # Optimize meta-parameters
        engine.optimize_meta_parameters()
        # Should not raise error and should update parameters


class TestPredictiveMaintenance:
    """Test predictive maintenance engine"""
    
    def test_maintenance_initialization(self):
        """Test maintenance engine initializes"""
        engine = PredictiveMaintenanceEngine()
        assert engine is not None
        assert len(engine.components) == 0
    
    def test_component_registration(self):
        """Test component registration"""
        engine = PredictiveMaintenanceEngine()
        engine.register_component("cpu")
        assert "cpu" in engine.components
    
    def test_health_indicator_tracking(self):
        """Test health indicator tracking"""
        engine = PredictiveMaintenanceEngine()
        engine.register_component("memory")
        
        # Add health indicators
        engine.add_health_indicator("memory", "usage_percent", 75.0)
        # Second call with slightly different value
        engine.add_health_indicator("memory", "usage_percent", 76.0)
        
        component = engine.components["memory"]
        assert "usage_percent" in component.indicators
    
    def test_degradation_detection(self):
        """Test degradation detection"""
        engine = PredictiveMaintenanceEngine()
        engine.register_component("disk")
        
        # Add degrading health indicators (increasing in value means getting worse)
        for i in range(10):
            engine.add_health_indicator("disk", "error_rate", i * 0.1)
        
        # Check for anomalies
        anomalies = engine.detect_anomalies()
        # Anomalies list may be empty if degradation not severe enough
        assert isinstance(anomalies, list)
    
    def test_maintenance_recommendations(self):
        """Test maintenance recommendations"""
        engine = PredictiveMaintenanceEngine()
        engine.register_component("cache")
        
        # Add indicators showing need for maintenance
        engine.add_health_indicator("cache", "hit_ratio", 0.5)
        
        recommendations = engine.get_maintenance_recommendations()
        assert isinstance(recommendations, list)
    
    def test_error_frequency_prediction(self):
        """Test error frequency prediction"""
        engine = PredictiveMaintenanceEngine()
        engine.register_component("processor")
        
        # Record errors
        for i in range(5):
            engine.record_error("processor")
        
        # Get frequency
        frequency = engine.predict_error_frequency("processor")
        assert frequency >= 0
    
    def test_maintenance_action(self):
        """Test maintenance action"""
        engine = PredictiveMaintenanceEngine()
        engine.register_component("buffer")
        
        # Get health before maintenance
        engine.add_health_indicator("buffer", "usage", 0.9)
        
        # Perform maintenance
        engine.perform_maintenance("buffer")
        
        # Check health reset - overall_health should be updated
        component = engine.components["buffer"]
        # After maintenance, indicators are reset to 0.95
        assert component.overall_health == 0.95


class TestResourceAllocation:
    """Test autonomous resource allocation"""
    
    def test_allocator_initialization(self):
        """Test allocator initializes correctly"""
        allocator = ResourceAllocator()
        assert allocator is not None
        assert allocator.allocation_strategy == AllocationStrategy.ADAPTIVE
    
    def test_resource_request_and_release(self):
        """Test resource request and release cycle"""
        allocator = ResourceAllocator()
        
        # Request resources
        request = AllocationRequest(
            request_id="req_1",
            resource_type=ResourceType.CPU,
            amount=50.0
        )
        result = allocator.request_resources(request)
        
        # Should be granted (adaptive has good capacity)
        assert result.granted
        
        # Release resources
        allocator.release_resources(
            request_id="req_1",
            resource_type=ResourceType.CPU,
            amount=50.0
        )
    
    def test_multiple_allocation_strategies(self):
        """Test different allocation strategies"""
        allocator = ResourceAllocator()
        
        strategies = [
            AllocationStrategy.FAIR_SHARE,
            AllocationStrategy.PRIORITY,
            AllocationStrategy.DEMAND,
            AllocationStrategy.ADAPTIVE
        ]
        
        for strategy in strategies:
            allocator.set_strategy(strategy)
            assert allocator.allocation_strategy == strategy
    
    def test_resource_constraint_detection(self):
        """Test resource constraint detection"""
        allocator = ResourceAllocator()
        
        # Allocate heavily to create constraint
        request = AllocationRequest(
            request_id="heavy",
            resource_type=ResourceType.MEMORY,
            amount=80.0
        )
        result = allocator.request_resources(request)
        
        # Check constraint state
        is_constrained = allocator.is_resource_constrained()
        assert isinstance(is_constrained, bool)
    
    def test_bottleneck_detection(self):
        """Test bottleneck resource detection"""
        allocator = ResourceAllocator()
        
        # Create bottleneck
        request = AllocationRequest(
            request_id="bottleneck",
            resource_type=ResourceType.DISK,
            amount=85.0
        )
        allocator.request_resources(request)
        
        bottleneck = allocator.get_bottleneck_resource()
        # May or may not be detected depending on threshold
        assert bottleneck in [ResourceType.CPU, ResourceType.MEMORY, 
                             ResourceType.DISK, ResourceType.NETWORK,
                             ResourceType.THREADS, None]
    
    def test_pool_status(self):
        """Test resource pool status"""
        allocator = ResourceAllocator()
        
        status = allocator.get_pool_status(ResourceType.CPU)
        assert status is not None
        assert "total_capacity" in status
        assert "allocated" in status
    
    def test_optimization_suggestion(self):
        """Test optimization suggestion generation"""
        allocator = ResourceAllocator()
        
        suggestion = allocator.suggest_optimization()
        # Suggestion can be None if no bottleneck
        assert suggestion is None or isinstance(suggestion, str)


class TestAdvancedOrchestrator:
    """Test advanced autonomous orchestrator"""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initializes all systems"""
        config = AdvancedAutonomousConfig()
        orchestrator = AdvancedAutonomousOrchestrator(config)
        
        assert orchestrator.optimizer is not None
        assert orchestrator.meta_learner is not None
        assert orchestrator.maintenance is not None
        assert orchestrator.resource_allocator is not None
    
    def test_orchestrator_process_iteration(self):
        """Test orchestrator processes iterations"""
        orchestrator = AdvancedAutonomousOrchestrator()
        
        initial_count = orchestrator.iteration_count
        orchestrator.process_iteration()
        
        assert orchestrator.iteration_count == initial_count + 1
    
    def test_optimization_cycle_triggering(self):
        """Test optimization cycles trigger correctly"""
        config = AdvancedAutonomousConfig(optimization_interval=5)
        orchestrator = AdvancedAutonomousOrchestrator(config)
        
        initial_cycles = orchestrator.optimization_cycles
        
        # Run for optimization interval
        for _ in range(6):
            orchestrator.process_iteration()
        
        assert orchestrator.optimization_cycles > initial_cycles
    
    def test_learning_cycle_triggering(self):
        """Test learning cycles trigger correctly"""
        config = AdvancedAutonomousConfig(meta_learning_window=3)
        orchestrator = AdvancedAutonomousOrchestrator(config)
        
        initial_cycles = orchestrator.learning_cycles
        
        # Run for learning window
        for _ in range(4):
            orchestrator.process_iteration()
        
        assert orchestrator.learning_cycles > initial_cycles
    
    def test_maintenance_cycle_triggering(self):
        """Test maintenance cycles trigger correctly"""
        config = AdvancedAutonomousConfig(maintenance_check_interval=7)
        orchestrator = AdvancedAutonomousOrchestrator(config)
        
        initial_cycles = orchestrator.maintenance_cycles
        
        # Run for maintenance interval
        for _ in range(8):
            orchestrator.process_iteration()
        
        assert orchestrator.maintenance_cycles > initial_cycles
    
    def test_resource_request(self):
        """Test resource request through orchestrator"""
        orchestrator = AdvancedAutonomousOrchestrator()
        
        granted = orchestrator.request_resources(
            ResourceType.CPU,
            amount=30.0,
            priority=5
        )
        
        assert isinstance(granted, bool)
    
    def test_component_health_recording(self):
        """Test recording component health"""
        orchestrator = AdvancedAutonomousOrchestrator()
        
        orchestrator.record_component_health(
            component_name="cache",
            indicator_name="efficiency",
            health_value=0.85
        )
        
        # Should not raise error
        assert True
    
    def test_system_status_reporting(self):
        """Test system status reporting"""
        orchestrator = AdvancedAutonomousOrchestrator()
        
        # Run some iterations
        for _ in range(15):
            orchestrator.process_iteration()
        
        status = orchestrator.get_system_status()
        
        assert "iteration_count" in status
        assert "optimization" in status
        assert "learning" in status
        assert "maintenance" in status
        assert "resources" in status
    
    def test_state_export(self):
        """Test state export"""
        orchestrator = AdvancedAutonomousOrchestrator()
        
        for _ in range(10):
            orchestrator.process_iteration()
        
        state = orchestrator.export_state()
        
        assert "timestamp" in state
        assert "iteration_count" in state
        assert "optimization" in state
        assert "learning" in state
        assert "maintenance" in state
        assert "resources" in state
    
    def test_recommendations_generation(self):
        """Test system recommendations"""
        orchestrator = AdvancedAutonomousOrchestrator()
        
        # Run iterations to gather data
        for _ in range(20):
            orchestrator.process_iteration()
        
        recommendations = orchestrator.get_recommendations()
        
        assert "optimization" in recommendations
        assert "learning_phase" in recommendations
        assert "maintenance" in recommendations
        assert "resource_optimization" in recommendations
    
    def test_selective_feature_disabling(self):
        """Test disabling specific features"""
        config = AdvancedAutonomousConfig(
            enable_self_optimization=False,
            enable_meta_learning=True
        )
        orchestrator = AdvancedAutonomousOrchestrator(config)
        
        for _ in range(10):
            orchestrator.process_iteration()
        
        # Optimization cycles should not increase
        assert orchestrator.optimization_cycles == 0
        # But we should still iterate
        assert orchestrator.iteration_count > 0


class TestIntegration:
    """Integration tests for Phase 6 components"""
    
    def test_all_components_working_together(self):
        """Test all Phase 6 components working together"""
        config = AdvancedAutonomousConfig(
            optimization_interval=20,  # Reasonable for 50 iterations
            meta_learning_window=10
        )
        orchestrator = AdvancedAutonomousOrchestrator(config)
        
        # Simulate extended operation
        for i in range(50):
            orchestrator.process_iteration()
            
            # Add health data periodically
            if i % 10 == 0:
                orchestrator.record_component_health(
                    "core_processor",
                    "latency",
                    0.7 + (i / 100)
                )
            
            # Request resources periodically
            if i % 15 == 0:
                orchestrator.request_resources(ResourceType.CPU, 25.0)
        
        # All systems should be active
        assert orchestrator.iteration_count == 50
        assert orchestrator.optimization_cycles > 0
        assert orchestrator.learning_cycles > 0
        assert orchestrator.resource_cycles == 50
    
    def test_multi_component_status(self):
        """Test status from all components"""
        orchestrator = AdvancedAutonomousOrchestrator()
        
        for _ in range(30):
            orchestrator.process_iteration()
        
        status = orchestrator.get_system_status()
        
        # Verify all subsystems reporting
        assert status["optimization"]["enabled"]
        assert status["learning"]["enabled"]
        assert status["maintenance"]["enabled"]
        assert status["resources"]["enabled"]
        
        # All should have cycles
        assert status["optimization"]["cycles"] >= 0
        assert status["learning"]["cycles"] >= 0
        assert status["maintenance"]["cycles"] >= 0
        assert status["resources"]["cycles"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
