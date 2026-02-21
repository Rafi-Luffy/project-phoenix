"""
Learning and Adaptation System - Module 3
Meta-learning, reinforcement learning, and continuous improvement
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
from collections import defaultdict
import uuid


class ExperienceType(Enum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"


@dataclass
class Experience:
    """Represents a learning experience"""
    experience_id: str
    action: str
    state: Dict[str, Any]
    outcome: str
    reward: float
    experience_type: ExperienceType
    timestamp: datetime = None
    source_failure_id: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> Dict:
        return {
            'experience_id': self.experience_id,
            'action': self.action,
            'outcome': self.outcome,
            'reward': self.reward,
            'type': self.experience_type.value
        }


class FailurePattern:
    """Learned pattern about a type of failure"""

    def __init__(self, pattern_id: str, failure_type: str):
        self.pattern_id = pattern_id
        self.failure_type = failure_type
        self.action_effectiveness: Dict[str, float] = {}
        self.occurrences: int = 0
        self.successful_recoveries: int = 0
        self.metadata: Dict[str, Any] = {}
        self.last_updated = datetime.now()

    def record_recovery(self, action: str, success: bool, reward: float):
        """Record a recovery attempt"""
        self.occurrences += 1
        if success:
            self.successful_recoveries += 1

        current = self.action_effectiveness.get(action, 0)
        # Exponential moving average
        self.action_effectiveness[action] = 0.7 * current + 0.3 * reward
        self.last_updated = datetime.now()

    def get_best_action(self) -> Optional[str]:
        """Get highest-rated action for this failure"""
        if not self.action_effectiveness:
            return None
        return max(self.action_effectiveness.items(), key=lambda x: x[1])[0]

    def success_rate(self) -> float:
        """Get success rate of recoveries"""
        return self.successful_recoveries / self.occurrences if self.occurrences > 0 else 0

    def to_dict(self) -> Dict:
        return {
            'pattern_id': self.pattern_id,
            'failure_type': self.failure_type,
            'occurrences': self.occurrences,
            'success_rate': self.success_rate(),
            'best_action': self.get_best_action(),
            'action_effectiveness': self.action_effectiveness
        }


class MetaLearner:
    """Meta-learning framework for learning how to learn"""

    def __init__(self):
        self.failure_patterns: Dict[str, FailurePattern] = {}
        self.pattern_similarities: Dict[Tuple[str, str], float] = {}
        self.transfer_knowledge: Dict[str, Dict[str, Any]] = {}

    def register_pattern(self, failure_type: str) -> str:
        """Register a new failure pattern"""
        pattern_id = str(uuid.uuid4())
        self.failure_patterns[pattern_id] = FailurePattern(pattern_id, failure_type)
        return pattern_id

    def learn_from_failure(self, failure_type: str, action: str, 
                          success: bool, reward: float):
        """Learn from a failure recovery experience"""
        # Find or create pattern
        pattern = None
        for p in self.failure_patterns.values():
            if p.failure_type == failure_type:
                pattern = p
                break

        if not pattern:
            pattern_id = self.register_pattern(failure_type)
            pattern = self.failure_patterns[pattern_id]

        pattern.record_recovery(action, success, reward)

    def find_similar_patterns(self, failure_type: str, threshold: float = 0.6) -> List[str]:
        """Find patterns similar to given failure type"""
        similar = []
        target_pattern = None

        for p in self.failure_patterns.values():
            if p.failure_type == failure_type:
                target_pattern = p
                break

        if not target_pattern:
            return []

        for p in self.failure_patterns.values():
            if p.failure_type != failure_type:
                similarity = self._calculate_pattern_similarity(target_pattern, p)
                if similarity >= threshold:
                    similar.append(p.pattern_id)

        return similar

    def _calculate_pattern_similarity(self, pattern1: FailurePattern, 
                                     pattern2: FailurePattern) -> float:
        """Calculate similarity between patterns"""
        if not pattern1.action_effectiveness or not pattern2.action_effectiveness:
            return 0.0

        # Find common actions
        common_actions = set(pattern1.action_effectiveness.keys()) & set(
            pattern2.action_effectiveness.keys()
        )

        if not common_actions:
            return 0.0

        # Calculate similarity based on action effectiveness correlation
        similarity = 0.0
        for action in common_actions:
            eff1 = pattern1.action_effectiveness[action]
            eff2 = pattern2.action_effectiveness[action]
            similarity += min(eff1, eff2) / max(eff1, eff2) if max(eff1, eff2) > 0 else 0

        return similarity / len(common_actions)

    def transfer_learning(self, source_pattern_id: str, target_failure_type: str):
        """Transfer learning from one pattern to another"""
        source = self.failure_patterns.get(source_pattern_id)
        if not source:
            return

        # Find or create target pattern
        target = None
        for p in self.failure_patterns.values():
            if p.failure_type == target_failure_type:
                target = p
                break

        if not target:
            target_id = self.register_pattern(target_failure_type)
            target = self.failure_patterns[target_id]

        # Transfer action effectiveness with decay
        decay = 0.8  # Assume 20% loss in transfer
        for action, effectiveness in source.action_effectiveness.items():
            transferred = effectiveness * decay
            current = target.action_effectiveness.get(action, 0)
            target.action_effectiveness[action] = 0.6 * current + 0.4 * transferred

    def get_meta_knowledge(self) -> Dict[str, Any]:
        """Get meta-learning insights"""
        if not self.failure_patterns:
            return {}

        all_actions = set()
        for pattern in self.failure_patterns.values():
            all_actions.update(pattern.action_effectiveness.keys())

        action_across_patterns = defaultdict(float)
        for pattern in self.failure_patterns.values():
            for action in all_actions:
                eff = pattern.action_effectiveness.get(action, 0)
                action_across_patterns[action] += eff

        avg_effectiveness = {
            action: score / len(self.failure_patterns)
            for action, score in action_across_patterns.items()
        }

        return {
            'total_patterns': len(self.failure_patterns),
            'total_actions': len(all_actions),
            'average_action_effectiveness': avg_effectiveness,
            'best_general_action': max(avg_effectiveness.items(), key=lambda x: x[1])[0]
            if avg_effectiveness else None
        }


class ReinforcementLearner:
    """Reinforcement learning system for policy optimization"""

    def __init__(self, learning_rate: float = 0.1, discount_factor: float = 0.95):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.q_table: Dict[Tuple[str, str], float] = {}  # (state, action) -> Q-value
        self.experience_replay: List[Experience] = []
        self.max_replay_size = 10000

    def select_action(self, state: str, available_actions: List[str], 
                     exploration_rate: float = 0.1) -> str:
        """Select action using epsilon-greedy strategy"""
        import random

        if random.random() < exploration_rate:
            # Exploration
            return random.choice(available_actions)
        else:
            # Exploitation
            best_action = None
            best_value = float('-inf')

            for action in available_actions:
                value = self.q_table.get((state, action), 0)
                if value > best_value:
                    best_value = value
                    best_action = action

            return best_action or random.choice(available_actions)

    def learn(self, state: str, action: str, reward: float, next_state: str):
        """Update Q-values based on experience"""
        current_q = self.q_table.get((state, action), 0)
        
        # Find max Q-value for next state
        next_q_values = [
            self.q_table.get((next_state, a), 0)
            for a in ['restart', 'failover', 'rebalance', 'circuit_break', 
                     'reduce_load', 'isolate', 'heal', 'monitor']
        ]
        max_next_q = max(next_q_values) if next_q_values else 0

        # Q-learning update
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )

        self.q_table[(state, action)] = new_q

    def store_experience(self, experience: Experience):
        """Store experience for replay"""
        self.experience_replay.append(experience)
        if len(self.experience_replay) > self.max_replay_size:
            self.experience_replay.pop(0)

    def replay_experiences(self, batch_size: int = 32):
        """Learn from replayed experiences"""
        import random

        if len(self.experience_replay) < batch_size:
            return

        batch = random.sample(self.experience_replay, batch_size)
        for experience in batch:
            self.learn(
                str(experience.state),
                experience.action,
                experience.reward,
                experience.outcome
            )

    def get_policy(self) -> Dict[str, str]:
        """Get learned policy"""
        policy = {}
        for (state, action), value in self.q_table.items():
            if state not in policy or value > self.q_table.get((state, policy[state]), 0):
                policy[state] = action
        return policy


class ContinuousLearningSystem:
    """Integrates meta-learning and RL for continuous improvement"""

    def __init__(self):
        self.meta_learner = MetaLearner()
        self.rl_learner = ReinforcementLearner()
        self.learning_history: List[Dict[str, Any]] = []
        self.adaptation_triggers: List[Dict[str, Any]] = []

    def process_recovery_outcome(self, failure_type: str, action: str,
                                state: Dict[str, Any], success: bool, 
                                outcome: str, reward: float):
        """Process recovery outcome for learning"""
        
        # Meta-learning
        self.meta_learner.learn_from_failure(failure_type, action, success, reward)

        # Reinforcement learning
        state_str = str(hash(str(state)))
        self.rl_learner.learn(state_str, action, reward, outcome)

        # Store experience
        experience = Experience(
            experience_id=str(uuid.uuid4()),
            action=action,
            state=state,
            outcome=outcome,
            reward=reward,
            experience_type=ExperienceType.SUCCESS if success else ExperienceType.FAILURE
        )
        self.rl_learner.store_experience(experience)

        # Record learning event
        self.learning_history.append({
            'timestamp': datetime.now().isoformat(),
            'failure_type': failure_type,
            'action': action,
            'success': success,
            'reward': reward
        })

        # Check if adaptation needed
        self._check_adaptation_triggers()

    def _check_adaptation_triggers(self):
        """Check if system should adapt strategy"""
        if len(self.learning_history) < 10:
            return

        recent = self.learning_history[-10:]
        success_rate = sum(1 for x in recent if x['success']) / len(recent)

        if success_rate < 0.5:
            self.adaptation_triggers.append({
                'trigger_type': 'low_success_rate',
                'success_rate': success_rate,
                'timestamp': datetime.now().isoformat(),
                'action': 'increase_exploration_rate'
            })

    def recommend_strategy_adjustment(self) -> Optional[Dict[str, Any]]:
        """Recommend strategy adjustments based on learning"""
        meta_knowledge = self.meta_learner.get_meta_knowledge()
        
        if not meta_knowledge:
            return None

        # Check recent performance
        if len(self.learning_history) < 20:
            return None

        recent = self.learning_history[-20:]
        success_rate = sum(1 for x in recent if x['success']) / len(recent)

        if success_rate < 0.6:
            return {
                'adjustment': 'adopt_more_conservative_strategy',
                'reason': f'Recent success rate {success_rate:.1%} below threshold',
                'recommended_actions': [
                    'increase_success_rate_threshold',
                    'favor_low_risk_actions',
                    'enable_rollback_by_default'
                ]
            }

        return None

    def get_learning_status(self) -> Dict[str, Any]:
        """Get status of learning system"""
        return {
            'meta_knowledge': self.meta_learner.get_meta_knowledge(),
            'learned_policy': self.rl_learner.get_policy(),
            'total_learning_events': len(self.learning_history),
            'recent_success_rate': sum(1 for x in self.learning_history[-10:] if x['success']) / 10
            if len(self.learning_history) >= 10 else 0,
            'adaptation_triggers': len(self.adaptation_triggers)
        }
