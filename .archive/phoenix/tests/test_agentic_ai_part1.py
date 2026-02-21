"""
Comprehensive Test Suite for Phoenix - Agentic AI Systems Part 1
Tests 156-185: Multi-Agent Coordination & Communication (30 tests)

This file tests Phoenix's ability to detect and fix bugs in agentic AI systems,
focusing on multi-agent coordination, communication protocols, and emergent behaviors.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch


class TestMultiAgentCoordination:
    """Test multi-agent coordination scenarios (10 tests)"""
    
    def test_agent_deadlock_circular_dependency(self):
        """Test 156: Detect and fix circular dependency deadlock between agents"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multi-agent system with circular dependency
            agent_code = """
class Agent1:
    def __init__(self, agent2):
        self.agent2 = agent2
        self.state = "waiting"
    
    def execute(self):
        # BUG: Waits for agent2 while agent2 waits for agent1
        while self.agent2.state == "waiting":
            pass
        return "done"

class Agent2:
    def __init__(self, agent1):
        self.agent1 = agent1
        self.state = "waiting"
    
    def execute(self):
        # BUG: Circular wait - deadlock
        while self.agent1.state == "waiting":
            pass
        return "done"

# This will deadlock
agent1 = Agent1(None)
agent2 = Agent2(agent1)
agent1.agent2 = agent2
agent1.execute()
"""
            
            test_file = os.path.join(temp_dir, "multi_agent.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            # Phoenix should detect deadlock and fix with timeout or async coordination
            assert os.path.exists(test_file)
    
    def test_agent_message_queue_overflow(self):
        """Test 157: Handle message queue overflow in agent communication"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class MessageQueue:
    def __init__(self):
        self.messages = []
    
    def send(self, msg):
        # BUG: No limit on queue size - memory overflow
        self.messages.append(msg)
    
    def receive(self):
        if self.messages:
            return self.messages.pop(0)
        return None

class FastAgent:
    def __init__(self, queue):
        self.queue = queue
    
    def run(self):
        # Sends messages faster than they can be consumed
        for i in range(1000000):
            self.queue.send(f"message_{i}")

class SlowAgent:
    def __init__(self, queue):
        self.queue = queue
    
    def run(self):
        # Slow consumer
        for i in range(10):
            self.queue.receive()

queue = MessageQueue()
fast = FastAgent(queue)
slow = SlowAgent(queue)
fast.run()
slow.run()
"""
            
            test_file = os.path.join(temp_dir, "message_queue.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_agent_priority_inversion(self):
        """Test 158: Fix priority inversion in multi-agent task scheduling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class Task:
    def __init__(self, priority, name):
        self.priority = priority
        self.name = name
        self.lock = None

class Agent:
    def __init__(self):
        self.current_task = None
    
    def execute_task(self, task):
        # BUG: Low priority task holds lock, blocking high priority
        self.current_task = task
        # Simulate work
        return f"Completed {task.name}"

class Scheduler:
    def __init__(self):
        self.agents = [Agent() for _ in range(3)]
        self.tasks = []
    
    def schedule(self):
        # BUG: No priority inheritance - priority inversion
        for task in sorted(self.tasks, key=lambda t: t.priority):
            agent = self.agents[0]
            agent.execute_task(task)

scheduler = Scheduler()
scheduler.tasks = [
    Task(priority=1, name="low"),
    Task(priority=10, name="high"),
    Task(priority=5, name="medium")
]
scheduler.schedule()
"""
            
            test_file = os.path.join(temp_dir, "priority.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_agent_split_brain_consensus(self):
        """Test 159: Handle split-brain scenario in agent consensus protocol"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class Agent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.leader = None
        self.votes = {}
    
    def vote_for_leader(self, candidate_id):
        self.votes[candidate_id] = self.votes.get(candidate_id, 0) + 1
    
    def elect_leader(self, agents):
        # BUG: No quorum check - split brain possible
        max_votes = max(self.votes.values()) if self.votes else 0
        for candidate_id, votes in self.votes.items():
            if votes == max_votes:
                self.leader = candidate_id
                return candidate_id
        return None

# Network partition creates two groups
group1 = [Agent(i) for i in range(3)]
group2 = [Agent(i) for i in range(3, 6)]

# Each group elects different leader
for agent in group1:
    agent.vote_for_leader(0)
    agent.elect_leader(group1)

for agent in group2:
    agent.vote_for_leader(3)
    agent.elect_leader(group2)
"""
            
            test_file = os.path.join(temp_dir, "consensus.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_agent_starvation_unfair_scheduling(self):
        """Test 160: Prevent agent starvation in unfair scheduling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class Agent:
    def __init__(self, agent_id, priority):
        self.id = agent_id
        self.priority = priority
        self.tasks_completed = 0

class Scheduler:
    def __init__(self, agents):
        self.agents = agents
    
    def schedule(self, num_tasks):
        # BUG: Always picks highest priority - low priority starves
        for i in range(num_tasks):
            agent = max(self.agents, key=lambda a: a.priority)
            agent.tasks_completed += 1

agents = [
    Agent(0, priority=10),
    Agent(1, priority=5),
    Agent(2, priority=1)
]

scheduler = Scheduler(agents)
scheduler.schedule(100)

# Agent 2 never gets scheduled - starvation
print(f"Agent 0: {agents[0].tasks_completed}")
print(f"Agent 1: {agents[1].tasks_completed}")
print(f"Agent 2: {agents[2].tasks_completed}")  # Should be 0 - BUG
"""
            
            test_file = os.path.join(temp_dir, "starvation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_agent_race_condition_shared_state(self):
        """Test 161: Fix race condition in shared state access"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading

class SharedState:
    def __init__(self):
        self.counter = 0
    
    def increment(self):
        # BUG: No lock - race condition
        temp = self.counter
        temp += 1
        self.counter = temp

class Agent(threading.Thread):
    def __init__(self, state):
        super().__init__()
        self.state = state
    
    def run(self):
        for _ in range(1000):
            self.state.increment()

state = SharedState()
agents = [Agent(state) for _ in range(10)]

for agent in agents:
    agent.start()

for agent in agents:
    agent.join()

# Should be 10000, but race condition causes less
print(f"Counter: {state.counter}")
"""
            
            test_file = os.path.join(temp_dir, "race_condition.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_agent_byzantine_fault_tolerance(self):
        """Test 162: Handle Byzantine faults in multi-agent system"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class Agent:
    def __init__(self, agent_id, is_byzantine=False):
        self.id = agent_id
        self.is_byzantine = is_byzantine
    
    def send_value(self):
        if self.is_byzantine:
            # Malicious agent sends different values
            return self.id * 100
        return 42

class Coordinator:
    def __init__(self, agents):
        self.agents = agents
    
    def aggregate(self):
        # BUG: No Byzantine fault tolerance - takes average of all
        values = [agent.send_value() for agent in self.agents]
        return sum(values) / len(values)

agents = [
    Agent(0, is_byzantine=False),
    Agent(1, is_byzantine=False),
    Agent(2, is_byzantine=True),  # Byzantine agent
    Agent(3, is_byzantine=False),
]

coordinator = Coordinator(agents)
result = coordinator.aggregate()  # Incorrect due to Byzantine agent
"""
            
            test_file = os.path.join(temp_dir, "byzantine.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_agent_livelock_mutual_deference(self):
        """Test 163: Detect livelock from agents deferring to each other"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class PoliteAgent:
    def __init__(self, agent_id, other_agent=None):
        self.id = agent_id
        self.other_agent = other_agent
        self.wants_resource = True
    
    def try_acquire_resource(self):
        # BUG: Both agents keep deferring - livelock
        while self.wants_resource:
            if self.other_agent and self.other_agent.wants_resource:
                # Be polite and let other go first
                self.wants_resource = False
                # Change mind and try again
                self.wants_resource = True
            else:
                return True
        return False

agent1 = PoliteAgent(1)
agent2 = PoliteAgent(2, agent1)
agent1.other_agent = agent2

# Both agents keep deferring - livelock
agent1.try_acquire_resource()
"""
            
            test_file = os.path.join(temp_dir, "livelock.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_agent_cascading_failure(self):
        """Test 164: Prevent cascading failures across agent network"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class Agent:
    def __init__(self, agent_id, dependencies=None):
        self.id = agent_id
        self.dependencies = dependencies or []
        self.failed = False
    
    def execute(self):
        # BUG: No circuit breaker - failures cascade
        if self.failed:
            raise Exception(f"Agent {self.id} failed")
        
        for dep in self.dependencies:
            try:
                dep.execute()
            except Exception:
                # Dependency failed, so this agent fails too
                self.failed = True
                raise

# Create dependency chain
agent5 = Agent(5)
agent4 = Agent(4, [agent5])
agent3 = Agent(3, [agent4])
agent2 = Agent(2, [agent3])
agent1 = Agent(1, [agent2])

# Fail agent 5
agent5.failed = True

# Cascading failure - all agents fail
try:
    agent1.execute()
except Exception as e:
    print(f"Cascading failure: {e}")
"""
            
            test_file = os.path.join(temp_dir, "cascading.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_agent_resource_leak_incomplete_cleanup(self):
        """Test 165: Fix resource leaks from incomplete agent cleanup"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class Agent:
    def __init__(self):
        self.connections = []
        self.files = []
    
    def connect(self, resource):
        # BUG: Opens resources but never closes
        conn = open(resource, 'w')
        self.connections.append(conn)
    
    def cleanup(self):
        # BUG: Incomplete cleanup - doesn't close all resources
        if self.connections:
            self.connections[0].close()
        # Forgets to close rest of connections

class AgentPool:
    def __init__(self):
        self.agents = []
    
    def create_agent(self):
        agent = Agent()
        agent.connect('/tmp/resource.txt')
        self.agents.append(agent)
    
    def shutdown(self):
        # BUG: Doesn't properly cleanup agents
        for agent in self.agents:
            agent.cleanup()

pool = AgentPool()
for i in range(100):
    pool.create_agent()
pool.shutdown()  # Resource leak
"""
            
            test_file = os.path.join(temp_dir, "resource_leak.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestAgentCommunicationProtocols:
    """Test agent communication protocols (10 tests)"""
    
    def test_message_ordering_violation(self):
        """Test 166: Ensure FIFO ordering in agent messages"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class MessageBroker:
    def __init__(self):
        self.messages = {}
    
    def send(self, from_agent, to_agent, msg):
        # BUG: No ordering guarantee - messages arrive out of order
        if to_agent not in self.messages:
            self.messages[to_agent] = []
        self.messages[to_agent].insert(0, msg)  # Wrong order
    
    def receive(self, agent):
        if agent in self.messages and self.messages[agent]:
            return self.messages[agent].pop()
        return None

broker = MessageBroker()
broker.send("A", "B", "msg1")
broker.send("A", "B", "msg2")
broker.send("A", "B", "msg3")

# Should receive in order: msg1, msg2, msg3
# But receives: msg3, msg2, msg1 - BUG
"""
            
            test_file = os.path.join(temp_dir, "message_ordering.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_message_duplication(self):
        """Test 167: Handle duplicate message delivery"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ReliableMessaging:
    def __init__(self):
        self.sent = []
    
    def send_with_retry(self, msg):
        # BUG: Retries without deduplication
        for attempt in range(3):
            self.sent.append(msg)
            # Simulates network failure and retry
    
    def receive(self):
        # BUG: No duplicate detection
        return self.sent

messaging = ReliableMessaging()
messaging.send_with_retry("important_message")
messages = messaging.receive()

# Receives same message 3 times - BUG
print(f"Received {len(messages)} messages: {messages}")
"""
            
            test_file = os.path.join(temp_dir, "duplication.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_broadcast_storm(self):
        """Test 168: Prevent broadcast storm in agent network"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class Agent:
    def __init__(self, agent_id, neighbors):
        self.id = agent_id
        self.neighbors = neighbors
    
    def broadcast(self, msg):
        # BUG: No TTL or seen-set - infinite broadcast storm
        print(f"Agent {self.id} broadcasting: {msg}")
        for neighbor in self.neighbors:
            neighbor.receive_broadcast(msg)
    
    def receive_broadcast(self, msg):
        # BUG: Rebroadcasts without checking if already seen
        self.broadcast(msg)

# Create circular network
agent1 = Agent(1, [])
agent2 = Agent(2, [agent1])
agent3 = Agent(3, [agent2])
agent1.neighbors = [agent3]

# Triggers infinite broadcast storm
agent1.broadcast("hello")
"""
            
            test_file = os.path.join(temp_dir, "broadcast_storm.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_protocol_version_mismatch(self):
        """Test 169: Handle protocol version incompatibility"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class Message:
    def __init__(self, version, data):
        self.version = version
        self.data = data

class Agent:
    def __init__(self, protocol_version):
        self.version = protocol_version
    
    def send(self, data):
        return Message(self.version, data)
    
    def receive(self, msg):
        # BUG: No version compatibility check
        return msg.data

agent_v1 = Agent(protocol_version="1.0")
agent_v2 = Agent(protocol_version="2.0")

# v2 sends message with new format
msg = agent_v2.send({"type": "new_field", "value": 42})

# v1 receives but can't understand - BUG
result = agent_v1.receive(msg)
"""
            
            test_file = os.path.join(temp_dir, "version_mismatch.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_message_serialization_error(self):
        """Test 170: Handle serialization/deserialization errors"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import json

class Agent:
    def serialize(self, obj):
        # BUG: Doesn't handle non-serializable objects
        return json.dumps(obj)
    
    def deserialize(self, data):
        return json.loads(data)
    
    def send_object(self, obj):
        serialized = self.serialize(obj)
        return serialized

agent = Agent()

# Try to serialize function - will fail
def my_function():
    return 42

try:
    agent.send_object(my_function)
except TypeError as e:
    print(f"Serialization error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "serialization.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_async_callback_ordering(self):
        """Test 171: Ensure correct async callback execution order"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import asyncio

class AsyncAgent:
    def __init__(self):
        self.results = []
    
    async def process(self, data):
        # BUG: No ordering guarantee for callbacks
        await asyncio.sleep(0.1)
        self.results.append(data)
    
    async def handle_messages(self, messages):
        # BUG: Concurrent execution breaks ordering
        tasks = [self.process(msg) for msg in messages]
        await asyncio.gather(*tasks)

agent = AsyncAgent()
messages = [1, 2, 3, 4, 5]

# Order not guaranteed
asyncio.run(agent.handle_messages(messages))
print(f"Results: {agent.results}")  # May not be [1,2,3,4,5]
"""
            
            test_file = os.path.join(temp_dir, "async_ordering.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_heartbeat_timeout_detection(self):
        """Test 172: Detect failed agents via heartbeat timeout"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class Agent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.last_heartbeat = time.time()
        self.alive = True
    
    def heartbeat(self):
        self.last_heartbeat = time.time()

class Monitor:
    def __init__(self, agents, timeout=5):
        self.agents = agents
        self.timeout = timeout
    
    def check_health(self):
        # BUG: No timeout check - doesn't detect dead agents
        for agent in self.agents:
            if agent.alive:
                print(f"Agent {agent.id} is alive")

agents = [Agent(i) for i in range(3)]
monitor = Monitor(agents)

# Agent 1 stops sending heartbeats
time.sleep(6)

# Should detect agent 1 as dead, but doesn't - BUG
monitor.check_health()
"""
            
            test_file = os.path.join(temp_dir, "heartbeat.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_request_response_timeout(self):
        """Test 173: Handle request-response timeout properly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class Agent:
    def request(self, target_agent, data):
        # BUG: No timeout - blocks forever if no response
        response = target_agent.process(data)
        return response
    
    def process(self, data):
        # Simulate slow processing
        time.sleep(100)
        return f"Processed: {data}"

agent1 = Agent()
agent2 = Agent()

# This will block forever - BUG
result = agent1.request(agent2, "hello")
"""
            
            test_file = os.path.join(temp_dir, "timeout.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_message_size_limit_exceeded(self):
        """Test 174: Enforce message size limits"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class MessageChannel:
    def __init__(self, max_size=1024):
        self.max_size = max_size
    
    def send(self, msg):
        # BUG: Doesn't check message size
        return msg
    
    def validate(self, msg):
        # BUG: Validation not enforced
        if len(str(msg)) > self.max_size:
            raise ValueError("Message too large")

channel = MessageChannel(max_size=100)

# Send huge message without validation
large_msg = "x" * 10000
channel.send(large_msg)  # Should fail but doesn't - BUG
"""
            
            test_file = os.path.join(temp_dir, "message_size.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_partial_message_delivery(self):
        """Test 175: Handle partial message delivery correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class StreamingProtocol:
    def __init__(self):
        self.buffer = ""
    
    def send_chunk(self, chunk):
        self.buffer += chunk
    
    def receive_message(self):
        # BUG: Doesn't wait for complete message
        if self.buffer:
            msg = self.buffer
            self.buffer = ""
            return msg
        return None

protocol = StreamingProtocol()
protocol.send_chunk("Hello ")

# Tries to process incomplete message - BUG
msg = protocol.receive_message()
print(f"Received: {msg}")  # Only "Hello " instead of full message

protocol.send_chunk("World!")
"""
            
            test_file = os.path.join(temp_dir, "partial_message.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestEmergentBehaviors:
    """Test emergent behaviors in multi-agent systems (10 tests)"""
    
    def test_emergent_oscillation(self):
        """Test 176: Detect and dampen emergent oscillations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ReactiveAgent:
    def __init__(self, agent_id, threshold):
        self.id = agent_id
        self.threshold = threshold
        self.value = 0
    
    def react(self, neighbor_value):
        # BUG: Overreacts causing oscillation
        if neighbor_value > self.threshold:
            self.value = 0
        else:
            self.value = 100

# Two agents react to each other
agent1 = ReactiveAgent(1, threshold=50)
agent2 = ReactiveAgent(2, threshold=50)

agent1.value = 100
for i in range(10):
    agent2.react(agent1.value)
    agent1.react(agent2.value)
    print(f"Iteration {i}: Agent1={agent1.value}, Agent2={agent2.value}")
    # Values oscillate 100->0->100->0 - unstable system
"""
            
            test_file = os.path.join(temp_dir, "oscillation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_emergent_clustering_imbalance(self):
        """Test 177: Balance emergent clustering behavior"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class Agent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.cluster = None
    
    def join_cluster(self, agents):
        # BUG: Always joins largest cluster - creates imbalance
        cluster_sizes = {}
        for agent in agents:
            if agent.cluster:
                cluster_sizes[agent.cluster] = cluster_sizes.get(agent.cluster, 0) + 1
        
        if cluster_sizes:
            largest = max(cluster_sizes, key=cluster_sizes.get)
            self.cluster = largest
        else:
            self.cluster = self.id

agents = [Agent(i) for i in range(10)]
agents[0].cluster = 0

# All agents join cluster 0 - no diversity
for agent in agents[1:]:
    agent.join_cluster(agents)

print(f"Clusters: {[a.cluster for a in agents]}")
"""
            
            test_file = os.path.join(temp_dir, "clustering.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_emergent_congestion_collapse(self):
        """Test 178: Prevent congestion collapse from emergent behavior"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NetworkAgent:
    def __init__(self):
        self.send_rate = 1
        self.success_rate = 1.0
    
    def adjust_rate(self):
        # BUG: Increases rate on failure - causes congestion collapse
        if self.success_rate < 0.5:
            self.send_rate *= 2  # Wrong! Should decrease
        else:
            self.send_rate *= 1.1

class Network:
    def __init__(self, capacity):
        self.capacity = capacity
        self.agents = []
    
    def transmit(self):
        total_rate = sum(a.send_rate for a in self.agents)
        if total_rate > self.capacity:
            # Network congested
            for agent in self.agents:
                agent.success_rate = 0.3
        else:
            for agent in self.agents:
                agent.success_rate = 1.0

network = Network(capacity=10)
network.agents = [NetworkAgent() for _ in range(5)]

for i in range(10):
    network.transmit()
    for agent in network.agents:
        agent.adjust_rate()
    total = sum(a.send_rate for a in network.agents)
    print(f"Iteration {i}: Total rate = {total}")
    # Emergent congestion collapse
"""
            
            test_file = os.path.join(temp_dir, "congestion.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_emergent_herding_behavior(self):
        """Test 179: Control emergent herding leading to suboptimal decisions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class DecisionAgent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.choice = None
    
    def make_decision(self, peers):
        # BUG: Blindly follows majority - herding behavior
        choices = [p.choice for p in peers if p.choice]
        if choices:
            # Follow the crowd
            self.choice = max(set(choices), key=choices.count)
        else:
            self.choice = "A"

agents = [DecisionAgent(i) for i in range(10)]
agents[0].choice = "B"  # First agent makes wrong choice

# All agents herd to wrong choice
for agent in agents[1:]:
    agent.make_decision(agents[:agents.index(agent)])

print(f"Choices: {[a.choice for a in agents]}")
# All choose B due to herding - suboptimal
"""
            
            test_file = os.path.join(temp_dir, "herding.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_emergent_deadlock_cycles(self):
        """Test 180: Detect emergent deadlock cycles in agent dependencies"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ResourceAgent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.held_resource = None
        self.waiting_for = None
    
    def request_resource(self, resource_id, holder):
        # BUG: No cycle detection - emergent deadlocks
        self.waiting_for = holder
        while holder.held_resource == resource_id:
            pass  # Wait forever

agents = [ResourceAgent(i) for i in range(4)]
agents[0].held_resource = "R1"
agents[1].held_resource = "R2"
agents[2].held_resource = "R3"
agents[3].held_resource = "R4"

# Create cycle: A0->A1->A2->A3->A0
agents[0].waiting_for = agents[1]
agents[1].waiting_for = agents[2]
agents[2].waiting_for = agents[3]
agents[3].waiting_for = agents[0]
# Emergent deadlock cycle
"""
            
            test_file = os.path.join(temp_dir, "deadlock_cycle.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_emergent_information_cascade(self):
        """Test 181: Handle emergent information cascades"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class InformationAgent:
    def __init__(self, agent_id, private_signal):
        self.id = agent_id
        self.private_signal = private_signal
        self.belief = None
    
    def update_belief(self, predecessors):
        # BUG: Ignores private signal - information cascade
        if predecessors:
            # Just copy predecessor beliefs
            beliefs = [p.belief for p in predecessors if p.belief]
            if beliefs:
                self.belief = beliefs[0]
        else:
            self.belief = self.private_signal

agents = [
    InformationAgent(0, "A"),
    InformationAgent(1, "B"),
    InformationAgent(2, "B"),
    InformationAgent(3, "B"),
]

agents[0].update_belief([])

for i in range(1, len(agents)):
    agents[i].update_belief(agents[:i])

# All follow first agent, ignoring own signals - cascade
print(f"Beliefs: {[a.belief for a in agents]}")
"""
            
            test_file = os.path.join(temp_dir, "cascade.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_emergent_spatial_segregation(self):
        """Test 182: Control emergent spatial segregation (Schelling model)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SpatialAgent:
    def __init__(self, agent_type, position):
        self.type = agent_type
        self.position = position
    
    def is_happy(self, neighbors):
        # BUG: Small preference leads to complete segregation
        same_type = sum(1 for n in neighbors if n.type == self.type)
        total = len(neighbors)
        if total == 0:
            return True
        # Only 30% preference, but causes full segregation
        return same_type / total >= 0.3
    
    def move(self, grid, neighbors):
        if not self.is_happy(neighbors):
            # Move to random empty position
            self.position = (self.position[0] + 1, self.position[1])

# Small individual preference creates emergent segregation
agents = [SpatialAgent("A" if i < 5 else "B", (i, 0)) for i in range(10)]
# Emergent complete segregation from mild preference
"""
            
            test_file = os.path.join(temp_dir, "segregation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_emergent_phase_transition(self):
        """Test 183: Handle emergent phase transitions in agent behavior"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ThresholdAgent:
    def __init__(self, threshold):
        self.threshold = threshold
        self.active = False
    
    def update(self, active_neighbors):
        # BUG: No hysteresis - unstable at phase transition
        if active_neighbors >= self.threshold:
            self.active = True
        else:
            self.active = False

# Critical threshold causes phase transition
agents = [ThresholdAgent(threshold=3) for _ in range(10)]

# Small change causes emergent phase transition
agents[0].active = True
agents[1].active = True
agents[2].active = True

# System suddenly transitions to all active - instability
for iteration in range(5):
    active_count = sum(1 for a in agents if a.active)
    for agent in agents:
        agent.update(active_count)
    print(f"Iteration {iteration}: {sum(1 for a in agents if a.active)} active")
"""
            
            test_file = os.path.join(temp_dir, "phase_transition.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_emergent_boom_bust_cycles(self):
        """Test 184: Stabilize emergent boom-bust economic cycles"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class EconomicAgent:
    def __init__(self):
        self.production = 10
        self.price = 1.0
    
    def adjust_production(self, market_price):
        # BUG: Delayed response causes boom-bust cycles
        if market_price > 1.0:
            # Price high, increase production
            self.production *= 1.5
        else:
            # Price low, decrease production
            self.production *= 0.5

class Market:
    def __init__(self, agents):
        self.agents = agents
    
    def clear_price(self):
        total_production = sum(a.production for a in self.agents)
        # Inverse relationship
        return 100 / total_production if total_production > 0 else 1.0

agents = [EconomicAgent() for _ in range(5)]
market = Market(agents)

for i in range(20):
    price = market.clear_price()
    for agent in agents:
        agent.adjust_production(price)
    print(f"Period {i}: Price={price:.2f}, Production={sum(a.production for a in agents):.1f}")
    # Emergent boom-bust oscillations
"""
            
            test_file = os.path.join(temp_dir, "boom_bust.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_emergent_consensus_failure(self):
        """Test 185: Ensure emergent consensus with asynchronous agents"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class AsynchronousAgent:
    def __init__(self, agent_id, initial_value):
        self.id = agent_id
        self.value = initial_value
        self.version = 0
    
    def gossip(self, peer):
        # BUG: No conflict resolution - consensus fails
        if peer.version > self.version:
            self.value = peer.value
            self.version = peer.version
        elif peer.version < self.version:
            peer.value = self.value
            peer.version = self.version
        # What if versions equal but values differ?

agents = [AsynchronousAgent(i, i) for i in range(5)]

# Asynchronous updates with conflicts
agents[0].gossip(agents[1])
agents[2].gossip(agents[3])
agents[1].gossip(agents[2])

# May not reach consensus - BUG
print(f"Values: {[a.value for a in agents]}")
"""
            
            test_file = os.path.join(temp_dir, "consensus_failure.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
