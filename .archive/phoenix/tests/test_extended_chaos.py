"""
Extended Test Suite - Additional Chaos Scenarios
Covers: Byzantine failures, cascading cache effects, timeout storms, etc.
"""

import time
from collections import defaultdict
from typing import Dict, List, Tuple


class TestByzantineFailures:
    """Test 11-13: Byzantine validator failures"""
    
    def test_byzantine_node_detection(self):
        """Detect node lying about state"""
        
        class Node:
            def __init__(self, node_id, is_byzantine=False):
                self.node_id = node_id
                self.is_byzantine = is_byzantine
                self.state_hash = "correct"
            
            def report_state(self):
                if self.is_byzantine:
                    return "wrong_hash"
                return self.state_hash
        
        nodes = [Node(i, is_byzantine=(i==1)) for i in range(5)]
        
        reports = [node.report_state() for node in nodes]
        
        # Correct nodes agree, Byzantine is outlier
        from collections import Counter
        counts = Counter(reports)
        
        # Majority agree on correct state
        most_common = counts.most_common(1)[0]
        assert most_common[1] >= 4  # At least 4 agree
    
    def test_byzantine_resistance_2f_plus_1(self):
        """System tolerates up to f byzantine with 3f+1 nodes"""
        
        class ByzantineCluster:
            def __init__(self, total_nodes):
                self.total = total_nodes
                self.max_byzantine = (total_nodes - 1) // 3
                self.byzantine_count = 0
                self.consensus_reached = False
            
            def add_byzantine(self):
                if self.byzantine_count < self.max_byzantine:
                    self.byzantine_count += 1
                    return True
                return False
            
            def can_reach_consensus(self):
                honest = self.total - self.byzantine_count
                return honest > self.total // 2
        
        cluster = ByzantineCluster(total_nodes=7)
        
        # Add Byzantine nodes up to limit
        for _ in range(2):
            assert cluster.add_byzantine()
        
        # Still reach consensus
        assert cluster.can_reach_consensus()
        
        # Can't add 3rd
        assert not cluster.add_byzantine()
    
    def test_byzantine_equivocation_detection(self):
        """Detect node sending contradictory messages"""
        
        class MessageLog:
            def __init__(self):
                self.messages = defaultdict(list)
            
            def log_message(self, sender, message):
                self.messages[sender].append(message)
            
            def detect_equivocation(self, sender):
                msgs = self.messages[sender]
                return len(msgs) > 1 and len(set(msgs)) > 1
        
        log = MessageLog()
        
        # Honest node consistent
        log.log_message("node1", "state_A")
        log.log_message("node1", "state_A")
        assert not log.detect_equivocation("node1")
        
        # Byzantine node inconsistent
        log.log_message("node2", "state_B")
        log.log_message("node2", "state_C")
        assert log.detect_equivocation("node2")


class TestCacheFailures:
    """Test 14-16: Cache cascading effects"""
    
    def test_cache_stampede(self):
        """Prevent thundering herd on cache miss"""
        
        class CacheWithLock:
            def __init__(self):
                self.cache = {}
                self.lock_holders = {}
                self.backoff_wait = 0
            
            def get(self, key):
                if key in self.cache:
                    return self.cache[key]
                
                # Try to acquire lock
                if key not in self.lock_holders:
                    self.lock_holders[key] = "primary"
                    return None  # Primary will compute
                else:
                    # Others wait
                    self.backoff_wait += 1
                    return None
            
            def set(self, key, value):
                self.cache[key] = value
                if key in self.lock_holders:
                    del self.lock_holders[key]
        
        cache = CacheWithLock()
        
        # 100 concurrent misses
        for _ in range(100):
            cache.get("key1")
        
        # Only one should compute (lock holder)
        assert len(cache.lock_holders) <= 1
        
        # Others wait
        assert cache.backoff_wait == 99
    
    def test_cache_invalidation_storm(self):
        """Handle rapid cache invalidations"""
        
        class ResilientCache:
            def __init__(self):
                self.data = {"key": "v1"}
                self.invalidations = 0
                self.batch_invalidations = False
            
            def invalidate(self):
                self.invalidations += 1
                if self.invalidations > 50:
                    self.batch_invalidations = True
                    self.invalidations = 0
            
            def handle_batch(self):
                # Rebuild cache in batch
                self.data = {"key": "v1"}
                return True
        
        cache = ResilientCache()
        
        # Rapid invalidations
        for _ in range(100):
            cache.invalidate()
        
        # Triggered batch processing
        assert cache.batch_invalidations
        assert cache.handle_batch()
        assert cache.data["key"] == "v1"
    
    def test_cache_poisoning_detection(self):
        """Detect corrupted cached data"""
        
        class CacheWithValidation:
            def __init__(self):
                self.cache = {"key": "valid_data"}
                self.checksum = hash("valid_data")
                self.poison_detected = False
            
            def verify_integrity(self, key):
                if key in self.cache:
                    computed = hash(self.cache[key])
                    if computed != self.checksum:
                        self.poison_detected = True
                        self.cache[key] = "CORRUPTED"
                        return False
                return True
            
            def poison_cache(self, key):
                self.cache[key] = "corrupted"
        
        cache = CacheWithValidation()
        
        # Cache is valid
        assert cache.verify_integrity("key")
        
        # Poison it
        cache.poison_cache("key")
        
        # Detection works
        assert not cache.verify_integrity("key")
        assert cache.poison_detected


class TestTimeoutStorms:
    """Test 17-19: Timeout cascades"""
    
    def test_timeout_cascading_through_layers(self):
        """Timeout from one layer propagates"""
        
        class TimeoutLayer:
            def __init__(self, name, timeout_ms):
                self.name = name
                self.timeout_ms = timeout_ms
                self.timed_out = False
                self.propagated = False
            
            def call_downstream(self, downstream):
                # Timeout here
                self.timed_out = True
                
                # Propagate to downstream
                downstream.receive_timeout()
                self.propagated = True
            
            def receive_timeout(self):
                self.timed_out = True
        
        api_layer = TimeoutLayer("api", 1000)
        cache_layer = TimeoutLayer("cache", 500)
        db_layer = TimeoutLayer("db", 100)
        
        # DB times out, propagates up
        cache_layer.call_downstream(db_layer)
        
        assert cache_layer.propagated
        assert cache_layer.timed_out
        assert db_layer.timed_out
    
    def test_timeout_jitter_prevents_storms(self):
        """Add jitter to prevent synchronized retries"""
        
        import random
        
        class JitteredRetry:
            def __init__(self):
                self.retry_times = []
                self.successful = False
            
            def retry_with_jitter(self, attempt):
                # Base backoff with jitter
                base = 100 * (2 ** attempt)
                jitter = random.randint(-base//4, base//4)
                wait_time = base + jitter
                
                self.retry_times.append(wait_time)
                if attempt >= 3:
                    self.successful = True
                
                return wait_time
        
        retry = JitteredRetry()
        
        for attempt in range(4):
            retry.retry_with_jitter(attempt)
        
        # All times different (low probability of collision)
        assert len(set(retry.retry_times)) >= 3
        assert retry.successful
    
    def test_timeout_prevention_via_shedding(self):
        """Drop requests to prevent cascading timeouts"""
        
        class AdaptiveLoadShedder:
            def __init__(self, max_queue=100):
                self.queue = []
                self.max_queue = max_queue
                self.dropped = 0
                self.processed = 0
            
            def submit(self, request):
                if len(self.queue) >= self.max_queue:
                    self.dropped += 1
                    return False
                
                self.queue.append(request)
                return True
            
            def process_batch(self):
                batch = self.queue[:10]
                self.queue = self.queue[10:]
                self.processed += len(batch)
                return len(batch)
        
        shedder = AdaptiveLoadShedder()
        
        # Submit many requests
        for i in range(150):
            shedder.submit(f"req{i}")
        
        # Some dropped
        assert shedder.dropped > 0
        
        # Process in batches
        shedder.process_batch()
        assert shedder.processed > 0


class TestDataCorruption:
    """Test 20-22: Data corruption handling"""
    
    def test_corruption_detection_via_checksums(self):
        """Detect data corruption via hash mismatches"""
        
        class ChecksumValidator:
            def __init__(self, data):
                self.data = data
                self.original_checksum = hash(data)
                self.corrupted = False
            
            def verify(self):
                current = hash(self.data)
                if current != self.original_checksum:
                    self.corrupted = True
                    return False
                return True
            
            def corrupt(self):
                self.data = self.data + "_corrupted"
        
        validator = ChecksumValidator("original_data")
        
        assert validator.verify()
        
        validator.corrupt()
        assert not validator.verify()
        assert validator.corrupted
    
    def test_corruption_recovery_via_replicas(self):
        """Recover from corruption using replicas"""
        
        class ReplicatedStore:
            def __init__(self):
                self.replicas = ["original_data", "original_data", "original_data"]
                self.corrupted_count = 0
            
            def corrupt_replica(self, idx):
                self.replicas[idx] = "corrupted"
                self.corrupted_count += 1
            
            def recover(self):
                # Find majority
                from collections import Counter
                counts = Counter(self.replicas)
                majority = counts.most_common(1)[0][0]
                
                # Repair all
                self.replicas = [majority] * len(self.replicas)
                return True
        
        store = ReplicatedStore()
        
        # Corrupt one replica
        store.corrupt_replica(0)
        assert store.corrupted_count == 1
        
        # Recover
        assert store.recover()
        assert all(r == "original_data" for r in store.replicas)
    
    def test_corruption_containment(self):
        """Prevent corruption spread to healthy replicas"""
        
        class IsolatedReplica:
            def __init__(self, replica_id):
                self.replica_id = replica_id
                self.data = "clean"
                self.isolated = False
            
            def receive_data(self, data, is_valid):
                # Validate before accepting
                if not is_valid:
                    self.isolated = True
                    return False
                
                self.data = data
                return True
        
        replica = IsolatedReplica(1)
        
        # Reject corrupted data
        assert not replica.receive_data("corrupted", is_valid=False)
        assert replica.isolated
        
        # Accept clean data
        replica.isolated = False  # Reset
        assert replica.receive_data("clean", is_valid=True)
        assert not replica.isolated


class TestRateLimiting:
    """Test 23-24: Rate limit failures"""
    
    def test_rate_limit_quota_exhaustion(self):
        """System recovers from quota exhaustion"""
        
        class TokenBucket:
            def __init__(self, capacity, refill_rate):
                self.capacity = capacity
                self.tokens = capacity
                self.refill_rate = refill_rate
                self.requests_denied = 0
            
            def request(self, tokens=1):
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return True
                
                self.requests_denied += 1
                return False
            
            def refill(self):
                self.tokens = min(self.capacity, self.tokens + self.refill_rate)
        
        bucket = TokenBucket(capacity=10, refill_rate=2)
        
        # Exhaust quota
        for _ in range(10):
            assert bucket.request(1)
        
        # Deny further
        assert not bucket.request(1)
        assert bucket.requests_denied == 1
        
        # Refill
        bucket.refill()
        assert bucket.tokens > 0


class TestMonitoringRecovery:
    """Test 25-26: Monitoring and self-healing"""
    
    def test_metric_anomaly_detection(self):
        """Detect anomalies in metrics"""
        
        class AnomalyDetector:
            def __init__(self, baseline_mean, baseline_stddev):
                self.baseline_mean = baseline_mean
                self.baseline_stddev = baseline_stddev
                self.anomalies = 0
            
            def check(self, value):
                # Detect if > 3 stddevs from mean
                z_score = abs((value - self.baseline_mean) / self.baseline_stddev)
                if z_score > 3:
                    self.anomalies += 1
                    return True
                return False
        
        detector = AnomalyDetector(baseline_mean=100, baseline_stddev=10)
        
        # Normal value
        assert not detector.check(105)
        
        # Anomaly
        assert detector.check(200)
        assert detector.anomalies == 1
    
    def test_self_healing_via_restart(self):
        """Component restart heals state corruption"""
        
        class RestartableService:
            def __init__(self):
                self.state = "clean"
                self.restarts = 0
            
            def corrupt(self):
                self.state = "corrupted"
            
            def restart(self):
                self.state = "clean"
                self.restarts += 1
                return True
            
            def is_healthy(self):
                return self.state == "clean"
        
        service = RestartableService()
        
        assert service.is_healthy()
        
        service.corrupt()
        assert not service.is_healthy()
        
        service.restart()
        assert service.is_healthy()
        assert service.restarts == 1


if __name__ == "__main__":
    test_classes = [
        TestByzantineFailures,
        TestCacheFailures,
        TestTimeoutStorms,
        TestDataCorruption,
        TestRateLimiting,
        TestMonitoringRecovery,
    ]
    
    passed = 0
    failed = 0
    
    for test_class in test_classes:
        test_instance = test_class()
        
        for method_name in dir(test_instance):
            if method_name.startswith("test_"):
                try:
                    method = getattr(test_instance, method_name)
                    method()
                    print(f"✅ {test_class.__name__}.{method_name}")
                    passed += 1
                except Exception as e:
                    print(f"❌ {test_class.__name__}.{method_name}: {e}")
                    failed += 1
    
    print(f"\n{'='*60}")
    print(f"Extended Tests: {passed} passed, {failed} failed")
    print(f"{'='*60}")
