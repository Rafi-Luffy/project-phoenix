"""
Phase 1.2 Integration Tests
Tests for specialized agents, message protocols, and state coordination
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

from autonomous_system.core.specialized_agents import (
    SupervisorAgent, WorkerAgent, MonitorAgent, LearningAgent, DecisionAgent
)
from autonomous_system.core.message_protocol import (
    MessageProtocol, MessageProtocolHandler, ConversationManager,
    AcknowledgmentStatus, ProtocolEndpoint
)
from autonomous_system.core.state_coordination import (
    StateCoordinator, ConsensusManager, DistributedLockManager,
    CoordinationMode, ConsensusStrategy
)
from autonomous_system.core.agent_framework import (
    BaseAgent, AgentRegistry, MessageBus, StateManager, AgentConfig, Message, MessageType
)


class TestSpecializedAgents:
    """Test specialized agent types"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.message_bus = MessageBus()
        self.state_manager = StateManager()
        
    def test_supervisor_agent_creation(self):
        """Test SupervisorAgent creation and basic operations"""
        config = AgentConfig(
            agent_id="supervisor-1",
            agent_type="supervisor",
            name="TestSupervisor"
        )
        
        supervisor = SupervisorAgent(config, self.message_bus, self.state_manager)
        
        assert supervisor.agent_id == "supervisor-1"
        assert supervisor.name == "TestSupervisor"
        assert len(supervisor.managed_agents) == 0
        
    def test_supervisor_agent_worker_registration(self):
        """Test supervisor registering and managing workers"""
        supervisor_config = AgentConfig(
            agent_id="supervisor-1",
            agent_type="supervisor",
            name="TestSupervisor"
        )
        
        worker_config = AgentConfig(
            agent_id="worker-1",
            agent_type="worker",
            name="TestWorker"
        )
        
        supervisor = SupervisorAgent(supervisor_config, self.message_bus, self.state_manager)
        worker = WorkerAgent(worker_config, self.message_bus, self.state_manager)
        
        # Register worker with supervisor
        supervisor.register_managed_agent(worker.agent_id)
        
        assert worker.agent_id in supervisor.managed_agents
        assert len(supervisor.managed_agents) == 1
        
    def test_worker_agent_creation(self):
        """Test WorkerAgent creation"""
        config = AgentConfig(
            agent_id="worker-1",
            agent_type="worker",
            name="TestWorker"
        )
        
        worker = WorkerAgent(config, self.message_bus, self.state_manager)
        
        assert worker.agent_id == "worker-1"
        assert worker.supervisor_id is None
        assert len(worker.task_handlers) == 0
        
    def test_monitor_agent_metric_recording(self):
        """Test MonitorAgent recording metrics"""
        config = AgentConfig(
            agent_id="monitor-1",
            agent_type="monitor",
            name="TestMonitor"
        )
        
        monitor = MonitorAgent(config, self.message_bus, self.state_manager)
        monitor.set_metric_threshold("cpu_usage", 80)
        
        # Record normal metric
        monitor.record_metric("cpu_usage", 45.0)
        assert "cpu_usage" in monitor.metrics
        
        # Record anomalous metric
        monitor.record_metric("cpu_usage", 95.0)
        assert len(monitor.anomalies_detected) > 0
        
    def test_learning_agent_experience_storage(self):
        """Test LearningAgent storing and extracting patterns"""
        config = AgentConfig(
            agent_id="learning-1",
            agent_type="learning",
            name="TestLearning"
        )
        
        learning_agent = LearningAgent(config, self.message_bus, self.state_manager)
        
        # Store experiences
        experience_1 = {"action": "restart", "outcome": "success"}
        experience_2 = {"action": "restart", "outcome": "success"}
        
        learning_agent.store_experience(experience_1)
        learning_agent.store_experience(experience_2)
        
        assert len(learning_agent.experience_buffer) == 2
        
    def test_decision_agent_autonomous_decisions(self):
        """Test DecisionAgent making autonomous decisions"""
        config = AgentConfig(
            agent_id="decision-1",
            agent_type="decision",
            name="TestDecision"
        )
        
        decision_agent = DecisionAgent(config, self.message_bus, self.state_manager)
        
        # Register decision rule
        def simple_rule(context):
            return context.get("health") < 50
        
        decision_agent.register_decision_rule("health_check", simple_rule)
        
        # Evaluate alternatives
        context = {"health": 30, "options": ["restart", "scale_up"]}
        decision = decision_agent.make_decision(context)
        
        assert decision is not None
        assert len(decision_agent.decision_history) > 0


class TestMessageProtocol:
    """Test message protocol system"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.protocol_handler = MessageProtocolHandler()
        
    def test_protocol_handler_initialization(self):
        """Test message protocol handler creation"""
        assert self.protocol_handler is not None
        assert len(self.protocol_handler.pending_acknowledgments) == 0
        
    def test_request_reply_protocol(self):
        """Test REQUEST_REPLY protocol"""
        message_id = self.protocol_handler.send_with_protocol(
            sender_id="agent-1",
            receiver_id="agent-2",
            protocol=MessageProtocol.REQUEST_REPLY,
            content={"query": "status"}
        )
        
        assert message_id is not None
        
    def test_fire_and_forget_protocol(self):
        """Test FIRE_AND_FORGET protocol"""
        message_id = self.protocol_handler.send_with_protocol(
            sender_id="agent-1",
            receiver_id="agent-2",
            protocol=MessageProtocol.FIRE_AND_FORGET,
            content={"notification": "task complete"}
        )
        
        assert message_id is not None
        
    def test_conversation_manager(self):
        """Test conversation management"""
        conversation_manager = ConversationManager()
        
        conv_id = conversation_manager.start_conversation("agent-1", "agent-2")
        assert conv_id is not None
        
        # Add messages to conversation
        conversation_manager.add_message_to_conversation(
            conv_id, "agent-1", {"text": "Hello"}
        )
        
        conversation_manager.add_message_to_conversation(
            conv_id, "agent-2", {"text": "Hi there"}
        )
        
        conversation = conversation_manager.get_conversation(conv_id)
        assert conversation is not None
        assert len(conversation.messages) == 2
        
    def test_acknowledgment_tracking(self):
        """Test message acknowledgment tracking"""
        message_id = self.protocol_handler.send_with_protocol(
            sender_id="agent-1",
            receiver_id="agent-2",
            protocol=MessageProtocol.REQUEST_WAIT_REPLY,
            content={"data": "important"}
        )
        
        # Track acknowledgment
        self.protocol_handler.track_acknowledgment(
            message_id, AcknowledgmentStatus.ACKNOWLEDGED
        )
        
        assert message_id in self.protocol_handler.pending_acknowledgments


class TestStateCoordination:
    """Test state coordination system"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.state_coordinator = StateCoordinator(
            coordination_mode=CoordinationMode.DISTRIBUTED
        )
        self.consensus_manager = ConsensusManager()
        self.lock_manager = DistributedLockManager()
        
    def test_state_coordinator_creation(self):
        """Test state coordinator initialization"""
        assert self.state_coordinator is not None
        assert self.state_coordinator.coordination_mode == CoordinationMode.DISTRIBUTED
        
    def test_state_registration_and_retrieval(self):
        """Test registering and retrieving state"""
        agent_id = "agent-1"
        state = {"status": "active", "health": 100}
        
        self.state_coordinator.register_state(agent_id, state)
        retrieved_state = self.state_coordinator.get_state(agent_id)
        
        assert retrieved_state["status"] == "active"
        assert retrieved_state["health"] == 100
        
    def test_state_update(self):
        """Test state updates"""
        agent_id = "agent-1"
        initial_state = {"status": "active"}
        
        self.state_coordinator.register_state(agent_id, initial_state)
        
        # Update state
        new_state = {"status": "inactive", "reason": "error"}
        self.state_coordinator.update_state(agent_id, new_state)
        
        updated_state = self.state_coordinator.get_state(agent_id)
        assert updated_state["status"] == "inactive"
        
    def test_state_change_tracking(self):
        """Test state change history"""
        agent_id = "agent-1"
        
        self.state_coordinator.register_state(agent_id, {"status": "starting"})
        self.state_coordinator.update_state(agent_id, {"status": "running"})
        self.state_coordinator.update_state(agent_id, {"status": "stopped"})
        
        # State changes should be tracked
        assert len(self.state_coordinator.state_changes) > 0
        
    def test_consensus_manager_voting(self):
        """Test consensus voting"""
        proposal = {"action": "scale_up", "factor": 2}
        
        vote_id = self.consensus_manager.start_voting_round(proposal)
        assert vote_id is not None
        
        # Cast votes
        self.consensus_manager.cast_vote(vote_id, "agent-1", True)
        self.consensus_manager.cast_vote(vote_id, "agent-2", True)
        self.consensus_manager.cast_vote(vote_id, "agent-3", False)
        
        # Check voting round
        voting_round = self.consensus_manager.voting_rounds.get(vote_id)
        assert voting_round is not None
        assert len(voting_round.votes) == 3
        
    def test_distributed_lock_acquisition(self):
        """Test distributed lock acquisition"""
        resource_id = "shared_resource"
        lock = self.lock_manager.create_lock(resource_id, timeout=300)
        
        assert lock is not None
        assert lock.resource_id == resource_id
        
        # Acquire lock
        success = self.lock_manager.acquire_lock(lock.lock_id, "agent-1")
        assert success is True
        
    def test_distributed_lock_release(self):
        """Test distributed lock release"""
        resource_id = "shared_resource"
        lock = self.lock_manager.create_lock(resource_id, timeout=300)
        
        # Acquire lock
        self.lock_manager.acquire_lock(lock.lock_id, "agent-1")
        
        # Release lock
        success = self.lock_manager.release_lock(lock.lock_id, "agent-1")
        assert success is True
        
        # Check lock is no longer held
        assert not lock.is_held()


class TestIntegration:
    """Integration tests combining multiple Phase 1.2 components"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.message_bus = MessageBus()
        self.state_manager = StateManager()
        self.state_coordinator = StateCoordinator(CoordinationMode.DISTRIBUTED)
        self.protocol_handler = MessageProtocolHandler()
        
    def test_supervisor_worker_communication(self):
        """Test supervisor and worker communication through protocol"""
        # Create supervisor
        supervisor_config = AgentConfig(
            agent_id="supervisor-1",
            agent_type="supervisor",
            name="Supervisor"
        )
        supervisor = SupervisorAgent(supervisor_config, self.message_bus, self.state_manager)
        
        # Create worker
        worker_config = AgentConfig(
            agent_id="worker-1",
            agent_type="worker",
            name="Worker"
        )
        worker = WorkerAgent(worker_config, self.message_bus, self.state_manager)
        
        # Register worker
        supervisor.register_managed_agent(worker.agent_id)
        
        # Send protocol message
        message_id = self.protocol_handler.send_with_protocol(
            sender_id=supervisor.agent_id,
            receiver_id=worker.agent_id,
            protocol=MessageProtocol.REQUEST_REPLY,
            content={"task": "process_data", "data": [1, 2, 3]}
        )
        
        assert message_id is not None
        
    def test_monitor_learning_feedback_loop(self):
        """Test monitor collecting metrics and learning agent adapting"""
        # Create monitor
        monitor_config = AgentConfig(
            agent_id="monitor-1",
            agent_type="monitor",
            name="Monitor"
        )
        monitor = MonitorAgent(monitor_config, self.message_bus, self.state_manager)
        
        # Create learning agent
        learning_config = AgentConfig(
            agent_id="learning-1",
            agent_type="learning",
            name="LearningAgent"
        )
        learning_agent = LearningAgent(learning_config, self.message_bus, self.state_manager)
        
        # Monitor records metrics
        monitor.set_metric_threshold("response_time", 1000)
        monitor.record_metric("response_time", 800)
        monitor.record_metric("response_time", 900)
        
        # Learning agent stores these as experiences
        learning_agent.store_experience({
            "metric": "response_time",
            "value": 800,
            "outcome": "healthy"
        })
        
        learning_agent.store_experience({
            "metric": "response_time",
            "value": 900,
            "outcome": "healthy"
        })
        
        assert len(learning_agent.experience_buffer) == 2
        
    def test_coordinated_decision_with_locks(self):
        """Test decision agent making decision with distributed locks"""
        # Create decision agent
        decision_config = AgentConfig(
            agent_id="decision-1",
            agent_type="decision",
            name="DecisionAgent"
        )
        decision_agent = DecisionAgent(decision_config, self.message_bus, self.state_manager)
        
        # Create distributed lock manager
        lock_manager = DistributedLockManager()
        
        # Decision agent acquires lock
        resource_id = "critical_section"
        lock = lock_manager.create_lock(resource_id, timeout=300)
        acquired = lock_manager.acquire_lock(lock.lock_id, decision_agent.agent_id)
        
        assert acquired is True
        
        # Make decision while holding lock
        context = {"resource": resource_id, "options": ["option_a", "option_b"]}
        decision = decision_agent.make_decision(context)
        
        assert decision is not None
        
        # Release lock
        released = lock_manager.release_lock(lock.lock_id, decision_agent.agent_id)
        assert released is True


class TestErrorHandling:
    """Test error handling in Phase 1.2 components"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.message_bus = MessageBus()
        self.state_manager = StateManager()
        
    def test_nonexistent_agent_state(self):
        """Test getting state for non-existent agent"""
        coordinator = StateCoordinator(CoordinationMode.DISTRIBUTED)
        state = coordinator.get_state("nonexistent-agent")
        
        assert state is None
        
    def test_invalid_lock_release(self):
        """Test releasing lock not held"""
        lock_manager = DistributedLockManager()
        lock = lock_manager.create_lock("resource-1", timeout=300)
        
        # Try to release without acquiring
        success = lock_manager.release_lock(lock.lock_id, "agent-1")
        assert success is False
        
    def test_protocol_message_with_invalid_type(self):
        """Test protocol handler with invalid message type"""
        handler = MessageProtocolHandler()
        
        # Send with valid protocol
        message_id = handler.send_with_protocol(
            sender_id="agent-1",
            receiver_id="agent-2",
            protocol=MessageProtocol.REQUEST_REPLY,
            content={"data": "test"}
        )
        
        assert message_id is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
