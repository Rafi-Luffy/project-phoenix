"""
Core System Orchestrator
Integrates all Phase 1.1, 1.2, 1.3 components
Phase 1.1: Database, API, Auth, Monitoring, Agents, Memory
Phase 1.2: Specialized Agents, Message Protocols, State Coordination
Phase 1.3: Enhanced Memory System Integration
"""

from typing import Dict, Optional, Any, List
from datetime import datetime
import logging
import asyncio

from autonomous_system.core.database import PostgreSQLDatabase
from autonomous_system.core.auth import AuthenticationManager, UserRole, PermissionLevel
from autonomous_system.core.monitoring import (
    EventTracker, EventType, StructuredLogger, MetricsCollector, 
    MetricType, AlertManager, PerformanceMonitor
)
from autonomous_system.core.agent_framework import (
    MessageBus, StateManager, AgentRegistry, AgentConfig, AgentState,
    MessageType, Priority
)
from autonomous_system.core.memory_system import (
    MemoryManager, MemoryType, MemoryPriority, ContextWindow
)

# Phase 1.2: Agent Framework Expansion
from autonomous_system.core.specialized_agents import (
    SupervisorAgent, WorkerAgent, MonitorAgent, LearningAgent, DecisionAgent
)
from autonomous_system.core.message_protocol import (
    MessageProtocol, MessageProtocolHandler, ConversationManager
)
from autonomous_system.core.state_coordination import (
    StateCoordinator, ConsensusManager, DistributedLockManager,
    CoordinationMode, ConsensusStrategy
)

# Phase 1.3: Enhanced Memory System
from autonomous_system.core.enhanced_memory import EnhancedMemoryManager
from autonomous_system.core.memory_integration import (
    EnhancedLearningAgent, EnhancedDecisionAgent, EnhancedMonitorAgent,
    MemoryIntegrationManager
)


class CoreOrchestrator:
    """Main system orchestrator for autonomous self-healing system"""
    
    def __init__(self, db_url: str = "postgresql://user:password@localhost/autonomous_db"):
        """Initialize the core system"""
        
        # Initialize logger
        self.logger = logging.getLogger("CoreOrchestrator")
        self.logger.info("Initializing Core Orchestrator...")
        
        # Initialize components
        self.db_manager = PostgreSQLDatabase()
        self.auth_manager = AuthenticationManager()
        self.event_tracker = EventTracker()
        self.structured_logger = StructuredLogger()
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.performance_monitor = PerformanceMonitor()
        
        # Initialize agent framework
        self.message_bus = MessageBus()
        self.state_manager = StateManager()
        self.agent_registry = AgentRegistry()
        
        # Initialize memory system
        self.memory_manager = MemoryManager(short_term_size=1000)
        self.context_window = ContextWindow(memory_manager=self.memory_manager)
        
        # Phase 1.2: Advanced agent framework
        self.message_protocol_handler = MessageProtocolHandler()
        self.conversation_manager = ConversationManager()
        self.state_coordinator = StateCoordinator(coordination_mode=CoordinationMode.DISTRIBUTED)
        self.consensus_manager = ConsensusManager()
        self.distributed_lock_manager = DistributedLockManager()
        
        # Phase 1.3: Enhanced Memory System Integration
        self.enhanced_memory_manager = EnhancedMemoryManager()
        self.memory_integration_manager = MemoryIntegrationManager(self.enhanced_memory_manager)
        self.enhanced_agents: Dict[str, Any] = {}
        
        # System state
        self.system_initialized = False
        self.startup_time = None
        self.system_id = None
    
    async def initialize(self) -> bool:
        """Initialize all system components"""
        try:
            # Track initialization event
            perf_id = "system_init"
            self.performance_monitor.start_timer(perf_id)
            
            # Connect to database and run migrations
            self.logger.info("Initializing database...")
            await self.db_manager.connect()
            await self.db_manager.migrate()
            
            # Initialize default admin user
            self.logger.info("Setting up default admin user...")
            admin_id = self.auth_manager.register_user(
                username="admin",
                email="admin@autonomous-system.local",
                password="admin_password",  # Should be changed in production
                role=UserRole.ADMIN
            )
            
            # Record initialization event
            self.event_tracker.track_event(
                EventType.SYSTEM_HEALTH_CHECK,
                {
                    'status': 'initializing',
                    'components': [
                        'database', 'auth', 'monitoring', 'agents', 'memory'
                    ]
                }
            )
            
            # Record initialization metric
            init_time = self.performance_monitor.end_timer(perf_id)
            
            self.system_initialized = True
            self.startup_time = datetime.now()
            
            self.structured_logger.info(
                "Core Orchestrator initialized successfully",
                {
                    'initialization_time_ms': init_time,
                    'admin_user_created': admin_id is not None
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            self.event_tracker.track_event(
                EventType.ERROR_DETECTED,
                {'error': str(e), 'phase': 'initialization'}
            )
            return False
    
    async def shutdown(self) -> bool:
        """Graceful shutdown"""
        try:
            self.logger.info("Initiating system shutdown...")
            
            # Stop all agents
            for agent_id in list(self.agent_registry.agents.keys()):
                self.agent_registry.remove_agent(agent_id)
            
            # Flush metrics and logs
            self.memory_manager.optimize_memory()
            
            # Disconnect database
            await self.db_manager.disconnect()
            
            self.structured_logger.info("System shutdown completed", {
                'uptime_seconds': (datetime.now() - self.startup_time).total_seconds()
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")
            return False
    
    # --- Authentication & Authorization ---
    
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and get token"""
        token_data = self.auth_manager.authenticate(username, password)
        if token_data:
            self.event_tracker.track_event(
                EventType.SYSTEM_HEALTH_CHECK,
                {'action': 'user_authentication', 'user': username}
            )
            return token_data.token
        return None
    
    def verify_user_permission(self, token: str, required_permission: PermissionLevel) -> bool:
        """Verify user has required permission"""
        return self.auth_manager.check_permission(token, required_permission)
    
    # --- Agent Management ---
    
    def create_agent(self, agent_type: str, agent_name: str, 
                    description: str = "", config_data: Dict[str, Any] = None) -> Optional[str]:
        """Create a new agent"""
        try:
            import uuid
            agent_id = str(uuid.uuid4())
            
            config = AgentConfig(
                agent_id=agent_id,
                agent_type=agent_type,
                name=agent_name,
                description=description,
                **(config_data or {})
            )
            
            agent = self.agent_registry.create_agent(
                config,
                message_bus=self.message_bus,
                state_manager=self.state_manager
            )
            
            if agent:
                self.event_tracker.track_event(
                    EventType.AGENT_CREATED,
                    {'agent_id': agent_id, 'agent_type': agent_type, 'name': agent_name}
                )
                
                self.structured_logger.info(
                    f"Agent created: {agent_name}",
                    {'agent_id': agent_id, 'agent_type': agent_type}
                )
                
                return agent_id
        except Exception as e:
            self.logger.error(f"Agent creation failed: {e}")
        
        return None
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent status"""
        agent = self.agent_registry.get_agent(agent_id)
        if agent:
            return agent.get_status()
        return None
    
    def get_all_agents_status(self) -> List[Dict[str, Any]]:
        """Get status of all agents"""
        return [agent.get_status() for agent in self.agent_registry.get_all_agents().values()]
    
    # --- Task Management ---
    
    async def execute_task(self, agent_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task on an agent"""
        agent = self.agent_registry.get_agent(agent_id)
        if not agent:
            return {'error': f'Agent not found: {agent_id}', 'success': False}
        
        try:
            perf_id = f"task_execution_{agent_id}"
            self.performance_monitor.start_timer(perf_id)
            
            self.event_tracker.track_event(
                EventType.TASK_STARTED,
                {'agent_id': agent_id, 'task_data': task_data}
            )
            
            result = await agent.execute_task(task_data)
            
            execution_time = self.performance_monitor.end_timer(perf_id)
            
            self.event_tracker.track_event(
                EventType.TASK_COMPLETED,
                {'agent_id': agent_id, 'execution_time_ms': execution_time}
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            self.event_tracker.track_event(
                EventType.TASK_FAILED,
                {'agent_id': agent_id, 'error': str(e)}
            )
            return {'error': str(e), 'success': False}
    
    # --- Memory Management ---
    
    def store_memory(self, content: Dict[str, Any], memory_type: MemoryType,
                    agent_id: str = None, tags: List[str] = None,
                    priority: MemoryPriority = MemoryPriority.NORMAL) -> str:
        """Store memory"""
        return self.memory_manager.store_memory(
            content=content,
            memory_type=memory_type,
            priority=priority,
            tags=tags,
            agent_id=agent_id
        )
    
    def retrieve_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve memory"""
        item = self.memory_manager.retrieve_memory(memory_id)
        if item:
            return item.to_dict()
        return None
    
    def search_memories(self, query: str = None, agent_id: str = None,
                       memory_type: MemoryType = None) -> List[Dict[str, Any]]:
        """Search memories"""
        memories = self.memory_manager.search_memory(
            query=query,
            agent_id=agent_id,
            memory_type=memory_type
        )
        return [m.to_dict() for m in memories]
    
    # --- Monitoring & Logging ---
    
    def record_metric(self, metric_type: MetricType, value: float, tags: Dict[str, str] = None):
        """Record system metric"""
        self.metrics_collector.record_metric(metric_type, value, tags)
    
    def get_system_metrics(self, metric_type: Optional[MetricType] = None) -> List[Dict]:
        """Get system metrics"""
        return self.metrics_collector.get_metrics(metric_type)
    
    def get_active_alerts(self) -> List[Dict]:
        """Get active system alerts"""
        return self.alert_manager.get_active_alerts()
    
    def get_system_logs(self, limit: int = 100) -> List[Dict]:
        """Get system logs"""
        return self.structured_logger.get_logs(limit)
    
    def get_event_history(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[Dict]:
        """Get event history"""
        return self.event_tracker.get_events(event_type, limit)
    
    # --- System Status ---
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        uptime = None
        if self.startup_time:
            uptime = (datetime.now() - self.startup_time).total_seconds()
        
        return {
            'system_id': self.system_id,
            'initialized': self.system_initialized,
            'uptime_seconds': uptime,
            'startup_time': self.startup_time.isoformat() if self.startup_time else None,
            'timestamp': datetime.now().isoformat(),
            'components': {
                'database': {'connected': True},  # Would check actual connection
                'auth': {'users_registered': len(self.auth_manager.users)},
                'agents': {
                    'total': len(self.agent_registry.agents),
                    'by_state': self._count_agents_by_state()
                },
                'memory': self.memory_manager.get_memory_stats(),
                'monitoring': {
                    'active_alerts': len(self.alert_manager.get_active_alerts()),
                    'total_events': len(self.event_tracker.events),
                    'total_logs': len(self.structured_logger.logs)
                }
            }
        }
    
    def _count_agents_by_state(self) -> Dict[str, int]:
        """Count agents by state"""
        counts = {state.value: 0 for state in AgentState}
        for agent in self.agent_registry.get_all_agents().values():
            state = agent.get_state()
            counts[state.value] += 1
        return counts
    
    # --- Message Passing ---
    
    def send_message(self, sender_id: str, receiver_id: Optional[str],
                    message_type: MessageType, content: Dict[str, Any],
                    priority: Priority = Priority.NORMAL) -> str:
        """Send message between agents"""
        from autonomous_system.core.agent_framework import Message
        import uuid
        
        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content,
            priority=priority,
            message_id=str(uuid.uuid4())
        )
        
        self.message_bus.publish(message)
        return message.message_id
    
    def get_pending_messages(self, agent_id: str) -> List[Dict]:
        """Get pending messages for agent"""
        messages = self.message_bus.get_messages(receiver_id=agent_id)
        return [m.to_dict() for m in messages]
    
    # --- Health Checks ---
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform system health check"""
        perf_id = "health_check"
        self.performance_monitor.start_timer(perf_id)
        
        try:
            # Check database
            db_healthy = await self.db_manager.connect()
            
            # Check agents
            agents_healthy = len(self.agent_registry.agents) >= 0
            
            # Check memory
            memory_stats = self.memory_manager.get_memory_stats()
            memory_healthy = memory_stats['total_memories'] >= 0
            
            health_check_time = self.performance_monitor.end_timer(perf_id)
            
            is_healthy = db_healthy and agents_healthy and memory_healthy
            
            return {
                'status': 'healthy' if is_healthy else 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'health_check_time_ms': health_check_time,
                'checks': {
                    'database': {'healthy': db_healthy},
                    'agents': {'healthy': agents_healthy, 'count': len(self.agent_registry.agents)},
                    'memory': {'healthy': memory_healthy, 'stats': memory_stats}
                }
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    # --- Phase 1.2: Advanced Agent Framework ---
    
    def create_specialized_agent(self, agent_type: str, agent_name: str, 
                                description: str = "", config_data: Dict[str, Any] = None) -> Optional[str]:
        """Create a specialized agent (Supervisor, Worker, Monitor, Learning, Decision)"""
        try:
            import uuid
            agent_id = str(uuid.uuid4())
            
            config = AgentConfig(
                agent_id=agent_id,
                agent_type=agent_type,
                name=agent_name,
                description=description,
                **(config_data or {})
            )
            
            # Create specialized agent based on type
            specialized_agent = None
            if agent_type.lower() == "supervisor":
                specialized_agent = SupervisorAgent(config, self.message_bus, self.state_manager)
            elif agent_type.lower() == "worker":
                specialized_agent = WorkerAgent(config, self.message_bus, self.state_manager)
            elif agent_type.lower() == "monitor":
                specialized_agent = MonitorAgent(config, self.message_bus, self.state_manager)
            elif agent_type.lower() == "learning":
                specialized_agent = LearningAgent(config, self.message_bus, self.state_manager)
            elif agent_type.lower() == "decision":
                specialized_agent = DecisionAgent(config, self.message_bus, self.state_manager)
            
            if specialized_agent:
                # Register with agent registry
                self.agent_registry.agents[agent_id] = specialized_agent
                
                # Register state with coordinator
                self.state_coordinator.register_state(agent_id, {'status': 'created', 'type': agent_type})
                
                self.event_tracker.track_event(
                    EventType.AGENT_CREATED,
                    {'agent_id': agent_id, 'agent_type': agent_type, 'name': agent_name}
                )
                
                self.structured_logger.info(
                    f"Specialized agent created: {agent_name}",
                    {'agent_id': agent_id, 'agent_type': agent_type}
                )
                
                return agent_id
                
        except Exception as e:
            self.logger.error(f"Specialized agent creation failed: {e}")
        
        return None
    
    def send_protocol_message(self, sender_id: str, receiver_id: str, 
                             protocol: MessageProtocol, content: Dict[str, Any]) -> str:
        """Send message with specific protocol"""
        try:
            message_id = self.message_protocol_handler.send_with_protocol(
                sender_id=sender_id,
                receiver_id=receiver_id,
                protocol=protocol,
                content=content
            )
            
            self.event_tracker.track_event(
                EventType.TASK_STARTED,
                {'sender': sender_id, 'receiver': receiver_id, 'protocol': protocol.value}
            )
            
            return message_id
            
        except Exception as e:
            self.logger.error(f"Protocol message sending failed: {e}")
            return None
    
    def get_agent_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent state from coordinator"""
        return self.state_coordinator.get_state(agent_id)
    
    def update_agent_state(self, agent_id: str, new_state: Dict[str, Any]) -> bool:
        """Update agent state in coordinator"""
        try:
            self.state_coordinator.update_state(agent_id, new_state)
            
            self.event_tracker.track_event(
                EventType.SYSTEM_HEALTH_CHECK,
                {'agent_id': agent_id, 'state_update': new_state}
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"State update failed: {e}")
            return False
    
    def subscribe_to_state_changes(self, agent_id: str, callback) -> str:
        """Subscribe to state changes for an agent"""
        return self.state_coordinator.subscribe_to_state_changes(agent_id, callback)
    
    def acquire_distributed_lock(self, resource_id: str, agent_id: str, timeout: int = 300) -> bool:
        """Acquire distributed lock for resource"""
        try:
            lock = self.distributed_lock_manager.create_lock(resource_id, timeout)
            success = self.distributed_lock_manager.acquire_lock(lock.lock_id, agent_id)
            
            if success:
                self.event_tracker.track_event(
                    EventType.SYSTEM_HEALTH_CHECK,
                    {'lock_acquired': resource_id, 'agent_id': agent_id}
                )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Lock acquisition failed: {e}")
            return False
    
    def release_distributed_lock(self, resource_id: str, agent_id: str) -> bool:
        """Release distributed lock"""
        try:
            locks = self.distributed_lock_manager.locks
            lock = next((l for l in locks.values() if l.resource_id == resource_id), None)
            
            if lock:
                success = self.distributed_lock_manager.release_lock(lock.lock_id, agent_id)
                
                if success:
                    self.event_tracker.track_event(
                        EventType.SYSTEM_HEALTH_CHECK,
                        {'lock_released': resource_id, 'agent_id': agent_id}
                    )
                
                return success
            
            return False
            
        except Exception as e:
            self.logger.error(f"Lock release failed: {e}")
            return False
    
    def start_consensus_vote(self, proposal: Dict[str, Any], 
                            required_agents: List[str] = None) -> Optional[str]:
        """Start consensus voting round"""
        try:
            vote_id = self.consensus_manager.start_voting_round(proposal)
            
            self.event_tracker.track_event(
                EventType.TASK_STARTED,
                {'vote_id': vote_id, 'proposal': proposal}
            )
            
            return vote_id
            
        except Exception as e:
            self.logger.error(f"Consensus vote failed: {e}")
            return None
    
    def cast_consensus_vote(self, vote_id: str, agent_id: str, vote: bool) -> bool:
        """Cast vote in consensus round"""
        try:
            self.consensus_manager.cast_vote(vote_id, agent_id, vote)
            
            self.event_tracker.track_event(
                EventType.TASK_COMPLETED,
                {'vote_id': vote_id, 'voter': agent_id, 'vote': vote}
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Vote casting failed: {e}")
            return False
    
    def get_phase_1_2_status(self) -> Dict[str, Any]:
        """Get Phase 1.2 component status"""
        return {
            'message_protocol_handler': {
                'active': True,
                'protocols_supported': [p.value for p in MessageProtocol]
            },
            'conversation_manager': {
                'active_conversations': len(self.conversation_manager.active_conversations),
                'completed_conversations': len(self.conversation_manager.completed_conversations)
            },
            'state_coordinator': {
                'coordination_mode': self.state_coordinator.coordination_mode.value,
                'agents_tracked': len(self.state_coordinator.agent_states)
            },
            'consensus_manager': {
                'active_votes': len(self.consensus_manager.voting_rounds),
                'completed_votes': len(self.consensus_manager.consensus_history)
            },
            'distributed_locks': {
                'active_locks': len(self.distributed_lock_manager.locks)
            },
            'enhanced_memory': {
                'episodic_count': len(self.enhanced_memory_manager.episodic_memories),
                'semantic_count': len(self.enhanced_memory_manager.semantic_memories),
                'procedural_count': len(self.enhanced_memory_manager.procedural_memories),
                'enhanced_agents': len(self.enhanced_agents)
            }
        }
    
    # ==================== Phase 1.3: Enhanced Memory Methods ====================
    
    def get_enhanced_memory_manager(self) -> EnhancedMemoryManager:
        """Get enhanced memory manager instance"""
        return self.enhanced_memory_manager
    
    def get_memory_integration_manager(self) -> MemoryIntegrationManager:
        """Get memory integration manager instance"""
        return self.memory_integration_manager
    
    def enhance_learning_agent(self, agent: LearningAgent) -> EnhancedLearningAgent:
        """Enhance learning agent with memory capabilities"""
        enhanced = self.memory_integration_manager.enhance_learning_agent(agent)
        self.enhanced_agents[agent.agent_id] = enhanced
        self.logger.info(f"Enhanced learning agent: {agent.agent_id}")
        return enhanced
    
    def enhance_decision_agent(self, agent: DecisionAgent) -> EnhancedDecisionAgent:
        """Enhance decision agent with memory capabilities"""
        enhanced = self.memory_integration_manager.enhance_decision_agent(agent)
        self.enhanced_agents[agent.agent_id] = enhanced
        self.logger.info(f"Enhanced decision agent: {agent.agent_id}")
        return enhanced
    
    def enhance_monitor_agent(self, agent: MonitorAgent) -> EnhancedMonitorAgent:
        """Enhance monitor agent with memory capabilities"""
        enhanced = self.memory_integration_manager.enhance_monitor_agent(agent)
        self.enhanced_agents[agent.agent_id] = enhanced
        self.logger.info(f"Enhanced monitor agent: {agent.agent_id}")
        return enhanced
    
    def get_enhanced_agent(self, agent_id: str) -> Optional[Any]:
        """Get enhanced agent by ID"""
        return self.enhanced_agents.get(agent_id)
    
    def store_episodic_memory(self, description: str, agents: List[str],
                             outcome: str, confidence: float = 0.8,
                             tags: List[str] = None, metadata: Dict = None) -> str:
        """Store episodic memory"""
        return self.enhanced_memory_manager.store_episodic(
            description=description,
            agents_involved=agents,
            outcome=outcome,
            confidence=confidence,
            tags=tags or [],
            metadata=metadata or {}
        )
    
    def retrieve_episodic_memory(self, episode_id: str):
        """Retrieve episodic memory"""
        return self.enhanced_memory_manager.retrieve_episodic(episode_id)
    
    def store_semantic_memory(self, concept_name: str, properties: Dict,
                             source: str, confidence: float = 0.8) -> str:
        """Store semantic memory"""
        return self.enhanced_memory_manager.store_semantic(
            concept_name=concept_name,
            properties=properties,
            source=source,
            confidence=confidence
        )
    
    def retrieve_semantic_memory(self, concept_name: str):
        """Retrieve semantic memory"""
        return self.enhanced_memory_manager.retrieve_semantic(concept_name)
    
    def store_procedural_memory(self, name: str, steps: List[Dict],
                               parameters: Dict = None, complexity: int = 5) -> str:
        """Store procedural memory"""
        return self.enhanced_memory_manager.store_procedural(
            name=name,
            steps=steps,
            parameters=parameters or {},
            complexity=complexity
        )
    
    def retrieve_procedural_memory(self, procedure_name: str):
        """Retrieve procedural memory"""
        return self.enhanced_memory_manager.retrieve_procedural(procedure_name)
    
    def search_episodic_by_agent(self, agent_id: str, limit: int = 50):
        """Search episodic memories by agent"""
        return self.enhanced_memory_manager.search_episodic_by_agent(agent_id, limit)
    
    def search_episodic_by_tag(self, tag: str, limit: int = 50):
        """Search episodic memories by tag"""
        return self.enhanced_memory_manager.search_episodic_by_tag(tag, limit)
    
    def semantic_search(self, query: str, limit: int = 10):
        """Perform semantic search across all memories"""
        return self.enhanced_memory_manager.semantic_search(query, limit)
    
    def temporal_search(self, agent_id: str, days_back: int = 30):
        """Temporal search for agent memories"""
        return self.enhanced_memory_manager.temporal_search(agent_id, days_back)
    
    def optimize_memory(self) -> Dict[str, int]:
        """Optimize all memory types"""
        return self.enhanced_memory_manager.optimize_all()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        return self.enhanced_memory_manager.get_memory_stats()


# Global orchestrator instance
_orchestrator: Optional[CoreOrchestrator] = None


def get_orchestrator() -> CoreOrchestrator:
    """Get or create global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = CoreOrchestrator()
    return _orchestrator


def set_orchestrator(orchestrator: CoreOrchestrator):
    """Set global orchestrator instance"""
    global _orchestrator
    _orchestrator = orchestrator
