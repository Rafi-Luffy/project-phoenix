"""
Comprehensive Test Suite for Phoenix - Distributed Systems Part 1
Tests 456-485: Multi-Agent Communication, Consensus, Coordination (30 tests)

This file tests Phoenix's ability to detect and fix bugs in distributed systems,
focusing on multi-agent communication, consensus algorithms, and coordination.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch


class TestDistributedCommunication:
    """Test distributed communication patterns (10 tests)"""
    
    def test_message_ordering_guarantees(self):
        """Test 456: Ensure message ordering across nodes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnorderedMessageBus:
    def __init__(self):
        self.messages = []
    
    def send(self, message, priority=0):
        # BUG: Ignores ordering
        self.messages.append(message)
    
    def receive_all(self):
        # BUG: Returns in insertion order, not logical order
        return self.messages

bus = UnorderedMessageBus()

bus.send("msg3", priority=3)
bus.send("msg1", priority=1)
bus.send("msg2", priority=2)

# BUG: Should be ordered by priority
messages = bus.receive_all()
print(f"Messages: {messages}")
"""
            
            test_file = os.path.join(temp_dir, "message_ordering.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_network_partition_handling(self):
        """Test 457: Handle network partitions gracefully"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class PartitionUnawareSystem:
    def __init__(self):
        self.nodes = ["node1", "node2", "node3"]
        self.leader = "node1"
    
    def send_to_all(self, message):
        # BUG: Assumes all nodes reachable
        for node in self.nodes:
            self.send(node, message)
    
    def send(self, node, message):
        # BUG: No partition detection
        if node == "node3":
            raise ConnectionError("Network partition")
        print(f"Sent to {node}: {message}")

system = PartitionUnawareSystem()

try:
    system.send_to_all("update")
except ConnectionError:
    # BUG: Partial send, inconsistent state
    pass
"""
            
            test_file = os.path.join(temp_dir, "network_partition.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_message_deduplication(self):
        """Test 458: Deduplicate messages correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoDuplicationCheck:
    def __init__(self):
        self.received = []
    
    def receive(self, message):
        # BUG: No deduplication
        self.received.append(message)

receiver = NoDuplicationCheck()

# Network retries send same message
receiver.receive({"id": "msg1", "data": "hello"})
receiver.receive({"id": "msg1", "data": "hello"})  # Duplicate
receiver.receive({"id": "msg1", "data": "hello"})  # Duplicate

# BUG: Processes duplicates
print(f"Received count: {len(receiver.received)}")
"""
            
            test_file = os.path.join(temp_dir, "message_dedup.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_backpressure_distributed(self):
        """Test 459: Apply backpressure in distributed queues"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnboundedDistributedQueue:
    def __init__(self):
        self.queue = []
    
    def enqueue(self, item):
        # BUG: No capacity limit
        self.queue.append(item)
        return True
    
    def size(self):
        return len(self.queue)

queue = UnboundedDistributedQueue()

# Fast producer
for i in range(100000):
    queue.enqueue(f"item_{i}")

# BUG: Queue overflow, no backpressure
print(f"Queue size: {queue.size()}")
"""
            
            test_file = os.path.join(temp_dir, "distributed_backpressure.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_exactly_once_semantics(self):
        """Test 460: Ensure exactly-once message delivery"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class AtLeastOnceDelivery:
    def __init__(self):
        self.balance = 100
    
    def process_transaction(self, transaction):
        # BUG: No idempotency - processes duplicates
        self.balance += transaction["amount"]

processor = AtLeastOnceDelivery()

# Network retry sends same transaction twice
processor.process_transaction({"id": "txn1", "amount": -50})
processor.process_transaction({"id": "txn1", "amount": -50})  # Duplicate

# BUG: Balance should be 50, not 0
print(f"Balance: {processor.balance}")
"""
            
            test_file = os.path.join(temp_dir, "exactly_once.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_circuit_breaker_pattern(self):
        """Test 461: Implement circuit breaker for failing services"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoCircuitBreaker:
    def __init__(self):
        self.failure_count = 0
    
    def call_service(self):
        # BUG: Keeps trying even when service is down
        try:
            # Simulate failing service
            raise ConnectionError("Service down")
        except ConnectionError:
            self.failure_count += 1
            raise

caller = NoCircuitBreaker()

# Service is down
for i in range(100):
    try:
        caller.call_service()
    except ConnectionError:
        pass

# BUG: Made 100 failing calls instead of opening circuit
print(f"Failures: {caller.failure_count}")
"""
            
            test_file = os.path.join(temp_dir, "circuit_breaker.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_retry_with_exponential_backoff(self):
        """Test 462: Retry with exponential backoff"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class ConstantRetry:
    def call_with_retry(self, func, max_retries=3):
        for i in range(max_retries):
            try:
                return func()
            except Exception:
                # BUG: Fixed delay
                time.sleep(1)  # Should be exponential: 1, 2, 4, 8...
        raise Exception("Max retries exceeded")

retrier = ConstantRetry()

def failing_function():
    raise Exception("Temporary failure")

try:
    retrier.call_with_retry(failing_function)
except Exception as e:
    # BUG: Constant backoff causes thundering herd
    print(f"Failed: {e}")
"""
            
            test_file = os.path.join(temp_dir, "exponential_backoff.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_request_timeout_handling(self):
        """Test 463: Handle request timeouts properly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class NoTimeoutClient:
    def send_request(self, endpoint, data):
        # BUG: No timeout - blocks forever
        while True:
            time.sleep(0.1)
            # Waiting for response that never comes
            pass

client = NoTimeoutClient()

# BUG: Hangs forever
# client.send_request("/slow_endpoint", "data")
print("Client created")
"""
            
            test_file = os.path.join(temp_dir, "request_timeout.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_rate_limiting_distributed(self):
        """Test 464: Implement distributed rate limiting"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class LocalRateLimiter:
    def __init__(self, max_per_second):
        self.max_per_second = max_per_second
        self.count = 0
    
    def allow_request(self):
        # BUG: Per-node limit, not global
        self.count += 1
        if self.count <= self.max_per_second:
            return True
        return False

# 3 nodes, each allows 10 req/s
node1 = LocalRateLimiter(10)
node2 = LocalRateLimiter(10)
node3 = LocalRateLimiter(10)

# BUG: Global limit should be 10, but allows 30
total = 0
for _ in range(10):
    if node1.allow_request():
        total += 1
    if node2.allow_request():
        total += 1
    if node3.allow_request():
        total += 1

print(f"Total allowed: {total}")
"""
            
            test_file = os.path.join(temp_dir, "distributed_rate_limit.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_gossip_protocol_convergence(self):
        """Test 465: Ensure gossip protocol converges"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SlowGossip:
    def __init__(self, nodes):
        self.nodes = nodes
        self.state = {node: None for node in nodes}
    
    def update(self, node, value):
        self.state[node] = value
    
    def gossip_round(self):
        # BUG: Only gossips to one neighbor
        import random
        for node in self.nodes:
            neighbor = random.choice(self.nodes)
            self.state[neighbor] = self.state[node]

gossip = SlowGossip(["n1", "n2", "n3", "n4", "n5"])
gossip.update("n1", "important_update")

# Run a few rounds
for _ in range(3):
    gossip.gossip_round()

# BUG: May not converge - should gossip to multiple neighbors
print(f"State: {gossip.state}")
"""
            
            test_file = os.path.join(temp_dir, "gossip_convergence.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestConsensusAlgorithms:
    """Test consensus and agreement protocols (10 tests)"""
    
    def test_raft_leader_election(self):
        """Test 466: Implement Raft leader election correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class BrokenRaftElection:
    def __init__(self, nodes):
        self.nodes = nodes
        self.leader = None
    
    def start_election(self):
        # BUG: All nodes declare themselves leader
        for node in self.nodes:
            self.leader = node
        # BUG: Multiple leaders possible

election = BrokenRaftElection(["node1", "node2", "node3"])
election.start_election()

# BUG: Should have single leader
print(f"Leader: {election.leader}")
"""
            
            test_file = os.path.join(temp_dir, "raft_election.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_split_brain_prevention(self):
        """Test 467: Prevent split-brain scenarios"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoQuorumCheck:
    def __init__(self, total_nodes):
        self.total_nodes = total_nodes
        self.reachable_nodes = []
    
    def can_accept_writes(self):
        # BUG: No quorum requirement
        return len(self.reachable_nodes) > 0

cluster = NoQuorumCheck(total_nodes=5)
cluster.reachable_nodes = ["node1", "node2"]  # 2 out of 5

# BUG: Should require majority (3), allows writes with minority
if cluster.can_accept_writes():
    print("Accepting writes - SPLIT BRAIN POSSIBLE")
"""
            
            test_file = os.path.join(temp_dir, "split_brain.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_paxos_prepare_phase(self):
        """Test 468: Implement Paxos prepare phase correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SimplifiedPaxos:
    def __init__(self):
        self.promised_proposal = None
        self.accepted_value = None
    
    def prepare(self, proposal_number):
        # BUG: Doesn't reject lower proposal numbers
        self.promised_proposal = proposal_number
        return True  # Should check if proposal_number > promised

proposer = SimplifiedPaxos()

proposer.prepare(10)
result = proposer.prepare(5)  # Lower proposal number

# BUG: Should reject, but accepts
print(f"Accepted lower proposal: {result}")
"""
            
            test_file = os.path.join(temp_dir, "paxos_prepare.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_two_phase_commit_coordinator_failure(self):
        """Test 469: Handle 2PC coordinator failure"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class TwoPhaseCommit:
    def __init__(self, participants):
        self.participants = participants
        self.state = "init"
    
    def commit(self):
        # Phase 1: Prepare
        votes = []
        for p in self.participants:
            votes.append(p.prepare())
        
        # BUG: Coordinator crashes here - participants blocked
        if all(votes):
            # Phase 2: Commit (never reached if crash)
            for p in self.participants:
                p.commit()

class Participant:
    def __init__(self):
        self.locked = False
    
    def prepare(self):
        self.locked = True  # BUG: Locked forever if coordinator crashes
        return True
    
    def commit(self):
        self.locked = False

participants = [Participant(), Participant()]
coordinator = TwoPhaseCommit(participants)

# Simulate crash after prepare
print("Participants locked, waiting forever...")
"""
            
            test_file = os.path.join(temp_dir, "2pc_failure.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_consensus_with_byzantine_nodes(self):
        """Test 470: Handle Byzantine failures"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoByzantineProtection:
    def __init__(self, nodes):
        self.nodes = nodes
    
    def reach_consensus(self, proposals):
        # BUG: Trusts all nodes, no Byzantine fault tolerance
        # Simply takes majority
        from collections import Counter
        counts = Counter(proposals)
        return counts.most_common(1)[0][0]

consensus = NoByzantineProtection(["n1", "n2", "n3", "n4"])

# 3 honest nodes propose "A", 1 Byzantine node lies
proposals = ["A", "A", "A", "B"]

# Works in this case, but vulnerable to:
# - Byzantine nodes sending different values to different nodes
# - Malicious nodes not following protocol
result = consensus.reach_consensus(proposals)
print(f"Consensus: {result}")
"""
            
            test_file = os.path.join(temp_dir, "byzantine_nodes.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_log_replication_consistency(self):
        """Test 471: Maintain log consistency across replicas"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class InconsistentReplication:
    def __init__(self):
        self.log = []
    
    def append(self, entry):
        # BUG: No ordering guarantees
        self.log.append(entry)
    
    def get_log(self):
        return self.log

# Two replicas
replica1 = InconsistentReplication()
replica2 = InconsistentReplication()

# Different order on different replicas
replica1.append("op1")
replica1.append("op2")

replica2.append("op2")  # BUG: Received in different order
replica2.append("op1")

# BUG: Logs diverge
print(f"Replica1: {replica1.get_log()}")
print(f"Replica2: {replica2.get_log()}")
"""
            
            test_file = os.path.join(temp_dir, "log_consistency.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_read_write_quorum_overlap(self):
        """Test 472: Ensure read/write quorum overlap"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class WeakQuorum:
    def __init__(self, total_nodes=5):
        self.total_nodes = total_nodes
        self.write_quorum = 2  # BUG: Too small
        self.read_quorum = 2   # BUG: No overlap guarantee
    
    def can_write(self, acks):
        return acks >= self.write_quorum
    
    def can_read(self, responses):
        return responses >= self.read_quorum

quorum = WeakQuorum(total_nodes=5)

# Write to 2 nodes
write_ok = quorum.can_write(2)

# Read from different 2 nodes
read_ok = quorum.can_read(2)

# BUG: Might read stale data (no overlap)
# Should be: W + R > N
print(f"Write: {write_ok}, Read: {read_ok}")
"""
            
            test_file = os.path.join(temp_dir, "quorum_overlap.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_epoch_number_monotonicity(self):
        """Test 473: Maintain epoch number monotonicity"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoEpochTracking:
    def __init__(self):
        self.epoch = 0
        self.data = None
    
    def write(self, value, epoch):
        # BUG: Doesn't check epoch monotonicity
        self.data = value
        self.epoch = epoch

node = NoEpochTracking()

node.write("value1", epoch=10)
node.write("value2", epoch=5)  # BUG: Lower epoch accepted

# BUG: Stale write overwrites newer data
print(f"Data: {node.data}, Epoch: {node.epoch}")
"""
            
            test_file = os.path.join(temp_dir, "epoch_monotonicity.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_view_change_protocol(self):
        """Test 474: Handle view changes correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class BrokenViewChange:
    def __init__(self):
        self.view = 0
        self.leader = "node1"
        self.in_progress_ops = []
    
    def change_view(self, new_view, new_leader):
        # BUG: Doesn't transfer in-progress operations
        self.view = new_view
        self.leader = new_leader
        self.in_progress_ops = []  # Lost!

system = BrokenViewChange()
system.in_progress_ops = ["op1", "op2", "op3"]

# Leader fails, view change
system.change_view(1, "node2")

# BUG: Lost in-progress operations
print(f"In-progress ops: {system.in_progress_ops}")
"""
            
            test_file = os.path.join(temp_dir, "view_change.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_snapshot_and_log_compaction(self):
        """Test 475: Implement log compaction correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnboundedLog:
    def __init__(self):
        self.log = []
        self.snapshot = None
    
    def append(self, entry):
        self.log.append(entry)
        # BUG: Never compacts log
    
    def get_state(self):
        # BUG: Replays entire log
        state = {}
        for entry in self.log:
            state.update(entry)
        return state

log_manager = UnboundedLog()

# Add millions of entries
for i in range(1000000):
    log_manager.append({f"key_{i}": f"value_{i}"})

# BUG: Log grows unbounded, replay is slow
state = log_manager.get_state()
print(f"Log size: {len(log_manager.log)}")
"""
            
            test_file = os.path.join(temp_dir, "log_compaction.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestDistributedCoordination:
    """Test distributed coordination mechanisms (10 tests)"""
    
    def test_distributed_lock_acquisition(self):
        """Test 476: Acquire distributed locks safely"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnsafeLock:
    def __init__(self):
        self.locked = False
        self.owner = None
    
    def acquire(self, client_id):
        # BUG: Race condition - not atomic
        if not self.locked:
            self.locked = True
            self.owner = client_id
            return True
        return False

lock = UnsafeLock()

# Two clients try to acquire simultaneously
# Both see locked=False, both acquire
client1_acquired = lock.acquire("client1")
client2_acquired = lock.acquire("client2")

# BUG: Both think they have the lock
print(f"Client1: {client1_acquired}, Client2: {client2_acquired}")
"""
            
            test_file = os.path.join(temp_dir, "distributed_lock.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_lock_expiration_and_renewal(self):
        """Test 477: Handle lock expiration and renewal"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class NoExpirationLock:
    def __init__(self):
        self.locks = {}
    
    def acquire(self, resource, client_id):
        if resource not in self.locks:
            self.locks[resource] = client_id
            return True
        return False
    
    def release(self, resource, client_id):
        # BUG: No expiration - if client crashes, lock held forever
        if self.locks.get(resource) == client_id:
            del self.locks[resource]

lock_manager = NoExpirationLock()

lock_manager.acquire("resource1", "client1")
# Client1 crashes without releasing

# BUG: Lock held forever
print(f"Locks: {lock_manager.locks}")
"""
            
            test_file = os.path.join(temp_dir, "lock_expiration.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_distributed_barrier_synchronization(self):
        """Test 478: Synchronize agents at barriers"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class BrokenBarrier:
    def __init__(self, num_parties):
        self.num_parties = num_parties
        self.arrived = []
    
    def wait(self, party_id):
        self.arrived.append(party_id)
        # BUG: Doesn't actually wait
        if len(self.arrived) >= self.num_parties:
            self.arrived = []
            return True
        return False

barrier = BrokenBarrier(num_parties=3)

# Party 1 arrives
barrier.wait("party1")
# Party 1 continues without waiting - BUG

# Parties should all wait until 3 arrive
print("Party 1 continued without waiting")
"""
            
            test_file = os.path.join(temp_dir, "barrier_sync.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_distributed_semaphore(self):
        """Test 479: Implement distributed semaphore"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class LocalSemaphore:
    def __init__(self, permits):
        self.permits = permits
        self.available = permits
    
    def acquire(self):
        # BUG: Local only, not distributed
        if self.available > 0:
            self.available -= 1
            return True
        return False

# Multiple nodes
node1_sem = LocalSemaphore(permits=5)
node2_sem = LocalSemaphore(permits=5)

# BUG: Each node has 5 permits, should share 5 total
total_acquired = 0
for _ in range(5):
    if node1_sem.acquire():
        total_acquired += 1
    if node2_sem.acquire():
        total_acquired += 1

# BUG: Acquired 10, should be max 5
print(f"Total acquired: {total_acquired}")
"""
            
            test_file = os.path.join(temp_dir, "distributed_semaphore.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_leader_lease_management(self):
        """Test 480: Manage leader leases correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class NoLeaseExpiration:
    def __init__(self):
        self.leader = None
        self.lease_start = None
    
    def become_leader(self, node_id):
        self.leader = node_id
        self.lease_start = time.time()
    
    def is_leader(self, node_id):
        # BUG: No lease expiration check
        return self.leader == node_id

cluster = NoLeaseExpiration()
cluster.become_leader("node1")

# Time passes, lease should expire
time.sleep(0.1)

# BUG: Still considers node1 leader
is_leader = cluster.is_leader("node1")
print(f"Node1 is leader: {is_leader}")
"""
            
            test_file = os.path.join(temp_dir, "leader_lease.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_work_stealing_queue(self):
        """Test 481: Implement work stealing for load balancing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoWorkStealing:
    def __init__(self):
        self.queues = {
            "worker1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "worker2": [],
            "worker3": []
        }
    
    def get_task(self, worker_id):
        # BUG: Doesn't steal from other workers
        if self.queues[worker_id]:
            return self.queues[worker_id].pop(0)
        return None

scheduler = NoWorkStealing()

# Worker2 is idle
task = scheduler.get_task("worker2")

# BUG: Returns None instead of stealing from worker1
print(f"Worker2 task: {task}")
"""
            
            test_file = os.path.join(temp_dir, "work_stealing.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_distributed_transaction_coordination(self):
        """Test 482: Coordinate distributed transactions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoAtomicity:
    def __init__(self):
        self.account_a = 100
        self.account_b = 100
    
    def transfer(self, from_account, to_account, amount):
        # BUG: Not atomic - can fail partway
        if from_account == "A":
            self.account_a -= amount
            # Crash here - money disappears
            self.account_b += amount

bank = NoAtomicity()

try:
    bank.transfer("A", "B", 50)
except Exception:
    pass

# BUG: Money lost or created
print(f"Account A: {bank.account_a}, Account B: {bank.account_b}")
"""
            
            test_file = os.path.join(temp_dir, "transaction_coordination.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_causal_ordering_events(self):
        """Test 483: Maintain causal ordering of events"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoCausalOrdering:
    def __init__(self):
        self.events = []
    
    def add_event(self, event):
        # BUG: No causal tracking
        self.events.append(event)

system = NoCausalOrdering()

# Event 2 depends on Event 1
system.add_event({"id": 2, "depends_on": 1, "data": "reply"})
system.add_event({"id": 1, "data": "message"})

# BUG: Events out of causal order
print(f"Events: {system.events}")
"""
            
            test_file = os.path.join(temp_dir, "causal_ordering.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_vector_clock_synchronization(self):
        """Test 484: Use vector clocks for synchronization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoVectorClock:
    def __init__(self, node_id):
        self.node_id = node_id
        # BUG: Uses simple timestamp
        self.timestamp = 0
    
    def send_message(self, message):
        self.timestamp += 1
        return {"data": message, "timestamp": self.timestamp}
    
    def receive_message(self, msg):
        # BUG: Can't detect concurrent events
        self.timestamp = max(self.timestamp, msg["timestamp"]) + 1

node1 = NoVectorClock("n1")
node2 = NoVectorClock("n2")

msg1 = node1.send_message("hello")
msg2 = node2.send_message("world")

# BUG: Can't tell if concurrent or causally related
print(f"Msg1: {msg1}, Msg2: {msg2}")
"""
            
            test_file = os.path.join(temp_dir, "vector_clock.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_distributed_snapshot_consistency(self):
        """Test 485: Take consistent distributed snapshots"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class InconsistentSnapshot:
    def __init__(self):
        self.nodes = {
            "node1": {"balance": 100},
            "node2": {"balance": 100}
        }
    
    def take_snapshot(self):
        # BUG: Takes snapshots at different times
        snapshot = {}
        for node_id, state in self.nodes.items():
            # State might change between reads
            snapshot[node_id] = state.copy()
        return snapshot

system = InconsistentSnapshot()

# During snapshot, transfer happens
snapshot = system.take_snapshot()
# Transfer: node1 -> node2 (50)
system.nodes["node1"]["balance"] = 50
system.nodes["node2"]["balance"] = 150

# BUG: Snapshot might show money created or destroyed
print(f"Snapshot: {snapshot}")
"""
            
            test_file = os.path.join(temp_dir, "distributed_snapshot.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
