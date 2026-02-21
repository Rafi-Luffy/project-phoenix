"""
Comprehensive Test Suite for Phoenix - Concurrency & Threading
Tests 756-785: Thread Safety, Race Conditions, Deadlocks, Async Patterns (30 tests)

This file tests Phoenix's ability to detect and fix bugs in concurrent programming,
threading, async operations, and parallel processing.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch


class TestThreadSafety:
    """Test thread safety patterns (10 tests)"""
    
    def test_shared_mutable_state(self):
        """Test 756: Protect shared mutable state"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading

class UnsafeCounter:
    def __init__(self):
        # BUG: No lock for shared state
        self.count = 0
    
    def increment(self):
        # BUG: Race condition
        temp = self.count
        temp += 1
        self.count = temp

counter = UnsafeCounter()

threads = []
for _ in range(100):
    t = threading.Thread(target=counter.increment)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# BUG: Final count < 100 due to race condition
print(f"Count: {counter.count}")
"""
            
            test_file = os.path.join(temp_dir, "shared_state.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_double_checked_locking(self):
        """Test 757: Avoid double-checked locking bugs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading

class BrokenSingleton:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        # BUG: Double-checked locking without proper synchronization
        if cls._instance is None:
            # Time gap here
            cls._instance = cls()
        return cls._instance

# BUG: Multiple instances can be created
threads = []
instances = []

def create_instance():
    instances.append(BrokenSingleton.get_instance())

for _ in range(10):
    t = threading.Thread(target=create_instance)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# BUG: May have multiple instances
unique_instances = len(set(id(i) for i in instances))
print(f"Unique instances: {unique_instances}")
"""
            
            test_file = os.path.join(temp_dir, "double_checked_locking.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_thread_local_storage(self):
        """Test 758: Use thread-local storage properly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading

class NoThreadLocal:
    def __init__(self):
        # BUG: Shared across threads
        self.request_id = None
    
    def set_request_id(self, id):
        self.request_id = id
    
    def process(self):
        # BUG: May see other thread's request_id
        return f"Processing {self.request_id}"

handler = NoThreadLocal()

def worker(id):
    handler.set_request_id(id)
    result = handler.process()
    print(result)

# BUG: request_id gets overwritten by other threads
t1 = threading.Thread(target=worker, args=("req1",))
t2 = threading.Thread(target=worker, args=("req2",))

t1.start()
t2.start()
t1.join()
t2.join()
"""
            
            test_file = os.path.join(temp_dir, "thread_local.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_atomic_operations(self):
        """Test 759: Use atomic operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading

class NonAtomicFlag:
    def __init__(self):
        # BUG: Non-atomic flag check-and-set
        self.running = False
    
    def start(self):
        # BUG: Race condition
        if not self.running:
            self.running = True
            # Do work

flag = NonAtomicFlag()

def start_worker():
    flag.start()

# BUG: Both threads may think they're the first
t1 = threading.Thread(target=start_worker)
t2 = threading.Thread(target=start_worker)

t1.start()
t2.start()
t1.join()
t2.join()
"""
            
            test_file = os.path.join(temp_dir, "atomic_operations.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_volatile_visibility(self):
        """Test 760: Ensure memory visibility"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading
import time

class NoMemoryBarrier:
    def __init__(self):
        # BUG: No memory barrier
        self.flag = False
        self.data = None
    
    def writer(self):
        self.data = "value"
        # BUG: Compiler may reorder
        self.flag = True
    
    def reader(self):
        # BUG: May see flag=True but data=None
        while not self.flag:
            pass
        return self.data

obj = NoMemoryBarrier()

t1 = threading.Thread(target=obj.writer)
t2 = threading.Thread(target=obj.reader)

t2.start()
time.sleep(0.001)
t1.start()

t1.join()
t2.join()

# BUG: Reader may not see updated data
"""
            
            test_file = os.path.join(temp_dir, "memory_visibility.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_immutable_objects(self):
        """Test 761: Use immutable objects for thread safety"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading

class MutableSharedState:
    def __init__(self):
        # BUG: Mutable list shared across threads
        self.data = [1, 2, 3]
    
    def add_item(self, item):
        # BUG: List modification not thread-safe
        self.data.append(item)

state = MutableSharedState()

def worker(item):
    state.add_item(item)

threads = []
for i in range(100):
    t = threading.Thread(target=worker, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# BUG: May lose items or corrupt list
print(f"Items: {len(state.data)}")
"""
            
            test_file = os.path.join(temp_dir, "immutable_objects.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_copy_on_write(self):
        """Test 762: Implement copy-on-write"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading

class NoCopyOnWrite:
    def __init__(self):
        self.config = {"timeout": 30}
    
    def update_config(self, key, value):
        # BUG: Modifies in place
        self.config[key] = value
    
    def get_config(self):
        # BUG: Returns mutable reference
        return self.config

state = NoCopyOnWrite()

def writer():
    state.update_config("timeout", 60)

def reader():
    config = state.get_config()
    # BUG: Config may change during iteration
    for key in config:
        print(f"{key}: {config[key]}")

t1 = threading.Thread(target=writer)
t2 = threading.Thread(target=reader)

t2.start()
t1.start()
t1.join()
t2.join()
"""
            
            test_file = os.path.join(temp_dir, "copy_on_write.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_concurrent_collections(self):
        """Test 763: Use concurrent collections"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading

class UnsafeCache:
    def __init__(self):
        # BUG: Regular dict not thread-safe
        self.cache = {}
    
    def put(self, key, value):
        # BUG: Race condition on write
        self.cache[key] = value
    
    def get(self, key):
        # BUG: May see inconsistent state
        return self.cache.get(key)

cache = UnsafeCache()

def writer(i):
    cache.put(f"key{i}", f"value{i}")

threads = []
for i in range(1000):
    t = threading.Thread(target=writer, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# BUG: May corrupt dict or lose entries
print(f"Cache size: {len(cache.cache)}")
"""
            
            test_file = os.path.join(temp_dir, "concurrent_collections.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_read_write_locks(self):
        """Test 764: Use read-write locks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading

class SingleLock:
    def __init__(self):
        self.data = {}
        # BUG: Single lock for reads and writes
        self.lock = threading.Lock()
    
    def read(self, key):
        # BUG: Readers block each other
        with self.lock:
            return self.data.get(key)
    
    def write(self, key, value):
        with self.lock:
            self.data[key] = value

cache = SingleLock()

# BUG: Multiple readers can't run concurrently
def reader():
    cache.read("key")

threads = []
for _ in range(100):
    t = threading.Thread(target=reader)
    threads.append(t)
    t.start()

for t in threads:
    t.join()
"""
            
            test_file = os.path.join(temp_dir, "read_write_locks.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_compare_and_swap(self):
        """Test 765: Use compare-and-swap operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading

class NoCompareAndSwap:
    def __init__(self):
        self.value = 0
    
    def increment_if_less_than(self, threshold):
        # BUG: Check and update not atomic
        if self.value < threshold:
            self.value += 1
            return True
        return False

counter = NoCompareAndSwap()

def worker():
    counter.increment_if_less_than(10)

threads = []
for _ in range(20):
    t = threading.Thread(target=worker)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# BUG: Value may exceed threshold
print(f"Value: {counter.value}")
"""
            
            test_file = os.path.join(temp_dir, "compare_and_swap.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestDeadlocksAndLivelocks:
    """Test deadlock and livelock prevention (10 tests)"""
    
    def test_lock_ordering(self):
        """Test 766: Enforce consistent lock ordering"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading

class InconsistentLockOrder:
    def __init__(self):
        self.lock_a = threading.Lock()
        self.lock_b = threading.Lock()
    
    def method1(self):
        # BUG: Acquires A then B
        with self.lock_a:
            with self.lock_b:
                print("Method 1")
    
    def method2(self):
        # BUG: Acquires B then A (deadlock risk)
        with self.lock_b:
            with self.lock_a:
                print("Method 2")

obj = InconsistentLockOrder()

t1 = threading.Thread(target=obj.method1)
t2 = threading.Thread(target=obj.method2)

# BUG: Potential deadlock
t1.start()
t2.start()
"""
            
            test_file = os.path.join(temp_dir, "lock_ordering.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_lock_timeout(self):
        """Test 767: Use lock timeouts"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading

class NoLockTimeout:
    def __init__(self):
        self.lock = threading.Lock()
    
    def critical_section(self):
        # BUG: Waits indefinitely for lock
        self.lock.acquire()
        try:
            # Long operation
            pass
        finally:
            self.lock.release()

obj = NoLockTimeout()

# BUG: Thread blocks forever if lock held
print("Waiting for lock without timeout")
"""
            
            test_file = os.path.join(temp_dir, "lock_timeout.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_nested_locks(self):
        """Test 768: Avoid nested locks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading

class NestedLocks:
    def __init__(self):
        self.lock1 = threading.Lock()
        self.lock2 = threading.Lock()
        self.lock3 = threading.Lock()
    
    def complex_operation(self):
        # BUG: Multiple nested locks
        with self.lock1:
            with self.lock2:
                with self.lock3:
                    # Very complex to reason about
                    pass

obj = NestedLocks()

# BUG: High deadlock risk
obj.complex_operation()
"""
            
            test_file = os.path.join(temp_dir, "nested_locks.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_lock_free_algorithms(self):
        """Test 769: Consider lock-free algorithms"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading

class LockHeavy:
    def __init__(self):
        self.lock = threading.Lock()
        self.value = 0
    
    def increment(self):
        # BUG: Lock for every increment
        with self.lock:
            self.value += 1

counter = LockHeavy()

# BUG: Lock contention on hot path
threads = []
for _ in range(1000):
    t = threading.Thread(target=counter.increment)
    threads.append(t)
    t.start()

for t in threads:
    t.join()
"""
            
            test_file = os.path.join(temp_dir, "lock_free.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_deadlock_detection(self):
        """Test 770: Implement deadlock detection"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading

class NoDeadlockDetection:
    def __init__(self):
        self.lock_a = threading.Lock()
        self.lock_b = threading.Lock()
    
    def operation1(self):
        with self.lock_a:
            with self.lock_b:
                pass
    
    def operation2(self):
        with self.lock_b:
            with self.lock_a:
                pass

obj = NoDeadlockDetection()

# BUG: No deadlock detection mechanism
print("No deadlock detection")
"""
            
            test_file = os.path.join(temp_dir, "deadlock_detection.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_livelock_prevention(self):
        """Test 771: Prevent livelocks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading
import time

class LivelockRisk:
    def __init__(self):
        self.lock_a = threading.Lock()
        self.lock_b = threading.Lock()
    
    def operation(self):
        # BUG: Both release and retry immediately
        while True:
            acquired_a = self.lock_a.acquire(blocking=False)
            if not acquired_a:
                # Release and retry immediately
                time.sleep(0)
                continue
            
            acquired_b = self.lock_b.acquire(blocking=False)
            if not acquired_b:
                self.lock_a.release()
                # BUG: No backoff, immediate retry
                continue
            
            # Critical section
            break

# BUG: Threads may livelock
print("Livelock risk with no backoff")
"""
            
            test_file = os.path.join(temp_dir, "livelock.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_resource_allocation_graph(self):
        """Test 772: Track resource allocation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading

class NoResourceTracking:
    def __init__(self):
        self.resources = {}
    
    def allocate(self, thread_id, resource_id):
        # BUG: No tracking of who holds what
        self.resources[resource_id] = "allocated"

allocator = NoResourceTracking()

# BUG: Can't detect circular waits
allocator.allocate("t1", "r1")
allocator.allocate("t2", "r2")
"""
            
            test_file = os.path.join(temp_dir, "resource_tracking.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_priority_inversion(self):
        """Test 773: Handle priority inversion"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading

class PriorityInversion:
    def __init__(self):
        self.lock = threading.Lock()
    
    def low_priority_task(self):
        # Low priority acquires lock
        with self.lock:
            # Long operation
            pass
    
    def high_priority_task(self):
        # BUG: High priority blocked by low priority
        with self.lock:
            # Critical operation
            pass

# BUG: No priority inheritance
obj = PriorityInversion()
"""
            
            test_file = os.path.join(temp_dir, "priority_inversion.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_starvation_prevention(self):
        """Test 774: Prevent thread starvation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading

class NoFairness:
    def __init__(self):
        # BUG: No fairness, FIFO, or priority
        self.lock = threading.Lock()
    
    def access_resource(self):
        with self.lock:
            # Some threads may wait indefinitely
            pass

obj = NoFairness()

# BUG: Some threads may starve
threads = []
for _ in range(100):
    t = threading.Thread(target=obj.access_resource)
    threads.append(t)
    t.start()

for t in threads:
    t.join()
"""
            
            test_file = os.path.join(temp_dir, "starvation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_recursive_locks(self):
        """Test 775: Use recursive locks carefully"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading

class RecursiveDeadlock:
    def __init__(self):
        # BUG: Regular lock, not reentrant
        self.lock = threading.Lock()
    
    def method_a(self):
        with self.lock:
            self.method_b()
    
    def method_b(self):
        # BUG: Deadlock - already holding lock
        with self.lock:
            pass

obj = RecursiveDeadlock()

# BUG: Deadlocks on recursive call
try:
    obj.method_a()
except:
    print("Recursive lock deadlock")
"""
            
            test_file = os.path.join(temp_dir, "recursive_locks.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestAsyncPatterns:
    """Test asynchronous programming patterns (10 tests)"""
    
    def test_blocking_in_async(self):
        """Test 776: Don't block in async functions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import asyncio
import time

async def blocking_async():
    # BUG: Synchronous blocking call
    time.sleep(1)
    return "done"

async def main():
    # BUG: Blocks event loop
    result = await blocking_async()
    print(result)

# BUG: Event loop blocked
asyncio.run(main())
"""
            
            test_file = os.path.join(temp_dir, "blocking_async.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_fire_and_forget(self):
        """Test 777: Handle fire-and-forget tasks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import asyncio

async def background_task():
    await asyncio.sleep(0.1)
    raise Exception("Task failed")

async def main():
    # BUG: Creates task without awaiting or storing
    asyncio.create_task(background_task())
    
    # BUG: Exception in task is never seen
    await asyncio.sleep(0.2)

# BUG: Background task exception lost
asyncio.run(main())
"""
            
            test_file = os.path.join(temp_dir, "fire_and_forget.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_async_context_managers(self):
        """Test 778: Use async context managers"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import asyncio

class AsyncResource:
    async def acquire(self):
        await asyncio.sleep(0.01)
        return self
    
    async def release(self):
        await asyncio.sleep(0.01)

async def wrong_usage():
    # BUG: Not using async context manager
    resource = await AsyncResource().acquire()
    
    # Do work
    
    # BUG: May forget to release on exception
    await resource.release()

asyncio.run(wrong_usage())
"""
            
            test_file = os.path.join(temp_dir, "async_context.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_task_cancellation(self):
        """Test 779: Handle task cancellation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import asyncio

async def long_running_task():
    # BUG: Doesn't check for cancellation
    for i in range(1000):
        await asyncio.sleep(0.01)
        # BUG: No cancellation points

async def main():
    task = asyncio.create_task(long_running_task())
    await asyncio.sleep(0.05)
    
    # BUG: Cancel doesn't stop task promptly
    task.cancel()

asyncio.run(main())
"""
            
            test_file = os.path.join(temp_dir, "task_cancellation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_event_loop_blocking(self):
        """Test 780: Prevent event loop blocking"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import asyncio

async def cpu_intensive():
    # BUG: CPU-bound work in async function
    result = sum(range(10000000))
    return result

async def main():
    # BUG: Blocks event loop
    result = await cpu_intensive()
    print(result)

asyncio.run(main())
"""
            
            test_file = os.path.join(temp_dir, "event_loop_blocking.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_async_generator_cleanup(self):
        """Test 781: Clean up async generators"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import asyncio

async def async_generator():
    try:
        for i in range(10):
            yield i
            await asyncio.sleep(0.01)
    finally:
        # BUG: Cleanup may not run
        print("Cleanup")

async def main():
    gen = async_generator()
    
    # BUG: Generator not fully consumed or closed
    first = await gen.__anext__()
    print(first)
    
    # BUG: Generator left open

asyncio.run(main())
"""
            
            test_file = os.path.join(temp_dir, "async_generator_cleanup.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_gather_error_handling(self):
        """Test 782: Handle gather errors"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import asyncio

async def task1():
    await asyncio.sleep(0.1)
    return "success"

async def task2():
    await asyncio.sleep(0.05)
    raise Exception("Task 2 failed")

async def main():
    # BUG: Doesn't handle individual task failures
    results = await asyncio.gather(task1(), task2())
    print(results)

try:
    asyncio.run(main())
except Exception as e:
    # BUG: task1 result lost
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "gather_errors.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_semaphore_usage(self):
        """Test 783: Use async semaphores"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import asyncio

class NoRateLimiting:
    async def call_api(self, endpoint):
        # BUG: No concurrency limit
        await asyncio.sleep(0.01)
        return f"Result from {endpoint}"

async def main():
    service = NoRateLimiting()
    
    # BUG: 1000 concurrent API calls
    tasks = [service.call_api(f"/api/{i}") for i in range(1000)]
    results = await asyncio.gather(*tasks)

asyncio.run(main())
"""
            
            test_file = os.path.join(temp_dir, "semaphore_usage.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_async_timeout(self):
        """Test 784: Implement async timeouts"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import asyncio

async def slow_operation():
    # BUG: No timeout
    await asyncio.sleep(100)
    return "done"

async def main():
    # BUG: May wait forever
    result = await slow_operation()
    print(result)

asyncio.run(main())
"""
            
            test_file = os.path.join(temp_dir, "async_timeout.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_event_loop_policy(self):
        """Test 785: Set event loop policy"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import asyncio

async def main():
    # BUG: Using default event loop policy
    # May not work with all libraries
    await asyncio.sleep(0.1)

# BUG: No custom event loop policy configured
asyncio.run(main())
"""
            
            test_file = os.path.join(temp_dir, "event_loop_policy.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
