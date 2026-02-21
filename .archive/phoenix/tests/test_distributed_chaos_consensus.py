"""
Distributed System Chaos Testing: Multi-Component Failure Coordination

Most complex scenarios involving:
- Consensus failure recovery
- Two-phase commit failures with rollback
- Distributed lock failures
- State consistency violations and repair
- Multi-region failover with data reconciliation
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set, Tuple
from unittest.mock import Mock, AsyncMock, patch
import random
from enum import Enum
from collections import defaultdict


# ==================== CONSENSUS & CONSISTENCY ====================

class TestDistributedConsensusFailures:
    """Test consensus and consistency recovery"""
    
    @pytest.mark.asyncio
    async def test_leader_election_with_multiple_failures(self):
        """
        Scenario: Leader fails, new leaders proposed but split-brain
        Expected: System converges on single leader after multiple rounds
        """
        
        class ConsensusNode:
            def __init__(self, node_id: str, total_nodes: int):
                self.node_id = node_id
                self.total_nodes = total_nodes
                self.current_leader = None
                self.voted_for = None
                self.term = 0
                self.peers = set()
                self.state = "follower"  # follower, candidate, leader
                self.election_rounds = 0
                self.votes_received = 0
                self.is_alive = True
            
            def add_peer(self, peer_id: str):
                self.peers.add(peer_id)
            
            def kill_node(self):
                """Simulate node failure"""
                self.is_alive = False
            
            def revive_node(self):
                """Recover from failure"""
                self.is_alive = True
            
            async def request_vote(self) -> bool:
                """Request votes from peers"""
                if not self.is_alive:
                    return False
                
                self.election_rounds += 1
                
                # Get votes from peers
                votes_available = len([p for p in self.peers if p != self.node_id])
                votes_needed = (self.total_nodes // 2) + 1
                
                # Simulate vote collection
                self.votes_received = min(votes_available, votes_needed - 1)
                
                return self.votes_received >= votes_needed - 1
            
            async def become_leader(self):
                """Become leader if won election"""
                if self.votes_received >= (self.total_nodes // 2):
                    self.state = "leader"
                    self.current_leader = self.node_id
                    return True
                
                self.state = "follower"
                return False
            
            async def heartbeat(self) -> bool:
                """Send heartbeat to maintain leadership"""
                if self.state != "leader" or not self.is_alive:
                    return False
                
                return True
        
        # Create 5-node cluster
        nodes = {
            f"node-{i}": ConsensusNode(f"node-{i}", 5)
            for i in range(1, 6)
        }
        
        # Connect peers
        for node_id, node in nodes.items():
            for other_id in nodes:
                if other_id != node_id:
                    node.add_peer(other_id)
        
        # Initial election
        for node in nodes.values():
            await node.request_vote()
            await node.become_leader()
        
        # One node becomes leader
        leaders = [n for n in nodes.values() if n.state == "leader"]
        assert len(leaders) == 1
        initial_leader = leaders[0].node_id
        
        # Kill leader
        nodes[initial_leader].kill_node()
        
        # New election round
        for node in nodes.values():
            if node.is_alive:
                await node.request_vote()
                await node.become_leader()
        
        # Check convergence
        leaders = [n for n in nodes.values() if n.state == "leader" and n.is_alive]
        assert len(leaders) == 1
        assert leaders[0].node_id != initial_leader
        
        # Revive old leader (now follower)
        nodes[initial_leader].revive_node()
        
        # Old leader should recognize new leader through heartbeats
        assert nodes[initial_leader].state == "follower"
    
    @pytest.mark.asyncio
    async def test_split_brain_detection_and_resolution(self):
        """
        Scenario: Network partition creates two leaders
        Expected: Detect split, preserve data on majority, heal on reconnect
        """
        
        class SplitBrainDetector:
            def __init__(self):
                self.leaders = set()
                self.term = 0
                self.split_brain_detected = False
                self.log_divergence = []
                self.conflict_resolution_count = 0
            
            async def detect_multiple_leaders(self, leader_signals: List[str]):
                """Detect if multiple leaders claim leadership"""
                if len(set(leader_signals)) > 1:
                    self.split_brain_detected = True
                    self.leaders = set(leader_signals)
                    return True
                return False
            
            async def detect_log_divergence(self, logs: Dict[str, List[int]]):
                """Detect if logs diverged"""
                log_hashes = {}
                
                for node_id, log_entries in logs.items():
                    log_hash = hash(tuple(log_entries))
                    
                    if log_hash not in log_hashes:
                        log_hashes[log_hash] = []
                    
                    log_hashes[log_hash].append(node_id)
                
                diverged = len(log_hashes) > 1
                
                if diverged:
                    self.log_divergence = list(log_hashes.keys())
                
                return diverged
            
            async def resolve_split_brain(self, logs: Dict[str, List[int]]):
                """Resolve by taking majority log"""
                from collections import Counter
                
                log_tuples = [tuple(log) for log in logs.values()]
                counts = Counter(log_tuples)
                
                majority_log = max(counts, key=counts.get)
                
                # Force all to majority
                self.conflict_resolution_count += 1
                self.split_brain_detected = False
                
                return majority_log
        
        detector = SplitBrainDetector()
        
        # Detect split brain
        split = await detector.detect_multiple_leaders(["leader-1", "leader-2"])
        assert split
        
        # Detect log divergence
        logs = {
            "node-1": [1, 2, 3],
            "node-2": [1, 2, 3],
            "node-3": [1, 2, 4],
            "node-4": [1, 2, 4],
            "node-5": [1, 2, 4],
        }
        
        diverged = await detector.detect_log_divergence(logs)
        assert diverged
        
        # Resolve
        majority_log = await detector.resolve_split_brain(logs)
        assert majority_log == (1, 2, 4)  # Majority (3 nodes)
        assert detector.conflict_resolution_count == 1


# ==================== TWO-PHASE COMMIT FAILURES ====================

class TestTwoPhaseCommitFailures:
    """Test 2PC failure scenarios and recovery"""
    
    @pytest.mark.asyncio
    async def test_coordinator_failure_during_commit(self):
        """
        Scenario: Coordinator crashes after voting phase but before commit
        Expected: Timeout on participants, rollback, recovery
        """
        
        class TwoPhaseCommitParticipant:
            def __init__(self, participant_id: str):
                self.participant_id = participant_id
                self.state = "idle"  # idle, prepared, committed, aborted
                self.transaction_id = None
                self.local_changes = {}
                self.can_commit = True
            
            async def vote_request(self, txn_id: str, changes: Dict) -> bool:
                """Phase 1: Vote on whether can commit"""
                self.transaction_id = txn_id
                self.local_changes = changes
                
                if self.can_commit:
                    self.state = "prepared"
                    return True
                
                return False
            
            async def wait_for_commit_decision(self, timeout_sec: float = 5.0) -> Optional[str]:
                """Wait for commit or rollback decision"""
                start = datetime.now()
                
                while (datetime.now() - start).total_seconds() < timeout_sec:
                    await asyncio.sleep(0.1)
                
                # Timeout - no decision received
                return None
            
            async def local_rollback(self) -> bool:
                """Rollback if no commit decision"""
                self.state = "aborted"
                self.local_changes = {}
                return True
            
            async def commit(self) -> bool:
                """Phase 2: Commit"""
                self.state = "committed"
                return True
        
        class TwoPhaseCommitCoordinator:
            def __init__(self):
                self.participants = {}
                self.votes = {}
                self.transaction_id = 0
                self.coordinator_crashed = False
                self.aborted_transactions = 0
            
            def add_participant(self, participant):
                self.participants[participant.participant_id] = participant
            
            async def phase_1_vote(self, changes: Dict) -> bool:
                """Phase 1: Get votes"""
                self.transaction_id += 1
                txn_id = self.transaction_id
                
                self.votes[txn_id] = []
                
                for participant in self.participants.values():
                    vote = await participant.vote_request(txn_id, changes)
                    self.votes[txn_id].append(vote)
                
                return all(self.votes[txn_id])
            
            async def phase_2_commit(self) -> bool:
                """Phase 2: Commit or abort"""
                if self.coordinator_crashed:
                    # Can't send commit decision
                    return False
                
                for participant in self.participants.values():
                    await participant.commit()
                
                return True
            
            async def crash_before_phase2(self):
                """Simulate coordinator crash"""
                self.coordinator_crashed = True
        
        # Setup
        coordinator = TwoPhaseCommitCoordinator()
        participants = [
            TwoPhaseCommitParticipant(f"p-{i}")
            for i in range(1, 4)
        ]
        
        for p in participants:
            coordinator.add_participant(p)
        
        # Phase 1: Vote
        all_voted = await coordinator.phase_1_vote({"key": "value"})
        assert all_voted
        assert all(p.state == "prepared" for p in participants)
        
        # Coordinator crashes before phase 2
        await coordinator.crash_before_phase2()
        
        # Phase 2 fails to commit
        committed = await coordinator.phase_2_commit()
        assert not committed
        
        # Participants timeout and rollback
        for participant in participants:
            decision = await participant.wait_for_commit_decision(timeout_sec=0.2)
            assert decision is None
            
            rolled_back = await participant.local_rollback()
            assert rolled_back
            assert participant.state == "aborted"
    
    @pytest.mark.asyncio
    async def test_2pc_with_cascading_failures(self):
        """
        Scenario: During 2PC, multiple participants fail
        Expected: Detect failures, abort gracefully, restore consistency
        """
        
        class Participant2PC:
            def __init__(self, participant_id: str):
                self.participant_id = participant_id
                self.state = "idle"
                self.is_alive = True
                self.voted = False
                self.committed = False
            
            async def vote(self) -> bool:
                if not self.is_alive:
                    return False
                self.voted = True
                return True
            
            async def commit(self) -> bool:
                if not self.is_alive:
                    return False
                self.committed = True
                return True
            
            async def crash(self):
                self.is_alive = False
        
        # Create participants
        participants = {
            f"p-{i}": Participant2PC(f"p-{i}")
            for i in range(1, 6)
        }
        
        # Phase 1: Vote
        votes = {}
        for p_id, participant in participants.items():
            votes[p_id] = await participant.vote()
        
        assert all(votes.values())
        
        # Simulate cascading failures during commit
        participants["p-3"].crash()
        participants["p-4"].crash()
        
        # Phase 2: Try commit
        commit_results = {}
        for p_id, participant in participants.items():
            commit_results[p_id] = await participant.commit()
        
        # Some succeed, some fail
        successful = sum(1 for r in commit_results.values() if r)
        failed = sum(1 for r in commit_results.values() if not r)
        
        assert failed > 0  # Some failed
        assert successful > 0  # Some succeeded
        
        # Consistency issue: partial commit
        # Must restore consistency by undoing successful commits
        for p_id, result in commit_results.items():
            if result:  # This one committed
                # Rollback to restore consistency
                participants[p_id].committed = False


# ==================== DISTRIBUTED LOCK FAILURES ====================

class TestDistributedLockFailures:
    """Test distributed locking under failure"""
    
    @pytest.mark.asyncio
    async def test_lock_holder_death_with_recovery(self):
        """
        Scenario: Lock holder crashes, lock becomes orphaned
        Expected: Timeout detects, other waiters acquire, holder recovers
        """
        
        class DistributedLock:
            def __init__(self, lock_id: str):
                self.lock_id = lock_id
                self.holder = None
                self.holder_heartbeat_time = None
                self.waiters_queue = []
                self.lock_timeout_sec = 5.0
            
            async def acquire(self, client_id: str) -> bool:
                """Try to acquire lock"""
                if self.holder is None:
                    self.holder = client_id
                    self.holder_heartbeat_time = datetime.now()
                    return True
                
                # Queue as waiter
                self.waiters_queue.append(client_id)
                return False
            
            async def heartbeat(self, client_id: str) -> bool:
                """Send heartbeat to keep lock"""
                if self.holder != client_id:
                    return False
                
                self.holder_heartbeat_time = datetime.now()
                return True
            
            async def check_holder_alive(self) -> bool:
                """Check if lock holder is alive (via heartbeat)"""
                if self.holder is None:
                    return True
                
                elapsed = (datetime.now() - self.holder_heartbeat_time).total_seconds()
                
                if elapsed > self.lock_timeout_sec:
                    return False
                
                return True
            
            async def timeout_lock_holder(self):
                """Force release lock due to timeout"""
                if not await self.check_holder_alive():
                    dead_holder = self.holder
                    self.holder = None
                    self.holder_heartbeat_time = None
                    return dead_holder
                
                return None
            
            async def grant_to_next_waiter(self) -> Optional[str]:
                """Grant lock to next waiter"""
                if self.holder is None and self.waiters_queue:
                    next_waiter = self.waiters_queue.pop(0)
                    self.holder = next_waiter
                    self.holder_heartbeat_time = datetime.now()
                    return next_waiter
                
                return None
        
        lock = DistributedLock("resource_1")
        
        # Client 1 acquires
        acquired = await lock.acquire("client-1")
        assert acquired
        assert lock.holder == "client-1"
        
        # Client 2 waits
        acquired = await lock.acquire("client-2")
        assert not acquired
        assert "client-2" in lock.waiters_queue
        
        # Client 1 crashes (stops sending heartbeats)
        # Simulate time passing without heartbeat
        lock.holder_heartbeat_time = datetime.now() - timedelta(seconds=10)
        
        # Timeout detected
        alive = await lock.check_holder_alive()
        assert not alive
        
        # Force release
        dead_holder = await lock.timeout_lock_holder()
        assert dead_holder == "client-1"
        assert lock.holder is None
        
        # Grant to waiting client
        granted = await lock.grant_to_next_waiter()
        assert granted == "client-2"
        assert lock.holder == "client-2"
    
    @pytest.mark.asyncio
    async def test_distributed_lock_deadlock_prevention(self):
        """
        Scenario: Multiple clients try to acquire locks in circular order
        Expected: Detect, break deadlock, enforce ordering
        """
        
        class DeadlockPreventingLockManager:
            def __init__(self):
                self.locks = {}
                self.acquisition_order = defaultdict(list)  # client -> locks acquired
                self.deadlocks_detected = 0
            
            async def acquire_with_ordering(self, client_id: str, 
                                          locks: List[str]) -> bool:
                """Acquire locks in strict order to prevent deadlock"""
                sorted_locks = sorted(locks)  # Enforce ordering
                
                for lock_name in sorted_locks:
                    if lock_name not in self.locks:
                        self.locks[lock_name] = None
                    
                    if self.locks[lock_name] is None:
                        self.locks[lock_name] = client_id
                        self.acquisition_order[client_id].append(lock_name)
                    else:
                        # Failed to acquire - rollback
                        await self.release_all(client_id)
                        return False
                
                return True
            
            async def detect_circular_wait(self) -> bool:
                """Detect if circular wait pattern exists"""
                wait_graph = defaultdict(set)
                
                for client, locks in self.acquisition_order.items():
                    for lock_name in locks:
                        holder = self.locks.get(lock_name)
                        if holder and holder != client:
                            wait_graph[client].add(holder)
                
                # Check for cycles (simplified)
                for client in wait_graph:
                    if client in wait_graph.get(list(wait_graph[client])[0], set()) \
                       if wait_graph[client] else False:
                        return True
                
                return False
            
            async def release_all(self, client_id: str):
                """Release all locks held by client"""
                for lock_name in self.acquisition_order[client_id]:
                    if self.locks.get(lock_name) == client_id:
                        self.locks[lock_name] = None
                
                self.acquisition_order[client_id] = []
        
        manager = DeadlockPreventingLockManager()
        
        # Client 1: acquire lock_a, lock_b
        success1 = await manager.acquire_with_ordering("client-1", ["lock_a", "lock_b"])
        assert success1
        
        # Client 2: try lock_a, lock_b (will fail on lock_a - held by client-1)
        success2 = await manager.acquire_with_ordering("client-2", ["lock_a", "lock_b"])
        assert not success2
        
        # Ordered acquisition prevents deadlock
        assert not await manager.detect_circular_wait()


# ==================== STATE CONSISTENCY & REPAIR ====================

class TestStateConsistencyAndRepair:
    """Test detection and repair of inconsistent state"""
    
    @pytest.mark.asyncio
    async def test_state_divergence_detection_and_reconciliation(self):
        """
        Scenario: Different replicas have diverged state
        Expected: Detect divergence, reconcile to consistent state
        """
        
        class StatefulReplica:
            def __init__(self, replica_id: str):
                self.replica_id = replica_id
                self.state = {}
                self.version = 0
                self.last_write_time = None
            
            async def write(self, key: str, value: str):
                """Write with version"""
                self.state[key] = {"value": value, "version": self.version}
                self.version += 1
                self.last_write_time = datetime.now()
            
            async def get_state_hash(self) -> int:
                """Get hash of current state"""
                return hash(frozenset(
                    (k, tuple(v.items())) for k, v in self.state.items()
                ))
            
            async def get_state_version(self) -> int:
                """Get current version"""
                return self.version
        
        class ConsistencyChecker:
            def __init__(self):
                self.replicas = {}
                self.divergence_detected = False
                self.reconciliations = 0
            
            def add_replica(self, replica: StatefulReplica):
                self.replicas[replica.replica_id] = replica
            
            async def detect_divergence(self) -> bool:
                """Detect if replicas have different state"""
                hashes = {}
                
                for replica_id, replica in self.replicas.items():
                    state_hash = await replica.get_state_hash()
                    
                    if state_hash not in hashes:
                        hashes[state_hash] = []
                    
                    hashes[state_hash].append(replica_id)
                
                if len(hashes) > 1:
                    self.divergence_detected = True
                    return True
                
                return False
            
            async def reconcile_to_majority(self) -> bool:
                """Reconcile to majority state"""
                state_groups = defaultdict(list)
                
                for replica_id, replica in self.replicas.items():
                    state_hash = await replica.get_state_hash()
                    state_groups[state_hash].append(replica_id)
                
                # Find majority
                majority_hash = max(state_groups, key=lambda h: len(state_groups[h]))
                majority_replicas = state_groups[majority_hash]
                
                # Get majority state
                master_replica = self.replicas[majority_replicas[0]]
                master_state = master_replica.state.copy()
                
                # Apply to others
                for replica_id, replica in self.replicas.items():
                    if replica_id not in majority_replicas:
                        replica.state = master_state.copy()
                
                self.divergence_detected = False
                self.reconciliations += 1
                return True
        
        # Create replicas
        replicas = [
            StatefulReplica(f"replica-{i}")
            for i in range(1, 4)
        ]
        
        # Write same data to all
        for replica in replicas:
            await replica.write("key-1", "value-1")
        
        checker = ConsistencyChecker()
        for replica in replicas:
            checker.add_replica(replica)
        
        # Verify consistent
        diverged = await checker.detect_divergence()
        assert not diverged
        
        # Corrupt one replica
        replicas[1].state["key-1"]["value"] = "corrupted"
        
        # Detect divergence
        diverged = await checker.detect_divergence()
        assert diverged
        
        # Reconcile
        reconciled = await checker.reconcile_to_majority()
        assert reconciled
        assert checker.reconciliations == 1
        
        # Verify all consistent again
        diverged = await checker.detect_divergence()
        assert not diverged
    
    @pytest.mark.asyncio
    async def test_multi_region_failover_with_data_recovery(self):
        """
        Scenario: Primary region fails, secondary takes over
        Expected: Detect failure, promote secondary, recover data
        """
        
        class RegionalDataStore:
            def __init__(self, region: str):
                self.region = region
                self.is_primary = False
                self.data = {}
                self.is_reachable = True
                self.sync_lag_ms = 0
            
            async def write(self, key: str, value: str) -> bool:
                """Write data"""
                if not self.is_reachable:
                    return False
                
                self.data[key] = {
                    "value": value,
                    "written_at": datetime.now(),
                    "region": self.region
                }
                return True
            
            async def read(self, key: str) -> Optional[str]:
                """Read data"""
                if not self.is_reachable:
                    return None
                
                if key in self.data:
                    return self.data[key]["value"]
                
                return None
            
            async def get_last_write_time(self, key: str) -> Optional[datetime]:
                """Get when key was last written"""
                if key in self.data:
                    return self.data[key]["written_at"]
                
                return None
        
        class MultiRegionCoordinator:
            def __init__(self):
                self.primary = RegionalDataStore("us-east-1")
                self.primary.is_primary = True
                self.secondary = RegionalDataStore("us-west-1")
                self.failover_count = 0
                self.recovery_count = 0
            
            async def detect_primary_failure(self) -> bool:
                """Detect if primary is down"""
                return not self.primary.is_reachable
            
            async def failover_to_secondary(self) -> bool:
                """Promote secondary to primary"""
                if not await self.detect_primary_failure():
                    return False
                
                self.primary.is_primary = False
                self.secondary.is_primary = True
                self.failover_count += 1
                return True
            
            async def recover_lost_data(self) -> int:
                """Recover data from secondary"""
                recovered = 0
                
                for key in self.secondary.data:
                    if key not in self.primary.data:
                        self.primary.data[key] = self.secondary.data[key]
                        recovered += 1
                
                self.recovery_count += 1
                return recovered
        
        # Setup
        coordinator = MultiRegionCoordinator()
        
        # Write to primary
        await coordinator.primary.write("key-1", "value-1")
        
        # Replicate to secondary
        await coordinator.secondary.write("key-1", "value-1")
        await coordinator.secondary.write("key-2", "value-2")
        
        # Primary fails
        coordinator.primary.is_reachable = False
        
        # Detect failure
        failed = await coordinator.detect_primary_failure()
        assert failed
        
        # Failover
        fo_success = await coordinator.failover_to_secondary()
        assert fo_success
        assert coordinator.failover_count == 1
        assert coordinator.secondary.is_primary
        
        # Recover data
        recovered = await coordinator.recover_lost_data()
        assert recovered > 0
        
        # Restore primary
        coordinator.primary.is_reachable = True
        
        # Verify data present
        assert await coordinator.primary.read("key-1") is not None
        assert await coordinator.primary.read("key-2") is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
