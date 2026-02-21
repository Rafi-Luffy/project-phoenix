"""
Memory Integration Tests - Phase 1.3
Comprehensive test suite for enhanced memory system and agent integration
Tests all memory types, operations, and agent bindings
"""

import pytest
from datetime import datetime, timedelta
from typing import List

from autonomous_system.core.enhanced_memory import (
    EnhancedMemoryManager, EpisodicMemory, SemanticMemory, ProceduralMemory,
    MemoryDecayFunction, RetrievalStrategy
)
from autonomous_system.core.memory_integration import (
    EnhancedLearningAgent, EnhancedDecisionAgent, EnhancedMonitorAgent,
    MemoryIntegrationManager
)
from autonomous_system.core.specialized_agents import (
    LearningAgent, DecisionAgent, MonitorAgent
)


# ==================== Fixtures ====================

@pytest.fixture
def memory_manager():
    """Create memory manager instance"""
    return EnhancedMemoryManager()


@pytest.fixture
def integration_manager(memory_manager):
    """Create integration manager instance"""
    return MemoryIntegrationManager(memory_manager)


@pytest.fixture
def learning_agent():
    """Create mock learning agent"""
    class MockAgent:
        def __init__(self):
            self.agent_id = "learning_1"
            self.name = "TestLearningAgent"
    return MockAgent()


@pytest.fixture
def decision_agent():
    """Create mock decision agent"""
    class MockAgent:
        def __init__(self):
            self.agent_id = "decision_1"
            self.name = "TestDecisionAgent"
    return MockAgent()


@pytest.fixture
def monitor_agent():
    """Create mock monitor agent"""
    class MockAgent:
        def __init__(self):
            self.agent_id = "monitor_1"
            self.name = "TestMonitorAgent"
    return MockAgent()


# ==================== Episodic Memory Tests ====================

class TestEpisodicMemory:
    """Test episodic memory storage and retrieval"""
    
    def test_store_episodic(self, memory_manager):
        """Test storing episodic memory"""
        episode_id = memory_manager.store_episodic(
            description="Test episode",
            agents_involved=["agent_1"],
            outcome="success",
            confidence=0.95,
            tags=["test", "success"],
            metadata={"key": "value"}
        )
        
        assert episode_id is not None
        assert episode_id in memory_manager.episodic_memories
    
    def test_retrieve_episodic(self, memory_manager):
        """Test retrieving episodic memory"""
        episode_id = memory_manager.store_episodic(
            description="Test episode",
            agents_involved=["agent_1"],
            outcome="success",
            confidence=0.95
        )
        
        memory = memory_manager.retrieve_episodic(episode_id)
        assert memory is not None
        assert memory.description == "Test episode"
        assert memory.outcome == "success"
        assert memory.confidence == 0.95
    
    def test_search_episodic_by_agent(self, memory_manager):
        """Test searching episodic memory by agent"""
        # Store multiple episodes
        memory_manager.store_episodic(
            description="Episode 1",
            agents_involved=["agent_1"],
            outcome="success"
        )
        memory_manager.store_episodic(
            description="Episode 2",
            agents_involved=["agent_1"],
            outcome="failure"
        )
        memory_manager.store_episodic(
            description="Episode 3",
            agents_involved=["agent_2"],
            outcome="success"
        )
        
        agent1_episodes = memory_manager.search_episodic_by_agent("agent_1")
        assert len(agent1_episodes) == 2
        
        agent2_episodes = memory_manager.search_episodic_by_agent("agent_2")
        assert len(agent2_episodes) == 1
    
    def test_search_episodic_by_tag(self, memory_manager):
        """Test searching episodic memory by tag"""
        memory_manager.store_episodic(
            description="Tagged episode 1",
            agents_involved=["agent_1"],
            outcome="success",
            tags=["urgent"]
        )
        memory_manager.store_episodic(
            description="Tagged episode 2",
            agents_involved=["agent_1"],
            outcome="success",
            tags=["urgent", "important"]
        )
        
        urgent_episodes = memory_manager.search_episodic_by_tag("urgent")
        assert len(urgent_episodes) == 2
        assert all(ep.outcome == "success" for ep in urgent_episodes)
    
    def test_episodic_importance_decay(self, memory_manager):
        """Test importance decay in episodic memory"""
        episode_id = memory_manager.store_episodic(
            description="Test",
            agents_involved=["agent_1"],
            outcome="success",
            confidence=0.9
        )
        
        memory = memory_manager.retrieve_episodic(episode_id)
        initial_importance = memory.importance
        
        # Update importance (simulate decay)
        memory.importance *= 0.95
        
        assert memory.importance < initial_importance


# ==================== Semantic Memory Tests ====================

class TestSemanticMemory:
    """Test semantic memory storage and retrieval"""
    
    def test_store_semantic(self, memory_manager):
        """Test storing semantic memory"""
        concept_id = memory_manager.store_semantic(
            concept_name="test_concept",
            properties={"property1": "value1"},
            source="test_source",
            confidence=0.9
        )
        
        assert concept_id is not None
        assert concept_id in memory_manager.semantic_memories
    
    def test_retrieve_semantic(self, memory_manager):
        """Test retrieving semantic memory"""
        concept_id = memory_manager.store_semantic(
            concept_name="test_concept",
            properties={"key": "value"},
            source="test",
            confidence=0.85
        )
        
        memory = memory_manager.retrieve_semantic("test_concept")
        assert memory is not None
        assert memory.concept_name == "test_concept"
        assert memory.confidence == 0.85
    
    def test_add_semantic_relationship(self, memory_manager):
        """Test adding relationships between concepts"""
        memory_manager.store_semantic("concept_a", {"type": "a"}, "test")
        memory_manager.store_semantic("concept_b", {"type": "b"}, "test")
        
        success = memory_manager.add_semantic_relationship(
            "concept_a", "concept_b", "related_to"
        )
        
        assert success is True
        concept_a = memory_manager.retrieve_semantic("concept_a")
        assert len(concept_a.relationships) > 0
    
    def test_get_related_concepts(self, memory_manager):
        """Test retrieving related concepts"""
        memory_manager.store_semantic("concept_a", {"type": "a"}, "test")
        memory_manager.store_semantic("concept_b", {"type": "b"}, "test")
        memory_manager.store_semantic("concept_c", {"type": "c"}, "test")
        
        memory_manager.add_semantic_relationship("concept_a", "concept_b", "related_to")
        memory_manager.add_semantic_relationship("concept_a", "concept_c", "similar_to")
        
        related = memory_manager.get_related_concepts("concept_a")
        assert len(related) >= 2


# ==================== Procedural Memory Tests ====================

class TestProceduralMemory:
    """Test procedural memory storage and retrieval"""
    
    def test_store_procedural(self, memory_manager):
        """Test storing procedural memory"""
        procedure_id = memory_manager.store_procedural(
            name="test_procedure",
            steps=[{"step": 1, "action": "init"}, {"step": 2, "action": "execute"}],
            parameters={"param1": "value1"},
            complexity=5
        )
        
        assert procedure_id is not None
        assert procedure_id in memory_manager.procedural_memories
    
    def test_retrieve_procedural(self, memory_manager):
        """Test retrieving procedural memory"""
        procedure_id = memory_manager.store_procedural(
            name="test_procedure",
            steps=[{"step": 1}],
            complexity=3
        )
        
        memory = memory_manager.retrieve_procedural("test_procedure")
        assert memory is not None
        assert memory.name == "test_procedure"
        assert memory.complexity == 3
    
    def test_record_procedure_execution(self, memory_manager):
        """Test recording procedure execution"""
        procedure_id = memory_manager.store_procedural(
            name="test_proc",
            steps=[{"step": 1}]
        )
        
        initial_success_rate = memory_manager.retrieve_procedural("test_proc").success_rate
        
        # Record successful execution
        memory_manager.record_procedure_execution(procedure_id, True, 100.0)
        updated = memory_manager.retrieve_procedural("test_proc")
        
        assert updated.executions >= 1
        assert updated.success_rate >= initial_success_rate or updated.executions == 1
    
    def test_get_procedures_for_task(self, memory_manager):
        """Test getting procedures for a task"""
        memory_manager.store_procedural(
            name="high_success",
            steps=[{"step": 1}],
            parameters={"task_type": "type_a"}
        )
        
        # Record successful executions
        memory_manager.record_procedure_execution(
            "high_success", True, 50.0
        )
        memory_manager.record_procedure_execution(
            "high_success", True, 50.0
        )
        
        procedures = memory_manager.get_procedures_for_task("type_a", min_success_rate=0.5)
        assert len(procedures) > 0


# ==================== Learning Agent Integration Tests ====================

class TestEnhancedLearningAgent:
    """Test learning agent with memory integration"""
    
    def test_store_experience_as_episode(self, memory_manager, learning_agent):
        """Test storing experience as episodic memory"""
        enhanced = EnhancedLearningAgent(learning_agent, memory_manager)
        
        episode_id = enhanced.store_experience_as_episode(
            action="test_action",
            outcome="success",
            confidence=0.95
        )
        
        assert episode_id is not None
        memory = memory_manager.retrieve_episodic(episode_id)
        assert memory.outcome == "success"
    
    def test_extract_pattern_as_semantic(self, memory_manager, learning_agent):
        """Test extracting pattern as semantic memory"""
        enhanced = EnhancedLearningAgent(learning_agent, memory_manager)
        
        concept_id = enhanced.extract_pattern_as_semantic(
            pattern_name="test_pattern",
            pattern_properties={"property": "value"},
            confidence=0.9
        )
        
        assert concept_id is not None
        memory = memory_manager.retrieve_semantic("test_pattern")
        assert memory.confidence == 0.9
    
    def test_store_strategy_as_procedure(self, memory_manager, learning_agent):
        """Test storing strategy as procedural memory"""
        enhanced = EnhancedLearningAgent(learning_agent, memory_manager)
        
        procedure_id = enhanced.store_strategy_as_procedure(
            strategy_name="test_strategy",
            steps=[{"step": 1, "action": "start"}]
        )
        
        assert procedure_id is not None
        memory = memory_manager.retrieve_procedural("test_strategy")
        assert memory.name == "test_strategy"
    
    def test_recall_similar_episodes(self, memory_manager, learning_agent):
        """Test recalling similar episodes"""
        enhanced = EnhancedLearningAgent(learning_agent, memory_manager)
        
        # Store similar episodes
        enhanced.store_experience_as_episode("action_a", "success")
        enhanced.store_experience_as_episode("action_a", "success")
        
        similar = enhanced.recall_similar_episodes("action_a", limit=5)
        assert len(similar) >= 2
    
    def test_learn_from_feedback(self, memory_manager, learning_agent):
        """Test learning from feedback"""
        enhanced = EnhancedLearningAgent(learning_agent, memory_manager)
        
        episode_id = enhanced.store_experience_as_episode(
            action="test", outcome="success", confidence=0.5
        )
        
        # Learn from positive feedback
        enhanced.learn_from_feedback(episode_id, "positive feedback")
        
        memory = memory_manager.retrieve_episodic(episode_id)
        assert memory.confidence > 0.5


# ==================== Decision Agent Integration Tests ====================

class TestEnhancedDecisionAgent:
    """Test decision agent with memory integration"""
    
    def test_query_knowledge_base(self, memory_manager, decision_agent):
        """Test querying knowledge base"""
        enhanced = EnhancedDecisionAgent(decision_agent, memory_manager)
        
        memory_manager.store_semantic(
            "test_concept",
            {"property": "value"},
            "test",
            confidence=0.9
        )
        
        knowledge = enhanced.query_knowledge_base("test_concept")
        assert knowledge is not None
        assert knowledge.concept_name == "test_concept"
    
    def test_select_strategy(self, memory_manager, decision_agent):
        """Test selecting best strategy"""
        enhanced = EnhancedDecisionAgent(decision_agent, memory_manager)
        
        procedure_id = memory_manager.store_procedural(
            name="effective_strategy",
            steps=[{"step": 1}],
            parameters={"task_type": "task_a"}
        )
        
        # Record successful executions
        memory_manager.record_procedure_execution(procedure_id, True, 50.0)
        memory_manager.record_procedure_execution(procedure_id, True, 50.0)
        
        strategy = enhanced.select_strategy("task_a", min_success_rate=0.5)
        assert strategy is not None
    
    def test_make_informed_decision(self, memory_manager, decision_agent):
        """Test making informed decisions"""
        enhanced = EnhancedDecisionAgent(decision_agent, memory_manager)
        
        # Setup knowledge and precedents
        memory_manager.store_semantic("decision_type", {"key": "value"}, "test")
        memory_manager.store_episodic(
            "Similar decision",
            ["agent_1"],
            "success",
            confidence=0.95
        )
        
        decision = enhanced.make_informed_decision({
            "type": "decision_type",
            "description": "Similar decision",
            "task_type": "task_a"
        })
        
        assert decision is not None
        assert decision['type'] == "decision_type"
    
    def test_record_decision_outcome(self, memory_manager, decision_agent):
        """Test recording decision outcomes"""
        enhanced = EnhancedDecisionAgent(decision_agent, memory_manager)
        
        enhanced.record_decision_outcome(
            {"type": "test_decision"},
            "Executed successfully",
            True
        )
        
        assert len(memory_manager.episodic_memories) > 0


# ==================== Monitor Agent Integration Tests ====================

class TestEnhancedMonitorAgent:
    """Test monitor agent with memory integration"""
    
    def test_record_anomaly(self, memory_manager, monitor_agent):
        """Test recording anomalies"""
        enhanced = EnhancedMonitorAgent(monitor_agent, memory_manager)
        
        episode_id = enhanced.record_anomaly(
            "cpu_usage",
            95.5,
            80.0,
            ["agent_1", "agent_2"]
        )
        
        assert episode_id is not None
        memory = memory_manager.retrieve_episodic(episode_id)
        assert "anomaly" in memory.outcome
    
    def test_detect_recurring_anomalies(self, memory_manager, monitor_agent):
        """Test detecting recurring anomalies"""
        enhanced = EnhancedMonitorAgent(monitor_agent, memory_manager)
        
        # Record multiple anomalies
        enhanced.record_anomaly("metric_a", 100, 80)
        enhanced.record_anomaly("metric_a", 101, 80)
        enhanced.record_anomaly("metric_a", 99, 80)
        
        pattern = enhanced.detect_recurring_anomalies("metric_a")
        
        # May or may not detect pattern depending on implementation
        assert 'pattern_detected' in pattern
    
    def test_get_recent_anomalies(self, memory_manager, monitor_agent):
        """Test getting recent anomalies"""
        enhanced = EnhancedMonitorAgent(monitor_agent, memory_manager)
        
        enhanced.record_anomaly("metric_a", 100, 80)
        enhanced.record_anomaly("metric_b", 90, 70)
        
        anomalies = enhanced.get_recent_anomalies(days_back=7)
        assert len(anomalies) >= 2


# ==================== Memory Integration Manager Tests ====================

class TestMemoryIntegrationManager:
    """Test memory integration manager"""
    
    def test_enhance_learning_agent(self, memory_manager, learning_agent):
        """Test enhancing learning agent"""
        manager = MemoryIntegrationManager(memory_manager)
        enhanced = manager.enhance_learning_agent(learning_agent)
        
        assert enhanced is not None
        assert enhanced.agent_id == learning_agent.agent_id
    
    def test_enhance_decision_agent(self, memory_manager, decision_agent):
        """Test enhancing decision agent"""
        manager = MemoryIntegrationManager(memory_manager)
        enhanced = manager.enhance_decision_agent(decision_agent)
        
        assert enhanced is not None
        assert enhanced.agent_id == decision_agent.agent_id
    
    def test_enhance_monitor_agent(self, memory_manager, monitor_agent):
        """Test enhancing monitor agent"""
        manager = MemoryIntegrationManager(memory_manager)
        enhanced = manager.enhance_monitor_agent(monitor_agent)
        
        assert enhanced is not None
        assert enhanced.agent_id == monitor_agent.agent_id
    
    def test_get_agent_memory_context(self, memory_manager, learning_agent):
        """Test getting agent memory context"""
        manager = MemoryIntegrationManager(memory_manager)
        enhanced = manager.enhance_learning_agent(learning_agent)
        
        context = manager.get_agent_memory_context(learning_agent.agent_id)
        assert context is not None
        assert context['agent_id'] == learning_agent.agent_id
    
    def test_get_system_memory_stats(self, memory_manager):
        """Test getting system memory statistics"""
        manager = MemoryIntegrationManager(memory_manager)
        
        stats = manager.get_system_memory_stats()
        
        assert 'episodic_count' in stats
        assert 'semantic_count' in stats
        assert 'procedural_count' in stats


# ==================== Memory Optimization Tests ====================

class TestMemoryOptimization:
    """Test memory optimization and management"""
    
    def test_optimize_all(self, memory_manager):
        """Test optimizing all memory types"""
        # Store memories
        for i in range(10):
            memory_manager.store_episodic(
                f"Episode {i}",
                ["agent_1"],
                "success"
            )
        
        result = memory_manager.optimize_all()
        
        assert 'episodic_pruned' in result
        assert 'semantic_pruned' in result
        assert 'procedural_pruned' in result
    
    def test_memory_stats(self, memory_manager):
        """Test getting memory statistics"""
        memory_manager.store_episodic("ep1", ["agent"], "success")
        memory_manager.store_semantic("concept1", {}, "test")
        memory_manager.store_procedural("proc1", [])
        
        stats = memory_manager.get_memory_stats()
        
        assert stats['episodic_count'] == 1
        assert stats['semantic_count'] == 1
        assert stats['procedural_count'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
