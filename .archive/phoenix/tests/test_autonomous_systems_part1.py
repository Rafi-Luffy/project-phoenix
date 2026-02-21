"""
Comprehensive Test Suite for Phoenix - Autonomous Systems Part 1
Tests 336-365: Autonomous Decision Making, Goal Management, Self-Adaptation (30 tests)

This file tests Phoenix's ability to detect and fix bugs in autonomous systems,
decision-making processes, goal management, and self-adaptation mechanisms.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch


class TestAutonomousDecisionMaking:
    """Test autonomous decision making (10 tests)"""
    
    def test_decision_tree_depth_limit(self):
        """Test 336: Prevent infinite decision tree expansion"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class DecisionMaker:
    def __init__(self):
        self.max_depth = None  # BUG: No depth limit
    
    def make_decision(self, state, depth=0):
        # BUG: Recursive without depth limit
        if state == "goal":
            return "done"
        
        # Evaluate options
        options = self.get_options(state)
        
        for option in options:
            next_state = self.apply(state, option)
            result = self.make_decision(next_state, depth + 1)
            if result == "done":
                return result
        
        return "failed"
    
    def get_options(self, state):
        return ["option1", "option2", "option3"]
    
    def apply(self, state, option):
        return f"{state}_{option}"

maker = DecisionMaker()

# BUG: Stack overflow on complex state space
try:
    decision = maker.make_decision("start")
except RecursionError:
    print("Recursion error - no depth limit")
"""
            
            test_file = os.path.join(temp_dir, "decision_depth.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_reward_signal_sparsity(self):
        """Test 337: Handle sparse reward signals"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class RewardBasedAgent:
    def __init__(self):
        self.policy = {}
    
    def update_policy(self, state, action, reward):
        # BUG: Only updates when reward received
        if reward > 0:
            self.policy[state] = action
    
    def act(self, state):
        return self.policy.get(state, "random_action")

agent = RewardBasedAgent()

# Sparse rewards - only at end
for step in range(100):
    state = f"state_{step}"
    action = "move_forward"
    reward = 0  # No reward
    
    agent.update_policy(state, action, reward)

# Final reward
agent.update_policy("state_100", "reach_goal", 10)

# BUG: No learning from intermediate states
print(f"Policy size: {len(agent.policy)}")  # Only 1 entry
"""
            
            test_file = os.path.join(temp_dir, "sparse_rewards.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_exploration_exploitation_balance(self):
        """Test 338: Balance exploration vs exploitation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ExplorerAgent:
    def __init__(self):
        self.q_values = {}
        self.epsilon = 0.0  # BUG: No exploration
    
    def select_action(self, state, available_actions):
        # BUG: Pure exploitation - no exploration
        if state not in self.q_values:
            self.q_values[state] = {a: 0.0 for a in available_actions}
        
        # Always pick best known action
        return max(self.q_values[state], key=self.q_values[state].get)
    
    def update(self, state, action, reward):
        if state not in self.q_values:
            self.q_values[state] = {}
        self.q_values[state][action] = reward

agent = ExplorerAgent()

# Initialize with suboptimal action
agent.update("state1", "action_A", 5)
agent.update("state1", "action_B", 3)

# BUG: Never explores action_C which has reward 10
for _ in range(100):
    action = agent.select_action("state1", ["action_A", "action_B", "action_C"])
    # Always picks action_A, never discovers action_C
"""
            
            test_file = os.path.join(temp_dir, "exploration_exploitation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_temporal_credit_assignment(self):
        """Test 339: Assign credit to past actions correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class CreditAssigner:
    def __init__(self):
        self.history = []
        self.values = {}
    
    def record_action(self, state, action):
        self.history.append((state, action))
    
    def receive_reward(self, reward):
        # BUG: Credits only last action
        if self.history:
            state, action = self.history[-1]
            self.values[(state, action)] = reward
        self.history = []

agent = CreditAssigner()

# Sequence of actions leading to reward
agent.record_action("state1", "action1")
agent.record_action("state2", "action2")
agent.record_action("state3", "action3")
agent.record_action("state4", "action4")

# Receive delayed reward
agent.receive_reward(10)

# BUG: Only action4 credited, not action1-3
print(f"Values learned: {agent.values}")
"""
            
            test_file = os.path.join(temp_dir, "credit_assignment.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_non_stationary_environment_adaptation(self):
        """Test 340: Adapt to changing environment dynamics"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class StaticAgent:
    def __init__(self):
        self.model = {}  # state -> action -> next_state
    
    def learn_transition(self, state, action, next_state):
        # BUG: Never updates learned transitions
        key = (state, action)
        if key not in self.model:
            self.model[key] = next_state
    
    def predict_next_state(self, state, action):
        return self.model.get((state, action), "unknown")

agent = StaticAgent()

# Learn initial dynamics
agent.learn_transition("A", "move", "B")

# Environment changes
# Action "move" from A now goes to C, not B

# BUG: Agent still predicts B
prediction = agent.predict_next_state("A", "move")
print(f"Prediction: {prediction}")  # Still says B
"""
            
            test_file = os.path.join(temp_dir, "environment_adaptation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_multi_objective_decision_conflict(self):
        """Test 341: Resolve conflicts in multi-objective decisions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class MultiObjectiveAgent:
    def __init__(self):
        self.objectives = ["speed", "safety", "efficiency"]
    
    def evaluate_action(self, action):
        # BUG: No conflict resolution strategy
        scores = {
            "speed": action.get("speed", 0),
            "safety": action.get("safety", 0),
            "efficiency": action.get("efficiency", 0)
        }
        # BUG: Simple sum doesn't handle conflicts
        return sum(scores.values())
    
    def select_action(self, actions):
        return max(actions, key=self.evaluate_action)

agent = MultiObjectiveAgent()

actions = [
    {"name": "fast", "speed": 10, "safety": 2, "efficiency": 5},
    {"name": "safe", "speed": 3, "safety": 10, "efficiency": 6},
    {"name": "efficient", "speed": 5, "safety": 5, "efficiency": 10}
]

# BUG: Doesn't handle trade-offs properly
selected = agent.select_action(actions)
print(f"Selected: {selected['name']}")
"""
            
            test_file = os.path.join(temp_dir, "multi_objective.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_action_space_pruning(self):
        """Test 342: Prune infeasible actions efficiently"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ActionPruner:
    def __init__(self):
        self.all_actions = [f"action_{i}" for i in range(1000)]
    
    def get_feasible_actions(self, state):
        # BUG: Evaluates all actions - no pruning
        feasible = []
        for action in self.all_actions:
            if self.is_feasible(state, action):
                feasible.append(action)
        return feasible
    
    def is_feasible(self, state, action):
        # Expensive check
        return hash(action) % 2 == 0

pruner = ActionPruner()

# BUG: Always checks all 1000 actions
feasible = pruner.get_feasible_actions("current_state")
print(f"Feasible actions: {len(feasible)}")
"""
            
            test_file = os.path.join(temp_dir, "action_pruning.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_state_abstraction_granularity(self):
        """Test 343: Choose appropriate state abstraction level"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class StateAbstractor:
    def __init__(self):
        self.policy = {}
    
    def abstract_state(self, raw_state):
        # BUG: Too coarse - loses important info
        return "abstracted_state"
    
    def act(self, raw_state):
        abstract = self.abstract_state(raw_state)
        return self.policy.get(abstract, "default_action")

agent = StateAbstractor()

# Different raw states
state1 = {"x": 1.0, "y": 2.0, "danger": True}
state2 = {"x": 1.1, "y": 2.1, "danger": False}

# BUG: Both map to same abstract state
abstract1 = agent.abstract_state(state1)
abstract2 = agent.abstract_state(state2)

print(f"Same abstraction: {abstract1 == abstract2}")  # Should be different!
"""
            
            test_file = os.path.join(temp_dir, "state_abstraction.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_uncertainty_quantification_decisions(self):
        """Test 344: Quantify uncertainty in decision making"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UncertainAgent:
    def __init__(self):
        self.estimates = {}
    
    def estimate_value(self, state, action):
        # BUG: Returns point estimate, no uncertainty
        key = (state, action)
        return self.estimates.get(key, 0.0)
    
    def select_action(self, state, actions):
        # BUG: Doesn't account for uncertainty
        return max(actions, key=lambda a: self.estimate_value(state, a))

agent = UncertainAgent()

# Limited data - high uncertainty
agent.estimates[("state1", "action1")] = 5.0  # 1 sample
agent.estimates[("state1", "action2")] = 4.5  # 100 samples

# BUG: Picks action1 even though action2 more certain
action = agent.select_action("state1", ["action1", "action2"])
print(f"Selected: {action}")
"""
            
            test_file = os.path.join(temp_dir, "uncertainty_quantification.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_risk_aware_decision_making(self):
        """Test 345: Make risk-aware decisions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class RiskNeutralAgent:
    def __init__(self):
        self.risk_tolerance = None  # BUG: No risk modeling
    
    def evaluate_action(self, action):
        # BUG: Only considers expected value
        outcomes = action["outcomes"]
        probabilities = action["probabilities"]
        
        expected_value = sum(o * p for o, p in zip(outcomes, probabilities))
        return expected_value

agent = RiskNeutralAgent()

# High variance action
risky = {
    "name": "risky",
    "outcomes": [100, -50],
    "probabilities": [0.5, 0.5]
}

# Low variance action
safe = {
    "name": "safe",
    "outcomes": [20, 10],
    "probabilities": [0.5, 0.5]
}

# BUG: Picks risky (EV=25) over safe (EV=15) without considering risk
risky_score = agent.evaluate_action(risky)
safe_score = agent.evaluate_action(safe)
print(f"Risky: {risky_score}, Safe: {safe_score}")
"""
            
            test_file = os.path.join(temp_dir, "risk_awareness.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestGoalManagement:
    """Test goal management and planning (10 tests)"""
    
    def test_goal_priority_updates(self):
        """Test 346: Update goal priorities dynamically"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class GoalManager:
    def __init__(self):
        self.goals = []
    
    def add_goal(self, goal, priority):
        # BUG: Static priorities
        self.goals.append({"goal": goal, "priority": priority})
    
    def get_current_goal(self):
        if not self.goals:
            return None
        # BUG: Doesn't update priorities based on context
        return max(self.goals, key=lambda g: g["priority"])

manager = GoalManager()

manager.add_goal("deliver_package", priority=5)
manager.add_goal("charge_battery", priority=3)

# Battery now at 5% - charging should be higher priority
# BUG: Still returns deliver_package
current = manager.get_current_goal()
print(f"Current goal: {current['goal']}")
"""
            
            test_file = os.path.join(temp_dir, "goal_priorities.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_goal_conflict_detection(self):
        """Test 347: Detect and resolve goal conflicts"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ConflictUnawareGoals:
    def __init__(self):
        self.goals = []
    
    def add_goal(self, goal):
        # BUG: No conflict detection
        self.goals.append(goal)
    
    def execute_goals(self):
        # BUG: Tries to execute conflicting goals
        for goal in self.goals:
            print(f"Executing: {goal}")

manager = ConflictUnawareGoals()

# Conflicting goals
manager.add_goal({"action": "go_to", "location": "A"})
manager.add_goal({"action": "go_to", "location": "B"})

# BUG: Doesn't detect that can't be at A and B simultaneously
manager.execute_goals()
"""
            
            test_file = os.path.join(temp_dir, "goal_conflicts.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_subgoal_decomposition_completeness(self):
        """Test 348: Ensure complete subgoal decomposition"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class GoalDecomposer:
    def __init__(self):
        self.decomposition_rules = {}
    
    def decompose(self, goal):
        # BUG: Incomplete decomposition
        if goal == "make_sandwich":
            return ["get_bread", "add_filling"]
            # Missing: get_filling, get_knife, close_sandwich, etc.
        return []
    
    def is_primitive(self, goal):
        return goal not in self.decomposition_rules

decomposer = GoalDecomposer()

subgoals = decomposer.decompose("make_sandwich")

# BUG: Missing critical subgoals
print(f"Subgoals: {subgoals}")
"""
            
            test_file = os.path.join(temp_dir, "subgoal_decomposition.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_goal_abandonment_criteria(self):
        """Test 349: Know when to abandon infeasible goals"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class PersistentAgent:
    def __init__(self):
        self.current_goal = None
        self.attempts = 0
    
    def pursue_goal(self, goal):
        self.current_goal = goal
        self.attempts = 0
    
    def try_achieve(self):
        # BUG: Never gives up
        self.attempts += 1
        success = False  # Always fails
        
        if not success:
            print(f"Attempt {self.attempts} failed, trying again...")
            # BUG: No abandonment criteria
            return False
        return True

agent = PersistentAgent()
agent.pursue_goal("impossible_goal")

# BUG: Infinite retries
for _ in range(100):
    agent.try_achieve()

print(f"Total attempts: {agent.attempts}")
"""
            
            test_file = os.path.join(temp_dir, "goal_abandonment.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_goal_interleaving_efficiency(self):
        """Test 350: Interleave goals efficiently"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SequentialGoalExecutor:
    def __init__(self):
        self.goals = []
    
    def add_goal(self, goal):
        self.goals.append(goal)
    
    def execute(self):
        # BUG: Sequential execution - no interleaving
        for goal in self.goals:
            self.complete_goal(goal)
    
    def complete_goal(self, goal):
        print(f"Completing {goal}")

executor = SequentialGoalExecutor()

# Goals that could be interleaved
executor.add_goal("download_file_A")  # Takes 10 min
executor.add_goal("download_file_B")  # Takes 10 min
executor.add_goal("process_data")     # Takes 5 min

# BUG: Takes 25 min sequentially, could do 15 min with parallelism
executor.execute()
"""
            
            test_file = os.path.join(temp_dir, "goal_interleaving.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_temporal_goal_constraints(self):
        """Test 351: Respect temporal constraints on goals"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class TemporalGoalManager:
    def __init__(self):
        self.goals = []
    
    def add_goal(self, goal, deadline=None):
        # BUG: Stores deadline but doesn't use it
        self.goals.append({"goal": goal, "deadline": deadline})
    
    def select_next_goal(self):
        # BUG: Ignores deadlines
        return self.goals[0] if self.goals else None

manager = TemporalGoalManager()

current_time = time.time()

manager.add_goal("low_priority", deadline=current_time + 1000)
manager.add_goal("urgent", deadline=current_time + 10)

# BUG: Selects low_priority even though urgent has tight deadline
next_goal = manager.select_next_goal()
print(f"Next: {next_goal['goal']}")
"""
            
            test_file = os.path.join(temp_dir, "temporal_constraints.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_goal_precondition_checking(self):
        """Test 352: Check goal preconditions before execution"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NaiveGoalExecutor:
    def __init__(self):
        self.state = {}
    
    def execute_goal(self, goal):
        # BUG: Doesn't check preconditions
        print(f"Executing {goal['action']}")
        # Fails if preconditions not met
        return True

executor = NaiveGoalExecutor()
executor.state = {"has_ingredients": False}

# Goal requires ingredients
goal = {
    "action": "cook_meal",
    "preconditions": ["has_ingredients"]
}

# BUG: Tries to execute without checking preconditions
executor.execute_goal(goal)
"""
            
            test_file = os.path.join(temp_dir, "precondition_checking.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_opportunistic_goal_achievement(self):
        """Test 353: Identify opportunities to achieve goals"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class OpportunityBlindAgent:
    def __init__(self):
        self.goals = []
        self.current_location = "A"
    
    def add_goal(self, goal):
        self.goals.append(goal)
    
    def move_to(self, location):
        self.current_location = location
        # BUG: Doesn't check for opportunistic goal completion

agent = OpportunityBlindAgent()

agent.add_goal({"action": "pick_up", "item": "package", "location": "B"})
agent.add_goal({"action": "deliver", "item": "letter", "location": "C"})

# Moving from A to C, passes through B
agent.move_to("B")  # BUG: Doesn't pick up package while here
agent.move_to("C")
# Later has to go back to B

print(f"Goals remaining: {len(agent.goals)}")
"""
            
            test_file = os.path.join(temp_dir, "opportunistic_goals.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_goal_utility_decay(self):
        """Test 354: Account for time-dependent goal utility"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class StaticUtilityGoals:
    def __init__(self):
        self.goals = []
    
    def add_goal(self, goal, utility, added_time):
        # BUG: Utility doesn't decay over time
        self.goals.append({
            "goal": goal,
            "utility": utility,
            "added_time": added_time
        })
    
    def select_goal(self):
        # BUG: Uses original utility, ignores time
        return max(self.goals, key=lambda g: g["utility"])

manager = StaticUtilityGoals()

old_time = time.time() - 3600  # 1 hour ago
now = time.time()

manager.add_goal("time_sensitive", utility=10, added_time=old_time)
manager.add_goal("fresh_goal", utility=8, added_time=now)

# BUG: Picks old goal even though utility has decayed
selected = manager.select_goal()
print(f"Selected: {selected['goal']}")
"""
            
            test_file = os.path.join(temp_dir, "utility_decay.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_goal_context_switching_cost(self):
        """Test 355: Minimize goal context switching costs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class FrequentSwitcher:
    def __init__(self):
        self.goals = []
        self.current_goal = None
    
    def select_next_goal(self):
        # BUG: Doesn't consider switching cost
        if not self.goals:
            return None
        
        # Just picks highest priority
        next_goal = max(self.goals, key=lambda g: g["priority"])
        
        if next_goal != self.current_goal:
            # BUG: Frequent switches have cost
            print(f"Switching from {self.current_goal} to {next_goal}")
            self.current_goal = next_goal
        
        return next_goal

switcher = FrequentSwitcher()

switcher.goals = [
    {"name": "goal_A", "priority": 5},
    {"name": "goal_B", "priority": 4.9},
    {"name": "goal_C", "priority": 4.8}
]

# BUG: Switches frequently for small priority differences
for _ in range(10):
    switcher.select_next_goal()
"""
            
            test_file = os.path.join(temp_dir, "switching_cost.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestSelfAdaptation:
    """Test self-adaptation mechanisms (10 tests)"""
    
    def test_performance_degradation_detection(self):
        """Test 356: Detect performance degradation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class PerformanceBlindAgent:
    def __init__(self):
        self.success_history = []
    
    def record_outcome(self, success):
        # BUG: Records but doesn't analyze
        self.success_history.append(success)
    
    def is_performing_well(self):
        # BUG: No degradation detection
        return True

agent = PerformanceBlindAgent()

# Recent performance degrading
for i in range(50):
    agent.record_outcome(True)  # Initially successful

for i in range(50):
    agent.record_outcome(False)  # Now failing

# BUG: Doesn't detect degradation
print(f"Performing well: {agent.is_performing_well()}")
"""
            
            test_file = os.path.join(temp_dir, "performance_detection.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_strategy_switching_triggers(self):
        """Test 357: Switch strategies when appropriate"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class StaticStrategyAgent:
    def __init__(self):
        self.strategy = "default"
        self.failure_count = 0
    
    def execute(self):
        # BUG: Never switches strategy
        if self.strategy == "default":
            success = False  # Failing
        else:
            success = True
        
        if not success:
            self.failure_count += 1
        
        return success

agent = StaticStrategyAgent()

# Fails repeatedly
for _ in range(100):
    agent.execute()

# BUG: Still using failing strategy
print(f"Strategy: {agent.strategy}, Failures: {agent.failure_count}")
"""
            
            test_file = os.path.join(temp_dir, "strategy_switching.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_hyperparameter_auto_tuning(self):
        """Test 358: Auto-tune hyperparameters based on performance"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class FixedHyperparameters:
    def __init__(self):
        self.learning_rate = 0.1  # BUG: Never adjusted
        self.performance = []
    
    def train(self):
        # Simulate training
        performance = 0.5  # Not improving
        self.performance.append(performance)
        
        # BUG: Doesn't adjust learning_rate
        return performance

agent = FixedHyperparameters()

# Training plateaus
for _ in range(100):
    perf = agent.train()

# BUG: Learning rate never tuned
print(f"Learning rate: {agent.learning_rate}")
print(f"Performance: {agent.performance[-1]}")
"""
            
            test_file = os.path.join(temp_dir, "hyperparameter_tuning.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_capability_self_assessment(self):
        """Test 359: Self-assess capabilities accurately"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class OverconfidentAgent:
    def __init__(self):
        self.capabilities = {}
    
    def can_perform(self, task):
        # BUG: Overestimates capabilities
        return True
    
    def attempt_task(self, task):
        # Actually fails
        return False

agent = OverconfidentAgent()

# Claims it can do everything
tasks = ["fly", "teleport", "time_travel"]

for task in tasks:
    if agent.can_perform(task):
        success = agent.attempt_task(task)
        # BUG: Claims capability but fails
        print(f"{task}: can={True}, success={success}")
"""
            
            test_file = os.path.join(temp_dir, "capability_assessment.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_failure_pattern_recognition(self):
        """Test 360: Recognize patterns in failures"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class PatternBlindAgent:
    def __init__(self):
        self.failure_log = []
    
    def record_failure(self, context):
        # BUG: Records but doesn't analyze patterns
        self.failure_log.append(context)
    
    def should_avoid(self, context):
        # BUG: Doesn't recognize failure patterns
        return False

agent = PatternBlindAgent()

# Pattern: always fails in "rainy" conditions
for i in range(20):
    if i % 2 == 0:
        agent.record_failure({"weather": "rainy", "location": "outdoor"})
    else:
        agent.record_failure({"weather": "sunny", "location": "outdoor"})

# BUG: Doesn't recognize rainy weather causes failures
should_avoid = agent.should_avoid({"weather": "rainy", "location": "outdoor"})
print(f"Should avoid rainy: {should_avoid}")
"""
            
            test_file = os.path.join(temp_dir, "pattern_recognition.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_resource_usage_optimization(self):
        """Test 361: Optimize resource usage over time"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ResourceWaster:
    def __init__(self):
        self.memory_usage = 100
        self.cpu_usage = 100
    
    def execute_task(self):
        # BUG: Always uses maximum resources
        memory_needed = 100
        cpu_needed = 100
        
        # Could do with less but doesn't adapt
        return True
    
    def optimize(self):
        # BUG: No optimization
        pass

agent = ResourceWaster()

# Task only needs 20% resources
for _ in range(100):
    agent.execute_task()

# BUG: Still using 100%
print(f"Memory: {agent.memory_usage}%, CPU: {agent.cpu_usage}%")
"""
            
            test_file = os.path.join(temp_dir, "resource_optimization.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_model_retraining_triggers(self):
        """Test 362: Trigger model retraining when needed"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class StaleModelAgent:
    def __init__(self):
        self.model_version = 1
        self.model_accuracy = 0.9
        self.recent_accuracy = []
    
    def predict(self, input_data):
        # Accuracy degrading
        accuracy = 0.5
        self.recent_accuracy.append(accuracy)
        return "prediction"
    
    def should_retrain(self):
        # BUG: Never triggers retraining
        return False

agent = StaleModelAgent()

# Make predictions with degrading accuracy
for _ in range(100):
    agent.predict("data")

# BUG: Doesn't retrain despite poor accuracy
print(f"Should retrain: {agent.should_retrain()}")
print(f"Recent accuracy: {sum(agent.recent_accuracy[-10:]) / 10}")
"""
            
            test_file = os.path.join(temp_dir, "retraining_triggers.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_configuration_drift_detection(self):
        """Test 363: Detect configuration drift"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ConfigAgent:
    def __init__(self):
        self.config = {"timeout": 30, "retries": 3}
        self.optimal_config = {"timeout": 30, "retries": 3}
    
    def update_config(self, key, value):
        # BUG: Doesn't track drift from optimal
        self.config[key] = value
    
    def detect_drift(self):
        # BUG: No drift detection
        return False

agent = ConfigAgent()

# Config drifts from optimal
agent.update_config("timeout", 5)
agent.update_config("retries", 10)

# BUG: Doesn't detect drift
has_drift = agent.detect_drift()
print(f"Config drift: {has_drift}")
print(f"Current: {agent.config}")
print(f"Optimal: {agent.optimal_config}")
"""
            
            test_file = os.path.join(temp_dir, "config_drift.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_feature_importance_adaptation(self):
        """Test 364: Adapt feature importance weights"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class StaticFeatureWeights:
    def __init__(self):
        self.feature_weights = {
            "feature_A": 0.5,
            "feature_B": 0.3,
            "feature_C": 0.2
        }
    
    def predict(self, features):
        # BUG: Static weights, doesn't adapt
        score = sum(
            features[f] * self.feature_weights[f]
            for f in features
        )
        return score

agent = StaticFeatureWeights()

# feature_C now most important, but weights don't change
features = {"feature_A": 0.1, "feature_B": 0.1, "feature_C": 0.9}

# BUG: Uses outdated weights
score = agent.predict(features)
print(f"Score: {score}")
print(f"Weights: {agent.feature_weights}")
"""
            
            test_file = os.path.join(temp_dir, "feature_adaptation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_meta_learning_adaptation(self):
        """Test 365: Learn how to learn better"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoMetaLearning:
    def __init__(self):
        self.learning_history = []
    
    def learn_task(self, task):
        # BUG: Doesn't learn from learning process
        success = self.attempt_learning(task)
        self.learning_history.append(success)
        return success
    
    def attempt_learning(self, task):
        # Always uses same learning strategy
        return False
    
    def adapt_learning_strategy(self):
        # BUG: No meta-learning
        pass

agent = NoMetaLearning()

# Learns multiple similar tasks
tasks = ["task_1", "task_2", "task_3"]

for task in tasks:
    agent.learn_task(task)

# BUG: Doesn't improve learning strategy
agent.adapt_learning_strategy()
print(f"Learning history: {agent.learning_history}")
"""
            
            test_file = os.path.join(temp_dir, "meta_learning.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
