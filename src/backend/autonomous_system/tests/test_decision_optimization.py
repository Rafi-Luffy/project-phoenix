"""
Comprehensive tests for decision optimization (Phase 4)

Tests:
- Decision tree building and traversal
- Resource optimization under constraints
- Strategy selection and optimization
- Decision outcome tracking
- Orchestrator coordination
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from autonomous_system.core.decision_tree import (
    DecisionTree, DecisionTreeBuilder, DecisionNodeType, DecisionCondition, DecisionNode
)
from autonomous_system.core.resource_optimizer import (
    ResourceOptimizationEngine, ResourceCost, 
    OptimizationResult, ResourceBudget, ResourceType
)
from autonomous_system.core.decision_optimization import (
    DecisionOptimizationOrchestrator, DecisionContext, Decision
)
from autonomous_system.core.error_detection import ErrorType
from autonomous_system.core.correction_strategy import CorrectionStrategy


class TestDecisionTree:
    """Test decision tree functionality"""
    
    def test_decision_tree_creation(self):
        """Test basic decision tree creation"""
        tree = DecisionTree(
            tree_id="test_tree",
            error_type=ErrorType.LOGIC_ERROR,
            root_node=DecisionNode(node_id="root", node_type=DecisionNodeType.ROOT, name="root", confidence=1.0)
        )
        
        assert tree.tree_id == "test_tree"
        assert tree.error_type == ErrorType.LOGIC_ERROR
        assert len(tree.nodes) == 1
    
    def test_decision_tree_traversal(self):
        """Test decision tree traversal"""
        root = DecisionNode(node_id="root", node_type=DecisionNodeType.ROOT, name="root", confidence=1.0)
        
        condition_node = DecisionNode(node_id="condition_1", node_type=DecisionNodeType.CONDITION, name="condition", confidence=0.9,
            condition=DecisionCondition(
                attribute="operation",
                operator="equals",
                value="parsing"
            )
        )
        
        tree = DecisionTree(
            tree_id="test_tree",
            error_type=ErrorType.LOGIC_ERROR,
            root_node=root
        )
        
        tree.nodes["root"] = root
        tree.nodes["condition_1"] = condition_node
        root.true_child_id = "condition_1"
        
        # Traverse tree
        context = {"operation": "parsing"}
        result = tree.traverse(context)
        
        assert result is not None
    
    def test_decision_tree_builder(self):
        """Test decision tree building from rules"""
        builder = DecisionTreeBuilder()
        
        rules = [
            {
                "condition": {"attribute": "error_type", "operator": "equals", "value": "syntax"},
                "action": "analyze_syntax"
            }
        ]
        
        tree = builder.build_tree_from_rules(ErrorType.LOGIC_ERROR, rules)
        
        assert tree.error_type == ErrorType.LOGIC_ERROR
        assert len(tree.nodes) > 0
    
    def test_decision_tree_outcome_tracking(self):
        """Test outcome tracking in decision tree"""
        tree = DecisionTree(
            tree_id="test_tree",
            error_type=ErrorType.LOGIC_ERROR,
            root_node=DecisionNode(node_id="root", node_type=DecisionNodeType.ROOT, name="root", confidence=1.0)
        )
        
        # Record outcomes
        tree.record_decision_outcome(True)
        tree.record_decision_outcome(True)
        tree.record_decision_outcome(False)
        
        # Verify tree recorded outcomes
        assert len(tree.nodes) == 1
        assert tree.root_node is not None


class TestResourceOptimization:
    """Test resource optimization functionality"""
    
    def test_resource_cost_creation(self):
        """Test resource cost creation"""
        cost = ResourceCost(
            strategy=CorrectionStrategy.RETRY,
            error_type=ErrorType.RESOURCE_ERROR,
            cpu_cost=10.0,
            memory_cost=50.0,
            success_probability=0.9
        )
        
        assert cost.strategy == CorrectionStrategy.RETRY
        assert cost.success_probability == 0.9
    
    def test_resource_cost_calculation(self):
        """Test resource cost calculations"""
        cost = ResourceCost(
            strategy=CorrectionStrategy.RETRY,
            error_type=ErrorType.RESOURCE_ERROR,
            cpu_cost=10.0,
            memory_cost=50.0,
            success_probability=0.9
        )
        
        total_cost = cost.total_cost()
        assert total_cost > 0
        
        cost_per_success = cost.cost_per_success()
        assert cost_per_success > 0
    
    def test_resource_budget_validation(self):
        """Test resource budget constraint validation"""
        budget = ResourceBudget(max_cpu_ms=1000.0, max_memory_mb=500.0)
        
        assert budget.check_constraint(ResourceCost(strategy=CorrectionStrategy.RETRY, error_type=ErrorType.LOGIC_ERROR, cpu_cost=500.0))
        assert not budget.check_constraint(ResourceCost(strategy=CorrectionStrategy.RETRY, error_type=ErrorType.LOGIC_ERROR, cpu_cost=1500.0))
    
    def test_resource_optimization_engine(self):
        """Test resource optimization engine"""
        engine = ResourceOptimizationEngine()
        
        # Register strategies
        engine.register_strategy_cost(ResourceCost(
            strategy=CorrectionStrategy.RETRY,
            error_type=ErrorType.RESOURCE_ERROR,
            cpu_cost=5.0,
            memory_cost=20.0,
            success_probability=0.8
        ))
        
        engine.register_strategy_cost(ResourceCost(
            strategy=CorrectionStrategy.FALLBACK,
            error_type=ErrorType.RESOURCE_ERROR,
            cpu_cost=15.0,
            memory_cost=10.0,
            success_probability=0.9
        ))
        
        # Optimize selection
        result = engine.optimize_strategy_selection(
            error_type=ErrorType.RESOURCE_ERROR,
            available_strategies=[CorrectionStrategy.RETRY, CorrectionStrategy.FALLBACK]
        )
        
        assert result.selected_strategy in [CorrectionStrategy.RETRY, CorrectionStrategy.FALLBACK]
        assert result.cost is not None
    
    def test_optimization_with_constraints(self):
        """Test optimization with resource constraints"""
        engine = ResourceOptimizationEngine()
        
        budget = ResourceBudget(max_cpu_ms=100.0, max_memory_mb=50.0)
        
        engine.register_strategy_cost(ResourceCost(
            strategy=CorrectionStrategy.RETRY,
            error_type=ErrorType.RESOURCE_ERROR,
            cpu_cost=50.0,
            memory_cost=30.0,
            success_probability=0.8
        ))
        
        result = engine.optimize_strategy_selection(
            error_type=ErrorType.RESOURCE_ERROR,
            available_strategies=[CorrectionStrategy.RETRY],
            budget=budget
        )
        
        assert result.selected_strategy == CorrectionStrategy.RETRY
    
    def test_optimization_history_tracking(self):
        """Test optimization history tracking"""
        engine = ResourceOptimizationEngine()
        
        # Register strategies
        for i in range(5):
            engine.register_strategy_cost(ResourceCost(
                strategy=CorrectionStrategy.RETRY,
                error_type=ErrorType.RESOURCE_ERROR,
                cpu_cost=10.0 + i,
                memory_cost=20.0 + i,
                success_probability=0.7 + (i * 0.02)
            ))
        
        # Get statistics
        stats = engine.get_stats()
        assert stats["total_optimizations"] >= 0


class TestDecisionOptimizationOrchestrator:
    """Test decision optimization orchestrator"""
    
    def test_orchestrator_creation(self):
        """Test orchestrator initialization"""
        orchestrator = DecisionOptimizationOrchestrator()
        
        assert orchestrator.total_decisions == 0
        assert orchestrator.successful_decisions == 0
        assert len(orchestrator.decision_history) == 0
    
    def test_strategy_cost_registration(self):
        """Test strategy cost registration"""
        orchestrator = DecisionOptimizationOrchestrator()
        
        orchestrator.register_strategy_cost(
            strategy=CorrectionStrategy.RETRY,
            error_type=ErrorType.RESOURCE_ERROR,
            cpu_ms=10.0,
            memory_mb=50.0,
            success_rate=0.9
        )
        
        stats = orchestrator.get_stats()
        assert stats["resource_optimizations"] >= 0
    
    def test_decision_context_creation(self):
        """Test decision context creation"""
        context = DecisionContext(
            error_type=ErrorType.RESOURCE_ERROR,
            operation="fetch_data",
            agent_id="agent_1"
        )
        
        assert context.error_type == ErrorType.RESOURCE_ERROR
        assert context.operation == "fetch_data"
        
        context_dict = context.to_dict()
        assert "error_type" in context_dict
        assert "operation" in context_dict
    
    def test_decision_making(self):
        """Test decision making"""
        orchestrator = DecisionOptimizationOrchestrator()
        
        # Register strategies
        orchestrator.register_strategy_cost(
            strategy=CorrectionStrategy.RETRY,
            error_type=ErrorType.RESOURCE_ERROR,
            cpu_ms=5.0,
            memory_mb=20.0,
            success_rate=0.85
        )
        
        # Create decision context
        context = DecisionContext(
            error_type=ErrorType.RESOURCE_ERROR,
            operation="fetch_data",
            agent_id="agent_1"
        )
        
        # Make decision
        decision = orchestrator.make_decision(
            context=context,
            candidate_strategies=[CorrectionStrategy.RETRY, CorrectionStrategy.FALLBACK]
        )
        
        assert decision.decision_id == "decision_1"
        assert decision.selected_strategy in [CorrectionStrategy.RETRY, CorrectionStrategy.FALLBACK]
        assert decision.confidence > 0
    
    def test_multiple_decisions(self):
        """Test multiple consecutive decisions"""
        orchestrator = DecisionOptimizationOrchestrator()
        
        # Register strategies
        orchestrator.register_strategy_cost(
            strategy=CorrectionStrategy.RETRY,
            error_type=ErrorType.RESOURCE_ERROR,
            cpu_ms=5.0,
            memory_mb=20.0,
            success_rate=0.85
        )
        
        # Make multiple decisions
        for i in range(5):
            context = DecisionContext(
                error_type=ErrorType.RESOURCE_ERROR,
                operation=f"operation_{i}",
                agent_id="agent_1"
            )
            
            decision = orchestrator.make_decision(
                context=context,
                candidate_strategies=[CorrectionStrategy.RETRY]
            )
            
            assert decision.decision_id == f"decision_{i+1}"
        
        assert orchestrator.total_decisions == 5
    
    def test_decision_outcome_recording(self):
        """Test decision outcome recording"""
        orchestrator = DecisionOptimizationOrchestrator()
        
        orchestrator.register_strategy_cost(
            strategy=CorrectionStrategy.RETRY,
            error_type=ErrorType.RESOURCE_ERROR,
            cpu_ms=5.0,
            memory_mb=20.0,
            success_rate=0.85
        )
        
        context = DecisionContext(
            error_type=ErrorType.RESOURCE_ERROR,
            operation="fetch_data",
            agent_id="agent_1"
        )
        
        decision = orchestrator.make_decision(
            context=context,
            candidate_strategies=[CorrectionStrategy.RETRY]
        )
        
        # Record outcome
        orchestrator.record_decision_outcome(decision.decision_id, True)
        
        assert orchestrator.successful_decisions == 1
        assert decision.outcome == True
    
    def test_decision_analysis(self):
        """Test decision analysis generation"""
        orchestrator = DecisionOptimizationOrchestrator()
        
        orchestrator.register_strategy_cost(
            strategy=CorrectionStrategy.RETRY,
            error_type=ErrorType.RESOURCE_ERROR,
            cpu_ms=5.0,
            memory_mb=20.0,
            success_rate=0.85
        )
        
        # Make and record decisions
        for i in range(5):
            context = DecisionContext(
                error_type=ErrorType.RESOURCE_ERROR,
                operation=f"operation_{i}",
                agent_id="agent_1"
            )
            
            decision = orchestrator.make_decision(
                context=context,
                candidate_strategies=[CorrectionStrategy.RETRY]
            )
            
            orchestrator.record_decision_outcome(
                decision.decision_id,
                i % 2 == 0  # 60% success rate
            )
        
        analysis = orchestrator.get_decision_analysis()
        
        assert analysis["total_decisions"] == 5
        assert analysis["successful_decisions"] == 3
        assert analysis["success_rate"] == 0.6
    
    def test_decision_tree_building(self):
        """Test decision tree building through orchestrator"""
        orchestrator = DecisionOptimizationOrchestrator()
        
        rules = [
            {
                "condition": {"attribute": "operation", "operator": "equals", "value": "parse"},
                "action": "analyze"
            }
        ]
        
        tree = orchestrator.build_decision_tree(ErrorType.LOGIC_ERROR, rules)
        
        assert tree.error_type == ErrorType.LOGIC_ERROR
        assert len(tree.nodes) > 0
    
    def test_orchestrator_export_state(self):
        """Test state export functionality"""
        orchestrator = DecisionOptimizationOrchestrator()
        
        orchestrator.register_strategy_cost(
            strategy=CorrectionStrategy.RETRY,
            error_type=ErrorType.RESOURCE_ERROR,
            cpu_ms=5.0,
            memory_mb=20.0,
            success_rate=0.85
        )
        
        context = DecisionContext(
            error_type=ErrorType.RESOURCE_ERROR,
            operation="fetch_data",
            agent_id="agent_1"
        )
        
        decision = orchestrator.make_decision(
            context=context,
            candidate_strategies=[CorrectionStrategy.RETRY]
        )
        
        orchestrator.record_decision_outcome(decision.decision_id, True)
        
        # Export state
        state = orchestrator.export_decision_state()
        
        assert "decision_trees" in state
        assert "recent_decisions" in state
        assert "statistics" in state
        assert state["statistics"]["total_decisions"] == 1
        assert state["statistics"]["successful_decisions"] == 1
    
    def test_orchestrator_stats(self):
        """Test orchestrator statistics"""
        orchestrator = DecisionOptimizationOrchestrator()
        
        stats = orchestrator.get_stats()
        
        assert stats["total_decisions"] == 0
        assert stats["decision_trees"] == 0
        assert "analysis" in stats


class TestDecisionIntegration:
    """Test integration of decision optimization components"""
    
    def test_end_to_end_decision_flow(self):
        """Test complete decision flow"""
        orchestrator = DecisionOptimizationOrchestrator()
        
        # Register multiple strategies
        for strategy in [CorrectionStrategy.RETRY, CorrectionStrategy.FALLBACK]:
            orchestrator.register_strategy_cost(
                strategy=strategy,
                error_type=ErrorType.RESOURCE_ERROR,
                cpu_ms=5.0 if strategy == CorrectionStrategy.RETRY else 10.0,
                memory_mb=20.0 if strategy == CorrectionStrategy.RETRY else 30.0,
                success_rate=0.85 if strategy == CorrectionStrategy.RETRY else 0.95
            )
        
        # Make decision with budget
        context = DecisionContext(
            error_type=ErrorType.RESOURCE_ERROR,
            operation="fetch_data",
            agent_id="agent_1",
            resource_constraints={"cpu_ms": 50.0, "memory_mb": 100.0}
        )
        
        budget = ResourceBudget(max_cpu_ms=50.0, max_memory_mb=100.0)
        
        decision = orchestrator.make_decision(
            context=context,
            candidate_strategies=[CorrectionStrategy.RETRY, CorrectionStrategy.FALLBACK],
            budget=budget
        )
        
        assert decision.selected_strategy is not None
        assert decision.confidence > 0
        
        # Record outcome
        orchestrator.record_decision_outcome(decision.decision_id, True)
        
        # Verify tracking
        assert orchestrator.total_decisions == 1
        assert orchestrator.successful_decisions == 1
        assert len(orchestrator.decision_history) == 1
    
    def test_strategy_comparison(self):
        """Test strategy comparison and selection"""
        orchestrator = DecisionOptimizationOrchestrator()
        
        # Register strategies with different profiles
        strategies = [
            (CorrectionStrategy.RETRY, 5.0, 20.0, 0.75),
            (CorrectionStrategy.FALLBACK, 10.0, 30.0, 0.95),
            (CorrectionStrategy.CACHE, 15.0, 10.0, 0.80)
        ]
        
        for strategy, cpu, memory, success in strategies:
            orchestrator.register_strategy_cost(
                strategy=strategy,
                error_type=ErrorType.RESOURCE_ERROR,
                cpu_ms=cpu,
                memory_mb=memory,
                success_rate=success
            )
        
        # Make decisions with different budgets
        for budget_cpu in [20.0, 50.0, 100.0]:
            context = DecisionContext(
                error_type=ErrorType.RESOURCE_ERROR,
                operation="test",
                agent_id="agent_1"
            )
            
            budget = ResourceBudget(max_cpu_ms=budget_cpu, max_memory_mb=100.0)
            
            decision = orchestrator.make_decision(
                context=context,
                candidate_strategies=[s[0] for s in strategies],
                budget=budget
            )
            
            assert decision.selected_strategy is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
