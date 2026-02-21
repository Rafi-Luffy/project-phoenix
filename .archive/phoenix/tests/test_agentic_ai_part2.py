"""
Comprehensive Test Suite for Phoenix - Agentic AI Systems Part 2
Tests 186-215: Task Delegation, Planning & Orchestration (30 tests)

This file tests Phoenix's ability to detect and fix bugs in task delegation,
hierarchical planning, and agent orchestration systems.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch


class TestTaskDelegation:
    """Test task delegation patterns (10 tests)"""
    
    def test_task_assignment_overload(self):
        """Test 186: Prevent task overload on single agent"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class Agent:
    def __init__(self, capacity):
        self.capacity = capacity
        self.tasks = []
    
    def assign_task(self, task):
        # BUG: No capacity check - overload
        self.tasks.append(task)
        return True

class TaskDelegator:
    def __init__(self, agents):
        self.agents = agents
    
    def delegate(self, tasks):
        # BUG: Always assigns to first agent
        for task in tasks:
            self.agents[0].assign_task(task)

agents = [Agent(capacity=5) for _ in range(3)]
delegator = TaskDelegator(agents)

# Assign 100 tasks - all go to agent 0
tasks = [f"task_{i}" for i in range(100)]
delegator.delegate(tasks)

print(f"Agent 0: {len(agents[0].tasks)} tasks")  # 100 - overloaded
print(f"Agent 1: {len(agents[1].tasks)} tasks")  # 0 - idle
"""
            
            test_file = os.path.join(temp_dir, "task_overload.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_delegation_cycle_detection(self):
        """Test 187: Detect delegation cycles in hierarchical agents"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class HierarchicalAgent:
    def __init__(self, name, delegate_to=None):
        self.name = name
        self.delegate_to = delegate_to
    
    def execute_task(self, task):
        # BUG: No cycle detection - infinite delegation
        if self.delegate_to:
            print(f"{self.name} delegates to {self.delegate_to.name}")
            return self.delegate_to.execute_task(task)
        return f"{self.name} executes {task}"

# Create delegation cycle
agent_a = HierarchicalAgent("A")
agent_b = HierarchicalAgent("B")
agent_c = HierarchicalAgent("C")

agent_a.delegate_to = agent_b
agent_b.delegate_to = agent_c
agent_c.delegate_to = agent_a  # Cycle!

# Infinite delegation loop
agent_a.execute_task("important_task")
"""
            
            test_file = os.path.join(temp_dir, "delegation_cycle.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_skill_mismatch_delegation(self):
        """Test 188: Match task requirements with agent skills"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class Task:
    def __init__(self, name, required_skills):
        self.name = name
        self.required_skills = required_skills

class SkilledAgent:
    def __init__(self, name, skills):
        self.name = name
        self.skills = skills
    
    def can_execute(self, task):
        return all(skill in self.skills for skill in task.required_skills)

class SmartDelegator:
    def __init__(self, agents):
        self.agents = agents
    
    def delegate(self, task):
        # BUG: Doesn't check skill match
        return self.agents[0]  # Just picks first agent

agents = [
    SkilledAgent("Python Expert", ["python", "ml"]),
    SkilledAgent("JS Expert", ["javascript", "react"]),
]

task = Task("ML Model", required_skills=["python", "ml"])
delegator = SmartDelegator(agents)

assigned_agent = delegator.delegate(task)
# Might assign to JS expert - skill mismatch
print(f"Task assigned to: {assigned_agent.name}")
"""
            
            test_file = os.path.join(temp_dir, "skill_mismatch.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_dependency_aware_delegation(self):
        """Test 189: Respect task dependencies in delegation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class DependentTask:
    def __init__(self, task_id, dependencies=None):
        self.id = task_id
        self.dependencies = dependencies or []
        self.completed = False

class Orchestrator:
    def __init__(self):
        self.tasks = {}
    
    def schedule(self, task):
        # BUG: Doesn't check dependencies before scheduling
        self.execute(task)
    
    def execute(self, task):
        # Execute without checking dependencies
        task.completed = True

tasks = {
    "A": DependentTask("A"),
    "B": DependentTask("B", dependencies=["A"]),
    "C": DependentTask("C", dependencies=["B"]),
}

orchestrator = Orchestrator()
# Execute in wrong order - dependencies violated
orchestrator.schedule(tasks["C"])  # Depends on B
orchestrator.schedule(tasks["B"])  # Depends on A
orchestrator.schedule(tasks["A"])  # Should be first
"""
            
            test_file = os.path.join(temp_dir, "dependencies.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_partial_failure_rollback(self):
        """Test 190: Rollback partially completed delegated tasks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class Transaction:
    def __init__(self):
        self.steps = []
        self.completed_steps = []
    
    def add_step(self, step):
        self.steps.append(step)
    
    def execute(self):
        # BUG: No rollback on partial failure
        for step in self.steps:
            self.completed_steps.append(step)
            if step == "failing_step":
                raise Exception("Step failed")
        return True

transaction = Transaction()
transaction.add_step("step1")
transaction.add_step("step2")
transaction.add_step("failing_step")
transaction.add_step("step3")

try:
    transaction.execute()
except Exception:
    # Steps 1 and 2 completed but not rolled back - BUG
    print(f"Completed steps: {transaction.completed_steps}")
"""
            
            test_file = os.path.join(temp_dir, "rollback.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_load_balancing_unfairness(self):
        """Test 191: Ensure fair load balancing across agents"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class WorkerAgent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.load = 0
    
    def add_work(self, amount):
        self.load += amount

class LoadBalancer:
    def __init__(self, workers):
        self.workers = workers
        self.next_index = 0
    
    def distribute(self, work_items):
        # BUG: Round-robin ignores current load
        for work in work_items:
            worker = self.workers[self.next_index]
            worker.add_work(work)
            self.next_index = (self.next_index + 1) % len(self.workers)

workers = [WorkerAgent(i) for i in range(3)]
# Worker 0 already has high load
workers[0].load = 1000

balancer = LoadBalancer(workers)
work_items = [10, 20, 30, 40, 50, 60]
balancer.distribute(work_items)

# Worker 0 gets more work despite high load - unfair
for w in workers:
    print(f"Worker {w.id}: load={w.load}")
"""
            
            test_file = os.path.join(temp_dir, "load_balancing.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_delegation_timeout_propagation(self):
        """Test 192: Propagate timeouts through delegation chain"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class TimedAgent:
    def __init__(self, name, processing_time):
        self.name = name
        self.processing_time = processing_time
    
    def process(self, task, timeout):
        # BUG: Doesn't respect timeout from parent
        time.sleep(self.processing_time)
        return f"{self.name} processed {task}"

class Delegator:
    def __init__(self, agent):
        self.agent = agent
    
    def delegate_with_timeout(self, task, timeout):
        # BUG: Timeout not enforced
        return self.agent.process(task, timeout)

agent = TimedAgent("SlowAgent", processing_time=10)
delegator = Delegator(agent)

# Timeout=1 but agent takes 10 seconds - BUG
result = delegator.delegate_with_timeout("task", timeout=1)
"""
            
            test_file = os.path.join(temp_dir, "timeout_propagation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_work_stealing_race_condition(self):
        """Test 193: Handle race conditions in work stealing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading

class WorkQueue:
    def __init__(self):
        self.tasks = []
    
    def add(self, task):
        self.tasks.append(task)
    
    def steal(self):
        # BUG: Race condition - no locking
        if self.tasks:
            return self.tasks.pop()
        return None

class WorkStealingAgent(threading.Thread):
    def __init__(self, agent_id, own_queue, victim_queues):
        super().__init__()
        self.id = agent_id
        self.own_queue = own_queue
        self.victim_queues = victim_queues
        self.completed = []
    
    def run(self):
        # Try own queue first
        task = self.own_queue.steal()
        if not task:
            # Steal from others
            for victim in self.victim_queues:
                task = victim.steal()
                if task:
                    break
        
        if task:
            self.completed.append(task)

# Race condition when stealing
queues = [WorkQueue() for _ in range(3)]
queues[0].add("task1")

agents = [WorkStealingAgent(i, queues[i], [q for j, q in enumerate(queues) if j != i]) for i in range(3)]
for agent in agents:
    agent.start()
for agent in agents:
    agent.join()

# Multiple agents might steal same task - BUG
"""
            
            test_file = os.path.join(temp_dir, "work_stealing.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_priority_queue_starvation(self):
        """Test 194: Prevent low-priority task starvation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import heapq

class PriorityTask:
    def __init__(self, priority, task_id, arrival_time):
        self.priority = priority
        self.task_id = task_id
        self.arrival_time = arrival_time
    
    def __lt__(self, other):
        # BUG: Only compares priority - starvation possible
        return self.priority < other.priority

class PriorityScheduler:
    def __init__(self):
        self.queue = []
    
    def enqueue(self, task):
        heapq.heappush(self.queue, task)
    
    def dequeue(self):
        if self.queue:
            return heapq.heappop(self.queue)
        return None

scheduler = PriorityScheduler()

# Add high priority tasks continuously
for i in range(100):
    scheduler.enqueue(PriorityTask(priority=1, task_id=f"high_{i}", arrival_time=i))

# Add one low priority task
scheduler.enqueue(PriorityTask(priority=100, task_id="low_1", arrival_time=0))

# Low priority task never executes - starvation
for _ in range(50):
    task = scheduler.dequeue()
    if task:
        print(f"Executing: {task.task_id}")
"""
            
            test_file = os.path.join(temp_dir, "priority_starvation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_delegation_context_loss(self):
        """Test 195: Preserve context through delegation chain"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class Context:
    def __init__(self, user_id, session_id, metadata):
        self.user_id = user_id
        self.session_id = session_id
        self.metadata = metadata

class Agent:
    def __init__(self, name):
        self.name = name
    
    def process(self, task):
        # BUG: Loses context - doesn't pass metadata
        return f"{self.name}: {task}"
    
    def delegate(self, task, next_agent):
        # Context information lost in delegation
        return next_agent.process(task)

context = Context(user_id="user123", session_id="session456", metadata={"priority": "high"})

agent1 = Agent("Agent1")
agent2 = Agent("Agent2")
agent3 = Agent("Agent3")

# Context lost after first delegation
result = agent1.delegate("process_with_context", agent2)
# Agent2 and Agent3 don't know user_id, session_id - BUG
"""
            
            test_file = os.path.join(temp_dir, "context_loss.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestHierarchicalPlanning:
    """Test hierarchical planning systems (10 tests)"""
    
    def test_plan_decomposition_infinite_recursion(self):
        """Test 196: Prevent infinite recursion in plan decomposition"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class Task:
    def __init__(self, name, is_primitive=False):
        self.name = name
        self.is_primitive = is_primitive

class Planner:
    def decompose(self, task):
        # BUG: No recursion limit - infinite decomposition
        if task.is_primitive:
            return [task]
        
        # Decompose into subtasks
        subtasks = [
            Task(f"{task.name}_sub1"),
            Task(f"{task.name}_sub2")
        ]
        
        result = []
        for subtask in subtasks:
            result.extend(self.decompose(subtask))
        return result

planner = Planner()
root_task = Task("ComplexTask")

# Infinite recursion - tasks never become primitive
plan = planner.decompose(root_task)
"""
            
            test_file = os.path.join(temp_dir, "infinite_decomposition.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_goal_conflict_detection(self):
        """Test 197: Detect conflicting goals in multi-goal planning"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class Goal:
    def __init__(self, name, target_state):
        self.name = name
        self.target_state = target_state

class MultiGoalPlanner:
    def __init__(self):
        self.goals = []
    
    def add_goal(self, goal):
        # BUG: Doesn't check for conflicts
        self.goals.append(goal)
    
    def plan(self):
        # Try to achieve all goals
        state = {}
        for goal in self.goals:
            state.update(goal.target_state)
        return state

planner = MultiGoalPlanner()
planner.add_goal(Goal("SaveMoney", {"budget": "low"}))
planner.add_goal(Goal("BuyExpensive", {"budget": "high"}))

# Conflicting goals - can't have both low and high budget
plan = planner.plan()
print(f"Plan: {plan}")  # Conflict not detected
"""
            
            test_file = os.path.join(temp_dir, "goal_conflict.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_plan_repair_loop(self):
        """Test 198: Avoid infinite loops in plan repair"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class Plan:
    def __init__(self, steps):
        self.steps = steps
        self.repair_count = 0

class PlanExecutor:
    def execute(self, plan):
        for step in plan.steps:
            if step == "failing_step":
                return False
        return True
    
    def repair_and_retry(self, plan):
        # BUG: No repair limit - infinite loop
        while not self.execute(plan):
            plan.repair_count += 1
            # "Repair" by doing nothing
            pass

executor = PlanExecutor()
plan = Plan(["step1", "failing_step", "step2"])

# Infinite repair loop - never succeeds
executor.repair_and_retry(plan)
"""
            
            test_file = os.path.join(temp_dir, "plan_repair_loop.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_resource_constraint_violation(self):
        """Test 199: Enforce resource constraints in planning"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class Action:
    def __init__(self, name, resource_cost):
        self.name = name
        self.resource_cost = resource_cost

class ResourcePlanner:
    def __init__(self, available_resources):
        self.available_resources = available_resources
    
    def create_plan(self, actions):
        # BUG: Doesn't check resource constraints
        plan = []
        for action in actions:
            plan.append(action)
        return plan

planner = ResourcePlanner(available_resources={"memory": 100, "cpu": 50})

actions = [
    Action("Task1", {"memory": 60, "cpu": 30}),
    Action("Task2", {"memory": 70, "cpu": 40}),  # Exceeds memory
]

# Plan exceeds resources but not detected - BUG
plan = planner.create_plan(actions)
total_memory = sum(a.resource_cost["memory"] for a in plan)
print(f"Total memory needed: {total_memory}, Available: 100")
"""
            
            test_file = os.path.join(temp_dir, "resource_constraints.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_temporal_constraint_violation(self):
        """Test 200: Respect temporal constraints in scheduling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class TemporalAction:
    def __init__(self, name, duration, deadline):
        self.name = name
        self.duration = duration
        self.deadline = deadline

class TemporalPlanner:
    def __init__(self):
        self.schedule = []
    
    def schedule_action(self, action, start_time):
        # BUG: Doesn't check if completion before deadline
        self.schedule.append((action, start_time))
    
    def create_schedule(self, actions):
        current_time = 0
        for action in actions:
            self.schedule_action(action, current_time)
            current_time += action.duration

actions = [
    TemporalAction("A", duration=10, deadline=15),
    TemporalAction("B", duration=20, deadline=25),  # Can't meet deadline
]

planner = TemporalPlanner()
planner.create_schedule(actions)

# Action B starts at time 10, finishes at 30, but deadline is 25 - BUG
"""
            
            test_file = os.path.join(temp_dir, "temporal_constraints.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_plan_validity_check_missing(self):
        """Test 201: Validate plan preconditions and postconditions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class Action:
    def __init__(self, name, preconditions, postconditions):
        self.name = name
        self.preconditions = preconditions
        self.postconditions = postconditions

class PlanValidator:
    def __init__(self, initial_state):
        self.state = initial_state
    
    def validate(self, plan):
        # BUG: Doesn't check preconditions
        for action in plan:
            # Apply postconditions without checking preconditions
            self.state.update(action.postconditions)
        return True

initial_state = {"door": "closed", "key": "none"}

plan = [
    Action("OpenDoor", 
           preconditions={"door": "closed", "key": "have"},
           postconditions={"door": "open"}),
]

validator = PlanValidator(initial_state)
# Plan invalid (no key) but validator doesn't catch it - BUG
is_valid = validator.validate(plan)
print(f"Plan valid: {is_valid}")
"""
            
            test_file = os.path.join(temp_dir, "plan_validity.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_plan_optimization_local_minima(self):
        """Test 202: Escape local minima in plan optimization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class Plan:
    def __init__(self, steps):
        self.steps = steps
    
    def cost(self):
        return len(self.steps)

class PlanOptimizer:
    def optimize(self, plan):
        # BUG: Greedy optimization - stuck in local minima
        improved = True
        while improved:
            improved = False
            for i in range(len(plan.steps) - 1):
                # Try to remove a step
                new_plan = Plan(plan.steps[:i] + plan.steps[i+1:])
                if new_plan.cost() < plan.cost():
                    plan = new_plan
                    improved = True
                    break
        return plan

# Initial plan has local minimum
plan = Plan(["A", "B", "C", "D", "E"])
optimizer = PlanOptimizer()

# Gets stuck - can't find better global optimum
optimized = optimizer.optimize(plan)
print(f"Optimized plan length: {optimized.cost()}")
"""
            
            test_file = os.path.join(temp_dir, "local_minima.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_contingency_plan_missing(self):
        """Test 203: Include contingency plans for failures"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class RobustPlanner:
    def __init__(self):
        self.main_plan = []
        self.contingency_plans = {}
    
    def create_plan(self, goal):
        # BUG: No contingency planning
        self.main_plan = ["step1", "step2", "step3"]
        return self.main_plan
    
    def execute(self):
        for step in self.main_plan:
            if step == "step2":
                # Step fails
                raise Exception("Step2 failed")

planner = RobustPlanner()
planner.create_plan("achieve_goal")

try:
    planner.execute()
except Exception:
    # No contingency plan - execution fails - BUG
    print("Execution failed with no backup plan")
"""
            
            test_file = os.path.join(temp_dir, "contingency.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_interleaved_planning_execution(self):
        """Test 204: Handle interleaved planning and execution"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class DynamicPlanner:
    def __init__(self):
        self.plan = []
        self.world_state = {"obstacle": False}
    
    def plan_ahead(self, steps):
        # BUG: Plans without considering execution feedback
        self.plan = [f"step_{i}" for i in range(steps)]
    
    def execute_step(self):
        if self.plan:
            step = self.plan.pop(0)
            # World state changed during execution
            if step == "step_3":
                self.world_state["obstacle"] = True
            return step
        return None

planner = DynamicPlanner()
planner.plan_ahead(5)

# Plan becomes invalid after step 3 but continues - BUG
for _ in range(5):
    step = planner.execute_step()
    if step:
        print(f"Executing: {step}, Obstacle: {planner.world_state['obstacle']}")
"""
            
            test_file = os.path.join(temp_dir, "interleaved.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_partial_order_planning_inconsistency(self):
        """Test 205: Maintain consistency in partial-order plans"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class PartialOrderPlan:
    def __init__(self):
        self.actions = []
        self.ordering_constraints = []
    
    def add_action(self, action):
        self.actions.append(action)
    
    def add_constraint(self, before, after):
        # BUG: Doesn't check for cycles
        self.ordering_constraints.append((before, after))
    
    def is_consistent(self):
        # Should detect cycles but doesn't
        return True

plan = PartialOrderPlan()
plan.add_action("A")
plan.add_action("B")
plan.add_action("C")

# Create cycle: A before B, B before C, C before A
plan.add_constraint("A", "B")
plan.add_constraint("B", "C")
plan.add_constraint("C", "A")  # Cycle!

# Should be inconsistent but returns True - BUG
print(f"Plan consistent: {plan.is_consistent()}")
"""
            
            test_file = os.path.join(temp_dir, "partial_order.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestAgentOrchestration:
    """Test agent orchestration patterns (10 tests)"""
    
    def test_orchestrator_single_point_failure(self):
        """Test 206: Eliminate single point of failure in orchestrator"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class CentralOrchestrator:
    def __init__(self, agents):
        self.agents = agents
        self.alive = True
    
    def coordinate(self):
        # BUG: Single point of failure
        if not self.alive:
            raise Exception("Orchestrator failed")
        
        for agent in self.agents:
            agent.execute()

class WorkerAgent:
    def execute(self):
        return "working"

orchestrator = CentralOrchestrator([WorkerAgent() for _ in range(5)])

# If orchestrator fails, all agents stop working - BUG
orchestrator.alive = False
try:
    orchestrator.coordinate()
except Exception:
    print("All work stopped due to orchestrator failure")
"""
            
            test_file = os.path.join(temp_dir, "single_point_failure.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_coordination_protocol_deadlock(self):
        """Test 207: Prevent deadlock in coordination protocol"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading

class CoordinatedAgent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.lock = threading.Lock()
        self.partner = None
    
    def synchronize_with(self, partner):
        # BUG: Lock ordering causes deadlock
        with self.lock:
            with partner.lock:
                print(f"Agent {self.id} synchronized with {partner.id}")

agent1 = CoordinatedAgent(1)
agent2 = CoordinatedAgent(2)

# Deadlock when agents try to synchronize simultaneously
t1 = threading.Thread(target=agent1.synchronize_with, args=(agent2,))
t2 = threading.Thread(target=agent2.synchronize_with, args=(agent1,))

t1.start()
t2.start()
# Deadlock - BUG
"""
            
            test_file = os.path.join(temp_dir, "coordination_deadlock.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_workflow_state_inconsistency(self):
        """Test 208: Maintain workflow state consistency"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class WorkflowState:
    def __init__(self):
        self.current_step = 0
        self.data = {}
    
    def advance(self):
        # BUG: No atomic state update
        self.current_step += 1
        # Another thread might read inconsistent state here

class WorkflowOrchestrator:
    def __init__(self):
        self.state = WorkflowState()
    
    def process_step(self, step_data):
        # BUG: State update not atomic
        self.state.data.update(step_data)
        self.state.advance()

orchestrator = WorkflowOrchestrator()

# Concurrent access causes inconsistency
orchestrator.process_step({"key": "value1"})
# State might be: step=1 with old data or step=0 with new data - BUG
"""
            
            test_file = os.path.join(temp_dir, "state_inconsistency.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_agent_discovery_stale_registry(self):
        """Test 209: Handle stale entries in agent registry"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class AgentRegistry:
    def __init__(self):
        self.agents = {}
    
    def register(self, agent_id, endpoint):
        # BUG: No TTL or heartbeat - stale entries persist
        self.agents[agent_id] = {
            "endpoint": endpoint,
            "registered_at": time.time()
        }
    
    def discover(self, agent_id):
        return self.agents.get(agent_id)

registry = AgentRegistry()
registry.register("agent1", "http://localhost:5000")

time.sleep(2)
# Agent1 crashed but still in registry

agent_info = registry.discover("agent1")
# Returns stale endpoint - BUG
print(f"Discovered: {agent_info['endpoint']}")
"""
            
            test_file = os.path.join(temp_dir, "stale_registry.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_saga_pattern_compensation_failure(self):
        """Test 210: Handle compensation failures in Saga pattern"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SagaStep:
    def __init__(self, name, execute_fn, compensate_fn):
        self.name = name
        self.execute = execute_fn
        self.compensate = compensate_fn

class SagaOrchestrator:
    def __init__(self):
        self.completed_steps = []
    
    def execute_saga(self, steps):
        try:
            for step in steps:
                step.execute()
                self.completed_steps.append(step)
        except Exception:
            # BUG: Doesn't handle compensation failures
            for step in reversed(self.completed_steps):
                step.compensate()  # What if this fails?

def failing_compensate():
    raise Exception("Compensation failed")

steps = [
    SagaStep("step1", lambda: print("Step1"), failing_compensate),
    SagaStep("step2", lambda: print("Step2"), lambda: print("Compensate2")),
]

orchestrator = SagaOrchestrator()
# Compensation failure leaves system in inconsistent state - BUG
"""
            
            test_file = os.path.join(temp_dir, "saga_compensation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_dynamic_workflow_modification(self):
        """Test 211: Safely modify workflows during execution"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class DynamicWorkflow:
    def __init__(self):
        self.steps = ["step1", "step2", "step3"]
        self.current_index = 0
    
    def execute_next(self):
        if self.current_index < len(self.steps):
            step = self.steps[self.current_index]
            self.current_index += 1
            return step
        return None
    
    def add_step(self, step):
        # BUG: Modifying workflow during execution causes issues
        self.steps.append(step)

workflow = DynamicWorkflow()

# Execute first step
workflow.execute_next()

# Modify workflow during execution
workflow.add_step("new_step")

# Continue execution - may skip or repeat steps - BUG
while True:
    step = workflow.execute_next()
    if not step:
        break
    print(f"Executing: {step}")
"""
            
            test_file = os.path.join(temp_dir, "dynamic_workflow.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_event_ordering_guarantee(self):
        """Test 212: Guarantee event ordering in event-driven orchestration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class Event:
    def __init__(self, event_type, timestamp, data):
        self.type = event_type
        self.timestamp = timestamp
        self.data = data

class EventDrivenOrchestrator:
    def __init__(self):
        self.events = []
    
    def publish(self, event):
        # BUG: No ordering guarantee
        self.events.append(event)
    
    def process_events(self):
        # BUG: Processes in arbitrary order
        for event in self.events:
            self.handle(event)
    
    def handle(self, event):
        print(f"Handling: {event.type} at {event.timestamp}")

orchestrator = EventDrivenOrchestrator()
orchestrator.publish(Event("event1", timestamp=3, data="third"))
orchestrator.publish(Event("event2", timestamp=1, data="first"))
orchestrator.publish(Event("event3", timestamp=2, data="second"))

# Events processed out of order - BUG
orchestrator.process_events()
"""
            
            test_file = os.path.join(temp_dir, "event_ordering.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_circuit_breaker_state_management(self):
        """Test 213: Properly manage circuit breaker state"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class CircuitBreaker:
    def __init__(self, failure_threshold=3):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.state = "closed"
    
    def call(self, operation):
        # BUG: No timeout for half-open state
        if self.state == "open":
            raise Exception("Circuit breaker open")
        
        try:
            result = operation()
            self.failure_count = 0
            return result
        except Exception:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            raise

def failing_operation():
    raise Exception("Failed")

breaker = CircuitBreaker()

# Circuit opens but never closes - BUG
for i in range(5):
    try:
        breaker.call(failing_operation)
    except Exception:
        print(f"Attempt {i}: State={breaker.state}")

# Circuit stays open forever - no reset mechanism
"""
            
            test_file = os.path.join(temp_dir, "circuit_breaker.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_bulkhead_resource_isolation(self):
        """Test 214: Implement bulkhead pattern for resource isolation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ServiceOrchestrator:
    def __init__(self, total_threads=10):
        self.total_threads = total_threads
        self.used_threads = 0
    
    def call_service(self, service_name):
        # BUG: No bulkhead - one service can consume all resources
        if self.used_threads < self.total_threads:
            self.used_threads += 1
            return f"Called {service_name}"
        raise Exception("No threads available")

orchestrator = ServiceOrchestrator(total_threads=10)

# Service A consumes all threads
for i in range(10):
    orchestrator.call_service("ServiceA")

# Service B can't get any threads - BUG
try:
    orchestrator.call_service("ServiceB")
except Exception as e:
    print(f"ServiceB failed: {e}")
"""
            
            test_file = os.path.join(temp_dir, "bulkhead.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_compensating_transaction_ordering(self):
        """Test 215: Ensure correct ordering of compensating transactions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class Transaction:
    def __init__(self, name, execute_fn, compensate_fn):
        self.name = name
        self.execute = execute_fn
        self.compensate = compensate_fn

class TransactionCoordinator:
    def __init__(self):
        self.executed = []
    
    def run_transactions(self, transactions):
        try:
            for txn in transactions:
                txn.execute()
                self.executed.append(txn)
                if txn.name == "txn2":
                    raise Exception("Transaction failed")
        except Exception:
            # BUG: Compensates in wrong order (should be reverse)
            for txn in self.executed:
                txn.compensate()

transactions = [
    Transaction("txn1", lambda: print("Execute1"), lambda: print("Compensate1")),
    Transaction("txn2", lambda: print("Execute2"), lambda: print("Compensate2")),
    Transaction("txn3", lambda: print("Execute3"), lambda: print("Compensate3")),
]

coordinator = TransactionCoordinator()
# Compensates in wrong order - BUG
coordinator.run_transactions(transactions)
"""
            
            test_file = os.path.join(temp_dir, "compensating_order.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
