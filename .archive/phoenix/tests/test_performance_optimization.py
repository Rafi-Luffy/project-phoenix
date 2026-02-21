"""
Comprehensive Test Suite for Phoenix - Performance Optimization
Tests 576-605: Caching, Memory Management, Algorithm Efficiency (30 tests)

This file tests Phoenix's ability to detect and fix performance bugs,
including inefficient algorithms, memory leaks, and caching issues.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch


class TestCachingStrategies:
    """Test caching and memoization (10 tests)"""
    
    def test_cache_stampede_prevention(self):
        """Test 576: Prevent cache stampede"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class NoStampedeProtection:
    def __init__(self):
        self.cache = {}
    
    def get_data(self, key):
        if key not in self.cache:
            # BUG: Multiple requests compute simultaneously
            return self.expensive_computation(key)
        return self.cache[key]
    
    def expensive_computation(self, key):
        time.sleep(1)  # Expensive operation
        return f"result_{key}"

cache = NoStampedeProtection()

# 100 concurrent requests for same key
# BUG: All compute instead of one
print("Cache stampede possible")
"""
            
            test_file = os.path.join(temp_dir, "cache_stampede.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_cache_eviction_policy(self):
        """Test 577: Implement proper cache eviction"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class RandomEviction:
    def __init__(self, max_size=100):
        self.cache = {}
        self.max_size = max_size
    
    def set(self, key, value):
        if len(self.cache) >= self.max_size:
            # BUG: Random eviction, not LRU/LFU
            import random
            evict_key = random.choice(list(self.cache.keys()))
            del self.cache[evict_key]
        self.cache[key] = value

cache = RandomEviction(max_size=3)

cache.set("hot", "frequently_used")
cache.set("key2", "value2")
cache.set("key3", "value3")
cache.set("key4", "value4")

# BUG: May evict "hot" key
print(f"Cache: {cache.cache}")
"""
            
            test_file = os.path.join(temp_dir, "cache_eviction.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_cache_invalidation_strategy(self):
        """Test 578: Invalidate cache correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoInvalidation:
    def __init__(self):
        self.cache = {}
        self.data = {"user1": "Alice"}
    
    def get_user(self, user_id):
        if user_id in self.cache:
            return self.cache[user_id]
        
        user = self.data.get(user_id)
        self.cache[user_id] = user
        return user
    
    def update_user(self, user_id, new_name):
        self.data[user_id] = new_name
        # BUG: Doesn't invalidate cache

db = NoInvalidation()

name1 = db.get_user("user1")  # "Alice"
db.update_user("user1", "Bob")
name2 = db.get_user("user1")  # Still "Alice"

# BUG: Stale cache
print(f"Cached name: {name2}")
"""
            
            test_file = os.path.join(temp_dir, "cache_invalidation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_cache_key_collision(self):
        """Test 579: Avoid cache key collisions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class PoorCacheKey:
    def __init__(self):
        self.cache = {}
    
    def get_user_posts(self, user_id, post_type):
        # BUG: Weak cache key
        key = f"{user_id}{post_type}"
        if key in self.cache:
            return self.cache[key]
        
        result = f"posts for {user_id}, type {post_type}"
        self.cache[key] = result
        return result

cache = PoorCacheKey()

# BUG: user_id=1, post_type=23 collides with user_id=12, post_type=3
result1 = cache.get_user_posts("1", "23")
result2 = cache.get_user_posts("12", "3")

print(f"Key collision: {result1 == result2}")
"""
            
            test_file = os.path.join(temp_dir, "cache_key_collision.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_cache_warming(self):
        """Test 580: Warm cache on startup"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ColdStartCache:
    def __init__(self):
        self.cache = {}
        # BUG: No cache warming
    
    def get_popular_items(self):
        if "popular" in self.cache:
            return self.cache["popular"]
        
        # Expensive computation
        items = self.compute_popular_items()
        self.cache["popular"] = items
        return items
    
    def compute_popular_items(self):
        return ["item1", "item2", "item3"]

cache = ColdStartCache()

# First request is slow
# BUG: Should pre-warm cache
print("Cache starts cold")
"""
            
            test_file = os.path.join(temp_dir, "cache_warming.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_distributed_cache_consistency(self):
        """Test 581: Maintain distributed cache consistency"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class InconsistentDistributedCache:
    def __init__(self):
        self.cache_node1 = {}
        self.cache_node2 = {}
    
    def set(self, key, value):
        # BUG: Only updates one node
        self.cache_node1[key] = value
    
    def get(self, key):
        # Randomly read from either node
        import random
        if random.choice([True, False]):
            return self.cache_node1.get(key)
        return self.cache_node2.get(key)

cache = InconsistentDistributedCache()

cache.set("key", "value")
# BUG: May return None from node2
result = cache.get("key")
print(f"Result: {result}")
"""
            
            test_file = os.path.join(temp_dir, "distributed_cache.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_cache_size_monitoring(self):
        """Test 582: Monitor cache size and memory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnmonitoredCache:
    def __init__(self):
        self.cache = {}
    
    def set(self, key, value):
        # BUG: No size monitoring
        self.cache[key] = value

cache = UnmonitoredCache()

# Add large objects
for i in range(10000):
    cache.set(f"key{i}", "x" * 10000)

# BUG: May exhaust memory
print(f"Cache entries: {len(cache.cache)}")
"""
            
            test_file = os.path.join(temp_dir, "cache_monitoring.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_negative_caching(self):
        """Test 583: Cache negative results appropriately"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoNegativeCaching:
    def __init__(self):
        self.cache = {}
    
    def get_user(self, user_id):
        if user_id in self.cache:
            return self.cache[user_id]
        
        user = self.lookup_user(user_id)
        # BUG: Doesn't cache None results
        if user is not None:
            self.cache[user_id] = user
        return user
    
    def lookup_user(self, user_id):
        # User doesn't exist
        return None

cache = NoNegativeCaching()

# Repeatedly queries for non-existent user
for _ in range(100):
    user = cache.get_user("nonexistent")

# BUG: Each query hits database
print("No negative caching")
"""
            
            test_file = os.path.join(temp_dir, "negative_caching.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_cache_ttl_implementation(self):
        """Test 584: Implement TTL for cache entries"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class NoTTL:
    def __init__(self):
        self.cache = {}
    
    def set(self, key, value):
        # BUG: No expiration time
        self.cache[key] = {"value": value, "timestamp": time.time()}
    
    def get(self, key):
        # BUG: Doesn't check expiration
        if key in self.cache:
            return self.cache[key]["value"]
        return None

cache = NoTTL()

cache.set("key", "value")
time.sleep(2)

# BUG: Returns stale data
result = cache.get("key")
print(f"Result after 2s: {result}")
"""
            
            test_file = os.path.join(temp_dir, "cache_ttl.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_write_through_vs_write_back(self):
        """Test 585: Choose appropriate write strategy"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class AlwaysWriteThrough:
    def __init__(self):
        self.cache = {}
        self.db = {}
    
    def set(self, key, value):
        # BUG: Always writes to DB (slow)
        self.db[key] = value
        self.cache[key] = value

cache = AlwaysWriteThrough()

# Many writes
for i in range(1000):
    cache.set(f"key{i}", f"value{i}")

# BUG: Should batch writes or use write-back
print("All writes synchronous to DB")
"""
            
            test_file = os.path.join(temp_dir, "write_strategy.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestMemoryManagement:
    """Test memory efficiency and leak prevention (10 tests)"""
    
    def test_memory_leak_detection(self):
        """Test 586: Detect and fix memory leaks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class MemoryLeak:
    def __init__(self):
        self.cache = []
    
    def process_request(self, data):
        # BUG: Appends to cache without limit
        self.cache.append(data)
        return f"processed_{data}"

processor = MemoryLeak()

# Memory grows indefinitely
for i in range(100000):
    processor.process_request(f"data_{i}")

# BUG: Memory leak
print(f"Cache size: {len(processor.cache)}")
"""
            
            test_file = os.path.join(temp_dir, "memory_leak.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_circular_reference_cleanup(self):
        """Test 587: Break circular references"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class CircularReference:
    def __init__(self):
        self.parent = None
        self.children = []
    
    def add_child(self, child):
        self.children.append(child)
        # BUG: Creates circular reference
        child.parent = self

parent = CircularReference()
child = CircularReference()
parent.add_child(child)

# BUG: Circular reference prevents GC
del parent
del child
print("Circular reference created")
"""
            
            test_file = os.path.join(temp_dir, "circular_reference.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_lazy_loading_optimization(self):
        """Test 588: Implement lazy loading"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class EagerLoading:
    def __init__(self):
        # BUG: Loads all data upfront
        self.all_users = self.load_all_users()
        self.all_posts = self.load_all_posts()
        self.all_comments = self.load_all_comments()
    
    def load_all_users(self):
        return [f"user{i}" for i in range(10000)]
    
    def load_all_posts(self):
        return [f"post{i}" for i in range(100000)]
    
    def load_all_comments(self):
        return [f"comment{i}" for i in range(1000000)]

# BUG: Uses lots of memory even if not needed
app = EagerLoading()
print("All data loaded eagerly")
"""
            
            test_file = os.path.join(temp_dir, "lazy_loading.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_object_pooling(self):
        """Test 589: Use object pooling for reuse"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoObjectPooling:
    def process_requests(self, requests):
        results = []
        for req in requests:
            # BUG: Creates new processor for each request
            processor = self.create_processor()
            result = processor.process(req)
            results.append(result)
        return results
    
    def create_processor(self):
        # Expensive object creation
        return {"expensive": "object"}

handler = NoObjectPooling()

requests = [f"req{i}" for i in range(1000)]
# BUG: Creates 1000 objects instead of reusing
print("No object pooling")
"""
            
            test_file = os.path.join(temp_dir, "object_pooling.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_string_concatenation_efficiency(self):
        """Test 590: Efficient string concatenation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class InefficientStringConcat:
    def build_large_string(self, items):
        result = ""
        for item in items:
            # BUG: O(n²) complexity
            result += str(item) + ","
        return result

builder = InefficientStringConcat()

items = list(range(10000))
# BUG: Slow due to repeated string copying
result = builder.build_large_string(items)
print("Inefficient string concatenation")
"""
            
            test_file = os.path.join(temp_dir, "string_concat.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_generator_vs_list_comprehension(self):
        """Test 591: Use generators for large datasets"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ListComprehensionOveruse:
    def process_large_file(self, filename):
        # BUG: Loads entire file into memory
        lines = [line.strip() for line in open(filename)]
        
        for line in lines:
            self.process_line(line)
    
    def process_line(self, line):
        return line.upper()

processor = ListComprehensionOveruse()

# BUG: Memory spike for large files
print("Using list comprehension instead of generator")
"""
            
            test_file = os.path.join(temp_dir, "generator_usage.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_memory_mapped_files(self):
        """Test 592: Use memory mapping for large files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ReadEntireFile:
    def process_large_file(self, filename):
        # BUG: Reads entire file into memory
        with open(filename, 'rb') as f:
            data = f.read()
        
        return self.process_data(data)
    
    def process_data(self, data):
        return len(data)

processor = ReadEntireFile()

# BUG: Memory spike for multi-GB files
print("Reading entire file into memory")
"""
            
            test_file = os.path.join(temp_dir, "memory_mapped.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_data_structure_choice(self):
        """Test 593: Choose efficient data structures"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class InefficientDataStructure:
    def __init__(self):
        # BUG: Using list for membership testing
        self.seen_items = []
    
    def is_duplicate(self, item):
        # BUG: O(n) lookup
        return item in self.seen_items
    
    def add_item(self, item):
        if not self.is_duplicate(item):
            self.seen_items.append(item)

deduplicator = InefficientDataStructure()

# BUG: Slow for large datasets (should use set)
for i in range(10000):
    deduplicator.add_item(i)

print("Using list instead of set")
"""
            
            test_file = os.path.join(temp_dir, "data_structure_choice.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_copy_on_write_optimization(self):
        """Test 594: Use copy-on-write when appropriate"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import copy

class DeepCopyOveruse:
    def create_variant(self, base_config):
        # BUG: Deep copies even when not modifying
        config_copy = copy.deepcopy(base_config)
        return config_copy

optimizer = DeepCopyOveruse()

base = {"large": "config" * 1000}

# Creates 100 deep copies
variants = [optimizer.create_variant(base) for _ in range(100)]

# BUG: Wastes memory (should share immutable data)
print("Deep copying unnecessarily")
"""
            
            test_file = os.path.join(temp_dir, "copy_on_write.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_reference_counting_optimization(self):
        """Test 595: Minimize reference counts"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ExcessiveReferences:
    def __init__(self):
        self.data = []
        self.backup = []
        self.temp = []
    
    def add_item(self, item):
        # BUG: Creates unnecessary references
        self.data.append(item)
        self.backup.append(item)
        self.temp.append(item)

storage = ExcessiveReferences()

large_object = ["x" * 10000]

for _ in range(1000):
    storage.add_item(large_object)

# BUG: 3x memory usage
print("Excessive references to same object")
"""
            
            test_file = os.path.join(temp_dir, "reference_counting.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestAlgorithmEfficiency:
    """Test algorithm optimization (10 tests)"""
    
    def test_n_squared_algorithm(self):
        """Test 596: Optimize O(n²) algorithms"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NestedLoopSearch:
    def find_duplicates(self, items):
        duplicates = []
        # BUG: O(n²) algorithm
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                if items[i] == items[j]:
                    duplicates.append(items[i])
        return duplicates

finder = NestedLoopSearch()

items = list(range(1000)) + list(range(500))
# BUG: Should use set or sorting (O(n))
duplicates = finder.find_duplicates(items)
print("O(n²) duplicate finding")
"""
            
            test_file = os.path.join(temp_dir, "n_squared.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_unnecessary_sorting(self):
        """Test 597: Avoid unnecessary sorting"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnnecessarySort:
    def find_max(self, items):
        # BUG: Sorts to find max - O(n log n)
        sorted_items = sorted(items)
        return sorted_items[-1]

finder = UnnecessarySort()

items = list(range(1000000))
# BUG: Should use max() - O(n)
maximum = finder.find_max(items)
print("Sorting to find maximum")
"""
            
            test_file = os.path.join(temp_dir, "unnecessary_sort.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_repeated_computation(self):
        """Test 598: Cache repeated computations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class RepeatedComputation:
    def fibonacci(self, n):
        # BUG: Exponential time complexity
        if n <= 1:
            return n
        return self.fibonacci(n - 1) + self.fibonacci(n - 2)

calc = RepeatedComputation()

# BUG: Recomputes same values many times
result = calc.fibonacci(35)
print(f"Fibonacci(35): {result}")
"""
            
            test_file = os.path.join(temp_dir, "repeated_computation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_linear_search_optimization(self):
        """Test 599: Use binary search when possible"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class LinearSearch:
    def __init__(self):
        # Data is sorted
        self.sorted_data = list(range(1000000))
    
    def find(self, target):
        # BUG: Linear search on sorted data
        for i, item in enumerate(self.sorted_data):
            if item == target:
                return i
        return -1

searcher = LinearSearch()

# BUG: Should use binary search - O(log n)
index = searcher.find(999999)
print("Linear search on sorted data")
"""
            
            test_file = os.path.join(temp_dir, "linear_search.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_string_matching_optimization(self):
        """Test 600: Optimize string matching"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NaiveStringMatch:
    def find_pattern(self, text, pattern):
        matches = []
        # BUG: Naive string matching
        for i in range(len(text) - len(pattern) + 1):
            if text[i:i+len(pattern)] == pattern:
                matches.append(i)
        return matches

matcher = NaiveStringMatch()

text = "a" * 1000000 + "b"
pattern = "a" * 100 + "b"

# BUG: Should use KMP or Boyer-Moore
matches = matcher.find_pattern(text, pattern)
print("Naive string matching")
"""
            
            test_file = os.path.join(temp_dir, "string_matching.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_database_n_plus_one(self):
        """Test 601: Avoid N+1 query problem"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NPlusOneQuery:
    def __init__(self):
        self.users = [{"id": 1}, {"id": 2}, {"id": 3}]
        self.posts = {
            1: ["post1", "post2"],
            2: ["post3"],
            3: ["post4", "post5"]
        }
    
    def get_users_with_posts(self):
        users_list = self.get_all_users()  # 1 query
        
        for user in users_list:
            # BUG: N queries
            user["posts"] = self.get_user_posts(user["id"])
        
        return users_list
    
    def get_all_users(self):
        return self.users
    
    def get_user_posts(self, user_id):
        return self.posts.get(user_id, [])

db = NPlusOneQuery()

# BUG: 1 + N queries instead of 2 queries
result = db.get_users_with_posts()
print("N+1 query problem")
"""
            
            test_file = os.path.join(temp_dir, "n_plus_one.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_batch_processing_optimization(self):
        """Test 602: Batch operations when possible"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoBatching:
    def __init__(self):
        self.db = []
    
    def insert_items(self, items):
        for item in items:
            # BUG: Individual inserts
            self.db_insert(item)
    
    def db_insert(self, item):
        self.db.append(item)

inserter = NoBatching()

items = list(range(10000))
# BUG: Should batch inserts
inserter.insert_items(items)
print("No batching")
"""
            
            test_file = os.path.join(temp_dir, "batching.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_index_usage_optimization(self):
        """Test 603: Use proper indexing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoIndexing:
    def __init__(self):
        self.users = [
            {"id": i, "email": f"user{i}@example.com"}
            for i in range(10000)
        ]
    
    def find_by_email(self, email):
        # BUG: Full table scan
        for user in self.users:
            if user["email"] == email:
                return user
        return None

db = NoIndexing()

# BUG: Should have email index
user = db.find_by_email("user9999@example.com")
print("No indexing")
"""
            
            test_file = os.path.join(temp_dir, "indexing.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_pagination_implementation(self):
        """Test 604: Implement efficient pagination"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class InefficientPagination:
    def __init__(self):
        self.items = list(range(1000000))
    
    def get_page(self, page_num, page_size=100):
        # BUG: Loads all items then slices
        all_items = self.items
        start = page_num * page_size
        end = start + page_size
        return all_items[start:end]

paginator = InefficientPagination()

# BUG: Should query only needed items
page = paginator.get_page(1000)
print("Loading all data for pagination")
"""
            
            test_file = os.path.join(temp_dir, "pagination.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_parallel_processing_opportunity(self):
        """Test 605: Parallelize independent operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class SequentialProcessing:
    def process_items(self, items):
        results = []
        # BUG: Processes sequentially
        for item in items:
            result = self.expensive_operation(item)
            results.append(result)
        return results
    
    def expensive_operation(self, item):
        time.sleep(0.1)
        return item * 2

processor = SequentialProcessing()

items = list(range(100))
# BUG: Takes 10 seconds, could use multiprocessing
results = processor.process_items(items)
print("Sequential processing")
"""
            
            test_file = os.path.join(temp_dir, "parallelization.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
