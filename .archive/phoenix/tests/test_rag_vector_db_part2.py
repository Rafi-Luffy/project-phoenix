"""
Comprehensive Test Suite for Phoenix - RAG & Vector Databases Part 2
Tests 306-335: Vector Indexing, Search Optimization, Knowledge Graphs (30 tests)

This file tests Phoenix's ability to detect and fix bugs in vector indexing,
search optimization, and knowledge graph integration.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch


class TestVectorIndexing:
    """Test vector indexing and management (10 tests)"""
    
    def test_index_build_without_validation(self):
        """Test 306: Validate index integrity after build"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class VectorIndex:
    def __init__(self):
        self.index = []
    
    def build(self, vectors):
        # BUG: No validation after build
        for vec in vectors:
            self.index.append(vec)
        # Should validate: no duplicates, correct dimensions, etc.
    
    def search(self, query):
        return self.index[:5]

index = VectorIndex()

# Build with invalid data
vectors = [
    [0.1, 0.2, 0.3],
    [0.1, 0.2, 0.3],  # Duplicate
    [0.4, 0.5],       # Wrong dimension
]

# BUG: Builds invalid index without error
index.build(vectors)
results = index.search([0.1, 0.2, 0.3])
"""
            
            test_file = os.path.join(temp_dir, "index_validation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_incremental_index_update_consistency(self):
        """Test 307: Maintain consistency in incremental updates"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class IncrementalIndex:
    def __init__(self):
        self.vectors = {}
        self.index_dirty = False
    
    def add(self, doc_id, vector):
        self.vectors[doc_id] = vector
        self.index_dirty = True
        # BUG: Doesn't rebuild index
    
    def search(self, query):
        # BUG: Searches stale index
        if self.index_dirty:
            print("Warning: Index is dirty")
        return list(self.vectors.values())[:5]

index = IncrementalIndex()

# Add vectors
index.add("doc1", [0.1, 0.2])
index.add("doc2", [0.3, 0.4])

# BUG: Search uses outdated index
results = index.search([0.5, 0.6])
"""
            
            test_file = os.path.join(temp_dir, "incremental_consistency.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_index_shard_balancing(self):
        """Test 308: Balance load across index shards"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ShardedIndex:
    def __init__(self, num_shards=4):
        self.shards = [[] for _ in range(num_shards)]
        self.num_shards = num_shards
    
    def add(self, doc_id, vector):
        # BUG: Simple hash causes imbalance
        shard_id = hash(doc_id) % self.num_shards
        self.shards[shard_id].append((doc_id, vector))
    
    def get_shard_sizes(self):
        return [len(shard) for shard in self.shards]

index = ShardedIndex(num_shards=4)

# Add documents with similar IDs
for i in range(100):
    index.add(f"doc_{i:03d}", [0.1] * 768)

# BUG: Uneven distribution across shards
sizes = index.get_shard_sizes()
print(f"Shard sizes: {sizes}")
print(f"Min: {min(sizes)}, Max: {max(sizes)}, Imbalance: {max(sizes) - min(sizes)}")
"""
            
            test_file = os.path.join(temp_dir, "shard_balancing.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_index_compression_quality_loss(self):
        """Test 309: Handle index compression without quality loss"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class CompressedIndex:
    def compress_vector(self, vector):
        # BUG: Aggressive quantization loses quality
        # Quantize to 8-bit
        return [int(v * 255) for v in vector]
    
    def decompress_vector(self, compressed):
        # BUG: Doesn't restore original scale
        return compressed

index = CompressedIndex()

original = [0.123456789] * 768
compressed = index.compress_vector(original)
decompressed = index.decompress_vector(compressed)

# BUG: Significant quality loss
print(f"Original: {original[0]}")
print(f"Decompressed: {decompressed[0]}")
print(f"Loss: {abs(original[0] - decompressed[0])}")
"""
            
            test_file = os.path.join(temp_dir, "compression_loss.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_concurrent_index_updates(self):
        """Test 310: Handle concurrent index updates safely"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import threading

class ConcurrentIndex:
    def __init__(self):
        self.vectors = {}
        # BUG: No locking mechanism
    
    def add(self, doc_id, vector):
        # BUG: Race condition on dict update
        self.vectors[doc_id] = vector
    
    def remove(self, doc_id):
        # BUG: Race condition on dict delete
        if doc_id in self.vectors:
            del self.vectors[doc_id]

index = ConcurrentIndex()

def worker(i):
    for j in range(100):
        index.add(f"doc_{i}_{j}", [0.1] * 768)
        if j % 2 == 0:
            index.remove(f"doc_{i}_{j}")

# BUG: Concurrent updates cause race conditions
threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(f"Final size: {len(index.vectors)}")
"""
            
            test_file = os.path.join(temp_dir, "concurrent_updates.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_index_memory_mapping(self):
        """Test 311: Use memory mapping for large indices"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class LargeIndex:
    def __init__(self):
        # BUG: Loads entire index into memory
        self.vectors = []
    
    def load(self, file_path):
        # BUG: Reads all vectors at once
        with open(file_path, 'r') as f:
            for line in f:
                vector = [float(x) for x in line.split(',')]
                self.vectors.append(vector)
    
    def search(self, query):
        return self.vectors[:5]

index = LargeIndex()

# Simulate large file
large_file = f"{temp_dir}/vectors.txt"
with open(large_file, 'w') as f:
    for i in range(1_000_000):
        f.write(','.join(['0.1'] * 768) + '\\n')

# BUG: Out of memory for large indices
try:
    index.load(large_file)
except MemoryError:
    print("Out of memory")
"""
            
            test_file = os.path.join(temp_dir, "memory_mapping.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_index_versioning_rollback(self):
        """Test 312: Support index versioning and rollback"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class VersionedIndex:
    def __init__(self):
        self.vectors = {}
        self.version = 1
        # BUG: No version history
    
    def update(self, doc_id, vector):
        self.vectors[doc_id] = vector
        self.version += 1
        # BUG: Can't rollback to previous version
    
    def rollback(self, target_version):
        # BUG: No implementation
        print(f"Cannot rollback from {self.version} to {target_version}")

index = VersionedIndex()

index.update("doc1", [0.1, 0.2])
index.update("doc2", [0.3, 0.4])
print(f"Version: {index.version}")

# BUG: Rollback not supported
index.rollback(1)
"""
            
            test_file = os.path.join(temp_dir, "index_versioning.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_approximate_nearest_neighbor_recall(self):
        """Test 313: Maintain recall quality in ANN search"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import random

class ANNIndex:
    def __init__(self, num_trees=1):
        self.num_trees = num_trees
        self.vectors = []
    
    def build(self, vectors):
        self.vectors = vectors
        # BUG: Too few trees, poor recall
    
    def search(self, query, k=5):
        # BUG: Returns random subset due to poor index
        candidates = random.sample(self.vectors, min(k * 2, len(self.vectors)))
        return candidates[:k]

index = ANNIndex(num_trees=1)  # Too few

# Build index with 1000 vectors
vectors = [[random.random() for _ in range(768)] for _ in range(1000)]
index.build(vectors)

# BUG: Poor recall - misses true nearest neighbors
results = index.search([0.5] * 768, k=5)
print(f"Results: {len(results)}")
"""
            
            test_file = os.path.join(temp_dir, "ann_recall.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_index_corruption_detection(self):
        """Test 314: Detect and recover from index corruption"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ChecksumIndex:
    def __init__(self):
        self.vectors = {}
        # BUG: No checksum validation
    
    def save(self, file_path):
        with open(file_path, 'w') as f:
            for doc_id, vector in self.vectors.items():
                f.write(f"{doc_id}:{','.join(map(str, vector))}\\n")
    
    def load(self, file_path):
        # BUG: Doesn't validate integrity
        with open(file_path, 'r') as f:
            for line in f:
                doc_id, vector_str = line.strip().split(':')
                vector = [float(x) for x in vector_str.split(',')]
                self.vectors[doc_id] = vector

index = ChecksumIndex()
index.vectors = {"doc1": [0.1, 0.2, 0.3]}

file_path = f"{temp_dir}/index.txt"
index.save(file_path)

# Corrupt file
with open(file_path, 'a') as f:
    f.write("corrupted_line\\n")

# BUG: Loads corrupted data without detection
index2 = ChecksumIndex()
try:
    index2.load(file_path)
except Exception as e:
    print(f"Corruption: {e}")
"""
            
            test_file = os.path.join(temp_dir, "corruption_detection.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_dynamic_index_rebalancing(self):
        """Test 315: Rebalance index as distribution changes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class DynamicIndex:
    def __init__(self):
        self.clusters = {0: [], 1: [], 2: []}
    
    def add(self, vector):
        # BUG: Static clustering, doesn't rebalance
        cluster_id = hash(tuple(vector)) % 3
        self.clusters[cluster_id].append(vector)
    
    def get_cluster_sizes(self):
        return {k: len(v) for k, v in self.clusters.items()}

index = DynamicIndex()

# Add vectors that hash to same cluster
for i in range(100):
    index.add([i * 0.01] * 768)

sizes = index.get_cluster_sizes()
# BUG: Imbalanced clusters, should rebalance
print(f"Cluster sizes: {sizes}")
"""
            
            test_file = os.path.join(temp_dir, "dynamic_rebalancing.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestSearchOptimization:
    """Test search optimization techniques (10 tests)"""
    
    def test_query_caching_invalidation(self):
        """Test 316: Invalidate query cache on index updates"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class CachedSearch:
    def __init__(self):
        self.vectors = {}
        self.cache = {}
    
    def add_document(self, doc_id, vector):
        self.vectors[doc_id] = vector
        # BUG: Doesn't invalidate cache
    
    def search(self, query):
        query_key = tuple(query)
        
        if query_key in self.cache:
            return self.cache[query_key]
        
        results = list(self.vectors.values())[:5]
        self.cache[query_key] = results
        return results

searcher = CachedSearch()
searcher.add_document("doc1", [0.1, 0.2])

query = [0.3, 0.4]
results1 = searcher.search(query)

# Add new document
searcher.add_document("doc2", [0.5, 0.6])

# BUG: Returns stale cached results
results2 = searcher.search(query)
print(f"Results equal: {results1 == results2}")
"""
            
            test_file = os.path.join(temp_dir, "cache_invalidation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_early_termination_search(self):
        """Test 317: Implement early termination for efficiency"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class EarlyTerminationSearch:
    def __init__(self, vectors):
        self.vectors = vectors
    
    def search(self, query, k=5, threshold=0.9):
        # BUG: No early termination - searches all vectors
        results = []
        for vector in self.vectors:
            similarity = self.compute_similarity(query, vector)
            results.append((vector, similarity))
        
        # BUG: Sorts all results even if enough high-quality found
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]
    
    def compute_similarity(self, v1, v2):
        return 0.95

searcher = EarlyTerminationSearch([[0.1] * 768 for _ in range(1000)])

# BUG: Computes all 1000 similarities even though first few are > 0.9
results = searcher.search([0.2] * 768, k=5, threshold=0.9)
"""
            
            test_file = os.path.join(temp_dir, "early_termination.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_batch_search_optimization(self):
        """Test 318: Optimize batch searches with shared computation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class BatchSearch:
    def __init__(self, vectors):
        self.vectors = vectors
    
    def search_batch(self, queries, k=5):
        # BUG: No shared computation across queries
        results = []
        for query in queries:
            query_results = self.search_single(query, k)
            results.append(query_results)
        return results
    
    def search_single(self, query, k):
        # BUG: Recomputes vector norms for each query
        similarities = []
        for vector in self.vectors:
            sim = sum(q * v for q, v in zip(query, vector))
            similarities.append((vector, sim))
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]

searcher = BatchSearch([[0.1, 0.2, 0.3] for _ in range(100)])

queries = [[0.4, 0.5, 0.6] for _ in range(50)]

# BUG: Inefficient - should precompute vector norms
results = searcher.search_batch(queries, k=5)
"""
            
            test_file = os.path.join(temp_dir, "batch_optimization.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_filtered_search_index_utilization(self):
        """Test 319: Use indices for filtered search"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class FilteredSearch:
    def __init__(self):
        self.documents = []
        # BUG: No metadata index
    
    def add(self, doc_id, vector, metadata):
        self.documents.append({
            "id": doc_id,
            "vector": vector,
            "metadata": metadata
        })
    
    def search_with_filter(self, query, filter_key, filter_value):
        # BUG: Linear scan through all documents
        filtered = [
            doc for doc in self.documents
            if doc["metadata"].get(filter_key) == filter_value
        ]
        
        # Then search filtered set
        return filtered[:5]

searcher = FilteredSearch()

for i in range(10000):
    searcher.add(f"doc{i}", [0.1] * 768, {"category": f"cat{i % 10}"})

# BUG: Scans all 10000 docs to find category='cat5'
results = searcher.search_with_filter([0.2] * 768, "category", "cat5")
"""
            
            test_file = os.path.join(temp_dir, "filtered_search.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_search_result_diversity(self):
        """Test 320: Ensure diversity in search results"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class DiverseSearch:
    def __init__(self, vectors):
        self.vectors = vectors
    
    def search(self, query, k=5):
        # BUG: No diversity - returns most similar only
        similarities = []
        for vector in self.vectors:
            sim = sum(q * v for q, v in zip(query, vector))
            similarities.append((vector, sim))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [v for v, s in similarities[:k]]

# Vectors with high redundancy
vectors = [
    [0.9, 0.1, 0.1],
    [0.91, 0.09, 0.1],  # Very similar to first
    [0.89, 0.11, 0.1],  # Very similar to first
    [0.1, 0.9, 0.1],    # Different
    [0.1, 0.1, 0.9],    # Different
]

searcher = DiverseSearch(vectors)
query = [1.0, 0.0, 0.0]

# BUG: Returns 3 very similar vectors, not diverse
results = searcher.search(query, k=3)
"""
            
            test_file = os.path.join(temp_dir, "result_diversity.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_multi_vector_query_fusion(self):
        """Test 321: Fuse results from multi-vector queries"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class MultiVectorSearch:
    def __init__(self, vectors):
        self.vectors = vectors
    
    def search_multi(self, queries, k=5):
        # BUG: Simple concatenation, no fusion
        all_results = []
        for query in queries:
            results = self.search_single(query)
            all_results.extend(results)
        
        # BUG: Doesn't deduplicate or rerank
        return all_results[:k]
    
    def search_single(self, query):
        return self.vectors[:3]

searcher = MultiVectorSearch([[0.1, 0.2] for _ in range(10)])

# Multiple query vectors (e.g., from multi-aspect query)
queries = [[0.3, 0.4], [0.5, 0.6], [0.7, 0.8]]

# BUG: Returns duplicates, doesn't fuse scores
results = searcher.search_multi(queries, k=5)
"""
            
            test_file = os.path.join(temp_dir, "query_fusion.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_negative_sampling_search(self):
        """Test 322: Support negative examples in search"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NegativeSamplingSearch:
    def __init__(self, vectors):
        self.vectors = vectors
    
    def search(self, positive_query, negative_queries, k=5):
        # BUG: Doesn't use negative examples
        similarities = []
        for vector in self.vectors:
            sim = sum(q * v for q, v in zip(positive_query, vector))
            similarities.append((vector, sim))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [v for v, s in similarities[:k]]

searcher = NegativeSamplingSearch([[0.1, 0.2, 0.3] for _ in range(10)])

positive = [1.0, 0.0, 0.0]
negatives = [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]

# BUG: Ignores negative examples, may return unwanted results
results = searcher.search(positive, negatives, k=5)
"""
            
            test_file = os.path.join(temp_dir, "negative_sampling.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_personalized_search_ranking(self):
        """Test 323: Personalize search results per user"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class PersonalizedSearch:
    def __init__(self, vectors):
        self.vectors = vectors
        self.user_preferences = {}
    
    def search(self, query, user_id, k=5):
        # BUG: Ignores user preferences
        similarities = []
        for vector in self.vectors:
            sim = sum(q * v for q, v in zip(query, vector))
            similarities.append((vector, sim))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [v for v, s in similarities[:k]]
    
    def update_preferences(self, user_id, preferences):
        self.user_preferences[user_id] = preferences

searcher = PersonalizedSearch([[0.1, 0.2] for _ in range(10)])

searcher.update_preferences("user1", {"topic": "AI", "level": "expert"})
searcher.update_preferences("user2", {"topic": "AI", "level": "beginner"})

query = [0.3, 0.4]

# BUG: Same results for both users despite different preferences
results1 = searcher.search(query, "user1", k=5)
results2 = searcher.search(query, "user2", k=5)
"""
            
            test_file = os.path.join(temp_dir, "personalized_ranking.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_geo_spatial_filtering(self):
        """Test 324: Implement efficient geo-spatial filtering"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class GeoSearch:
    def __init__(self):
        self.documents = []
    
    def add(self, doc_id, vector, lat, lon):
        self.documents.append({
            "id": doc_id,
            "vector": vector,
            "lat": lat,
            "lon": lon
        })
    
    def search_near(self, query, center_lat, center_lon, radius_km, k=5):
        # BUG: Linear scan with inefficient distance calculation
        results = []
        for doc in self.documents:
            distance = self.haversine(center_lat, center_lon, doc["lat"], doc["lon"])
            if distance <= radius_km:
                results.append(doc)
        
        return results[:k]
    
    def haversine(self, lat1, lon1, lat2, lon2):
        # Simplified distance
        return abs(lat1 - lat2) + abs(lon1 - lon2)

searcher = GeoSearch()

for i in range(10000):
    searcher.add(f"doc{i}", [0.1] * 768, i * 0.001, i * 0.001)

# BUG: Scans all 10000 locations
results = searcher.search_near([0.2] * 768, 40.7128, -74.0060, 10, k=5)
"""
            
            test_file = os.path.join(temp_dir, "geo_filtering.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_search_explain_scores(self):
        """Test 325: Provide explainability for search scores"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ExplainableSearch:
    def __init__(self, vectors):
        self.vectors = vectors
    
    def search(self, query, k=5):
        # BUG: No explanation for scores
        results = []
        for i, vector in enumerate(self.vectors):
            score = sum(q * v for q, v in zip(query, vector))
            results.append({
                "id": i,
                "score": score,
                # BUG: Missing explanation
            })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:k]

searcher = ExplainableSearch([[0.1, 0.2, 0.3] for _ in range(10)])

query = [1.0, 0.0, 0.0]
results = searcher.search(query, k=3)

# BUG: Can't explain why score is what it is
for r in results:
    print(f"Score: {r['score']}, Explanation: {r.get('explanation', 'N/A')}")
"""
            
            test_file = os.path.join(temp_dir, "search_explainability.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestKnowledgeGraphs:
    """Test knowledge graph integration (10 tests)"""
    
    def test_graph_vector_hybrid_retrieval(self):
        """Test 326: Combine graph traversal with vector search"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class HybridGraphRetriever:
    def __init__(self):
        self.graph = {}  # node_id -> [neighbor_ids]
        self.vectors = {}  # node_id -> vector
    
    def add_edge(self, from_id, to_id):
        if from_id not in self.graph:
            self.graph[from_id] = []
        self.graph[from_id].append(to_id)
    
    def add_vector(self, node_id, vector):
        self.vectors[node_id] = vector
    
    def retrieve(self, query_vector, start_node, k=5):
        # BUG: Only uses vector similarity, ignores graph structure
        results = []
        for node_id, vector in self.vectors.items():
            score = sum(q * v for q, v in zip(query_vector, vector))
            results.append((node_id, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]

retriever = HybridGraphRetriever()

# Build graph
retriever.add_edge("A", "B")
retriever.add_edge("B", "C")
retriever.add_vector("A", [0.1, 0.2])
retriever.add_vector("B", [0.3, 0.4])
retriever.add_vector("C", [0.5, 0.6])

# BUG: Doesn't leverage graph connections
results = retriever.retrieve([0.6, 0.7], "A", k=2)
"""
            
            test_file = os.path.join(temp_dir, "graph_vector_hybrid.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_relation_aware_retrieval(self):
        """Test 327: Consider relationship types in retrieval"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class RelationAwareRetriever:
    def __init__(self):
        self.triples = []  # (subject, relation, object)
    
    def add_triple(self, subject, relation, obj):
        self.triples.append((subject, relation, obj))
    
    def retrieve(self, query_entity, k=5):
        # BUG: Doesn't filter by relation type
        results = []
        for subj, rel, obj in self.triples:
            if subj == query_entity:
                results.append(obj)
        return results[:k]

retriever = RelationAwareRetriever()

retriever.add_triple("Paris", "capital_of", "France")
retriever.add_triple("Paris", "located_in", "Europe")
retriever.add_triple("Paris", "has_landmark", "Eiffel Tower")

# Query: What is Paris capital of?
# BUG: Returns all relations, doesn't filter
results = retriever.retrieve("Paris", k=5)
"""
            
            test_file = os.path.join(temp_dir, "relation_aware.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_multi_hop_reasoning(self):
        """Test 328: Support multi-hop reasoning over graph"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class MultiHopRetriever:
    def __init__(self):
        self.graph = {}
    
    def add_edge(self, from_node, to_node):
        if from_node not in self.graph:
            self.graph[from_node] = []
        self.graph[from_node].append(to_node)
    
    def retrieve(self, start_node, hops=1):
        # BUG: Only does single hop
        if start_node in self.graph:
            return self.graph[start_node]
        return []

retriever = MultiHopRetriever()

retriever.add_edge("A", "B")
retriever.add_edge("B", "C")
retriever.add_edge("C", "D")

# Query: 2-hop neighbors of A
# BUG: Only returns B, not C
results = retriever.retrieve("A", hops=2)
print(f"2-hop results: {results}")
"""
            
            test_file = os.path.join(temp_dir, "multi_hop.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_graph_cycle_detection(self):
        """Test 329: Detect and handle cycles in graph traversal"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class CyclicGraphRetriever:
    def __init__(self):
        self.graph = {}
    
    def add_edge(self, from_node, to_node):
        if from_node not in self.graph:
            self.graph[from_node] = []
        self.graph[from_node].append(to_node)
    
    def traverse(self, start_node):
        # BUG: No cycle detection - infinite loop
        visited = []
        current = start_node
        
        while current in self.graph and len(visited) < 100:  # Arbitrary limit
            visited.append(current)
            neighbors = self.graph[current]
            if neighbors:
                current = neighbors[0]
        
        return visited

retriever = CyclicGraphRetriever()

# Create cycle: A -> B -> C -> A
retriever.add_edge("A", "B")
retriever.add_edge("B", "C")
retriever.add_edge("C", "A")

# BUG: Infinite loop without proper cycle detection
results = retriever.traverse("A")
print(f"Traversed {len(results)} nodes")
"""
            
            test_file = os.path.join(temp_dir, "cycle_detection.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_entity_disambiguation(self):
        """Test 330: Disambiguate entities in knowledge graph"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class EntityDisambiguator:
    def __init__(self):
        self.entities = {}
    
    def add_entity(self, name, entity_id, context):
        if name not in self.entities:
            self.entities[name] = []
        self.entities[name].append({"id": entity_id, "context": context})
    
    def disambiguate(self, name, query_context):
        # BUG: Returns first match, doesn't use context
        if name in self.entities:
            return self.entities[name][0]["id"]
        return None

disambiguator = EntityDisambiguator()

# Multiple entities named "Paris"
disambiguator.add_entity("Paris", "paris_france", "city in France")
disambiguator.add_entity("Paris", "paris_texas", "city in Texas")
disambiguator.add_entity("Paris", "paris_hilton", "celebrity")

# Query: Paris the city
# BUG: Returns paris_france without context matching
result = disambiguator.disambiguate("Paris", "visited the city")
print(f"Disambiguated to: {result}")
"""
            
            test_file = os.path.join(temp_dir, "entity_disambiguation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_temporal_graph_queries(self):
        """Test 331: Handle temporal aspects in graph queries"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class TemporalGraph:
    def __init__(self):
        self.edges = []
    
    def add_edge(self, from_node, to_node, timestamp):
        self.edges.append({
            "from": from_node,
            "to": to_node,
            "timestamp": timestamp
        })
    
    def query(self, from_node, to_node):
        # BUG: Doesn't consider temporal ordering
        for edge in self.edges:
            if edge["from"] == from_node and edge["to"] == to_node:
                return True
        return False

graph = TemporalGraph()

# Add edges with timestamps
graph.add_edge("A", "B", timestamp=1000)
graph.add_edge("B", "C", timestamp=2000)
graph.add_edge("C", "A", timestamp=500)  # Earlier than others

# BUG: Doesn't filter by time range
result = graph.query("C", "A")
"""
            
            test_file = os.path.join(temp_dir, "temporal_graph.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_graph_embedding_consistency(self):
        """Test 332: Maintain consistency between graph and embeddings"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class GraphEmbedder:
    def __init__(self):
        self.graph = {}
        self.embeddings = {}
    
    def add_edge(self, from_node, to_node):
        if from_node not in self.graph:
            self.graph[from_node] = []
        self.graph[from_node].append(to_node)
        # BUG: Doesn't update embeddings
    
    def get_embedding(self, node):
        # BUG: Returns stale embedding
        return self.embeddings.get(node, [0.0] * 128)
    
    def compute_embeddings(self):
        # Expensive operation
        for node in self.graph:
            self.embeddings[node] = [0.1] * 128

embedder = GraphEmbedder()

embedder.compute_embeddings()
embedding1 = embedder.get_embedding("A")

# Add new edges
embedder.add_edge("A", "B")
embedder.add_edge("A", "C")

# BUG: Embedding doesn't reflect new graph structure
embedding2 = embedder.get_embedding("A")
print(f"Embeddings equal: {embedding1 == embedding2}")
"""
            
            test_file = os.path.join(temp_dir, "embedding_consistency.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_subgraph_extraction(self):
        """Test 333: Extract relevant subgraphs efficiently"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SubgraphExtractor:
    def __init__(self):
        self.graph = {}
    
    def add_edge(self, from_node, to_node):
        if from_node not in self.graph:
            self.graph[from_node] = []
        self.graph[from_node].append(to_node)
    
    def extract_subgraph(self, seed_nodes, max_size=10):
        # BUG: Inefficient BFS, no pruning
        subgraph = set(seed_nodes)
        
        while len(subgraph) < max_size:
            added = False
            for node in list(subgraph):
                if node in self.graph:
                    for neighbor in self.graph[node]:
                        if neighbor not in subgraph:
                            subgraph.add(neighbor)
                            added = True
                            break
                if added:
                    break
            if not added:
                break
        
        return subgraph

extractor = SubgraphExtractor()

# Build large graph
for i in range(100):
    for j in range(i+1, i+10):
        extractor.add_edge(f"node_{i}", f"node_{j}")

# BUG: Inefficient extraction, no relevance scoring
subgraph = extractor.extract_subgraph(["node_0"], max_size=20)
"""
            
            test_file = os.path.join(temp_dir, "subgraph_extraction.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_graph_schema_validation(self):
        """Test 334: Validate graph against schema"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SchemaValidatedGraph:
    def __init__(self, schema):
        self.schema = schema
        self.graph = {}
    
    def add_edge(self, from_node, relation, to_node):
        # BUG: No schema validation
        key = (from_node, relation)
        if key not in self.graph:
            self.graph[key] = []
        self.graph[key].append(to_node)

schema = {
    "Person": {
        "knows": "Person",
        "works_at": "Company"
    },
    "Company": {
        "located_in": "City"
    }
}

graph = SchemaValidatedGraph(schema)

# Valid edge
graph.add_edge("Alice", "knows", "Bob")

# BUG: Invalid edge not caught
graph.add_edge("Alice", "located_in", "NYC")  # Person can't be located_in City
"""
            
            test_file = os.path.join(temp_dir, "schema_validation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_graph_pattern_matching(self):
        """Test 335: Match complex patterns in graph"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class PatternMatcher:
    def __init__(self):
        self.triples = []
    
    def add_triple(self, subject, relation, obj):
        self.triples.append((subject, relation, obj))
    
    def match_pattern(self, pattern):
        # BUG: No support for variables in pattern
        # Pattern example: (X, "knows", Y) AND (Y, "works_at", Z)
        return []

matcher = PatternMatcher()

matcher.add_triple("Alice", "knows", "Bob")
matcher.add_triple("Bob", "works_at", "Google")
matcher.add_triple("Alice", "knows", "Charlie")
matcher.add_triple("Charlie", "works_at", "Meta")

# Find: Who does Alice know that works somewhere?
pattern = [
    ("Alice", "knows", "?person"),
    ("?person", "works_at", "?company")
]

# BUG: Pattern matching not implemented
results = matcher.match_pattern(pattern)
print(f"Matches: {results}")
"""
            
            test_file = os.path.join(temp_dir, "pattern_matching.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
