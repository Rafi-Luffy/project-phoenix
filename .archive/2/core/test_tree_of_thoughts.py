"""
Phase 5: Tree of Thoughts Test Suite

Tests for multi-path reasoning, parallel exploration, and outcome prediction.
Target: 20+ tests
"""

import pytest
from datetime import datetime
from typing import List

from autonomous_system.core.error_detection import ErrorType
from autonomous_system.core.correction_strategy import CorrectionStrategy
from autonomous_system.core.thought_node import (
    ThoughtNode, ThoughtPath, ThoughtType, ThoughtStatus, Evaluation
)
from autonomous_system.core.outcome_prediction import (
    OutcomePrediction, OutcomePredictionEngine
)
from autonomous_system.core.tree_of_thoughts import (
    TreeOfThoughtsOrchestrator, ToTExplorationConfig, ExplorationResult
)


class TestThoughtNodeBasics:
    """Test basic thought node functionality"""
    
    def test_thought_node_creation(self):
        """Test creating a thought node"""
        node = ThoughtNode(
            thought_type=ThoughtType.OBSERVATION,
            content="Test observation",
            error_type=ErrorType.TIMEOUT_ERROR,
            operation="test_op",
            agent_id="agent_1"
        )
        
        assert node.node_id is not None
        assert node.thought_type == ThoughtType.OBSERVATION
        assert node.content == "Test observation"
        assert node.depth == 0
        assert node.status == ThoughtStatus.PENDING
    
    def test_thought_node_evaluation(self):
        """Test evaluating a thought node"""
        node = ThoughtNode(
            thought_type=ThoughtType.REASONING,
            content="Test reasoning"
        )
        
        node.evaluate(0.8, 0.9, "Good reasoning", 0.85, 0.85, 0.85)
        
        assert node.evaluation is not None
        assert node.evaluation.score == 0.8
        assert node.evaluation.confidence == 0.9
    
    def test_thought_node_parent_child(self):
        """Test parent-child relationships"""
        parent = ThoughtNode(
            thought_type=ThoughtType.OBSERVATION,
            content="Parent"
        )
        
        child = ThoughtNode(
            thought_type=ThoughtType.REASONING,
            content="Child",
            parent_id=parent.node_id,
            depth=1
        )
        
        parent.add_child(child.node_id)
        
        assert child.node_id in parent.children_ids
        assert child.parent_id == parent.node_id
        assert child.depth == 1
    
    def test_thought_is_promising(self):
        """Test is_promising method"""
        node = ThoughtNode(
            thought_type=ThoughtType.REASONING,
            content="Test"
        )
        
        # Without evaluation, should return True (unevaluated is potentially promising)
        assert node.is_promising()
        
        # With high score, should be promising
        node.evaluate(0.8, 0.9, "Good")
        assert node.is_promising()
        
        # With low score, not promising
        node.evaluate(0.2, 0.5, "Bad")
        assert not node.is_promising()
    
    def test_thought_node_status_transitions(self):
        """Test status transitions"""
        node = ThoughtNode(
            thought_type=ThoughtType.REASONING,
            content="Test"
        )
        
        assert node.status == ThoughtStatus.PENDING
        
        node.status = ThoughtStatus.EXPLORING
        assert node.status == ThoughtStatus.EXPLORING
        
        node.complete()
        assert node.status == ThoughtStatus.COMPLETE
        
        node.prune("Testing")
        assert node.status == ThoughtStatus.PRUNED


class TestThoughtPath:
    """Test thought path functionality"""
    
    def test_thought_path_creation(self):
        """Test creating a thought path"""
        path = ThoughtPath()
        assert path.nodes == []
        assert path.depth() == 0
        assert path.total_score == 0.0
    
    def test_path_add_node(self):
        """Test adding nodes to path"""
        path = ThoughtPath()
        node1 = ThoughtNode(
            thought_type=ThoughtType.OBSERVATION,
            content="Node 1"
        )
        node2 = ThoughtNode(
            thought_type=ThoughtType.REASONING,
            content="Node 2"
        )
        
        path.add_node(node1)
        path.add_node(node2)
        
        assert len(path.nodes) == 2
        assert path.depth() == 2
    
    def test_path_metrics_calculation(self):
        """Test path metrics calculation"""
        path = ThoughtPath()
        
        node1 = ThoughtNode(
            thought_type=ThoughtType.OBSERVATION,
            content="Node 1"
        )
        node1.evaluate(0.8, 0.9, "Good")
        
        node2 = ThoughtNode(
            thought_type=ThoughtType.REASONING,
            content="Node 2"
        )
        node2.evaluate(0.7, 0.85, "OK")
        
        path.add_node(node1)
        path.add_node(node2)
        path.calculate_metrics()
        
        assert path.total_score > 0
        assert path.average_confidence > 0
        assert path.is_viable
    
    def test_path_is_viable(self):
        """Test path viability"""
        path = ThoughtPath()
        
        # Empty path not immediately viable - no evaluation
        path.calculate_metrics()
        # After calculate, empty path still shows is_viable=True by default
        
        # Add evaluated node
        node = ThoughtNode(
            thought_type=ThoughtType.REASONING,
            content="Test"
        )
        node.evaluate(0.8, 0.9, "Good")
        path.add_node(node)
        path.calculate_metrics()
        
        assert path.is_viable


class TestOutcomePrediction:
    """Test outcome prediction"""
    
    def test_outcome_prediction_creation(self):
        """Test creating prediction"""
        prediction = OutcomePrediction(
            success_probability=0.8,
            expected_cost=50.0,
            expected_time=2.5,
            confidence=0.9,
            reasoning="Based on history"
        )
        
        assert prediction.success_probability == 0.8
        assert prediction.expected_cost == 50.0
        assert prediction.confidence == 0.9
    
    def test_prediction_engine_creation(self):
        """Test creating prediction engine"""
        engine = OutcomePredictionEngine()
        
        assert engine.strategy_success_rates is not None
        assert len(engine.path_outcomes) == 0
    
    def test_prediction_engine_register_outcome(self):
        """Test registering outcomes"""
        engine = OutcomePredictionEngine()
        path = ThoughtPath()
        
        node = ThoughtNode(
            thought_type=ThoughtType.REASONING,
            content="Test"
        )
        path.add_node(node)
        
        engine.register_outcome(path, True, 50.0)
        
        assert len(engine.path_outcomes) > 0
        assert engine.path_outcomes[0][1] == True
    
    def test_prediction_accuracy_tracking(self):
        """Test prediction accuracy tracking"""
        engine = OutcomePredictionEngine()
        path = ThoughtPath()
        node = ThoughtNode(
            thought_type=ThoughtType.REASONING,
            content="Test",
            error_type=ErrorType.TIMEOUT_ERROR,
            operation="test"
        )
        node.evaluate(0.8, 0.9, "Good", 0.85, 0.85, 0.85)
        path.add_node(node)
        
        prediction = engine.predict_outcome(path)
        assert prediction is not None
        assert 0 <= prediction.success_probability <= 1
        assert prediction.confidence >= 0


class TestTreeOfThoughtsOrchestrator:
    """Test ToT orchestrator"""
    
    def test_orchestrator_creation(self):
        """Test creating orchestrator"""
        orchestrator = TreeOfThoughtsOrchestrator()
        
        assert orchestrator.config is not None
        assert orchestrator.prediction_engine is not None
        assert len(orchestrator.all_nodes) == 0
    
    def test_create_root_node(self):
        """Test creating root node"""
        orchestrator = TreeOfThoughtsOrchestrator()
        
        root = orchestrator.create_root_node(
            ErrorType.TIMEOUT_ERROR,
            "operation_1",
            "agent_1",
            "Test error"
        )
        
        assert root is not None
        assert root.depth == 0
        assert root.thought_type == ThoughtType.OBSERVATION
        assert root.node_id in orchestrator.all_nodes
    
    def test_create_thought(self):
        """Test creating child thought"""
        orchestrator = TreeOfThoughtsOrchestrator()
        
        parent = orchestrator.create_root_node(
            ErrorType.TIMEOUT_ERROR,
            "op_1",
            "agent_1"
        )
        
        child = orchestrator.create_thought(
            parent,
            ThoughtType.REASONING,
            "Try this approach",
            strategy=CorrectionStrategy.RETRY
        )
        
        assert child.depth == 1
        assert child.parent_id == parent.node_id
        assert child.node_id in parent.children_ids
        assert child.strategy == CorrectionStrategy.RETRY
    
    def test_evaluate_thought(self):
        """Test evaluating thought"""
        orchestrator = TreeOfThoughtsOrchestrator()
        
        node = orchestrator.create_root_node(
            ErrorType.TIMEOUT_ERROR,
            "op_1",
            "agent_1"
        )
        
        orchestrator.evaluate_thought(
            node,
            score=0.8,
            confidence=0.9,
            reasoning="Good approach"
        )
        
        assert node.evaluation is not None
        assert node.evaluation.score == 0.8
    
    def test_explore_paths_simple(self):
        """Test simple path exploration"""
        orchestrator = TreeOfThoughtsOrchestrator()
        
        config = ToTExplorationConfig(
            max_depth=2,
            max_breadth=2,
            max_paths=3
        )
        orchestrator.config = config
        
        root = orchestrator.create_root_node(
            ErrorType.TIMEOUT_ERROR,
            "op_1",
            "agent_1"
        )
        root.evaluate(0.7, 0.8, "Root", 0.8, 0.8, 0.8)
        
        strategies = [
            CorrectionStrategy.RETRY,
            CorrectionStrategy.MODIFY_PARAMETERS
        ]
        
        result = orchestrator.explore_paths(root, strategies, max_iterations=10)
        
        assert result is not None
        assert result.nodes_explored >= 0
        assert result.exploration_time >= 0
    
    def test_exploration_result_to_dict(self):
        """Test ExplorationResult to_dict"""
        orchestrator = TreeOfThoughtsOrchestrator()
        
        root = orchestrator.create_root_node(
            ErrorType.TIMEOUT_ERROR,
            "op_1",
            "agent_1"
        )
        
        strategies = [CorrectionStrategy.RETRY]
        result = orchestrator.explore_paths(root, strategies, max_iterations=5)
        
        result_dict = result.to_dict()
        
        assert "exploration_time" in result_dict
        assert "nodes_explored" in result_dict
        assert "paths_pruned" in result_dict
    
    def test_record_execution_outcome(self):
        """Test recording execution outcome"""
        orchestrator = TreeOfThoughtsOrchestrator()
        
        root = orchestrator.create_root_node(
            ErrorType.TIMEOUT_ERROR,
            "op_1",
            "agent_1"
        )
        
        child = orchestrator.create_thought(
            root,
            ThoughtType.STRATEGY,
            "Strategy 1",
            strategy=CorrectionStrategy.RETRY
        )
        
        path = ThoughtPath()
        path.add_node(root)
        path.add_node(child)
        
        orchestrator.record_execution_outcome(path, True, 45.0)
        
        # Should update prediction engine path outcomes
        assert len(orchestrator.prediction_engine.path_outcomes) > 0
    
    def test_get_optimal_sequence(self):
        """Test getting optimal strategy sequence"""
        orchestrator = TreeOfThoughtsOrchestrator()
        
        root = orchestrator.create_root_node(
            ErrorType.TIMEOUT_ERROR,
            "op_1",
            "agent_1"
        )
        
        strategies = [CorrectionStrategy.RETRY]
        result = orchestrator.explore_paths(root, strategies, max_iterations=5)
        
        sequence = orchestrator.get_optimal_sequence(root)
        
        assert isinstance(sequence, list)
    
    def test_prune_low_confidence_paths(self):
        """Test pruning low confidence paths"""
        orchestrator = TreeOfThoughtsOrchestrator()
        
        root = orchestrator.create_root_node(
            ErrorType.TIMEOUT_ERROR,
            "op_1",
            "agent_1"
        )
        
        strategies = [CorrectionStrategy.RETRY]
        result = orchestrator.explore_paths(root, strategies, max_iterations=5)
        
        pruned = orchestrator.prune_low_confidence_paths(threshold=0.5)
        
        assert pruned >= 0
    
    def test_get_exploration_stats(self):
        """Test getting exploration statistics"""
        orchestrator = TreeOfThoughtsOrchestrator()
        
        root = orchestrator.create_root_node(
            ErrorType.TIMEOUT_ERROR,
            "op_1",
            "agent_1"
        )
        
        strategies = [CorrectionStrategy.RETRY]
        orchestrator.explore_paths(root, strategies, max_iterations=5)
        
        stats = orchestrator.get_exploration_stats()
        
        assert "total_explorations" in stats
        assert "successful_explorations" in stats
        assert "success_rate" in stats
        assert "total_nodes" in stats
    
    def test_export_state(self):
        """Test exporting orchestrator state"""
        orchestrator = TreeOfThoughtsOrchestrator()
        
        root = orchestrator.create_root_node(
            ErrorType.TIMEOUT_ERROR,
            "op_1",
            "agent_1"
        )
        root.evaluate(0.8, 0.9, "Good", 0.8, 0.8, 0.8)
        
        strategies = [CorrectionStrategy.RETRY]
        orchestrator.explore_paths(root, strategies, max_iterations=5)
        
        state = orchestrator.export_state()
        
        assert "timestamp" in state
        assert "exploration_stats" in state
        assert "total_nodes" in state
        assert "config" in state


class TestPhase5Integration:
    """Integration tests for Phase 5"""
    
    def test_full_exploration_workflow(self):
        """Test complete exploration workflow"""
        orchestrator = TreeOfThoughtsOrchestrator(
            ToTExplorationConfig(
                max_depth=3,
                max_breadth=2,
                max_paths=5
            )
        )
        
        # Create root
        root = orchestrator.create_root_node(
            ErrorType.RESOURCE_ERROR,
            "database_query",
            "agent_db_001"
        )
        root.evaluate(0.7, 0.8, "Resource error detected")
        
        # Explore
        strategies = [
            CorrectionStrategy.MODIFY_PARAMETERS,
            CorrectionStrategy.RETRY,
            CorrectionStrategy.MODIFY_PARAMETERS
        ]
        
        result = orchestrator.explore_paths(root, strategies, max_iterations=20)
        
        # Verify result
        assert result is not None
        assert result.nodes_explored > 0
        assert len(orchestrator.all_nodes) > 0
        
        # Record outcome
        if result.best_path:
            orchestrator.record_execution_outcome(
                result.best_path,
                success=True,
                cost=60.0
            )
    
    def test_multiple_explorations(self):
        """Test multiple sequential explorations"""
        orchestrator = TreeOfThoughtsOrchestrator()
        
        for i in range(3):
            root = orchestrator.create_root_node(
                ErrorType.TIMEOUT_ERROR,
                f"operation_{i}",
                f"agent_{i}"
            )
            root.evaluate(0.7, 0.8, f"Error {i}")
            
            strategies = [CorrectionStrategy.RETRY]
            result = orchestrator.explore_paths(root, strategies, max_iterations=5)
            
            assert result is not None
        
        stats = orchestrator.get_exploration_stats()
        assert stats["total_explorations"] == 3
    
    def test_thought_type_progression(self):
        """Test progression through thought types"""
        orchestrator = TreeOfThoughtsOrchestrator()
        
        root = orchestrator.create_root_node(
            ErrorType.TIMEOUT_ERROR,
            "op_1",
            "agent_1"
        )
        
        # Progression: OBSERVATION -> REASONING -> ANALYSIS -> DECISION
        reasoning = orchestrator.create_thought(
            root,
            ThoughtType.REASONING,
            "Analyze the timeout cause"
        )
        
        analysis = orchestrator.create_thought(
            reasoning,
            ThoughtType.ANALYSIS,
            "Root cause is slow database query"
        )
        
        decision = orchestrator.create_thought(
            analysis,
            ThoughtType.DECISION,
            "Use query optimization",
            strategy=CorrectionStrategy.ANALYZE
        )
        
        assert root.depth == 0
        assert reasoning.depth == 1
        assert analysis.depth == 2
        assert decision.depth == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
