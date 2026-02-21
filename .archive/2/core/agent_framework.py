"""
Agent Framework Base
Abstract agent class, message passing, state management, event-driven architecture
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import json
import logging


class AgentState(Enum):
    """Agent operational states"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"
    INITIALIZING = "initializing"


class MessageType(Enum):
    """Message types for agent communication"""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    FEEDBACK = "feedback"
    QUERY = "query"
    RESULT = "result"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    COORDINATION = "coordination"
    MEMORY_STORE = "memory_store"
    MEMORY_RETRIEVE = "memory_retrieve"


class Priority(Enum):
    """Message priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


@dataclass
class Message:
    """Message for inter-agent communication"""
    
    sender_id: str
    receiver_id: Optional[str]  # None for broadcast
    message_type: MessageType
    content: Dict[str, Any]
    priority: Priority = Priority.NORMAL
    timestamp: datetime = None
    message_id: str = None
    requires_response: bool = False
    
    def __post_init__(self):
        """Initialize optional fields"""
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.message_id is None:
            import uuid
            self.message_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict:
        """Convert message to dictionary"""
        return {
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'message_type': self.message_type.value,
            'content': self.content,
            'priority': self.priority.name,
            'timestamp': self.timestamp.isoformat(),
            'message_id': self.message_id,
            'requires_response': self.requires_response
        }


@dataclass
class AgentConfig:
    """Agent configuration"""
    
    agent_id: str
    agent_type: str
    name: str
    description: str = ""
    max_memory_size: int = 10000
    timeout_seconds: int = 300
    retry_attempts: int = 3
    learning_enabled: bool = True
    auto_correction: bool = True
    enable_monitoring: bool = True


class MessageBus:
    """Central message bus for agent communication"""
    
    def __init__(self):
        self.message_queue: List[Message] = []
        self.message_handlers: Dict[str, List[Callable]] = {}
        self.subscribers: Dict[MessageType, Set[str]] = {}
        self.message_history: List[Message] = []
        self.max_history = 50000
        self.logger = logging.getLogger(__name__)
    
    def publish(self, message: Message):
        """Publish a message"""
        self.message_queue.append(message)
        self.message_history.append(message)
        
        # Trim history if exceeding max
        if len(self.message_history) > self.max_history:
            self.message_history = self.message_history[-self.max_history:]
        
        # Sort by priority (critical first)
        self.message_queue.sort(key=lambda m: m.priority.value)
        
        self.logger.info(f"Message published: {message.message_type.value} from {message.sender_id}")
    
    def subscribe(self, message_type: MessageType, agent_id: str):
        """Subscribe agent to message type"""
        if message_type not in self.subscribers:
            self.subscribers[message_type] = set()
        self.subscribers[message_type].add(agent_id)
    
    def unsubscribe(self, message_type: MessageType, agent_id: str):
        """Unsubscribe agent from message type"""
        if message_type in self.subscribers:
            self.subscribers[message_type].discard(agent_id)
    
    def get_messages(self, receiver_id: Optional[str] = None, message_type: Optional[MessageType] = None) -> List[Message]:
        """Get messages for specific receiver or type"""
        messages = []
        
        for msg in self.message_queue:
            # Check receiver
            if receiver_id and msg.receiver_id and msg.receiver_id != receiver_id:
                continue
            if receiver_id and msg.receiver_id is None:  # Broadcast message
                pass
            
            # Check type
            if message_type and msg.message_type != message_type:
                continue
            
            messages.append(msg)
        
        return messages
    
    def process_message(self, message: Message) -> bool:
        """Process and remove message from queue"""
        if message in self.message_queue:
            self.message_queue.remove(message)
            return True
        return False
    
    def get_message_history(self, sender_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get message history"""
        if sender_id:
            history = [m for m in self.message_history if m.sender_id == sender_id]
        else:
            history = self.message_history
        
        return [m.to_dict() for m in history[-limit:]]


class StateManager:
    """Manages agent state and transitions"""
    
    def __init__(self):
        self.states: Dict[str, AgentState] = {}
        self.state_history: Dict[str, List[tuple]] = {}
        self.state_callbacks: Dict[str, Dict[AgentState, List[Callable]]] = {}
        self.logger = logging.getLogger(__name__)
    
    def create_agent(self, agent_id: str, initial_state: AgentState = AgentState.INITIALIZING):
        """Create agent state tracking"""
        self.states[agent_id] = initial_state
        self.state_history[agent_id] = [(initial_state, datetime.now())]
        self.state_callbacks[agent_id] = {}
    
    def set_state(self, agent_id: str, new_state: AgentState):
        """Set agent state"""
        if agent_id not in self.states:
            self.create_agent(agent_id, new_state)
            return
        
        old_state = self.states[agent_id]
        self.states[agent_id] = new_state
        self.state_history[agent_id].append((new_state, datetime.now()))
        
        # Trim history if exceeding reasonable size
        if len(self.state_history[agent_id]) > 1000:
            self.state_history[agent_id] = self.state_history[agent_id][-1000:]
        
        self.logger.info(f"Agent {agent_id} state changed: {old_state.value} -> {new_state.value}")
        
        # Execute callbacks
        self._execute_callbacks(agent_id, new_state)
    
    def get_state(self, agent_id: str) -> Optional[AgentState]:
        """Get current agent state"""
        return self.states.get(agent_id)
    
    def subscribe_to_state_change(self, agent_id: str, new_state: AgentState, callback: Callable):
        """Subscribe to state changes"""
        if agent_id not in self.state_callbacks:
            self.state_callbacks[agent_id] = {}
        if new_state not in self.state_callbacks[agent_id]:
            self.state_callbacks[agent_id][new_state] = []
        
        self.state_callbacks[agent_id][new_state].append(callback)
    
    def _execute_callbacks(self, agent_id: str, state: AgentState):
        """Execute registered callbacks for state"""
        if agent_id in self.state_callbacks and state in self.state_callbacks[agent_id]:
            for callback in self.state_callbacks[agent_id][state]:
                try:
                    callback(agent_id, state)
                except Exception as e:
                    self.logger.error(f"State callback error: {e}")
    
    def get_state_history(self, agent_id: str, limit: int = 100) -> List[Dict]:
        """Get state history"""
        if agent_id not in self.state_history:
            return []
        
        history = self.state_history[agent_id][-limit:]
        return [
            {
                'state': state.value,
                'timestamp': timestamp.isoformat()
            }
            for state, timestamp in history
        ]


class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, config: AgentConfig, message_bus: MessageBus = None, state_manager: StateManager = None):
        self.config = config
        self.message_bus = message_bus or MessageBus()
        self.state_manager = state_manager or StateManager()
        self.logger = logging.getLogger(f"Agent-{config.agent_id}")
        
        # Initialize state
        self.state_manager.create_agent(config.agent_id)
        self.set_state(AgentState.IDLE)
        
        # Agent properties
        self.start_time = datetime.now()
        self.task_count = 0
        self.success_count = 0
        self.error_count = 0
        self.metadata: Dict[str, Any] = {}
    
    def set_state(self, state: AgentState):
        """Set agent state"""
        self.state_manager.set_state(self.config.agent_id, state)
    
    def get_state(self) -> AgentState:
        """Get current agent state"""
        return self.state_manager.get_state(self.config.agent_id)
    
    def publish_message(self, receiver_id: Optional[str], message_type: MessageType, 
                       content: Dict[str, Any], priority: Priority = Priority.NORMAL,
                       requires_response: bool = False):
        """Publish a message"""
        message = Message(
            sender_id=self.config.agent_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content,
            priority=priority,
            requires_response=requires_response
        )
        self.message_bus.publish(message)
    
    def get_messages(self, message_type: Optional[MessageType] = None) -> List[Message]:
        """Get messages for this agent"""
        return self.message_bus.get_messages(receiver_id=self.config.agent_id, message_type=message_type)
    
    def process_message(self, message: Message) -> bool:
        """Process a message"""
        self.message_bus.process_message(message)
        return True
    
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task - must be implemented by subclasses"""
        self.task_count += 1
        
        try:
            self.set_state(AgentState.RUNNING)
            result = await self._execute(task_data)
            self.success_count += 1
            self.set_state(AgentState.IDLE)
            return result
        except Exception as e:
            self.error_count += 1
            self.set_state(AgentState.ERROR)
            self.logger.error(f"Task execution error: {e}")
            return {'error': str(e), 'success': False}
    
    @abstractmethod
    async def _execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task logic - implement in subclasses"""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'agent_id': self.config.agent_id,
            'agent_type': self.config.agent_type,
            'name': self.config.name,
            'state': self.get_state().value,
            'started_at': self.start_time.isoformat(),
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
            'task_count': self.task_count,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'success_rate': self.success_count / max(1, self.task_count),
            'metadata': self.metadata
        }
    
    def set_metadata(self, key: str, value: Any):
        """Set metadata"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata"""
        return self.metadata.get(key, default)


class AgentRegistry:
    """Registry and lifecycle management for agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_types: Dict[str, type] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_agent_type(self, agent_type: str, agent_class: type):
        """Register an agent type"""
        self.agent_types[agent_type] = agent_class
        self.logger.info(f"Agent type registered: {agent_type}")
    
    def create_agent(self, config: AgentConfig, message_bus: MessageBus = None, 
                    state_manager: StateManager = None) -> Optional[BaseAgent]:
        """Create and register an agent"""
        if config.agent_type not in self.agent_types:
            self.logger.error(f"Unknown agent type: {config.agent_type}")
            return None
        
        agent_class = self.agent_types[config.agent_type]
        agent = agent_class(config, message_bus, state_manager)
        self.agents[config.agent_id] = agent
        
        self.logger.info(f"Agent created: {config.agent_id} ({config.agent_type})")
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def remove_agent(self, agent_id: str) -> bool:
        """Remove agent"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.set_state(AgentState.STOPPED)
            del self.agents[agent_id]
            self.logger.info(f"Agent removed: {agent_id}")
            return True
        return False
    
    def get_all_agents(self) -> Dict[str, BaseAgent]:
        """Get all agents"""
        return self.agents.copy()
    
    def get_agents_by_type(self, agent_type: str) -> List[BaseAgent]:
        """Get agents by type"""
        return [a for a in self.agents.values() if a.config.agent_type == agent_type]
