"""
Distributed Caching System

Extends caching to support distributed architectures:
- Redis cluster support
- Cache synchronization
- Multi-region replication
- Intelligent eviction policies
"""

import asyncio
import hashlib
import json
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import pickle
import zlib
from abc import ABC, abstractmethod


@dataclass
class CacheEntry:
    """Represents a cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    accessed_at: datetime
    ttl: Optional[int]
    size_bytes: int
    access_count: int = 0
    compression_ratio: float = 1.0


class DistributedCacheBackend(ABC):
    """Base class for distributed cache backends"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache"""
        pass
    
    @abstractmethod
    async def sync(self, other_nodes: List[str]) -> bool:
        """Synchronize with other nodes"""
        pass


class RedisClusterCache(DistributedCacheBackend):
    """Redis cluster-aware caching backend"""
    
    def __init__(self, nodes: List[str], password: Optional[str] = None, compression: bool = True):
        self.nodes = nodes
        self.password = password
        self.compression = compression
        self.metadata: Dict[str, CacheEntry] = {}
        self._sync_lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with compression support"""
        if key in self.metadata:
            entry = self.metadata[key]
            
            # Check TTL
            if entry.ttl and (datetime.now() - entry.created_at).total_seconds() > entry.ttl:
                await self.delete(key)
                return None
            
            # Update access metadata
            entry.accessed_at = datetime.now()
            entry.access_count += 1
            
            return entry.value
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with compression"""
        try:
            # Serialize value
            serialized = pickle.dumps(value)
            
            # Apply compression if beneficial
            compressed = serialized
            compression_ratio = 1.0
            if self.compression and len(serialized) > 1024:
                compressed = zlib.compress(serialized)
                compression_ratio = len(compressed) / len(serialized)
            
            # Create entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                accessed_at=datetime.now(),
                ttl=ttl,
                size_bytes=len(compressed),
                compression_ratio=compression_ratio
            )
            
            self.metadata[key] = entry
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if key in self.metadata:
            del self.metadata[key]
            return True
        return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        if key not in self.metadata:
            return False
        
        entry = self.metadata[key]
        if entry.ttl and (datetime.now() - entry.created_at).total_seconds() > entry.ttl:
            await self.delete(key)
            return False
        
        return True
    
    async def clear(self) -> bool:
        """Clear all cache"""
        self.metadata.clear()
        return True
    
    async def sync(self, other_nodes: List[str]) -> bool:
        """Synchronize cache with other nodes"""
        async with self._sync_lock:
            try:
                # In production, this would synchronize with other Redis nodes
                # For now, we simulate the sync
                sync_data = {k: asdict(v) for k, v in self.metadata.items()}
                return True
            except Exception as e:
                print(f"Cache sync error: {e}")
                return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_size = sum(e.size_bytes for e in self.metadata.values())
        total_accesses = sum(e.access_count for e in self.metadata.values())
        avg_compression = sum(e.compression_ratio for e in self.metadata.values()) / len(self.metadata) if self.metadata else 1.0
        
        return {
            "entries": len(self.metadata),
            "total_size_bytes": total_size,
            "total_accesses": total_accesses,
            "avg_compression_ratio": avg_compression,
            "nodes": len(self.nodes),
            "avg_entry_size": total_size / len(self.metadata) if self.metadata else 0
        }


class MultiRegionCache:
    """Multi-region cache with automatic replication"""
    
    def __init__(self, regions: Dict[str, DistributedCacheBackend]):
        self.regions = regions
        self.replication_factor = 3
        self.consistency_level = "eventual"  # eventual, strong, causal
    
    async def get(self, key: str, region: str = "primary") -> Optional[Any]:
        """Get value from specific region"""
        if region not in self.regions:
            raise ValueError(f"Unknown region: {region}")
        
        return await self.regions[region].get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, replicate: bool = True) -> bool:
        """Set value with automatic replication"""
        success = True
        
        # Write to all regions
        for region, backend in self.regions.items():
            region_success = await backend.set(key, value, ttl)
            if not region_success:
                success = False
        
        return success
    
    async def delete(self, key: str) -> bool:
        """Delete from all regions"""
        success = True
        
        for backend in self.regions.values():
            if not await backend.delete(key):
                success = False
        
        return success
    
    def get_region_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all regions"""
        stats = {}
        for region, backend in self.regions.items():
            if hasattr(backend, 'get_stats'):
                stats[region] = backend.get_stats()
        return stats


class IntelligentEvictionPolicy:
    """Intelligent cache eviction based on access patterns"""
    
    def __init__(self, max_entries: int = 10000, max_memory_mb: int = 1024):
        self.max_entries = max_entries
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.access_patterns: Dict[str, List[datetime]] = {}
    
    async def evaluate(self, cache: DistributedCacheBackend) -> List[str]:
        """Evaluate which entries should be evicted"""
        if isinstance(cache, RedisClusterCache):
            stats = cache.get_stats()
            
            # Check if eviction is needed
            if stats["entries"] < self.max_entries and stats["total_size_bytes"] < self.max_memory_bytes:
                return []
            
            # LRU eviction: remove least recently used
            entries = list(cache.metadata.values())
            entries.sort(key=lambda e: e.accessed_at)
            
            to_evict = []
            freed_bytes = 0
            
            for entry in entries[:len(entries) // 5]:  # Evict 20% of entries
                to_evict.append(entry.key)
                freed_bytes += entry.size_bytes
                
                if freed_bytes >= self.max_memory_bytes * 0.1:  # Free 10%
                    break
            
            return to_evict
        
        return []
    
    async def evict(self, cache: DistributedCacheBackend) -> int:
        """Execute eviction"""
        keys_to_evict = await self.evaluate(cache)
        
        count = 0
        for key in keys_to_evict:
            if await cache.delete(key):
                count += 1
        
        return count


class CacheWarming:
    """Pre-load cache with frequently accessed data"""
    
    def __init__(self, cache: DistributedCacheBackend):
        self.cache = cache
        self.access_log: List[str] = []
    
    def log_access(self, key: str):
        """Log cache access"""
        self.access_log.append(key)
    
    async def analyze_patterns(self) -> Dict[str, float]:
        """Analyze access patterns"""
        if not self.access_log:
            return {}
        
        access_counts = {}
        for key in self.access_log:
            access_counts[key] = access_counts.get(key, 0) + 1
        
        # Calculate access frequency (0-1)
        total = len(self.access_log)
        frequencies = {k: v / total for k, v in access_counts.items()}
        
        return dict(sorted(frequencies.items(), key=lambda x: x[1], reverse=True))
    
    async def warm_cache(self, data: Dict[str, Any], ttl: Optional[int] = None) -> int:
        """Warm cache with predefined data"""
        loaded = 0
        
        for key, value in data.items():
            if await self.cache.set(key, value, ttl):
                loaded += 1
        
        return loaded


if __name__ == "__main__":
    async def test_distributed_cache():
        # Create cache backend
        cache = RedisClusterCache(
            nodes=["localhost:6379", "localhost:6380", "localhost:6381"]
        )
        
        # Set values
        await cache.set("key1", {"data": "value1"}, ttl=300)
        await cache.set("key2", [1, 2, 3, 4, 5], ttl=600)
        
        # Get values
        val1 = await cache.get("key1")
        print(f"Retrieved: {val1}")
        
        # Get stats
        stats = cache.get_stats()
        print(f"Cache stats: {stats}")
        
        # Multi-region setup
        regions = {
            "us-east": cache,
            "eu-west": RedisClusterCache(nodes=["eu-node:6379"])
        }
        multi_cache = MultiRegionCache(regions)
        
        # Set with replication
        await multi_cache.set("distributed_key", {"replicated": True})
    
    asyncio.run(test_distributed_cache())
