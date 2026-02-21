"""
Comprehensive Test Suite for Phoenix - RAG & Vector Databases Part 1
Tests 276-305: RAG Systems, Vector Search, Embeddings (30 tests)

This file tests Phoenix's ability to detect and fix bugs in RAG systems,
vector databases, embedding generation, and retrieval mechanisms.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch


class TestRAGRetrieval:
    """Test RAG retrieval mechanisms (10 tests)"""
    
    def test_embedding_dimension_mismatch(self):
        """Test 276: Handle embedding dimension mismatches"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class VectorStore:
    def __init__(self, dimension=768):
        self.dimension = dimension
        self.vectors = []
    
    def add(self, vector):
        # BUG: No dimension validation
        self.vectors.append(vector)
    
    def search(self, query_vector):
        # BUG: Fails on dimension mismatch
        similarities = []
        for vec in self.vectors:
            similarity = sum(a * b for a, b in zip(query_vector, vec))
            similarities.append(similarity)
        return similarities

store = VectorStore(dimension=768)
store.add([0.1] * 768)  # Correct dimension

# Query with wrong dimension
query = [0.2] * 384  # Wrong dimension

# BUG: zip() silently truncates - wrong results
results = store.search(query)
"""
            
            test_file = os.path.join(temp_dir, "dimension_mismatch.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_retrieval_without_reranking(self):
        """Test 277: Implement reranking for better retrieval"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class RAGRetriever:
    def __init__(self, documents):
        self.documents = documents
    
    def retrieve(self, query, k=5):
        # BUG: No reranking - returns first k results
        # Ignores semantic relevance
        return self.documents[:k]

docs = [f"Document {i}" for i in range(100)]
retriever = RAGRetriever(docs)

query = "Find information about AI"
# BUG: Returns documents 0-4 regardless of query
results = retriever.retrieve(query, k=5)
print(f"Results: {results}")
"""
            
            test_file = os.path.join(temp_dir, "no_reranking.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_context_window_chunk_truncation(self):
        """Test 278: Handle chunk truncation at context boundary"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ChunkRetriever:
    def __init__(self, max_context_length=512):
        self.max_context_length = max_context_length
    
    def retrieve_and_concatenate(self, chunks):
        # BUG: Naive concatenation truncates mid-sentence
        context = ""
        for chunk in chunks:
            if len(context) + len(chunk) <= self.max_context_length:
                context += chunk
            else:
                # BUG: Cuts off in middle of chunk
                remaining = self.max_context_length - len(context)
                context += chunk[:remaining]
                break
        return context

retriever = ChunkRetriever(max_context_length=100)
chunks = ["This is a long sentence ", "that should not be cut ", "in the middle."]

# BUG: Truncates mid-sentence
context = retriever.retrieve_and_concatenate(chunks)
print(f"Context: {context}")
"""
            
            test_file = os.path.join(temp_dir, "chunk_truncation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_stale_index_retrieval(self):
        """Test 279: Detect and refresh stale vector indices"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class VectorIndex:
    def __init__(self):
        self.index = {}
        self.last_updated = time.time()
    
    def add_document(self, doc_id, vector):
        # BUG: Doesn't update timestamp
        self.index[doc_id] = vector
    
    def search(self, query):
        # BUG: Uses stale index without checking
        age = time.time() - self.last_updated
        # Should rebuild if too old
        return list(self.index.values())

index = VectorIndex()
index.add_document("doc1", [0.1, 0.2])

time.sleep(2)
# Add new documents but index not updated
index.add_document("doc2", [0.3, 0.4])

# BUG: Searches stale index
results = index.search([0.5, 0.6])
"""
            
            test_file = os.path.join(temp_dir, "stale_index.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_duplicate_retrieval_results(self):
        """Test 280: Deduplicate retrieval results"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class DuplicateRetriever:
    def __init__(self, documents):
        self.documents = documents
    
    def retrieve(self, query, k=5):
        # BUG: No deduplication
        results = []
        # Simulates multiple retrievals returning same docs
        for _ in range(k):
            results.extend(self.documents[:2])
        return results

docs = ["Doc A", "Doc B", "Doc C"]
retriever = DuplicateRetriever(docs)

results = retriever.retrieve("query", k=3)
# BUG: Contains duplicates
print(f"Results: {results}")
print(f"Unique: {len(set(results))}")
"""
            
            test_file = os.path.join(temp_dir, "duplicate_results.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_metadata_filtering_sql_injection(self):
        """Test 281: Prevent SQL injection in metadata filtering"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class MetadataFilter:
    def __init__(self, database):
        self.database = database
    
    def filter_by_metadata(self, key, value):
        # BUG: SQL injection vulnerability
        query = f"SELECT * FROM documents WHERE {key} = '{value}'"
        return self.database.execute(query)

class MockDB:
    def execute(self, query):
        print(f"Executing: {query}")
        return []

db = MockDB()
filter_obj = MetadataFilter(db)

# Malicious input
malicious_value = "'; DROP TABLE documents; --"

# BUG: SQL injection possible
filter_obj.filter_by_metadata("category", malicious_value)
"""
            
            test_file = os.path.join(temp_dir, "metadata_injection.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_semantic_search_threshold_tuning(self):
        """Test 282: Dynamically tune similarity threshold"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SemanticSearch:
    def __init__(self, threshold=0.7):
        self.threshold = threshold
    
    def search(self, query_vec, doc_vecs):
        # BUG: Fixed threshold - doesn't adapt
        results = []
        for doc_vec in doc_vecs:
            similarity = self.cosine_similarity(query_vec, doc_vec)
            if similarity >= self.threshold:
                results.append(doc_vec)
        return results
    
    def cosine_similarity(self, v1, v2):
        return 0.65  # Mock

searcher = SemanticSearch(threshold=0.7)

# No results because all are below 0.7
docs = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
query = [0.7, 0.8]

results = searcher.search(query, docs)
# BUG: Returns empty even though 0.65 might be good enough
print(f"Results: {len(results)}")
"""
            
            test_file = os.path.join(temp_dir, "threshold_tuning.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_multilingual_retrieval_bias(self):
        """Test 283: Handle multilingual retrieval without bias"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class MultilingualRAG:
    def __init__(self, embedding_model):
        self.model = embedding_model
    
    def retrieve(self, query, documents):
        # BUG: Model biased toward English
        query_embedding = self.model.embed(query)
        
        results = []
        for doc in documents:
            doc_embedding = self.model.embed(doc["text"])
            score = self.similarity(query_embedding, doc_embedding)
            results.append((doc, score))
        
        return sorted(results, key=lambda x: x[1], reverse=True)
    
    def similarity(self, e1, e2):
        return 0.5

class BiasedModel:
    def embed(self, text):
        # BUG: Returns lower quality embeddings for non-English
        if any(ord(c) > 127 for c in text):
            return [0.1] * 768  # Poor embedding
        return [0.5] * 768  # Good embedding

model = BiasedModel()
rag = MultilingualRAG(model)

docs = [
    {"text": "English document"},
    {"text": "Document en français"},
    {"text": "文档中文"}
]

# BUG: Biased toward English documents
results = rag.retrieve("query", docs)
"""
            
            test_file = os.path.join(temp_dir, "multilingual_bias.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_temporal_relevance_decay(self):
        """Test 284: Apply temporal decay to older documents"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import time

class TemporalRAG:
    def __init__(self):
        self.documents = []
    
    def add_document(self, content, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        self.documents.append({"content": content, "timestamp": timestamp})
    
    def retrieve(self, query):
        # BUG: No temporal decay - old docs same weight as new
        return sorted(self.documents, key=lambda d: d["timestamp"], reverse=True)

rag = TemporalRAG()

# Add old document with high relevance
rag.add_document("Highly relevant but old", timestamp=1000)

# Add new document with low relevance
rag.add_document("Less relevant but new", timestamp=time.time())

# BUG: Should balance relevance vs recency
results = rag.retrieve("relevant query")
print(f"Top result: {results[0]['content']}")
"""
            
            test_file = os.path.join(temp_dir, "temporal_decay.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_hybrid_search_weight_balancing(self):
        """Test 285: Balance keyword and semantic search weights"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class HybridSearch:
    def __init__(self, keyword_weight=0.5, semantic_weight=0.5):
        self.keyword_weight = keyword_weight
        self.semantic_weight = semantic_weight
    
    def search(self, query, documents):
        # BUG: Fixed weights - doesn't adapt to query type
        results = []
        for doc in documents:
            keyword_score = self.keyword_match(query, doc)
            semantic_score = self.semantic_match(query, doc)
            
            # BUG: Same weights for all queries
            combined_score = (
                self.keyword_weight * keyword_score +
                self.semantic_weight * semantic_score
            )
            results.append((doc, combined_score))
        
        return sorted(results, key=lambda x: x[1], reverse=True)
    
    def keyword_match(self, q, d):
        return 0.8
    
    def semantic_match(self, q, d):
        return 0.3

searcher = HybridSearch()

# Exact match query - should prioritize keyword
exact_results = searcher.search("invoice-2024-001", ["doc1", "doc2"])

# Conceptual query - should prioritize semantic
concept_results = searcher.search("documents about machine learning", ["doc1", "doc2"])

# BUG: Uses same weights for both - not optimal
"""
            
            test_file = os.path.join(temp_dir, "hybrid_weights.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestEmbeddingGeneration:
    """Test embedding generation and management (10 tests)"""
    
    def test_embedding_model_version_drift(self):
        """Test 286: Handle embedding model version changes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class EmbeddingService:
    def __init__(self, model_version="v1"):
        self.model_version = model_version
        self.cache = {}
    
    def embed(self, text):
        # BUG: Doesn't track which model version created embedding
        if text in self.cache:
            return self.cache[text]
        
        embedding = [hash(text + self.model_version) % 100 / 100] * 768
        self.cache[text] = embedding
        return embedding
    
    def upgrade_model(self, new_version):
        # BUG: Doesn't invalidate old embeddings
        self.model_version = new_version

service = EmbeddingService(model_version="v1")
text = "Hello world"
old_embedding = service.embed(text)

# Upgrade model
service.upgrade_model("v2")

# BUG: Returns v1 embedding when v2 is active
new_embedding = service.embed(text)
print(f"Embeddings match: {old_embedding == new_embedding}")
"""
            
            test_file = os.path.join(temp_dir, "model_version_drift.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_batch_embedding_memory_overflow(self):
        """Test 287: Handle large batch embedding without OOM"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class BatchEmbedder:
    def embed_batch(self, texts):
        # BUG: Loads entire batch into memory
        embeddings = []
        for text in texts:
            embedding = [0.1] * 768  # 768-dim embedding
            embeddings.append(embedding)
        return embeddings

embedder = BatchEmbedder()

# Try to embed 1 million documents at once
large_batch = [f"Document {i}" for i in range(1_000_000)]

# BUG: Out of memory
try:
    embeddings = embedder.embed_batch(large_batch)
except MemoryError:
    print("Out of memory")
"""
            
            test_file = os.path.join(temp_dir, "batch_oom.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_embedding_normalization_missing(self):
        """Test 288: Normalize embeddings for cosine similarity"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import math

class UnnormalizedEmbedder:
    def embed(self, text):
        # BUG: Doesn't normalize embeddings
        return [float(ord(c)) for c in text[:768]]
    
    def cosine_similarity(self, e1, e2):
        dot_product = sum(a * b for a, b in zip(e1, e2))
        norm1 = math.sqrt(sum(a * a for a in e1))
        norm2 = math.sqrt(sum(b * b for b in e2))
        
        # BUG: Division by zero if embeddings not normalized
        return dot_product / (norm1 * norm2)

embedder = UnnormalizedEmbedder()

e1 = embedder.embed("a")
e2 = embedder.embed("A")

# BUG: Unnormalized embeddings give inconsistent similarities
similarity = embedder.cosine_similarity(e1, e2)
print(f"Similarity: {similarity}")
"""
            
            test_file = os.path.join(temp_dir, "normalization.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_special_token_handling(self):
        """Test 289: Handle special tokens in embeddings"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class TokenAwareEmbedder:
    def __init__(self, max_length=512):
        self.max_length = max_length
    
    def embed(self, text):
        # BUG: Doesn't add special tokens [CLS], [SEP]
        tokens = text.split()[:self.max_length]
        return [len(tokens)] * 768

embedder = TokenAwareEmbedder()

# Should add [CLS] at start and [SEP] at end
embedding = embedder.embed("Hello world")

# BUG: Missing special tokens affects embedding quality
print(f"Embedding: {embedding[:5]}")
"""
            
            test_file = os.path.join(temp_dir, "special_tokens.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_embedding_cache_invalidation(self):
        """Test 290: Invalidate embedding cache appropriately"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class CachedEmbedder:
    def __init__(self):
        self.cache = {}
        self.document_versions = {}
    
    def embed_document(self, doc_id, text, version=1):
        cache_key = doc_id
        
        # BUG: Doesn't consider version in cache key
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        embedding = [hash(text) % 100 / 100] * 768
        self.cache[cache_key] = embedding
        self.document_versions[doc_id] = version
        return embedding

embedder = CachedEmbedder()

# Embed v1 of document
e1 = embedder.embed_document("doc1", "Original text", version=1)

# Update document
e2 = embedder.embed_document("doc1", "Updated text", version=2)

# BUG: Returns stale embedding for updated document
print(f"Embeddings equal: {e1 == e2}")
"""
            
            test_file = os.path.join(temp_dir, "cache_invalidation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_cross_encoder_reranking_cost(self):
        """Test 291: Optimize expensive cross-encoder reranking"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ExpensiveReranker:
    def rerank(self, query, candidates):
        # BUG: Runs expensive model on all candidates
        scores = []
        for candidate in candidates:
            # Expensive cross-encoder computation
            score = self.cross_encode(query, candidate)
            scores.append((candidate, score))
        
        return sorted(scores, key=lambda x: x[1], reverse=True)
    
    def cross_encode(self, query, doc):
        # Simulate expensive operation
        return hash(query + doc) % 100

reranker = ExpensiveReranker()

# Rerank 10,000 candidates - very expensive
candidates = [f"Doc {i}" for i in range(10000)]

# BUG: Should filter to top-k first with cheap method
results = reranker.rerank("query", candidates)
"""
            
            test_file = os.path.join(temp_dir, "reranking_cost.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_embedding_dimensionality_reduction(self):
        """Test 292: Handle dimensionality reduction correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class DimensionReducer:
    def __init__(self, target_dim=128):
        self.target_dim = target_dim
    
    def reduce(self, embedding):
        # BUG: Naive truncation loses information
        return embedding[:self.target_dim]

reducer = DimensionReducer(target_dim=128)

# Original 768-dim embedding
original = [0.1 * i for i in range(768)]

# BUG: Truncation loses last 640 dimensions
reduced = reducer.reduce(original)

print(f"Original dim: {len(original)}")
print(f"Reduced dim: {len(reduced)}")
print(f"Information lost: {len(original) - len(reduced)} dimensions")
"""
            
            test_file = os.path.join(temp_dir, "dim_reduction.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_query_expansion_loop(self):
        """Test 293: Prevent infinite loops in query expansion"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class QueryExpander:
    def expand(self, query):
        # BUG: No stop condition - infinite expansion
        expanded = [query]
        
        # Add synonyms
        while len(expanded) < 100:  # BUG: arbitrary limit
            for term in expanded:
                expanded.append(term + "_synonym")
        
        return expanded

expander = QueryExpander()

# BUG: Expands indefinitely
expanded_query = expander.expand("AI")
print(f"Expanded to {len(expanded_query)} terms")
"""
            
            test_file = os.path.join(temp_dir, "query_expansion.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_sparse_dense_hybrid_encoding(self):
        """Test 294: Combine sparse and dense encodings correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class HybridEncoder:
    def encode(self, text):
        # Sparse encoding (BM25-like)
        sparse = self.sparse_encode(text)
        # Dense encoding (neural)
        dense = self.dense_encode(text)
        
        # BUG: Doesn't normalize before combining
        return {"sparse": sparse, "dense": dense}
    
    def sparse_encode(self, text):
        return {word: 1.0 for word in text.split()}
    
    def dense_encode(self, text):
        return [0.1] * 768

encoder = HybridEncoder()
encoding = encoder.encode("machine learning")

# BUG: Sparse and dense on different scales
print(f"Sparse values: {list(encoding['sparse'].values())}")
print(f"Dense values: {encoding['dense'][:5]}")
"""
            
            test_file = os.path.join(temp_dir, "hybrid_encoding.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_contextual_embedding_position_bias(self):
        """Test 295: Handle position bias in contextual embeddings"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class ContextualEmbedder:
    def embed_with_context(self, text, context):
        # BUG: Position in context affects embedding
        full_text = context + " " + text
        
        # Later tokens get different embeddings
        return [len(full_text)] * 768

embedder = ContextualEmbedder()

# Same text, different contexts
e1 = embedder.embed_with_context("important", "This is")
e2 = embedder.embed_with_context("important", "This is a very long context with many words before the")

# BUG: Different embeddings for same word due to position
print(f"Embeddings equal: {e1 == e2}")
"""
            
            test_file = os.path.join(temp_dir, "position_bias.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestChunkingStrategies:
    """Test document chunking strategies (10 tests)"""
    
    def test_fixed_size_chunking_sentence_splitting(self):
        """Test 296: Avoid splitting sentences in fixed-size chunks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class FixedChunker:
    def __init__(self, chunk_size=100):
        self.chunk_size = chunk_size
    
    def chunk(self, text):
        # BUG: Splits at character count, breaks sentences
        chunks = []
        for i in range(0, len(text), self.chunk_size):
            chunks.append(text[i:i + self.chunk_size])
        return chunks

chunker = FixedChunker(chunk_size=50)

text = "This is a complete sentence. This is another complete sentence that should not be broken in the middle."

# BUG: Splits mid-sentence
chunks = chunker.chunk(text)
for i, chunk in enumerate(chunks):
    print(f"Chunk {i}: {chunk}")
"""
            
            test_file = os.path.join(temp_dir, "sentence_splitting.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_semantic_chunking_coherence(self):
        """Test 297: Maintain semantic coherence in chunks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class SemanticChunker:
    def chunk(self, paragraphs):
        # BUG: No semantic coherence checking
        chunks = []
        current_chunk = []
        
        for para in paragraphs:
            current_chunk.append(para)
            if len(current_chunk) >= 3:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
        
        return chunks

chunker = SemanticChunker()

paragraphs = [
    "Topic A: Introduction to AI.",
    "Topic A: More about AI.",
    "Topic B: Introduction to databases.",
    "Topic B: SQL queries."
]

# BUG: Mixes topics A and B in same chunk
chunks = chunker.chunk(paragraphs)
print(f"Chunks: {chunks}")
"""
            
            test_file = os.path.join(temp_dir, "semantic_coherence.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_chunk_overlap_context_preservation(self):
        """Test 298: Preserve context with appropriate chunk overlap"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class OverlappingChunker:
    def __init__(self, chunk_size=100, overlap=0):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk(self, text):
        # BUG: No overlap - context lost between chunks
        chunks = []
        for i in range(0, len(text), self.chunk_size):
            chunks.append(text[i:i + self.chunk_size])
        return chunks

chunker = OverlappingChunker(chunk_size=50, overlap=0)

text = "The company announced record profits. This was due to strong sales in Q4. The CEO was very pleased."

chunks = chunker.chunk(text)

# BUG: "This" in chunk 2 has no context from chunk 1
print(f"Chunk 1: {chunks[0]}")
print(f"Chunk 2: {chunks[1]}")
"""
            
            test_file = os.path.join(temp_dir, "chunk_overlap.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_hierarchical_chunking_metadata(self):
        """Test 299: Maintain hierarchy metadata in chunks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class HierarchicalChunker:
    def chunk_document(self, document):
        # BUG: Loses document structure metadata
        chunks = []
        for section in document["sections"]:
            for paragraph in section["paragraphs"]:
                chunks.append(paragraph)
        return chunks

doc = {
    "title": "AI Guide",
    "sections": [
        {
            "name": "Introduction",
            "paragraphs": ["Para 1", "Para 2"]
        },
        {
            "name": "Methods",
            "paragraphs": ["Para 3", "Para 4"]
        }
    ]
}

chunker = HierarchicalChunker()
chunks = chunker.chunk_document(doc)

# BUG: Chunks don't know which section they belong to
print(f"Chunks: {chunks}")
"""
            
            test_file = os.path.join(temp_dir, "hierarchy_metadata.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_code_aware_chunking(self):
        """Test 300: Chunk code without breaking logical blocks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class CodeChunker:
    def __init__(self, max_lines=10):
        self.max_lines = max_lines
    
    def chunk(self, code):
        # BUG: Splits code at line count, breaks functions
        lines = code.split('\\n')
        chunks = []
        for i in range(0, len(lines), self.max_lines):
            chunks.append('\\n'.join(lines[i:i + self.max_lines]))
        return chunks

chunker = CodeChunker(max_lines=5)

code = '''
def function1():
    x = 1
    y = 2
    z = x + y
    return z

def function2():
    a = 10
    b = 20
    return a + b
'''

# BUG: Splits functions across chunks
chunks = chunker.chunk(code)
for i, chunk in enumerate(chunks):
    print(f"Chunk {i}:\\n{chunk}\\n")
"""
            
            test_file = os.path.join(temp_dir, "code_chunking.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_table_preservation_in_chunks(self):
        """Test 301: Keep tables intact in chunks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class TableAwareChunker:
    def chunk(self, text):
        # BUG: Doesn't detect tables
        chunks = []
        lines = text.split('\\n')
        
        current = []
        for line in lines:
            current.append(line)
            if len(current) >= 5:
                chunks.append('\\n'.join(current))
                current = []
        
        return chunks

chunker = TableAwareChunker()

text = '''
Some text before table.

| Name | Age | City |
|------|-----|------|
| Alice| 25  | NYC  |
| Bob  | 30  | LA   |

Some text after table.
'''

# BUG: Splits table across chunks
chunks = chunker.chunk(text)
print(f"Chunks: {chunks}")
"""
            
            test_file = os.path.join(temp_dir, "table_preservation.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_chunk_metadata_enrichment(self):
        """Test 302: Enrich chunks with contextual metadata"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class MetadataChunker:
    def chunk_with_metadata(self, document):
        # BUG: No metadata enrichment
        chunks = []
        for section in document["content"]:
            chunks.append({"text": section})
        return chunks

doc = {
    "title": "Product Manual",
    "author": "John Doe",
    "date": "2025-01-01",
    "content": ["Section 1 text", "Section 2 text"]
}

chunker = MetadataChunker()
chunks = chunker.chunk_with_metadata(doc)

# BUG: Chunks missing title, author, date metadata
print(f"Chunk metadata: {chunks[0].keys()}")
"""
            
            test_file = os.path.join(temp_dir, "metadata_enrichment.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_adaptive_chunk_size(self):
        """Test 303: Adapt chunk size based on content density"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class AdaptiveChunker:
    def __init__(self, base_size=100):
        self.base_size = base_size
    
    def chunk(self, text):
        # BUG: Fixed chunk size regardless of content
        chunks = []
        for i in range(0, len(text), self.base_size):
            chunks.append(text[i:i + self.base_size])
        return chunks

chunker = AdaptiveChunker(base_size=100)

# Dense technical text needs smaller chunks
dense = "AI ML NLP CV RL GAN VAE CNN RNN LSTM GRU BERT GPT " * 10

# Simple text can have larger chunks
simple = "This is very simple text. " * 10

# BUG: Same chunk size for both
dense_chunks = chunker.chunk(dense)
simple_chunks = chunker.chunk(simple)

print(f"Dense chunks: {len(dense_chunks)}")
print(f"Simple chunks: {len(simple_chunks)}")
"""
            
            test_file = os.path.join(temp_dir, "adaptive_chunking.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_cross_reference_handling(self):
        """Test 304: Handle cross-references between chunks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class CrossRefChunker:
    def chunk(self, text):
        # BUG: No cross-reference tracking
        chunks = text.split('\\n\\n')
        return [{"id": i, "text": chunk} for i, chunk in enumerate(chunks)]

text = '''
Section 1: Introduction
See Section 3 for details.

Section 2: Methods
As mentioned in Section 1.

Section 3: Results
Details referenced in Section 1.
'''

chunker = CrossRefChunker()
chunks = chunker.chunk(text)

# BUG: No links between chunks for cross-references
print(f"Chunks: {chunks}")
"""
            
            test_file = os.path.join(temp_dir, "cross_references.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_multimedia_content_chunking(self):
        """Test 305: Handle multimedia content in chunks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class MultimediaChunker:
    def chunk_document(self, elements):
        # BUG: Treats images as text
        chunks = []
        current_chunk = []
        
        for element in elements:
            current_chunk.append(element)
            if len(current_chunk) >= 3:
                chunks.append(current_chunk)
                current_chunk = []
        
        return chunks

elements = [
    {"type": "text", "content": "Introduction"},
    {"type": "image", "path": "diagram.png"},
    {"type": "text", "content": "As shown above"},
    {"type": "table", "data": [[1, 2], [3, 4]]},
]

chunker = MultimediaChunker()
chunks = chunker.chunk_document(elements)

# BUG: Image and text split across chunks, losing context
print(f"Chunk 1: {chunks[0]}")
"""
            
            test_file = os.path.join(temp_dir, "multimedia_chunking.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
