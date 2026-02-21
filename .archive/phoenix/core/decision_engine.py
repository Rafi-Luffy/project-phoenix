"""
Decision Engine and Orchestrator - Module 2 & 4
Makes autonomous recovery decisions and orchestrates multi-agent execution
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import uuid
from dataclasses import dataclass, field


class DecisionStrategy(Enum):
    GREEDY = "greedy"  # Immediate best action
    CONSERVATIVE = "conservative"  # Lowest risk
    BALANCED = "balanced"  # Cost-benefit optimized
    LEARNING = "learning"  # Based on past success rates


@dataclass
class Decision:
    """Represents a decision made by the system"""
    decision_id: str
    failure_id: str
    recommended_action: str
    confidence: float
    risk_level: float  # 0-1, lower is better
    expected_outcome: str
    reasoning: str
    created_at: datetime = field(default_factory=datetime.now)
    executed: bool = False
    actual_outcome: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            'decision_id': self.decision_id,
            'action': self.recommended_action,
            'confidence': self.confidence,
            'risk': self.risk_level,
            'expected_outcome': self.expected_outcome,
            'executed': self.executed
        }


class DecisionEngine:
    """Autonomous decision making system"""

    def __init__(self, strategy: DecisionStrategy = DecisionStrategy.BALANCED):
        self.strategy = strategy
        self.decisions: Dict[str, Decision] = {}
        self.decision_history: List[Decision] = []
        self.success_rates: Dict[str, float] = {}  # Track action success rates

    def make_decision(self, failure_id: str, failure_type: str,
                     component_state: str, available_actions: List[str],
                     severity: int, system_load: float) -> Decision:
        """Make autonomous decision on recovery action"""
        
        decision_id = str(uuid.uuid4())
        
        # Rank available actions based on strategy
        ranked_actions = self._rank_actions(
            available_actions, failure_type, severity, system_load
        )

        if not ranked_actions:
            # Fallback decision
            action = "monitor"
            confidence = 0.5
        else:
            action, confidence = ranked_actions[0]

        # Calculate risk
        risk = self._calculate_risk(action, component_state, system_load)

        # Generate reasoning
        reasoning = self._generate_reasoning(
            action, failure_type, severity, confidence, risk
        )

        decision = Decision(
            decision_id=decision_id,
            failure_id=failure_id,
            recommended_action=action,
            confidence=confidence,
            risk_level=risk,
            expected_outcome=self._predict_outcome(action, failure_type),
            reasoning=reasoning
        )

        self.decisions[decision_id] = decision
        self.decision_history.append(decision)
        return decision

    def _rank_actions(self, actions: List[str], failure_type: str,
                     severity: int, system_load: float) -> List[Tuple[str, float]]:
        """Rank actions by effectiveness"""
        ranked = []

        for action in actions:
            # Base effectiveness score
            base_score = self._get_action_effectiveness(action, failure_type)
            
            # Adjust by severity
            severity_multiplier = 1.0 + (severity / 10.0)
            
            # Adjust by system load
            load_penalty = max(0, system_load - 0.7)
            
            # Apply strategy
            if self.strategy == DecisionStrategy.GREEDY:
                score = base_score * severity_multiplier
            elif self.strategy == DecisionStrategy.CONSERVATIVE:
                score = base_score * (1 - load_penalty)
            elif self.strategy == DecisionStrategy.LEARNING:
                historical_rate = self.success_rates.get(action, 0.5)
                score = base_score * historical_rate
            else:  # BALANCED
                score = base_score * severity_multiplier * (1 - load_penalty * 0.5)

            confidence = min(0.95, base_score * 0.8 + historical_rate * 0.2)
            ranked.append((action, confidence))

        # Sort by confidence descending
        return sorted(ranked, key=lambda x: x[1], reverse=True)

    def _get_action_effectiveness(self, action: str, failure_type: str) -> float:
        """Get base effectiveness of action for failure type"""
        effectiveness_map = {
            'restart': {'service_crash': 0.9, 'memory_leak': 0.7, 'latency': 0.5},
            'failover': {'network_partition': 0.95, 'node_failure': 0.9, 'service_crash': 0.8},
            'rebalance': {'uneven_load': 0.9, 'overload': 0.85},
            'circuit_break': {'cascading_failure': 0.95, 'downstream_failure': 0.9},
            'reduce_load': {'overload': 0.85, 'cpu_spike': 0.8},
            'isolate': {'byzantine_failure': 0.9, 'cascading_failure': 0.8},
            'heal': {'data_corruption': 0.7, 'consistency_error': 0.8},
            'monitor': {'unknown': 0.6}
        }

        return effectiveness_map.get(action, {}).get(failure_type, 0.5)

    def _calculate_risk(self, action: str, component_state: str, 
                       system_load: float) -> float:
        """Calculate risk of taking action"""
        action_risks = {
            'restart': 0.3,
            'failover': 0.2,
            'rebalance': 0.15,
            'circuit_break': 0.25,
            'reduce_load': 0.1,
            'isolate': 0.35,
            'heal': 0.4,
            'monitor': 0.05
        }

        base_risk = action_risks.get(action, 0.5)
        
        # High system load increases risk
        load_risk_increase = system_load * 0.2 if system_load > 0.8 else 0
        
        # Degraded component increases risk
        state_risk_increase = 0.15 if component_state == 'degraded' else 0

        total_risk = min(1.0, base_risk + load_risk_increase + state_risk_increase)
        return total_risk

    def _generate_reasoning(self, action: str, failure_type: str,
                           severity: int, confidence: float, risk: float) -> str:
        """Generate explanation for decision"""
        reasons = [
            f"Selected action: {action}",
            f"Failure type: {failure_type}",
            f"Severity level: {severity}/10",
            f"Decision confidence: {confidence:.1%}",
            f"Execution risk: {risk:.1%}"
        ]

        if confidence < 0.6:
            reasons.append("Low confidence - requires monitoring")
        if risk > 0.5:
            reasons.append("High risk action - proceed with caution")
        if severity >= 8:
            reasons.append("Critical severity - immediate action needed")

        return ". ".join(reasons)

    def _predict_outcome(self, action: str, failure_type: str) -> str:
        """Predict likely outcome of action"""
        predictions = {
            'restart': 'component_restart_and_health_restoration',
            'failover': 'traffic_rerouting_to_backup',
            'rebalance': 'load_distribution_optimization',
            'circuit_break': 'protection_of_downstream_services',
            'reduce_load': 'request_throttling_and_queue_management',
            'isolate': 'component_quarantine_and_containment',
            'heal': 'data_consistency_restoration',
            'monitor': 'continued_observation'
        }
        return predictions.get(action, 'uncertain_outcome')

    def record_outcome(self, decision_id: str, outcome: str, success: bool):
        """Record actual outcome of decision"""
        if decision_id in self.decisions:
            decision = self.decisions[decision_id]
            decision.actual_outcome = outcome
            decision.executed = True

            # Update success rates
            action = decision.recommended_action
            current_rate = self.success_rates.get(action, 0.5)
            weight = 0.7  # Weight recent results more
            new_rate = current_rate * (1 - weight) + (1.0 if success else 0.0) * weight
            self.success_rates[action] = new_rate

    def get_decision_quality_metrics(self) -> Dict[str, Any]:
        """Get metrics on decision quality"""
        if not self.decision_history:
            return {}

        executed = [d for d in self.decision_history if d.executed]
        if not executed:
            return {
                'total_decisions': len(self.decision_history),
                'executed_decisions': 0
            }

        successful = [d for d in executed if d.actual_outcome and 'success' in d.actual_outcome.lower()]
        
        return {
            'total_decisions': len(self.decision_history),
            'executed_decisions': len(executed),
            'successful_decisions': len(successful),
            'success_rate': len(successful) / len(executed) if executed else 0,
            'avg_confidence': sum(d.confidence for d in executed) / len(executed) if executed else 0,
            'avg_risk': sum(d.risk_level for d in executed) / len(executed) if executed else 0,
            'action_success_rates': self.success_rates.copy()
        }


class RecoveryOrchestrator:
    """Orchestrates recovery execution across multiple agents"""

    def __init__(self):
        self.active_recoveries: Dict[str, Dict[str, Any]] = {}
        self.recovery_history: List[Dict[str, Any]] = []
        self.agent_assignments: Dict[str, str] = {}  # failure_id -> agent_id

    def create_recovery_plan(self, failure_id: str, 
                            decision: Decision,
                            available_agents: List[str]) -> Dict[str, Any]:
        """Create comprehensive recovery plan"""
        
        recovery_plan = {
            'plan_id': str(uuid.uuid4()),
            'failure_id': failure_id,
            'primary_action': decision.recommended_action,
            'fallback_actions': self._generate_fallback_actions(decision.recommended_action),
            'assigned_agents': self._assign_agents(
                decision.recommended_action, available_agents
            ),
            'estimated_duration': self._estimate_duration(decision.recommended_action),
            'priority': self._calculate_priority(decision.severity),
            'rollback_plan': self._generate_rollback_plan(decision.recommended_action),
            'created_at': datetime.now().isoformat(),
            'status': 'created'
        }

        self.active_recoveries[failure_id] = recovery_plan
        return recovery_plan

    def _generate_fallback_actions(self, primary_action: str) -> List[str]:
        """Generate fallback actions if primary fails"""
        fallback_map = {
            'restart': ['failover', 'circuit_break', 'monitor'],
            'failover': ['rebalance', 'reduce_load', 'monitor'],
            'rebalance': ['reduce_load', 'monitor'],
            'circuit_break': ['isolate', 'monitor'],
            'reduce_load': ['circuit_break', 'monitor'],
            'isolate': ['heal', 'monitor'],
            'heal': ['rollback', 'monitor'],
            'monitor': []
        }
        return fallback_map.get(primary_action, ['monitor'])

    def _assign_agents(self, action: str, available_agents: List[str]) -> List[str]:
        """Assign appropriate agents to action"""
        action_agent_types = {
            'restart': ['executor', 'monitor'],
            'failover': ['executor', 'coordinator'],
            'rebalance': ['executor', 'monitor'],
            'circuit_break': ['executor', 'detector'],
            'reduce_load': ['executor', 'monitor'],
            'isolate': ['executor', 'detector'],
            'heal': ['executor', 'learner'],
            'monitor': ['monitor']
        }

        required_types = action_agent_types.get(action, ['monitor'])
        assigned = []

        for agent in available_agents:
            agent_type = agent.split('_')[0]
            if agent_type in required_types:
                assigned.append(agent)

        return assigned[:3]  # Limit to 3 agents

    def _estimate_duration(self, action: str) -> float:
        """Estimate recovery duration in seconds"""
        durations = {
            'restart': 10.0,
            'failover': 5.0,
            'rebalance': 15.0,
            'circuit_break': 1.0,
            'reduce_load': 2.0,
            'isolate': 3.0,
            'heal': 20.0,
            'monitor': 0.0
        }
        return durations.get(action, 5.0)

    def _calculate_priority(self, severity: int) -> int:
        """Calculate recovery priority"""
        if severity >= 9:
            return 1  # Highest
        elif severity >= 7:
            return 2
        elif severity >= 5:
            return 3
        else:
            return 4  # Lowest

    def _generate_rollback_plan(self, action: str) -> Dict[str, Any]:
        """Generate rollback plan if recovery fails"""
        return {
            'enabled': True,
            'timeout': 30,
            'undo_action': f'undo_{action}',
            'restore_previous_state': True
        }

    def start_recovery(self, failure_id: str) -> bool:
        """Start recovery execution"""
        if failure_id not in self.active_recoveries:
            return False

        plan = self.active_recoveries[failure_id]
        plan['status'] = 'executing'
        plan['started_at'] = datetime.now().isoformat()
        return True

    def complete_recovery(self, failure_id: str, success: bool, outcome: str):
        """Mark recovery as complete"""
        if failure_id not in self.active_recoveries:
            return

        plan = self.active_recoveries[failure_id]
        plan['status'] = 'completed' if success else 'failed'
        plan['success'] = success
        plan['outcome'] = outcome
        plan['completed_at'] = datetime.now().isoformat()

        self.recovery_history.append(plan)
        del self.active_recoveries[failure_id]

    def get_recovery_status(self, failure_id: str) -> Optional[Dict[str, Any]]:
        """Get status of recovery"""
        return self.active_recoveries.get(failure_id)

    def get_recovery_statistics(self) -> Dict[str, Any]:
        """Get recovery statistics"""
        if not self.recovery_history:
            return {}

        successful = [r for r in self.recovery_history if r.get('success')]
        
        return {
            'total_recoveries': len(self.recovery_history),
            'successful_recoveries': len(successful),
            'success_rate': len(successful) / len(self.recovery_history) if self.recovery_history else 0,
            'avg_duration': sum(
                float(r['estimated_duration']) 
                for r in self.recovery_history
            ) / len(self.recovery_history) if self.recovery_history else 0,
            'active_recoveries': len(self.active_recoveries)
        }
