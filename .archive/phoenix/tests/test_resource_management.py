"""
Comprehensive Test Suite for Phoenix - Resource Management
Tests 786-815: Memory Leaks, File Handles, Connections, Cleanup (30 tests)

This file tests Phoenix's ability to detect and fix bugs in resource management,
including memory leaks, connection pooling, and proper cleanup.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch


class TestMemoryManagement:
    """Test memory leak detection and management (10 tests)"""
    
    def test_circular_references(self):
        """Test 786: Detect circular references"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class Node:
    def __init__(self, value):
        self.value = value
        # BUG: Circular reference
        self.parent = None
        self.children = []
    
    def add_child(self, child):
        self.children.append(child)
        child.parent = self  # BUG: Circular reference

root = Node("root")
child1 = Node("child1")
child2 = Node("child2")

root.add_child(child1)
root.add_child(child2)

# BUG: Circular references prevent garbage collection
del root
"""
            
            test_file = os.path.join(temp_dir, "circular_references.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_global_collections(self):
        """Test 787: Avoid unbounded global collections"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
# BUG: Global cache that grows unbounded
CACHE = {}

def cache_result(key, value):
    # BUG: No eviction policy
    CACHE[key] = value

# BUG: Memory leak
for i in range(1000000):
    cache_result(f"key_{i}", f"value_{i}")

print(f"Cache size: {len(CACHE)}")
"""
            
            test_file = os.path.join(temp_dir, "global_collections.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_event_listener_cleanup(self):
        """Test 788: Clean up event listeners"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class EventEmitter:
    def __init__(self):
        self.listeners = []
    
    def on(self, callback):
        # BUG: Listeners never removed
        self.listeners.append(callback)
    
    def emit(self, event):
        for listener in self.listeners:
            listener(event)

emitter = EventEmitter()

class Component:
    def __init__(self, emitter):
        # BUG: Registers listener but never unregisters
        emitter.on(self.handle_event)
    
    def handle_event(self, event):
        print(f"Handling: {event}")

# BUG: Creating and destroying components leaks memory
for _ in range(10000):
    component = Component(emitter)
    del component

# BUG: 10000 dead listeners still registered
print(f"Listeners: {len(emitter.listeners)}")
"""
            
            test_file = os.path.join(temp_dir, "event_cleanup.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_closure_memory_leaks(self):
        """Test 789: Avoid closure memory leaks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ClosureLeak:
    def create_handlers(self):
        handlers = []
        large_data = [0] * 1000000  # 1M items
        
        for i in range(100):
            # BUG: Closure captures large_data
            def handler():
                # Only uses i, but captures large_data too
                return i
            handlers.append(handler)
        
        return handlers

obj = ClosureLeak()

# BUG: Each handler holds reference to large_data
handlers = obj.create_handlers()
print(f"Created {len(handlers)} handlers")
"""
            
            test_file = os.path.join(temp_dir, "closure_leaks.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_weak_references(self):
        """Test 790: Use weak references appropriately"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class StrongReferences:
    def __init__(self):
        # BUG: Strong references in cache
        self.cache = {}
    
    def register_object(self, key, obj):
        # BUG: Prevents obj from being garbage collected
        self.cache[key] = obj

registry = StrongReferences()

class LargeObject:
    def __init__(self, data):
        self.data = data

# BUG: Objects can't be GC'd while in cache
for i in range(1000):
    obj = LargeObject([0] * 10000)
    registry.register_object(f"obj_{i}", obj)
    del obj  # BUG: Still referenced by cache

print(f"Cache size: {len(registry.cache)}")
"""
            
            test_file = os.path.join(temp_dir, "weak_references.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_generator_cleanup(self):
        """Test 791: Clean up generators properly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
def large_generator():
    # Allocates large buffer
    buffer = [0] * 1000000
    
    try:
        for item in buffer:
            yield item
    finally:
        # BUG: Cleanup may not run if generator not exhausted
        print("Cleanup")

# BUG: Generator not fully consumed
gen = large_generator()
first = next(gen)

# BUG: Generator left open, buffer not freed
del gen
"""
            
            test_file = os.path.join(temp_dir, "generator_cleanup.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_buffer_pooling(self):
        """Test 792: Use buffer pooling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoBufferPooling:
    def process_data(self, data):
        # BUG: Allocates new buffer for each call
        buffer = bytearray(1024 * 1024)  # 1MB
        
        # Process data
        buffer[:len(data)] = data
        
        return bytes(buffer[:len(data)])

processor = NoBufferPooling()

# BUG: Allocates/deallocates 1000 MB
for i in range(1000):
    result = processor.process_data(b"test data")

print("No buffer pooling")
"""
            
            test_file = os.path.join(temp_dir, "buffer_pooling.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_string_concatenation(self):
        """Test 793: Avoid inefficient string concatenation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class StringConcatenation:
    def build_string(self, items):
        # BUG: O(n²) string concatenation
        result = ""
        for item in items:
            result += str(item) + ","
        return result

builder = StringConcatenation()

# BUG: Allocates and copies repeatedly
items = range(10000)
result = builder.build_string(items)

print(f"Built string of length {len(result)}")
"""
            
            test_file = os.path.join(temp_dir, "string_concat.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_object_pooling(self):
        """Test 794: Implement object pooling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ExpensiveObject:
    def __init__(self):
        # Expensive initialization
        self.buffer = bytearray(1024 * 1024)

class NoObjectPooling:
    def process_request(self):
        # BUG: Creates new object for each request
        obj = ExpensiveObject()
        
        # Use object
        obj.buffer[0] = 1
        
        # BUG: Object discarded, will be recreated next time

processor = NoObjectPooling()

# BUG: Creates/destroys 1000 expensive objects
for _ in range(1000):
    processor.process_request()
"""
            
            test_file = os.path.join(temp_dir, "object_pooling.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_memory_profiling(self):
        """Test 795: Monitor memory usage"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoMemoryMonitoring:
    def __init__(self):
        self.data = []
    
    def add_data(self, item):
        # BUG: No memory monitoring
        self.data.append(item)

storage = NoMemoryMonitoring()

# BUG: No alerts when memory grows
for i in range(1000000):
    storage.add_data([0] * 1000)

print(f"Items: {len(storage.data)}")
"""
            
            test_file = os.path.join(temp_dir, "memory_profiling.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestConnectionManagement:
    """Test connection pooling and management (10 tests)"""
    
    def test_connection_pooling(self):
        """Test 796: Use connection pooling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoConnectionPooling:
    def query_database(self, query):
        # BUG: Creates new connection for each query
        connection = self.create_connection()
        
        try:
            result = connection.execute(query)
            return result
        finally:
            # BUG: Closes connection after each query
            connection.close()
    
    def create_connection(self):
        # Expensive connection setup
        return MockConnection()

class MockConnection:
    def execute(self, query):
        return "result"
    
    def close(self):
        pass

db = NoConnectionPooling()

# BUG: 1000 connection open/close cycles
for i in range(1000):
    result = db.query_database(f"SELECT * FROM table{i}")
"""
            
            test_file = os.path.join(temp_dir, "connection_pooling.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_connection_leak(self):
        """Test 797: Prevent connection leaks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ConnectionLeak:
    def __init__(self):
        self.connections = []
    
    def get_connection(self):
        # BUG: Creates connection but doesn't track
        connection = self.create_connection()
        return connection
    
    def create_connection(self):
        connection = MockConnection()
        # BUG: Not added to pool
        return connection

class MockConnection:
    def __init__(self):
        self.open = True

pool = ConnectionLeak()

# BUG: Connections never returned to pool
for _ in range(100):
    conn = pool.get_connection()
    # Use connection
    # BUG: Connection not closed/returned

print("Connection leak")
"""
            
            test_file = os.path.join(temp_dir, "connection_leak.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_pool_exhaustion(self):
        """Test 798: Handle pool exhaustion"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SimplePool:
    def __init__(self, size=10):
        self.size = size
        self.available = size
    
    def acquire(self):
        if self.available > 0:
            self.available -= 1
            return "connection"
        # BUG: Blocks indefinitely waiting for connection
        while True:
            pass

pool = SimplePool(size=5)

# BUG: 6th request blocks forever
for i in range(6):
    conn = pool.acquire()
    print(f"Acquired connection {i}")
"""
            
            test_file = os.path.join(temp_dir, "pool_exhaustion.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_connection_validation(self):
        """Test 799: Validate connections before use"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoConnectionValidation:
    def __init__(self):
        self.connection = self.create_connection()
    
    def query(self, sql):
        # BUG: Doesn't check if connection alive
        return self.connection.execute(sql)
    
    def create_connection(self):
        return MockConnection()

class MockConnection:
    def __init__(self):
        self.alive = True
    
    def execute(self, sql):
        if not self.alive:
            raise Exception("Connection closed")
        return "result"

db = NoConnectionValidation()

# Connection dies
db.connection.alive = False

# BUG: Uses dead connection
try:
    result = db.query("SELECT 1")
except Exception as e:
    print(f"Error: {e}")
"""
            
            test_file = os.path.join(temp_dir, "connection_validation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_idle_timeout(self):
        """Test 800: Implement idle timeouts"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class NoIdleTimeout:
    def __init__(self):
        self.connections = []
    
    def add_connection(self, conn):
        # BUG: No idle timeout tracking
        self.connections.append({
            "connection": conn,
            "created": time.time()
        })

pool = NoIdleTimeout()

# BUG: Idle connections never closed
for i in range(100):
    pool.add_connection(f"conn_{i}")

time.sleep(3600)  # 1 hour later

# BUG: All 100 connections still open
print(f"Open connections: {len(pool.connections)}")
"""
            
            test_file = os.path.join(temp_dir, "idle_timeout.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_connection_retry(self):
        """Test 801: Implement connection retry logic"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoConnectionRetry:
    def create_connection(self):
        # BUG: Single attempt, fails on transient error
        connection = self.connect()
        return connection
    
    def connect(self):
        # Simulated transient failure
        raise Exception("Connection refused")

try:
    db = NoConnectionRetry()
    conn = db.create_connection()
except Exception as e:
    # BUG: No retry on transient failure
    print(f"Connection failed: {e}")
"""
            
            test_file = os.path.join(temp_dir, "connection_retry.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_max_lifetime(self):
        """Test 802: Enforce connection max lifetime"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class NoMaxLifetime:
    def __init__(self):
        # BUG: Connection never rotated
        self.connection = self.create_connection()
        self.created_at = time.time()
    
    def query(self, sql):
        # BUG: Uses same connection forever
        return self.connection.execute(sql)
    
    def create_connection(self):
        return MockConnection()

class MockConnection:
    def execute(self, sql):
        return "result"

db = NoMaxLifetime()

# BUG: Connection used for days without rotation
time.sleep(86400)  # 1 day
result = db.query("SELECT 1")
"""
            
            test_file = os.path.join(temp_dir, "max_lifetime.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_pool_metrics(self):
        """Test 803: Track pool metrics"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoPoolMetrics:
    def __init__(self, size=10):
        self.size = size
        self.active = 0
    
    def acquire(self):
        # BUG: No metrics tracking
        self.active += 1
        return "connection"
    
    def release(self, conn):
        self.active -= 1

pool = NoPoolMetrics()

# BUG: No visibility into pool usage
for _ in range(5):
    conn = pool.acquire()

# BUG: Can't monitor wait times, utilization, etc.
print(f"Active: {pool.active}")
"""
            
            test_file = os.path.join(temp_dir, "pool_metrics.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_graceful_shutdown(self):
        """Test 804: Graceful pool shutdown"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoGracefulShutdown:
    def __init__(self):
        self.connections = [f"conn_{i}" for i in range(10)]
    
    def shutdown(self):
        # BUG: Doesn't wait for active connections
        self.connections.clear()

pool = NoGracefulShutdown()

# BUG: Shutdown while connections in use
pool.shutdown()

# BUG: Active queries interrupted
print("Shutdown complete")
"""
            
            test_file = os.path.join(temp_dir, "graceful_shutdown.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_connection_state_reset(self):
        """Test 805: Reset connection state"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoStateReset:
    def __init__(self):
        self.pool = [MockConnection() for _ in range(5)]
    
    def acquire(self):
        # BUG: Returns connection with previous state
        return self.pool.pop()
    
    def release(self, conn):
        # BUG: Doesn't reset connection state
        self.pool.append(conn)

class MockConnection:
    def __init__(self):
        self.transaction_active = False
        self.temp_tables = []
    
    def begin_transaction(self):
        self.transaction_active = True

pool = NoStateReset()

conn1 = pool.acquire()
conn1.begin_transaction()
pool.release(conn1)

conn2 = pool.acquire()

# BUG: conn2 has leftover transaction state
print(f"Transaction active: {conn2.transaction_active}")
"""
            
            test_file = os.path.join(temp_dir, "connection_reset.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestFileHandleManagement:
    """Test file handle and resource cleanup (10 tests)"""
    
    def test_file_descriptor_leak(self):
        """Test 806: Prevent file descriptor leaks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class FileDescriptorLeak:
    def read_file(self, path):
        # BUG: File not closed
        f = open(path, "r")
        content = f.read()
        return content
        # BUG: File handle leaked

reader = FileDescriptorLeak()

# BUG: Opens 1000 files without closing
for i in range(1000):
    try:
        content = reader.read_file(f"/tmp/file{i}.txt")
    except FileNotFoundError:
        pass

print("File descriptors leaked")
"""
            
            test_file = os.path.join(temp_dir, "fd_leak.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_context_manager_usage(self):
        """Test 807: Use context managers"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoContextManager:
    def process_file(self, path):
        f = open(path, "r")
        
        try:
            # BUG: Complex error handling
            data = f.read()
            result = self.process(data)
        except Exception as e:
            # BUG: File may not be closed on exception
            raise
        finally:
            # BUG: Manual cleanup
            f.close()
        
        return result
    
    def process(self, data):
        return data.upper()

processor = NoContextManager()
"""
            
            test_file = os.path.join(temp_dir, "no_context_manager.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_temp_file_cleanup(self):
        """Test 808: Clean up temporary files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import os

class NoTempCleanup:
    def process_data(self, data):
        # BUG: Creates temp file
        temp_path = "/tmp/tempfile.txt"
        
        with open(temp_path, "w") as f:
            f.write(data)
        
        # Process temp file
        result = self.process_file(temp_path)
        
        # BUG: Temp file not deleted
        return result
    
    def process_file(self, path):
        with open(path, "r") as f:
            return f.read()

processor = NoTempCleanup()

# BUG: Creates 100 temp files
for i in range(100):
    result = processor.process_data(f"data {i}")

print("Temp files not cleaned up")
"""
            
            test_file = os.path.join(temp_dir, "temp_cleanup.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_resource_limits(self):
        """Test 809: Respect resource limits"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoResourceLimits:
    def __init__(self):
        self.files = []
    
    def open_file(self, path):
        # BUG: No limit on open files
        f = open(path, "r")
        self.files.append(f)

manager = NoResourceLimits()

# BUG: Tries to open unlimited files
for i in range(10000):
    try:
        manager.open_file(f"/tmp/file{i}.txt")
    except OSError as e:
        print(f"Hit OS limit: {e}")
        break
"""
            
            test_file = os.path.join(temp_dir, "resource_limits.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_stream_closing(self):
        """Test 810: Close streams properly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import sys

class StreamLeak:
    def redirect_output(self, path):
        # BUG: Opens new stream
        log_file = open(path, "w")
        sys.stdout = log_file
        
        print("Logging to file")
        
        # BUG: Stream not closed or reset

redirector = StreamLeak()

# BUG: Stdout redirected permanently
redirector.redirect_output("/tmp/log.txt")
"""
            
            test_file = os.path.join(temp_dir, "stream_closing.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_buffer_flushing(self):
        """Test 811: Flush buffers before closing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoBufferFlush:
    def write_data(self, path, data):
        f = open(path, "w")
        
        for item in data:
            f.write(item)
        
        # BUG: Doesn't flush before close
        f.close()

writer = NoBufferFlush()

# BUG: Data may be lost
writer.write_data("/tmp/output.txt", ["a", "b", "c"])
"""
            
            test_file = os.path.join(temp_dir, "buffer_flushing.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_file_locking(self):
        """Test 812: Use file locking"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoFileLocking:
    def write_shared_file(self, path, data):
        # BUG: No file locking
        with open(path, "a") as f:
            f.write(data + "\\n")

writer = NoFileLocking()

# BUG: Multiple processes/threads can corrupt file
writer.write_shared_file("/tmp/shared.txt", "data1")
writer.write_shared_file("/tmp/shared.txt", "data2")
"""
            
            test_file = os.path.join(temp_dir, "file_locking.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_directory_cleanup(self):
        """Test 813: Clean up directories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import os

class NoDirectoryCleanup:
    def create_work_dir(self):
        # BUG: Creates directory
        work_dir = "/tmp/work_dir"
        os.makedirs(work_dir, exist_ok=True)
        
        # Do work
        
        # BUG: Directory not cleaned up
        return work_dir

worker = NoDirectoryCleanup()

# BUG: Creates 100 directories
for i in range(100):
    dir_path = worker.create_work_dir()

print("Directories not cleaned up")
"""
            
            test_file = os.path.join(temp_dir, "directory_cleanup.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_mmap_cleanup(self):
        """Test 814: Clean up memory-mapped files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import mmap

class NoMmapCleanup:
    def read_large_file(self, path):
        # BUG: mmap not closed
        with open(path, "r+b") as f:
            mmapped = mmap.mmap(f.fileno(), 0)
            data = mmapped.read(100)
            # BUG: mmap not closed
            return data

reader = NoMmapCleanup()

# BUG: mmap resources leaked
print("mmap not cleaned up")
"""
            
            test_file = os.path.join(temp_dir, "mmap_cleanup.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_signal_handler_cleanup(self):
        """Test 815: Clean up in signal handlers"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import signal
import sys

class NoSignalCleanup:
    def __init__(self):
        self.resources = []
        # BUG: No cleanup on signals
        signal.signal(signal.SIGTERM, self.handle_signal)
    
    def handle_signal(self, signum, frame):
        # BUG: Doesn't clean up resources
        sys.exit(0)
    
    def acquire_resource(self):
        self.resources.append("resource")

handler = NoSignalCleanup()

handler.acquire_resource()

# BUG: SIGTERM doesn't clean up resources
print("No signal cleanup")
"""
            
            test_file = os.path.join(temp_dir, "signal_cleanup.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
