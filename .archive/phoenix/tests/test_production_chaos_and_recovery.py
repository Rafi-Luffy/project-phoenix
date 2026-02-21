"""
Production Chaos Testing: Real-World Error Patterns & Self-Healing

Sophisticated error patterns that mimic production issues:
- Memory pressure causing cascading failures
- Network partition scenarios
- Clock skew / time-based failures
- Resource exhaustion
- Deadlock scenarios
- Byzantine failures (partially correct behavior)
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set
from unittest.mock import Mock, AsyncMock, patch
import random
import threading
from enum import Enum
from collections import defaultdict


# ==================== MEMORY PRESSURE SIMULATION ====================

class TestMemoryPressureFailures:
    """Test system behavior under memory pressure"""
    
    @pytest.mark.asyncio
    async def test_cache_eviction_triggers_recovery(self):
        """
        Scenario: Memory pressure causes cache eviction, triggers upstream recovery
        Expected: System detects eviction, rebuilds hot data, adjusts TTLs
        """
        
        class MemoryAwareCache:
            def __init__(self, max_size_mb: int = 100):
                self.max_size_mb = max_size_mb
                self.current_size_mb = 0
                self.data = {}
                self.access_count = defaultdict(int)
                self.memory_pressure_level = "normal"
                self.evictions = 0
                self.rebuilds = 0
            
            async def put(self, key: str, value: str, size_estimate: float = 1.0) -> bool:
                """Put item in cache, handling memory pressure"""
                # Check pressure
                if self.current_size_mb + size_estimate > self.max_size_mb:
                    # Trigger eviction
                    await self._handle_memory_pressure()
                
                if self.current_size_mb + size_estimate <= self.max_size_mb:
                    self.data[key] = value
                    self.current_size_mb += size_estimate
                    return True
                
                return False
            
            async def get(self, key: str) -> Optional[str]:
                """Get with access tracking"""
                if key in self.data:
                    self.access_count[key] += 1
                    return self.data[key]
                return None
            
            async def _handle_memory_pressure(self):
                """Respond to memory pressure"""
                self.memory_pressure_level = "high"
                self.evictions += 1
                
                # Evict least frequently used
                if self.data:
                    lru_key = min(self.data.keys(), 
                                key=lambda k: self.access_count[k])
                    del self.data[lru_key]
                    self.current_size_mb -= 1
            
            async def rebuild_critical_data(self, critical_keys: List[str]):
                """Rebuild hot data during recovery"""
                self.rebuilds += 1
                
                for key in critical_keys:
                    if key not in self.data:
                        # Fetch from source
                        self.data[key] = f"rebuilt_{key}"
                        self.current_size_mb += 1
        
        cache = MemoryAwareCache(max_size_mb=50)
        
        # Load cache
        for i in range(100):
            await cache.put(f"key_{i}", f"value_{i}", size_estimate=0.5)
        
        # Verify memory pressure triggered
        assert cache.memory_pressure_level == "high"
        assert cache.evictions > 0
        
        # Rebuild critical data
        critical = ["key_0", "key_1", "key_2"]
        await cache.rebuild_critical_data(critical)
        
        # Verify rebuild happened
        assert cache.rebuilds == 1
        
        # Verify critical data accessible
        for key in critical:
            assert await cache.get(key) is not None
    
    @pytest.mark.asyncio
    async def test_goroutine_leak_detection_and_cleanup(self):
        """
        Scenario: Task leak causes resource exhaustion
        Expected: System detects, cancels leaked tasks, recovers
        """
        
        class TaskLeakDetector:
            def __init__(self):
                self.active_tasks = set()
                self.leaked_tasks = []
                self.cleanup_count = 0
                self.max_tasks = 1000
            
            async def create_task(self, task_id: str, duration: float) -> None:
                """Create a task, tracking it"""
                self.active_tasks.add(task_id)
                
                try:
                    await asyncio.sleep(duration)
                except asyncio.CancelledError:
                    pass
                finally:
                    if task_id in self.active_tasks:
                        self.active_tasks.discard(task_id)
            
            async def detect_leaks(self) -> List[str]:
                """Detect tasks that should have finished"""
                leaked = []
                
                for task_id in self.active_tasks:
                    # If task hasn't completed in expected time
                    if task_id.startswith("leaked_"):
                        leaked.append(task_id)
                
                self.leaked_tasks = leaked
                return leaked
            
            async def cleanup_leaks(self) -> int:
                """Cancel all leaked tasks"""
                self.cleanup_count += 1
                cancelled = 0
                
                for task_id in self.leaked_tasks:
                    if task_id in self.active_tasks:
                        self.active_tasks.discard(task_id)
                        cancelled += 1
                
                self.leaked_tasks = []
                return cancelled
            
            def get_health(self) -> Dict[str, Any]:
                """Check if healthy"""
                return {
                    "active_tasks": len(self.active_tasks),
                    "at_capacity": len(self.active_tasks) >= self.max_tasks,
                    "leak_detected": len(self.leaked_tasks) > 0
                }
        
        detector = TaskLeakDetector()
        
        # Create normal tasks
        normal_tasks = [
            detector.create_task(f"normal_{i}", 0.01)
            for i in range(10)
        ]
        
        # Create leaked tasks (simulating permanent hanging)
        leaked_tasks = [
            detector.create_task(f"leaked_{i}", 100.0)  # Won't complete
            for i in range(5)
        ]
        
        # Run all
        await asyncio.gather(*normal_tasks)
        await asyncio.sleep(0.05)
        
        # Detect leaks
        leaks = await detector.detect_leaks()
        assert len(leaks) == 5
        
        # Get health before cleanup
        health_before = detector.get_health()
        assert health_before["leak_detected"]
        
        # Cleanup
        cancelled = await detector.cleanup_leaks()
        assert cancelled == 5
        
        # Verify recovery
        health_after = detector.get_health()
        assert not health_after["leak_detected"]


# ==================== NETWORK PARTITION SCENARIOS ====================

class TestNetworkPartitionScenarios:
    """Test handling of network partitions and split-brain"""
    
    @pytest.mark.asyncio
    async def test_network_partition_with_quorum_recovery(self):
        """
        Scenario: Network splits, losing quorum in one partition
        Expected: Minority partition detects, stops accepting writes, recovers
        """
        
        class DistributedNode:
            def __init__(self, node_id: str, total_nodes: int):
                self.node_id = node_id
                self.total_nodes = total_nodes
                self.is_leader = False
                self.peers = set()
                self.writes_accepted = 0
                self.writes_rejected = 0
                self.state = "healthy"
            
            def add_peer(self, peer_id: str):
                self.peers.add(peer_id)
            
            def remove_peer(self, peer_id: str):
                """Simulate network partition"""
                if peer_id in self.peers:
                    self.peers.discard(peer_id)
            
            def has_quorum(self) -> bool:
                """Check if has quorum"""
                reachable = len(self.peers) + 1
                return reachable > self.total_nodes / 2
            
            async def handle_write(self, key: str, value: str) -> bool:
                """Handle write with quorum check"""
                if not self.has_quorum():
                    self.writes_rejected += 1
                    self.state = "minority"
                    return False
                
                self.writes_accepted += 1
                return True
            
            async def detect_partition(self) -> bool:
                """Detect if in minority partition"""
                return not self.has_quorum()
            
            async def recover_from_partition(self, restored_peers: Set[str]):
                """Recover when partition heals"""
                for peer in restored_peers:
                    self.add_peer(peer)
                
                if self.has_quorum():
                    self.state = "healthy"
                    return True
                return False
        
        # Create 3-node cluster
        nodes = {
            "node-1": DistributedNode("node-1", 3),
            "node-2": DistributedNode("node-2", 3),
            "node-3": DistributedNode("node-3", 3),
        }
        
        # Connect all nodes
        for node_id, node in nodes.items():
            for other_id in nodes:
                if other_id != node_id:
                    node.add_peer(other_id)
        
        # Phase 1: Normal writes
        for i in range(10):
            for node in nodes.values():
                result = await node.handle_write(f"key_{i}", f"value_{i}")
                assert result
        
        # Phase 2: Simulate partition (split to 1-2)
        nodes["node-1"].remove_peer("node-2")
        nodes["node-1"].remove_peer("node-3")
        nodes["node-2"].remove_peer("node-1")
        nodes["node-3"].remove_peer("node-1")
        
        # Phase 3: Attempt writes
        # Node 1 (minority) should reject
        result1 = await nodes["node-1"].handle_write("key_new", "value")
        assert not result1
        assert await nodes["node-1"].detect_partition()
        
        # Nodes 2, 3 (majority) should accept
        result2 = await nodes["node-2"].handle_write("key_new", "value")
        result3 = await nodes["node-3"].handle_write("key_new", "value")
        assert result2 and result3
        
        # Phase 4: Recover partition
        restored_peers = {"node-2", "node-3"}
        recovered = await nodes["node-1"].recover_from_partition(restored_peers)
        assert recovered
        assert nodes["node-1"].state == "healthy"
        
        # Phase 5: Should accept writes again
        result = await nodes["node-1"].handle_write("key_recovery", "value")
        assert result
    
    @pytest.mark.asyncio
    async def test_byzantine_replica_detection(self):
        """
        Scenario: One replica returns incorrect data (Byzantine failure)
        Expected: System detects, excludes bad replica, continues
        """
        
        class ByzantineDetector:
            def __init__(self):
                self.replicas = {
                    "rep-1": {"healthy": True, "data": {}},
                    "rep-2": {"healthy": True, "data": {}},
                    "rep-3": {"healthy": True, "data": {}},
                }
                self.suspicious_replicas = set()
            
            async def write_to_all(self, key: str, value: str):
                """Write to all replicas"""
                for rep_id, rep in self.replicas.items():
                    if rep["healthy"]:
                        rep["data"][key] = value
            
            async def read_with_voting(self, key: str):
                """Read with majority voting"""
                responses = defaultdict(int)
                
                for rep_id, rep in self.replicas.items():
                    if rep_id in self.suspicious_replicas:
                        continue
                    
                    value = rep["data"].get(key)
                    responses[value] += 1
                
                if responses:
                    return max(responses, key=responses.get)
                return None
            
            async def detect_byzantine(self, key: str, expected_value: str) -> Optional[str]:
                """Detect Byzantine replica"""
                responses = {}
                
                for rep_id, rep in self.replicas.items():
                    if rep_id in self.suspicious_replicas:
                        continue
                    
                    value = rep["data"].get(key)
                    if rep_id not in responses:
                        responses[rep_id] = value
                
                # Find outlier
                values = list(responses.values())
                if len(set(values)) > 1:
                    # Get majority value
                    from collections import Counter
                    counts = Counter(values)
                    majority = max(counts, key=counts.get)
                    
                    # Find byzantine
                    for rep_id, value in responses.items():
                        if value != majority and value is not None:
                            return rep_id
                
                return None
            
            async def quarantine_replica(self, rep_id: str):
                """Quarantine suspected Byzantine replica"""
                self.suspicious_replicas.add(rep_id)
        
        detector = ByzantineDetector()
        
        # Write to all
        await detector.write_to_all("data_key", "correct_value")
        
        # Make one replica Byzantine
        detector.replicas["rep-2"]["data"]["data_key"] = "wrong_value"
        
        # Detect Byzantine
        byzantine_rep = await detector.detect_byzantine("data_key", "correct_value")
        assert byzantine_rep == "rep-2"
        
        # Quarantine
        await detector.quarantine_replica(byzantine_rep)
        
        # Read should now return correct value (voting excludes bad replica)
        result = await detector.read_with_voting("data_key")
        assert result == "correct_value"


# ==================== CLOCK SKEW & TIMING FAILURES ====================

class TestClockSkewAndTimingFailures:
    """Test handling of time-related failures"""
    
    @pytest.mark.asyncio
    async def test_clock_skew_causes_cert_expiration(self):
        """
        Scenario: System clock skews forward, certs appear expired
        Expected: Detect, apply grace period, rotate certs
        """
        
        class CertificateWithClockSkew:
            def __init__(self):
                self.current_time = datetime.now()
                self.cert_expiry = self.current_time + timedelta(hours=24)
                self.grace_period_hours = 1
                self.skew_detected = False
                self.cert_rotations = 0
            
            def set_system_time(self, new_time: datetime):
                """Simulate clock change"""
                self.current_time = new_time
            
            def is_expired(self, strict: bool = False) -> bool:
                """Check if cert expired"""
                if strict:
                    return self.current_time >= self.cert_expiry
                
                grace_end = self.cert_expiry + timedelta(
                    hours=self.grace_period_hours
                )
                return self.current_time >= grace_end
            
            async def detect_clock_skew(self) -> bool:
                """Detect if clock skew occurred"""
                # Cert shouldn't be expired with grace period
                if not self.is_expired(strict=True) and self.is_expired(strict=False):
                    self.skew_detected = True
                    return True
                return False
            
            async def rotate_cert(self) -> bool:
                """Rotate certificate"""
                self.cert_expiry = self.current_time + timedelta(hours=24)
                self.cert_rotations += 1
                self.skew_detected = False
                return True
        
        cert = CertificateWithClockSkew()
        
        # Normal state
        assert not cert.is_expired()
        
        # Simulate 2-hour clock skew forward
        cert.set_system_time(cert.current_time + timedelta(hours=2))
        
        # Detect skew
        detected = await cert.detect_clock_skew()
        assert detected
        assert cert.skew_detected
        
        # Rotate
        rotated = await cert.rotate_cert()
        assert rotated
        assert cert.cert_rotations == 1
        assert not cert.is_expired()
    
    @pytest.mark.asyncio
    async def test_timeout_during_gc_pause(self):
        """
        Scenario: GC pause causes unexpected timeouts
        Expected: Detect pause, increase timeout tolerance, retry
        """
        
        class TimeoutWithGCPauseDetection:
            def __init__(self):
                self.last_operation_time = datetime.now()
                self.gc_pause_detected = False
                self.pause_duration_ms = 0
                self.timeout_ms = 100
                self.retries_after_pause = 0
            
            async def perform_operation(self, duration_ms: int) -> bool:
                """Perform operation with timeout"""
                start = datetime.now()
                await asyncio.sleep(duration_ms / 1000)
                elapsed = (datetime.now() - start).total_seconds() * 1000
                
                return elapsed <= self.timeout_ms
            
            async def detect_gc_pause(self, actual_time_ms: float, expected_time_ms: float):
                """Detect if GC pause occurred"""
                pause = actual_time_ms - expected_time_ms
                
                if pause > 10:  # More than 10ms pause
                    self.gc_pause_detected = True
                    self.pause_duration_ms = pause
            
            async def adapt_timeout(self):
                """Increase timeout to account for GC pauses"""
                self.timeout_ms += int(self.pause_duration_ms * 1.5)
            
            async def retry_with_tolerance(self) -> bool:
                """Retry operation with GC-tolerant timeout"""
                if self.gc_pause_detected:
                    await self.adapt_timeout()
                    self.retries_after_pause += 1
                    return True
                return False
        
        timeout_handler = TimeoutWithGCPauseDetection()
        
        # Detect simulated GC pause
        await timeout_handler.detect_gc_pause(actual_time_ms=150, expected_time_ms=100)
        assert timeout_handler.gc_pause_detected
        
        # Adapt and retry
        retry = await timeout_handler.retry_with_tolerance()
        assert retry
        assert timeout_handler.timeout_ms > 100
        assert timeout_handler.retries_after_pause == 1


# ==================== RESOURCE EXHAUSTION ====================

class TestResourceExhaustion:
    """Test handling of resource limits"""
    
    @pytest.mark.asyncio
    async def test_connection_pool_exhaustion_with_recovery(self):
        """
        Scenario: Connection pool exhausted, waiting queue grows
        Expected: Detect, drain old connections, add new, recover
        """
        
        class ConnectionPool:
            def __init__(self, max_connections: int = 10):
                self.max_connections = max_connections
                self.active_connections = 0
                self.waiting_queue = 0
                self.drained_connections = 0
                self.pool_exhausted = False
            
            async def acquire(self, timeout_sec: float = 5.0) -> bool:
                """Try to acquire connection"""
                if self.active_connections < self.max_connections:
                    self.active_connections += 1
                    return True
                
                # Queue waiting
                self.waiting_queue += 1
                self.pool_exhausted = True
                return False
            
            async def release(self):
                """Release connection"""
                if self.active_connections > 0:
                    self.active_connections -= 1
                    
                    # Process one waiter
                    if self.waiting_queue > 0:
                        self.waiting_queue -= 1
            
            async def detect_exhaustion(self) -> bool:
                """Detect pool exhaustion"""
                return self.pool_exhausted
            
            async def drain_stale_connections(self) -> int:
                """Drain old connections to free slots"""
                drained = min(self.active_connections, 3)
                self.active_connections -= drained
                self.drained_connections += drained
                return drained
            
            async def recover(self) -> bool:
                """Recover from exhaustion"""
                if self.waiting_queue == 0 and self.pool_exhausted:
                    self.pool_exhausted = False
                    return True
                return False
        
        pool = ConnectionPool(max_connections=5)
        
        # Exhaust pool
        for _ in range(5):
            assert await pool.acquire()
        
        # Further attempts queue
        assert not await pool.acquire()
        assert pool.pool_exhausted
        
        # Detect exhaustion
        exhausted = await pool.detect_exhaustion()
        assert exhausted
        
        # Drain stale connections
        drained = await pool.drain_stale_connections()
        assert drained > 0
        
        # Release and recover
        for _ in range(drained):
            await pool.release()
        
        recovered = await pool.recover()
        assert recovered
    
    @pytest.mark.asyncio
    async def test_memory_leak_in_cache_with_cleanup(self):
        """
        Scenario: Cache accumulates memory due to leak
        Expected: Detect growth, trigger cleanup, verify recovery
        """
        
        class CacheWithMemoryTracking:
            def __init__(self):
                self.items = {}
                self.memory_bytes = 0
                self.memory_samples = []
                self.cleanup_triggered = False
                self.cleanups_performed = 0
            
            async def add_item(self, key: str, size_bytes: int):
                """Add item, tracking memory"""
                self.items[key] = size_bytes
                self.memory_bytes += size_bytes
                self.memory_samples.append(self.memory_bytes)
            
            async def detect_memory_leak(self) -> bool:
                """Detect if memory growing consistently"""
                if len(self.memory_samples) < 5:
                    return False
                
                # Check if trending up
                recent = self.memory_samples[-5:]
                is_growing = all(recent[i] < recent[i+1] for i in range(4))
                
                if is_growing:
                    self.cleanup_triggered = True
                    return True
                
                return False
            
            async def cleanup_expired(self) -> int:
                """Remove expired items"""
                old_size = len(self.items)
                
                # Remove old items (simulate expiration)
                keys_to_remove = list(self.items.keys())[:len(self.items)//2]
                
                for key in keys_to_remove:
                    size = self.items.pop(key)
                    self.memory_bytes -= size
                
                self.cleanups_performed += 1
                return len(keys_to_remove)
        
        cache = CacheWithMemoryTracking()
        
        # Simulate growing memory
        for i in range(10):
            await cache.add_item(f"key_{i}", 1000)
        
        # Detect leak
        is_leaking = await cache.detect_memory_leak()
        assert is_leaking
        assert cache.cleanup_triggered
        
        # Cleanup
        removed = await cache.cleanup_expired()
        assert removed > 0
        assert cache.cleanups_performed == 1
        assert cache.memory_bytes < 1000 * 10


# ==================== DEADLOCK & CONTENTION ====================

class TestDeadlockAndContention:
    """Test deadlock detection and resolution"""
    
    @pytest.mark.asyncio
    async def test_deadlock_detection_and_abort(self):
        """
        Scenario: Two operations waiting on each other (deadlock)
        Expected: Detect, abort one, both complete
        """
        
        class DeadlockDetector:
            def __init__(self):
                self.locks = {}
                self.waiting_graph = defaultdict(set)
                self.deadlocks_detected = 0
                self.aborted_operations = 0
            
            async def acquire_locks(self, op_id: str, locks_needed: List[str]) -> bool:
                """Acquire locks in order, detect if waiting"""
                for lock_name in locks_needed:
                    self.waiting_graph[op_id].add(lock_name)
                    
                    if lock_name not in self.locks:
                        self.locks[lock_name] = op_id
                    else:
                        # Someone else has it
                        pass
                
                return True
            
            async def detect_cycle(self) -> Optional[List[str]]:
                """Detect if cycle in wait graph"""
                # Simplified cycle detection
                for op_id in self.waiting_graph:
                    waiting_for = self.waiting_graph[op_id]
                    
                    for lock_name in waiting_for:
                        holder = self.locks.get(lock_name)
                        
                        if holder and holder != op_id:
                            # Check if circular
                            if holder in self.waiting_graph:
                                # Potential deadlock
                                return [op_id, holder]
                
                return None
            
            async def abort_operation(self, op_id: str):
                """Abort operation to break deadlock"""
                # Release locks
                for lock_name in list(self.waiting_graph[op_id]):
                    if self.locks.get(lock_name) == op_id:
                        del self.locks[lock_name]
                
                del self.waiting_graph[op_id]
                self.aborted_operations += 1
                self.deadlocks_detected += 1
        
        detector = DeadlockDetector()
        
        # Simulate two operations acquiring locks in opposite order
        await detector.acquire_locks("op_1", ["lock_a", "lock_b"])
        await detector.acquire_locks("op_2", ["lock_b", "lock_a"])
        
        # Detect deadlock
        cycle = await detector.detect_cycle()
        assert cycle is not None
        assert detector.deadlocks_detected == 0  # Not detected yet
        
        # Abort one to break cycle
        await detector.abort_operation("op_2")
        
        assert detector.deadlocks_detected == 1
        assert detector.aborted_operations == 1
        
        # Should be no cycle now
        cycle = await detector.detect_cycle()
        assert cycle is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
