"""
Specialized Agent Types
Concrete implementations of different agent archetypes for the autonomous system
"""

from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
import asyncio
import logging

from autonomous_system.core.agent_framework import (
    BaseAgent, AgentConfig, AgentState, MessageBus, StateManager,
    Message, MessageType, Priority
)
from autonomous_system.core.memory_system import (
    MemoryType, MemoryPriority, MemoryManager
)


class SupervisorAgent(BaseAgent):
    """
    Orchestrates other agents and manages task coordination.
    Responsible for:
    - Task distribution to worker agents
    - Monitoring agent health and status
    - Managing task dependencies
    - Collecting and aggregating results
    """
    
    def __init__(self, config: AgentConfig, message_bus: MessageBus = None, 
                 state_manager: StateManager = None, memory_manager: MemoryManager = None):
        super().__init__(config, message_bus, state_manager)
        self.memory_manager = memory_manager
        self.logger = logging.getLogger(f"SupervisorAgent-{config.agent_id}")
        
        # Supervisor-specific attributes
        self.managed_agents: Set[str] = set()
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.task_results: Dict[str, Dict[str, Any]] = {}
        self.agent_health_status: Dict[str, Dict[str, Any]] = {}
        self.coordination_log: List[Dict[str, Any]] = []
        self.max_coordination_log = 1000
    
    def register_managed_agent(self, agent_id: str, agent_type: str):
        """Register an agent under supervision"""
        self.managed_agents.add(agent_id)
        self.agent_health_status[agent_id] = {
            'agent_id': agent_id,
            'agent_type': agent_type,
            'status': 'active',
            'last_heartbeat': datetime.now(),
            'task_count': 0,
            'success_count': 0,
            'error_count': 0
        }
        self.logger.info(f"Agent registered: {agent_id}")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        self.managed_agents.discard(agent_id)
        if agent_id in self.agent_health_status:
            del self.agent_health_status[agent_id]
        self.logger.info(f"Agent unregistered: {agent_id}")
    
    async def distribute_task(self, worker_agent_id: str, task_data: Dict[str, Any],
                             task_priority: Priority = Priority.NORMAL) -> str:
        """Distribute task to worker agent"""
        import uuid
        task_id = str(uuid.uuid4())
        
        message = Message(
            sender_id=self.config.agent_id,
            receiver_id=worker_agent_id,
            message_type=MessageType.TASK_REQUEST,
            content={
                'task_id': task_id,
                'task_data': task_data,
                'timestamp': datetime.now().isoformat()
            },
            priority=task_priority,
            requires_response=True
        )
        
        self.message_bus.publish(message)
        self.active_tasks[task_id] = {
            'task_id': task_id,
            'worker_agent_id': worker_agent_id,
            'task_data': task_data,
            'created_at': datetime.now(),
            'status': 'pending'
        }
        
        self.logger.info(f"Task distributed: {task_id} to {worker_agent_id}")
        return task_id
    
    async def collect_results(self, timeout_seconds: int = 30) -> Dict[str, Any]:
        """Collect results from worker agents"""
        results = {}
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < timeout_seconds:
            messages = self.get_messages(MessageType.TASK_RESPONSE)
            
            for message in messages:
                task_id = message.content.get('task_id')
                if task_id in self.active_tasks:
                    results[task_id] = message.content.get('result')
                    self.active_tasks[task_id]['status'] = 'completed'
                    self.task_results[task_id] = message.content
                    self.process_message(message)
            
            if len(results) >= len(self.active_tasks):
                break
            
            await asyncio.sleep(0.5)
        
        return results
    
    async def monitor_agents(self) -> Dict[str, Dict[str, Any]]:
        """Monitor health of managed agents"""
        status_report = {}
        
        for agent_id in self.managed_agents:
            health = self.agent_health_status.get(agent_id, {})
            status_report[agent_id] = health
            
            # Log to memory if memory manager available
            if self.memory_manager:
                self.memory_manager.store_memory(
                    content={'agent_id': agent_id, 'health': health},
                    memory_type=MemoryType.EPISODIC,
                    priority=MemoryPriority.NORMAL,
                    tags=['agent_health', agent_id],
                    agent_id=self.config.agent_id
                )
        
        return status_report
    
    def log_coordination_action(self, action: str, details: Dict[str, Any]):
        """Log coordination action"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details
        }
        self.coordination_log.append(log_entry)
        
        # Trim log if exceeding max
        if len(self.coordination_log) > self.max_coordination_log:
            self.coordination_log = self.coordination_log[-self.max_coordination_log:]
    
    async def _execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute supervisor task"""
        task_type = task_data.get('task_type', 'default')
        
        if task_type == 'distribute':
            worker_id = task_data.get('worker_agent_id')
            subtask = task_data.get('subtask')
            task_id = await self.distribute_task(worker_id, subtask)
            return {'task_id': task_id, 'status': 'distributed'}
        
        elif task_type == 'monitor':
            return await self.monitor_agents()
        
        elif task_type == 'collect_results':
            return await self.collect_results()
        
        else:
            return {'error': f'Unknown task type: {task_type}'}


class WorkerAgent(BaseAgent):
    """
    Executes specific tasks assigned by supervisor agents.
    Responsible for:
    - Processing tasks from supervisor
    - Executing work with error handling
    - Reporting results back
    - Task-specific business logic
    """
    
    def __init__(self, config: AgentConfig, message_bus: MessageBus = None,
                 state_manager: StateManager = None, memory_manager: MemoryManager = None):
        super().__init__(config, message_bus, state_manager)
        self.memory_manager = memory_manager
        self.logger = logging.getLogger(f"WorkerAgent-{config.agent_id}")
        
        # Worker-specific attributes
        self.supervisor_id: Optional[str] = None
        self.completed_tasks: List[Dict[str, Any]] = []
        self.task_handlers: Dict[str, callable] = {}
        self.max_task_history = 1000
    
    def set_supervisor(self, supervisor_id: str):
        """Set the supervisor for this worker"""
        self.supervisor_id = supervisor_id
        self.logger.info(f"Supervisor set: {supervisor_id}")
    
    def register_task_handler(self, task_type: str, handler: callable):
        """Register a handler for a specific task type"""
        self.task_handlers[task_type] = handler
        self.logger.info(f"Task handler registered: {task_type}")
    
    async def process_task_request(self, message: Message) -> Dict[str, Any]:
        """Process incoming task request from supervisor"""
        task_id = message.content.get('task_id')
        task_data = message.content.get('task_data')
        
        try:
            result = await self._execute(task_data)
            
            # Send result back to supervisor
            response_message = Message(
                sender_id=self.config.agent_id,
                receiver_id=message.sender_id,
                message_type=MessageType.TASK_RESPONSE,
                content={
                    'task_id': task_id,
                    'result': result,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                },
                priority=Priority.HIGH,
                requires_response=False
            )
            
            self.message_bus.publish(response_message)
            
            # Log completion
            completion_record = {
                'task_id': task_id,
                'completed_at': datetime.now(),
                'result': result,
                'status': 'success'
            }
            self.completed_tasks.append(completion_record)
            
            # Trim history
            if len(self.completed_tasks) > self.max_task_history:
                self.completed_tasks = self.completed_tasks[-self.max_task_history:]
            
            return result
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            
            # Send error back to supervisor
            error_message = Message(
                sender_id=self.config.agent_id,
                receiver_id=message.sender_id,
                message_type=MessageType.ERROR,
                content={
                    'task_id': task_id,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                },
                priority=Priority.HIGH
            )
            
            self.message_bus.publish(error_message)
            return {'error': str(e), 'status': 'failed'}
    
    async def _execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute worker task"""
        task_type = task_data.get('task_type', 'default')
        
        # Check if custom handler exists
        if task_type in self.task_handlers:
            return await self.task_handlers[task_type](task_data)
        
        # Default processing
        return {
            'task_type': task_type,
            'result': 'processed',
            'timestamp': datetime.now().isoformat()
        }


class MonitorAgent(BaseAgent):
    """
    Monitors system health and performance metrics.
    Responsible for:
    - Collecting system metrics
    - Detecting anomalies
    - Generating alerts
    - Maintaining health dashboards
    """
    
    def __init__(self, config: AgentConfig, message_bus: MessageBus = None,
                 state_manager: StateManager = None, memory_manager: MemoryManager = None):
        super().__init__(config, message_bus, state_manager)
        self.memory_manager = memory_manager
        self.logger = logging.getLogger(f"MonitorAgent-{config.agent_id}")
        
        # Monitor-specific attributes
        self.metrics: Dict[str, List[Tuple[datetime, float]]] = {}
        self.thresholds: Dict[str, Dict[str, float]] = {}
        self.alerts_raised: List[Dict[str, Any]] = []
        self.anomalies_detected: List[Dict[str, Any]] = []
        self.max_alerts = 1000
    
    def set_metric_threshold(self, metric_name: str, threshold_value: float,
                            threshold_type: str = 'upper'):
        """Set threshold for metric alerting"""
        if metric_name not in self.thresholds:
            self.thresholds[metric_name] = {}
        
        self.thresholds[metric_name][threshold_type] = threshold_value
        self.logger.info(f"Threshold set: {metric_name} {threshold_type}={threshold_value}")
    
    def record_metric(self, metric_name: str, value: float):
        """Record a metric value"""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].append((datetime.now(), value))
        
        # Check thresholds
        self._check_thresholds(metric_name, value)
    
    def _check_thresholds(self, metric_name: str, value: float):
        """Check if metric exceeds thresholds"""
        if metric_name not in self.thresholds:
            return
        
        thresholds = self.thresholds[metric_name]
        
        if 'upper' in thresholds and value > thresholds['upper']:
            self._raise_alert(
                f"High {metric_name}",
                f"{metric_name} exceeded upper threshold: {value} > {thresholds['upper']}"
            )
        
        if 'lower' in thresholds and value < thresholds['lower']:
            self._raise_alert(
                f"Low {metric_name}",
                f"{metric_name} below lower threshold: {value} < {thresholds['lower']}"
            )
    
    def _raise_alert(self, title: str, description: str):
        """Raise an alert"""
        alert = {
            'timestamp': datetime.now(),
            'title': title,
            'description': description,
            'status': 'active'
        }
        self.alerts_raised.append(alert)
        
        # Trim alerts if exceeding max
        if len(self.alerts_raised) > self.max_alerts:
            self.alerts_raised = self.alerts_raised[-self.max_alerts:]
        
        self.logger.warning(f"Alert raised: {title} - {description}")
    
    def detect_anomalies(self, metric_name: str, window_size: int = 10) -> List[Dict]:
        """Detect anomalies in metric data"""
        if metric_name not in self.metrics or len(self.metrics[metric_name]) < window_size:
            return []
        
        anomalies = []
        recent = self.metrics[metric_name][-window_size:]
        values = [v for _, v in recent]
        
        if len(values) == 0:
            return []
        
        # Simple statistical anomaly detection
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        # Flag values > 2 std devs from mean
        for i, (timestamp, value) in enumerate(recent):
            if abs(value - mean) > 2 * std_dev:
                anomaly = {
                    'timestamp': timestamp,
                    'metric': metric_name,
                    'value': value,
                    'mean': mean,
                    'std_dev': std_dev,
                    'z_score': (value - mean) / max(std_dev, 0.0001)
                }
                anomalies.append(anomaly)
                self.anomalies_detected.append(anomaly)
        
        return anomalies
    
    async def _execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute monitoring task"""
        task_type = task_data.get('task_type', 'default')
        
        if task_type == 'record_metric':
            metric_name = task_data.get('metric_name')
            value = task_data.get('value')
            self.record_metric(metric_name, value)
            return {'status': 'recorded', 'metric': metric_name, 'value': value}
        
        elif task_type == 'detect_anomalies':
            metric_name = task_data.get('metric_name')
            anomalies = self.detect_anomalies(metric_name)
            return {'metric': metric_name, 'anomalies': anomalies, 'count': len(anomalies)}
        
        elif task_type == 'get_alerts':
            return {'alerts': self.alerts_raised, 'count': len(self.alerts_raised)}
        
        else:
            return {'error': f'Unknown task type: {task_type}'}


class LearningAgent(BaseAgent):
    """
    Learns from experiences and adapts behavior.
    Responsible for:
    - Storing and retrieving experiences
    - Pattern recognition in task outcomes
    - Behavior adaptation based on feedback
    - Meta-learning from multiple tasks
    """
    
    def __init__(self, config: AgentConfig, message_bus: MessageBus = None,
                 state_manager: StateManager = None, memory_manager: MemoryManager = None):
        super().__init__(config, message_bus, state_manager)
        self.memory_manager = memory_manager
        self.logger = logging.getLogger(f"LearningAgent-{config.agent_id}")
        
        # Learning-specific attributes
        self.experience_buffer: List[Dict[str, Any]] = []
        self.learned_patterns: Dict[str, Dict[str, Any]] = {}
        self.behavior_strategies: Dict[str, callable] = {}
        self.learning_rate = 0.1
        self.max_buffer_size = 10000
        self.confidence_threshold = 0.7
    
    def store_experience(self, experience: Dict[str, Any]):
        """Store an experience for learning"""
        enriched_exp = {
            'timestamp': datetime.now(),
            'experience': experience,
            'processed': False
        }
        self.experience_buffer.append(enriched_exp)
        
        # Trim buffer if exceeding max
        if len(self.experience_buffer) > self.max_buffer_size:
            self.experience_buffer = self.experience_buffer[-self.max_buffer_size:]
        
        self.logger.info(f"Experience stored (buffer size: {len(self.experience_buffer)})")
    
    def extract_patterns(self, min_occurrences: int = 3) -> Dict[str, Dict[str, Any]]:
        """Extract patterns from experience buffer"""
        patterns = {}
        
        # Group experiences by task type
        by_task_type = {}
        for exp_record in self.experience_buffer:
            task_type = exp_record['experience'].get('task_type')
            if task_type:
                if task_type not in by_task_type:
                    by_task_type[task_type] = []
                by_task_type[task_type].append(exp_record['experience'])
        
        # Find patterns in each task type
        for task_type, experiences in by_task_type.items():
            if len(experiences) >= min_occurrences:
                successes = sum(1 for e in experiences if e.get('success'))
                success_rate = successes / len(experiences)
                
                pattern = {
                    'task_type': task_type,
                    'occurrences': len(experiences),
                    'success_rate': success_rate,
                    'confidence': min(success_rate, 1.0),
                    'discovered_at': datetime.now()
                }
                
                patterns[task_type] = pattern
                self.learned_patterns[task_type] = pattern
        
        return patterns
    
    def adapt_behavior(self, task_type: str, feedback: Dict[str, Any]):
        """Adapt behavior based on feedback"""
        if task_type in self.learned_patterns:
            pattern = self.learned_patterns[task_type]
            
            # Update success rate
            old_rate = pattern.get('success_rate', 0.5)
            new_success = feedback.get('success', False)
            new_value = feedback.get('value', 0)
            
            # Simple moving average update
            pattern['success_rate'] = old_rate * (1 - self.learning_rate) + \
                                      (1 if new_success else 0) * self.learning_rate
            pattern['last_feedback'] = datetime.now()
            
            self.logger.info(f"Behavior adapted for {task_type}: " +
                           f"success_rate={pattern['success_rate']:.2f}")
    
    async def _execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute learning task"""
        task_type = task_data.get('task_type', 'default')
        
        if task_type == 'store_experience':
            experience = task_data.get('experience')
            self.store_experience(experience)
            return {'status': 'stored', 'buffer_size': len(self.experience_buffer)}
        
        elif task_type == 'extract_patterns':
            patterns = self.extract_patterns()
            return {'patterns': patterns, 'count': len(patterns)}
        
        elif task_type == 'adapt_behavior':
            task = task_data.get('task')
            feedback = task_data.get('feedback')
            self.adapt_behavior(task, feedback)
            return {'status': 'adapted', 'task': task}
        
        else:
            return {'error': f'Unknown task type: {task_type}'}


class DecisionAgent(BaseAgent):
    """
    Makes autonomous decisions based on system state and learned knowledge.
    Responsible for:
    - Evaluating alternatives
    - Making autonomous decisions
    - Justifying decisions
    - Handling decision conflicts
    """
    
    def __init__(self, config: AgentConfig, message_bus: MessageBus = None,
                 state_manager: StateManager = None, memory_manager: MemoryManager = None):
        super().__init__(config, message_bus, state_manager)
        self.memory_manager = memory_manager
        self.logger = logging.getLogger(f"DecisionAgent-{config.agent_id}")
        
        # Decision-specific attributes
        self.decision_rules: Dict[str, callable] = {}
        self.decision_history: List[Dict[str, Any]] = []
        self.decision_confidence_threshold = 0.6
        self.max_history = 5000
    
    def register_decision_rule(self, rule_name: str, rule_func: callable):
        """Register a decision rule"""
        self.decision_rules[rule_name] = rule_func
        self.logger.info(f"Decision rule registered: {rule_name}")
    
    def evaluate_alternatives(self, alternatives: List[Dict[str, Any]],
                             criteria: Dict[str, float]) -> List[Tuple[str, float]]:
        """Evaluate alternatives based on criteria"""
        scored = []
        
        for alt in alternatives:
            score = 0.0
            alt_id = alt.get('id', 'unknown')
            
            for criterion, weight in criteria.items():
                value = alt.get(criterion, 0)
                score += value * weight
            
            scored.append((alt_id, score))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
    
    async def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make autonomous decision"""
        decision_id = context.get('decision_id', 'unknown')
        alternatives = context.get('alternatives', [])
        criteria = context.get('criteria', {})
        
        if not alternatives:
            return {'error': 'No alternatives provided', 'decision_id': decision_id}
        
        # Evaluate alternatives
        scored = self.evaluate_alternatives(alternatives, criteria)
        
        if not scored:
            return {'error': 'Could not score alternatives', 'decision_id': decision_id}
        
        best_choice_id, best_score = scored[0]
        confidence = min(best_score, 1.0)
        
        decision = {
            'decision_id': decision_id,
            'chosen_alternative': best_choice_id,
            'confidence': confidence,
            'all_scores': scored,
            'made_at': datetime.now(),
            'accepted': confidence >= self.decision_confidence_threshold
        }
        
        self.decision_history.append(decision)
        
        # Trim history
        if len(self.decision_history) > self.max_history:
            self.decision_history = self.decision_history[-self.max_history:]
        
        return decision
    
    async def _execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute decision task"""
        task_type = task_data.get('task_type', 'default')
        
        if task_type == 'evaluate':
            alternatives = task_data.get('alternatives', [])
            criteria = task_data.get('criteria', {})
            scored = self.evaluate_alternatives(alternatives, criteria)
            return {'evaluated': len(alternatives), 'scores': scored}
        
        elif task_type == 'decide':
            context = task_data.get('context', {})
            return await self.make_decision(context)
        
        elif task_type == 'get_history':
            limit = task_data.get('limit', 100)
            return {'history': self.decision_history[-limit:], 'count': len(self.decision_history)}
        
        else:
            return {'error': f'Unknown task type: {task_type}'}
