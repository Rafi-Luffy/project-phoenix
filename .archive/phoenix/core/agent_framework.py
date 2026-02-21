"""
Agent Framework Base - Module 1.2: Agent Framework Base
Abstract agent class, state management, event-driven communication
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
import json
import uuid
from dataclasses import dataclass, field
from collections import deque


class AgentRole(Enum):
    MONITOR = "monitor"
    DETECTOR = "detector"
    DECISION_MAKER = "decision_maker"
    EXECUTOR = "executor"
    LEARNER = "learner"
    COORDINATOR = "coordinator"


class AgentState(Enum):
    IDLE = "idle"
    ACTIVE = "active"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"
    LEARNING = "learning"


@dataclass
class AgentConfig:
    """Configuration for agent initialization"""
    agent_id: str
    agent_name: str
    role: AgentRole
    capabilities: List[str] = field(default_factory=list)
    max_memory_items: int = 1000
    decision_timeout: float = 5.0
    learning_rate: float = 0.1
    confidence_threshold: float = 0.75
    enable_self_correction: bool = True
    enable_learning: bool = True


@dataclass
class EventData:
    """Represents event data in the system"""
    event_type: str
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5

    def to_dict(self) -> Dict:
        return {
            'type': self.event_type,
            'source': self.source,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'priority': self.priority
        }


class EventBus:
    """Central event bus for agent communication"""

    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: deque = deque(maxlen=10000)

    def subscribe(self, event_type: str, handler: Callable) -> str:
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        return str(uuid.uuid4())

    def unsubscribe(self, event_type: str, handler: Callable) -> bool:
        """Unsubscribe from an event type"""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(handler)
            return True
        return False

    def publish(self, event: EventData) -> int:
        """Publish an event to all subscribers"""
        self.event_history.append(event)
        handlers = self.subscribers.get(event.event_type, [])
        handlers.extend(self.subscribers.get("*", []))  # Wildcard subscribers
        
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in event handler: {e}")
        
        return len(handlers)

    def get_recent_events(self, event_type: Optional[str] = None, limit: int = 100) -> List[EventData]:
        """Get recent events"""
        events = list(self.event_history)[-limit:]
        if event_type:
            return [e for e in events if e.event_type == event_type]
        return events


class MessageQueue:
    """Message passing system between agents"""

    def __init__(self, max_size: int = 10000):
        self.queue: deque = deque(maxlen=max_size)
        self.pending_responses: Dict[str, Any] = {}

    def enqueue(self, message: Dict[str, Any]) -> str:
        """Add message to queue"""
        message_id = str(uuid.uuid4())
        message['message_id'] = message_id
        message['timestamp'] = datetime.now().isoformat()
        self.queue.append(message)
        return message_id

    def dequeue(self) -> Optional[Dict[str, Any]]:
        """Get next message from queue"""
        try:
            return self.queue.popleft()
        except IndexError:
            return None

    def queue_size(self) -> int:
        """Get current queue size"""
        return len(self.queue)

    def mark_response(self, message_id: str, response: Any) -> bool:
        """Mark a message as having a response"""
        self.pending_responses[message_id] = response
        return True


class StateManager:
    """Manages agent state and context"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.current_state = AgentState.IDLE
        self.state_history: deque = deque(maxlen=1000)
        self.context: Dict[str, Any] = {}
        self.state_changed_handlers: List[Callable] = []

    def set_state(self, new_state: AgentState, context: Optional[Dict[str, Any]] = None):
        """Change agent state"""
        old_state = self.current_state
        self.current_state = new_state
        
        if context:
            self.context.update(context)
        
        state_record = {
            'timestamp': datetime.now().isoformat(),
            'from': old_state.value,
            'to': new_state.value,
            'context': self.context.copy()
        }
        self.state_history.append(state_record)
        
        for handler in self.state_changed_handlers:
            try:
                handler(old_state, new_state)
            except Exception as e:
                print(f"Error in state change handler: {e}")

    def on_state_change(self, handler: Callable):
        """Register state change handler"""
        self.state_changed_handlers.append(handler)

    def get_state(self) -> AgentState:
        """Get current state"""
        return self.current_state

    def get_context(self, key: Optional[str] = None) -> Any:
        """Get context data"""
        if key:
            return self.context.get(key)
        return self.context.copy()

    def get_state_history(self, limit: int = 100) -> List[Dict]:
        """Get state change history"""
        return list(self.state_history)[-limit:]


class BaseAgent(ABC):
    """Base class for all autonomous agents"""

    def __init__(self, config: AgentConfig, event_bus: EventBus, message_queue: MessageQueue):
        self.config = config
        self.event_bus = event_bus
        self.message_queue = message_queue
        self.state_manager = StateManager(config.agent_id)
        
        # Agent capabilities
        self.capabilities = set(config.capabilities)
        
        # Execution tracking
        self.execution_count = 0
        self.error_count = 0
        self.last_execution: Optional[datetime] = None
        
        # Subscribe to relevant events
        self._setup_event_subscriptions()

    def _setup_event_subscriptions(self):
        """Override in subclasses to subscribe to specific events"""
        pass

    def handle_event(self, event: EventData):
        """Handle an event"""
        if self._should_process_event(event):
            self.state_manager.set_state(AgentState.PROCESSING, {
                'processing_event': event.event_type
            })
            try:
                self._process_event(event)
                self.execution_count += 1
            except Exception as e:
                self.error_count += 1
                print(f"Error processing event: {e}")
            finally:
                self.state_manager.set_state(AgentState.IDLE)

    @abstractmethod
    def _should_process_event(self, event: EventData) -> bool:
        """Determine if agent should process this event"""
        pass

    @abstractmethod
    def _process_event(self, event: EventData):
        """Process an event"""
        pass

    def send_message(self, recipient: str, message_type: str, payload: Dict[str, Any], 
                    requires_response: bool = False) -> str:
        """Send a message to another agent"""
        message = {
            'sender': self.config.agent_id,
            'recipient': recipient,
            'type': message_type,
            'payload': payload,
            'requires_response': requires_response
        }
        return self.message_queue.enqueue(message)

    def publish_event(self, event_type: str, data: Dict[str, Any], priority: int = 5):
        """Publish an event"""
        event = EventData(
            event_type=event_type,
            source=self.config.agent_id,
            data=data,
            priority=priority
        )
        self.event_bus.publish(event)

    def get_capability(self, capability: str) -> bool:
        """Check if agent has a capability"""
        return capability in self.capabilities

    def add_capability(self, capability: str):
        """Add a capability to agent"""
        self.capabilities.add(capability)

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'agent_id': self.config.agent_id,
            'agent_name': self.config.agent_name,
            'role': self.config.role.value,
            'current_state': self.state_manager.get_state().value,
            'execution_count': self.execution_count,
            'error_count': self.error_count,
            'capabilities': list(self.capabilities),
            'last_execution': self.last_execution.isoformat() if self.last_execution else None
        }


class MonitoringAgent(BaseAgent):
    """Agent responsible for continuous health monitoring"""

    def __init__(self, config: AgentConfig, event_bus: EventBus, message_queue: MessageQueue):
        super().__init__(config, event_bus, message_queue)
        self.monitored_components: Set[str] = set()
        self.metrics_history: Dict[str, deque] = {}

    def _setup_event_subscriptions(self):
        self.event_bus.subscribe("metric_collected", self.handle_event)
        self.event_bus.subscribe("component_status", self.handle_event)

    def _should_process_event(self, event: EventData) -> bool:
        return event.event_type in ["metric_collected", "component_status"]

    def _process_event(self, event: EventData):
        """Process health metrics"""
        component = event.data.get('component')
        metric = event.data.get('metric')
        value = event.data.get('value')

        if component not in self.metrics_history:
            self.metrics_history[component] = deque(maxlen=1000)

        self.metrics_history[component].append({
            'metric': metric,
            'value': value,
            'timestamp': event.timestamp.isoformat()
        })

        if self._detect_anomaly(component, value):
            self.publish_event('anomaly_detected', {
                'component': component,
                'metric': metric,
                'value': value,
                'detected_by': self.config.agent_id
            })

    def _detect_anomaly(self, component: str, value: float) -> bool:
        """Detect if a metric indicates an anomaly"""
        if value < 0.3:  # Below critical threshold
            return True
        if value < 0.5:  # Warning level
            return True
        return False

    def add_component(self, component_name: str):
        """Add component to monitoring"""
        self.monitored_components.add(component_name)


class DetectionAgent(BaseAgent):
    """Agent responsible for failure detection"""

    def __init__(self, config: AgentConfig, event_bus: EventBus, message_queue: MessageQueue):
        super().__init__(config, event_bus, message_queue)
        self.detected_failures: Dict[str, Dict[str, Any]] = {}

    def _setup_event_subscriptions(self):
        self.event_bus.subscribe("anomaly_detected", self.handle_event)
        self.event_bus.subscribe("error_event", self.handle_event)

    def _should_process_event(self, event: EventData) -> bool:
        return event.event_type in ["anomaly_detected", "error_event"]

    def _process_event(self, event: EventData):
        """Detect failures from anomalies"""
        failure_id = str(uuid.uuid4())
        component = event.data.get('component')
        
        failure_info = {
            'failure_id': failure_id,
            'component': component,
            'type': event.data.get('metric', 'unknown'),
            'severity': self._calculate_severity(event.data),
            'timestamp': event.timestamp.isoformat(),
            'root_cause': self._analyze_root_cause(event.data)
        }
        
        self.detected_failures[failure_id] = failure_info
        
        self.publish_event('failure_detected', failure_info)

    def _calculate_severity(self, data: Dict[str, Any]) -> int:
        """Calculate failure severity (1-10)"""
        value = data.get('value', 1.0)
        if value < 0.1:
            return 10
        elif value < 0.3:
            return 8
        elif value < 0.5:
            return 5
        return 3

    def _analyze_root_cause(self, data: Dict[str, Any]) -> str:
        """Analyze potential root cause"""
        metric = data.get('metric', '')
        if 'memory' in metric.lower():
            return 'memory_exhaustion'
        elif 'cpu' in metric.lower():
            return 'cpu_overload'
        elif 'latency' in metric.lower():
            return 'performance_degradation'
        return 'unknown'
