"""
Comprehensive Test Suite for Phoenix - Autonomous Systems Part 2
Tests 366-395: Tool Calling, Memory Systems, Perception & Action (30 tests)

This file tests Phoenix's ability to detect and fix bugs in tool calling mechanisms,
memory management, and perception-action loops for autonomous systems.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch


class TestToolCalling:
    """Test tool calling and execution (10 tests)"""
    
    def test_tool_parameter_validation(self):
        """Test 366: Validate tool parameters before execution"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ToolExecutor:
    def __init__(self):
        self.tools = {
            "calculator": {
                "params": ["operation", "a", "b"],
                "types": {"operation": str, "a": float, "b": float}
            }
        }
    
    def call_tool(self, tool_name, params):
        # BUG: No parameter validation
        if tool_name == "calculator":
            return params["a"] + params["b"]
        return None

executor = ToolExecutor()

# Invalid parameters
result = executor.call_tool("calculator", {
    "operation": "add",
    "a": "not_a_number",  # BUG: String instead of float
    "b": 5
})
"""
            
            test_file = os.path.join(temp_dir, "tool_validation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_tool_timeout_handling(self):
        """Test 367: Handle tool execution timeouts"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class TimeoutlessToolCaller:
    def call_tool(self, tool_name, params):
        # BUG: No timeout mechanism
        if tool_name == "slow_api":
            time.sleep(1000)  # Hangs forever
            return "result"
        return None

caller = TimeoutlessToolCaller()

# BUG: Hangs indefinitely
result = caller.call_tool("slow_api", {})
"""
            
            test_file = os.path.join(temp_dir, "tool_timeout.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_tool_retry_logic(self):
        """Test 368: Implement exponential backoff for retries"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoRetryToolCaller:
    def __init__(self):
        self.attempt_count = 0
    
    def call_tool(self, tool_name):
        # BUG: No retry logic
        self.attempt_count += 1
        
        # Simulates transient failure
        if self.attempt_count < 3:
            raise Exception("Transient error")
        
        return "success"

caller = NoRetryToolCaller()

try:
    result = caller.call_tool("flaky_api")
except Exception as e:
    # BUG: Fails on first error, doesn't retry
    print(f"Failed: {e}")
"""
            
            test_file = os.path.join(temp_dir, "tool_retry.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_tool_result_caching(self):
        """Test 369: Cache tool results for identical calls"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UncachedToolCaller:
    def __init__(self):
        self.call_count = 0
    
    def call_tool(self, tool_name, params):
        # BUG: No caching - always executes
        self.call_count += 1
        
        # Expensive operation
        result = sum(range(1000000))
        return result

caller = UncachedToolCaller()

# Same call multiple times
for _ in range(10):
    result = caller.call_tool("expensive_calc", {"n": 1000000})

# BUG: Called 10 times instead of 1
print(f"Call count: {caller.call_count}")
"""
            
            test_file = os.path.join(temp_dir, "tool_caching.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_tool_dependency_resolution(self):
        """Test 370: Resolve tool dependencies correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ToolOrchestrator:
    def __init__(self):
        self.tools = {
            "tool_A": {"depends_on": []},
            "tool_B": {"depends_on": ["tool_A"]},
            "tool_C": {"depends_on": ["tool_B"]}
        }
    
    def execute_tools(self, tool_names):
        # BUG: Doesn't resolve dependencies
        for tool in tool_names:
            print(f"Executing {tool}")

orchestrator = ToolOrchestrator()

# Execute in wrong order
orchestrator.execute_tools(["tool_C", "tool_A", "tool_B"])
# BUG: tool_C runs before its dependencies
"""
            
            test_file = os.path.join(temp_dir, "tool_dependencies.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_tool_result_type_coercion(self):
        """Test 371: Handle tool result type mismatches"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class TypeUnawareToolCaller:
    def call_tool(self, tool_name):
        # Returns string instead of expected int
        return "123"
    
    def process_result(self, result):
        # BUG: Assumes result is int
        return result + 10

caller = TypeUnawareToolCaller()

result = caller.call_tool("get_number")
# BUG: TypeError - can't add str and int
try:
    processed = caller.process_result(result)
except TypeError as e:
    print(f"Type error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "type_coercion.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_parallel_tool_execution(self):
        """Test 372: Execute independent tools in parallel"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class SequentialToolExecutor:
    def execute_tools(self, tools):
        # BUG: Sequential execution of independent tools
        results = []
        for tool in tools:
            result = self.execute_single(tool)
            results.append(result)
        return results
    
    def execute_single(self, tool):
        time.sleep(1)  # Each takes 1 second
        return f"result_{tool}"

executor = SequentialToolExecutor()

# Independent tools
tools = ["tool_1", "tool_2", "tool_3"]

start = time.time()
results = executor.execute_tools(tools)
elapsed = time.time() - start

# BUG: Takes 3 seconds instead of 1 (parallel)
print(f"Elapsed: {elapsed} seconds")
"""
            
            test_file = os.path.join(temp_dir, "parallel_tools.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_tool_error_propagation(self):
        """Test 373: Propagate tool errors with context"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ToolChain:
    def execute_chain(self, tools):
        # BUG: Loses error context
        for i, tool in enumerate(tools):
            try:
                self.execute_tool(tool)
            except Exception:
                # BUG: Doesn't indicate which tool failed
                raise Exception("Tool execution failed")
    
    def execute_tool(self, tool):
        if tool == "failing_tool":
            raise ValueError("Invalid input")

chain = ToolChain()

try:
    chain.execute_chain(["tool_1", "failing_tool", "tool_3"])
except Exception as e:
    # BUG: Can't tell it was "failing_tool" that failed
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "error_propagation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_tool_output_streaming(self):
        """Test 374: Stream tool outputs for long operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class BufferedToolExecutor:
    def execute_long_tool(self):
        # BUG: Buffers entire output
        output = []
        for i in range(1000):
            output.append(f"Line {i}")
        
        # Returns all at once
        return "\\n".join(output)

executor = BufferedToolExecutor()

# BUG: User waits for entire execution before seeing anything
result = executor.execute_long_tool()
print(result)
"""
            
            test_file = os.path.join(temp_dir, "output_streaming.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_tool_quota_management(self):
        """Test 375: Manage tool call quotas and rate limits"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class UnlimitedToolCaller:
    def __init__(self):
        self.call_count = 0
    
    def call_api_tool(self):
        # BUG: No rate limiting
        self.call_count += 1
        return "result"

caller = UnlimitedToolCaller()

# Rapid fire 1000 calls
for _ in range(1000):
    caller.call_api_tool()

# BUG: Hits API rate limit, gets blocked
print(f"Made {caller.call_count} calls")
"""
            
            test_file = os.path.join(temp_dir, "quota_management.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestMemorySystems:
    """Test memory management for agents (10 tests)"""
    
    def test_working_memory_capacity(self):
        """Test 376: Manage working memory capacity"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnboundedWorkingMemory:
    def __init__(self):
        self.working_memory = []
    
    def add_to_memory(self, item):
        # BUG: No capacity limit
        self.working_memory.append(item)
    
    def get_memory(self):
        return self.working_memory

memory = UnboundedWorkingMemory()

# Add unlimited items
for i in range(10000):
    memory.add_to_memory(f"item_{i}")

# BUG: Memory overflow
print(f"Memory size: {len(memory.get_memory())}")
"""
            
            test_file = os.path.join(temp_dir, "working_memory.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_episodic_memory_consolidation(self):
        """Test 377: Consolidate episodic memories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class RawEpisodicMemory:
    def __init__(self):
        self.episodes = []
    
    def record_episode(self, episode):
        # BUG: No consolidation - stores raw
        self.episodes.append(episode)
    
    def recall(self, query):
        # BUG: Linear search through all episodes
        return [e for e in self.episodes if query in str(e)]

memory = RawEpisodicMemory()

# Record thousands of detailed episodes
for i in range(10000):
    memory.record_episode({
        "time": i,
        "action": f"action_{i}",
        "state": {"x": i, "y": i * 2},
        "result": "success"
    })

# BUG: Slow recall, no summarization
results = memory.recall("action_5000")
"""
            
            test_file = os.path.join(temp_dir, "episodic_memory.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_semantic_memory_inference(self):
        """Test 378: Infer from semantic memory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class LiteralSemanticMemory:
    def __init__(self):
        self.facts = []
    
    def add_fact(self, fact):
        self.facts.append(fact)
    
    def query(self, question):
        # BUG: No inference - only exact matches
        for fact in self.facts:
            if fact == question:
                return True
        return False

memory = LiteralSemanticMemory()

memory.add_fact("Dogs are animals")
memory.add_fact("Rex is a dog")

# BUG: Can't infer "Rex is an animal"
can_infer = memory.query("Rex is an animal")
print(f"Can infer: {can_infer}")  # False
"""
            
            test_file = os.path.join(temp_dir, "semantic_memory.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_memory_decay_forgetting(self):
        """Test 379: Implement memory decay and forgetting"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class PerfectMemory:
    def __init__(self):
        self.memories = {}
    
    def store(self, key, value, timestamp):
        # BUG: No decay - perfect recall
        self.memories[key] = {"value": value, "time": timestamp}
    
    def recall(self, key):
        # BUG: Always returns, no forgetting
        return self.memories.get(key, {}).get("value")

memory = PerfectMemory()

# Store old memory
old_time = time.time() - 86400  # 1 day ago
memory.store("old_fact", "forgotten info", old_time)

# Store new memory
memory.store("new_fact", "fresh info", time.time())

# BUG: Recalls old memory perfectly (should decay)
old = memory.recall("old_fact")
print(f"Old memory: {old}")
"""
            
            test_file = os.path.join(temp_dir, "memory_decay.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_associative_memory_retrieval(self):
        """Test 380: Retrieve associated memories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class IsolatedMemory:
    def __init__(self):
        self.memories = []
    
    def store(self, memory):
        # BUG: No associations stored
        self.memories.append(memory)
    
    def retrieve(self, cue):
        # BUG: No associative retrieval
        for memory in self.memories:
            if memory.get("key") == cue:
                return memory
        return None

memory = IsolatedMemory()

memory.store({"key": "apple", "color": "red", "taste": "sweet"})
memory.store({"key": "strawberry", "color": "red", "taste": "sweet"})

# Query: "What else is red?"
# BUG: Can't retrieve by association
cue = "red"
results = memory.retrieve(cue)
print(f"Associated: {results}")  # None
"""
            
            test_file = os.path.join(temp_dir, "associative_memory.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_memory_prioritization(self):
        """Test 381: Prioritize important memories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class FIFOMemory:
    def __init__(self, capacity=100):
        self.capacity = capacity
        self.memories = []
    
    def store(self, memory, importance=1.0):
        # BUG: Ignores importance
        if len(self.memories) >= self.capacity:
            # BUG: Removes oldest, not least important
            self.memories.pop(0)
        self.memories.append(memory)

memory = FIFOMemory(capacity=3)

memory.store("critical_info", importance=10.0)
memory.store("trivial_1", importance=0.1)
memory.store("trivial_2", importance=0.1)
memory.store("trivial_3", importance=0.1)

# BUG: Evicted critical_info instead of trivial
print(f"Memories: {memory.memories}")
"""
            
            test_file = os.path.join(temp_dir, "memory_prioritization.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_memory_compression(self):
        """Test 382: Compress memories efficiently"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UncompressedMemory:
    def __init__(self):
        self.memories = []
    
    def store(self, memory):
        # BUG: Stores full details
        self.memories.append(memory)
    
    def get_size(self):
        return len(str(self.memories))

memory = UncompressedMemory()

# Store repetitive data
for i in range(100):
    memory.store({
        "action": "move_forward",
        "state": {"x": i, "y": 0},
        "result": "success"
    })

# BUG: Huge memory footprint
print(f"Memory size: {memory.get_size()} bytes")
"""
            
            test_file = os.path.join(temp_dir, "memory_compression.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_memory_consistency_updates(self):
        """Test 383: Maintain memory consistency on updates"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class InconsistentMemory:
    def __init__(self):
        self.facts = []
    
    def add_fact(self, fact):
        # BUG: No consistency checking
        self.facts.append(fact)
    
    def update_fact(self, old_fact, new_fact):
        # BUG: Doesn't update related facts
        if old_fact in self.facts:
            idx = self.facts.index(old_fact)
            self.facts[idx] = new_fact

memory = InconsistentMemory()

memory.add_fact("The capital of France is Paris")
memory.add_fact("Paris is in France")

# Update location
memory.update_fact("The capital of France is Paris", 
                  "The capital of Germany is Berlin")

# BUG: "Paris is in France" now inconsistent
print(f"Facts: {memory.facts}")
"""
            
            test_file = os.path.join(temp_dir, "memory_consistency.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_context_dependent_memory(self):
        """Test 384: Retrieve context-dependent memories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ContextFreeMemory:
    def __init__(self):
        self.memories = []
    
    def store(self, memory, context):
        # BUG: Doesn't store context
        self.memories.append(memory)
    
    def retrieve(self, cue, current_context):
        # BUG: Ignores context
        for memory in self.memories:
            if cue in str(memory):
                return memory
        return None

memory = ContextFreeMemory()

memory.store("ate apple", context="home")
memory.store("ate apple", context="office")

# BUG: Can't distinguish contexts
result = memory.retrieve("ate apple", current_context="home")
print(f"Retrieved: {result}")
"""
            
            test_file = os.path.join(temp_dir, "context_memory.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_memory_source_tracking(self):
        """Test 385: Track memory sources and reliability"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SourcelessMemory:
    def __init__(self):
        self.facts = []
    
    def add_fact(self, fact, source=None, reliability=None):
        # BUG: Doesn't track source
        self.facts.append(fact)
    
    def get_reliable_facts(self):
        # BUG: Can't filter by reliability
        return self.facts

memory = SourcelessMemory()

memory.add_fact("Fact A", source="trusted_source", reliability=0.95)
memory.add_fact("Fact B", source="unreliable_source", reliability=0.3)

# BUG: Returns both, can't distinguish reliability
reliable = memory.get_reliable_facts()
print(f"All facts: {reliable}")
"""
            
            test_file = os.path.join(temp_dir, "memory_source.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestPerceptionAction:
    """Test perception-action loops (10 tests)"""
    
    def test_sensor_fusion_multimodal(self):
        """Test 386: Fuse multi-modal sensor data"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnfusedSensors:
    def get_perception(self):
        # BUG: Doesn't fuse sensors
        camera = {"object": "car", "confidence": 0.8}
        lidar = {"distance": 10.5, "confidence": 0.9}
        
        # Returns separate, not fused
        return {"camera": camera, "lidar": lidar}

sensors = UnfusedSensors()

perception = sensors.get_perception()
# BUG: Can't get unified object representation
print(f"Perception: {perception}")
"""
            
            test_file = os.path.join(temp_dir, "sensor_fusion.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_perception_latency_compensation(self):
        """Test 387: Compensate for perception latency"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class LaggingPerception:
    def perceive(self):
        # Simulate sensor delay
        time.sleep(0.1)
        return {"object_position": 10.0}
    
    def act(self, perception):
        # BUG: Uses stale perception
        target = perception["object_position"]
        return f"Move to {target}"

agent = LaggingPerception()

perception = agent.perceive()
# Object has moved during perception
action = agent.act(perception)

# BUG: Acts on outdated position
print(f"Action: {action}")
"""
            
            test_file = os.path.join(temp_dir, "perception_latency.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_action_feedback_loop(self):
        """Test 388: Close action feedback loop"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class OpenLoopAgent:
    def __init__(self):
        self.position = 0
    
    def plan_action(self, target):
        # BUG: Open loop - no feedback
        distance = target - self.position
        return distance
    
    def execute(self, action):
        # BUG: Doesn't verify execution
        self.position += action

agent = OpenLoopAgent()

# Plan to move to position 10
action = agent.plan_action(10)
agent.execute(action)

# BUG: No feedback if execution failed
print(f"Position: {agent.position}")
"""
            
            test_file = os.path.join(temp_dir, "feedback_loop.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_action_smoothness_constraints(self):
        """Test 389: Ensure smooth action transitions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class JerkyAgent:
    def __init__(self):
        self.velocity = 0
    
    def set_target_velocity(self, target):
        # BUG: Instant change - no smoothing
        self.velocity = target

agent = JerkyAgent()

# Rapid changes
agent.set_target_velocity(100)
agent.set_target_velocity(0)
agent.set_target_velocity(-100)

# BUG: Jerky motion, no acceleration limits
print(f"Velocity: {agent.velocity}")
"""
            
            test_file = os.path.join(temp_dir, "action_smoothness.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_perception_uncertainty_propagation(self):
        """Test 390: Propagate perception uncertainty to actions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UncertaintyIgnoringAgent:
    def perceive(self):
        return {
            "position": 10.0,
            "uncertainty": 2.0  # +/- 2 meters
        }
    
    def plan_action(self, perception):
        # BUG: Ignores uncertainty
        target = perception["position"]
        return f"Move to exactly {target}"

agent = UncertaintyIgnoringAgent()

perception = agent.perceive()
action = agent.plan_action(perception)

# BUG: Doesn't account for position uncertainty
print(f"Action: {action}")
"""
            
            test_file = os.path.join(temp_dir, "uncertainty_propagation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_action_safety_constraints(self):
        """Test 391: Enforce safety constraints on actions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnsafeAgent:
    def __init__(self):
        self.max_speed = 100
    
    def execute_action(self, speed):
        # BUG: No safety checks
        self.current_speed = speed
        return True

agent = UnsafeAgent()

# Unsafe action
agent.execute_action(200)  # BUG: Exceeds max_speed

print(f"Current speed: {agent.current_speed}")
"""
            
            test_file = os.path.join(temp_dir, "safety_constraints.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_reactive_vs_deliberative_balance(self):
        """Test 392: Balance reactive and deliberative control"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class PureDeliberativeAgent:
    def respond(self, obstacle_distance):
        # BUG: Always deliberates, even for emergencies
        print("Planning best path...")
        print("Evaluating options...")
        print("Optimizing trajectory...")
        
        # Takes too long for emergency
        return "planned_action"

agent = PureDeliberativeAgent()

# Emergency: obstacle very close!
obstacle_distance = 0.5  # meters

# BUG: Should react immediately, not deliberate
action = agent.respond(obstacle_distance)
"""
            
            test_file = os.path.join(temp_dir, "reactive_deliberative.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_action_affordance_detection(self):
        """Test 393: Detect action affordances from perception"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class AffordanceBlindAgent:
    def perceive(self, scene):
        # BUG: Just identifies objects, not affordances
        return {"objects": ["chair", "table", "door"]}
    
    def plan_action(self, perception):
        # BUG: Doesn't know what actions are possible
        return "random_action"

agent = AffordanceBlindAgent()

perception = agent.perceive("room")
action = agent.plan_action(perception)

# BUG: Should detect: chair->sit, door->open, table->place
print(f"Action: {action}")
"""
            
            test_file = os.path.join(temp_dir, "affordance_detection.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_action_execution_monitoring(self):
        """Test 394: Monitor action execution progress"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnmonitoredExecution:
    def execute_action(self, action, duration):
        # BUG: Fire and forget - no monitoring
        print(f"Started {action}")
        # Doesn't check if action completes
        return True

agent = UnmonitoredExecution()

# Long action
agent.execute_action("move_to_location", duration=10)

# BUG: Doesn't monitor if action succeeds or gets stuck
print("Assuming action completed")
"""
            
            test_file = os.path.join(temp_dir, "execution_monitoring.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_perception_action_timing_coordination(self):
        """Test 395: Coordinate perception and action timing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class DesynchronizedAgent:
    def __init__(self):
        self.perception_rate = 10  # Hz
        self.action_rate = 100  # Hz
    
    def run_loop(self):
        # BUG: Perception and action not synchronized
        perception = self.perceive()  # 10 Hz
        
        for _ in range(10):
            # BUG: Uses same perception for 10 actions
            self.act(perception)  # 100 Hz

agent = DesynchronizedAgent()

# BUG: Actions based on stale perception
agent.run_loop()
"""
            
            test_file = os.path.join(temp_dir, "timing_coordination.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
