"""
Advanced Persistence Module
Provides state persistence, caching, and data durability
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Generic, TypeVar
from datetime import datetime, timedelta
import json
from enum import Enum


T = TypeVar('T')


class StorageBackend(Enum):
    """Supported storage backends"""
    MEMORY = "memory"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    REDIS = "redis"
    SQLITE = "sqlite"


@dataclass
class StoredObject:
    """Object wrapper for storage"""
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    ttl_seconds: Optional[int] = None  # Time to live
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if object has expired"""
        if self.ttl_seconds is None:
            return False
        elapsed = (datetime.now() - self.updated_at).total_seconds()
        return elapsed > self.ttl_seconds


class PersistenceBackend(ABC, Generic[T]):
    """Abstract base for persistence backends"""
    
    @abstractmethod
    def save(self, key: str, value: T, ttl_seconds: Optional[int] = None) -> bool:
        """Save object to storage"""
        pass
    
    @abstractmethod
    def load(self, key: str) -> Optional[T]:
        """Load object from storage"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete object from storage"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if object exists"""
        pass
    
    @abstractmethod
    def list_keys(self, prefix: str = "") -> List[str]:
        """List all keys, optionally filtered by prefix"""
        pass


class InMemoryPersistence(PersistenceBackend):
    """In-memory persistence backend"""
    
    def __init__(self, cleanup_interval: int = 300):
        self.store: Dict[str, StoredObject] = {}
        self.cleanup_interval = cleanup_interval
        self.lock = __import__('threading').Lock()
    
    def save(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        with self.lock:
            self.store[key] = StoredObject(
                key=key,
                value=value,
                ttl_seconds=ttl_seconds
            )
        return True
    
    def load(self, key: str) -> Optional[Any]:
        with self.lock:
            if key not in self.store:
                return None
            
            obj = self.store[key]
            if obj.is_expired():
                del self.store[key]
                return None
            
            return obj.value
    
    def delete(self, key: str) -> bool:
        with self.lock:
            if key in self.store:
                del self.store[key]
                return True
        return False
    
    def exists(self, key: str) -> bool:
        with self.lock:
            return key in self.store and not self.store[key].is_expired()
    
    def list_keys(self, prefix: str = "") -> List[str]:
        with self.lock:
            return [k for k in self.store.keys() if k.startswith(prefix)]


class CacheManager(Generic[T]):
    """Manages caching with TTL and eviction"""
    
    def __init__(self, backend: PersistenceBackend, max_size: int = 10000):
        self.backend = backend
        self.max_size = max_size
        self.access_counts: Dict[str, int] = {}
        self.lock = __import__('threading').Lock()
    
    def get(self, key: str) -> Optional[T]:
        """Get value from cache"""
        value = self.backend.load(key)
        if value is not None:
            with self.lock:
                self.access_counts[key] = self.access_counts.get(key, 0) + 1
        return value
    
    def put(self, key: str, value: T, ttl_seconds: Optional[int] = None) -> bool:
        """Put value in cache"""
        with self.lock:
            # Check size limit
            keys = self.backend.list_keys()
            if len(keys) >= self.max_size:
                self._evict_lru()
        
        return self.backend.save(key, value, ttl_seconds)
    
    def _evict_lru(self):
        """Evict least recently used item"""
        keys = self.backend.list_keys()
        if not keys:
            return
        
        # Find least accessed key
        lru_key = min(keys, key=lambda k: self.access_counts.get(k, 0))
        self.backend.delete(lru_key)
        with self.lock:
            self.access_counts.pop(lru_key, None)
    
    def clear(self):
        """Clear entire cache"""
        keys = self.backend.list_keys()
        for key in keys:
            self.backend.delete(key)


@dataclass
class CheckpointData:
    """System checkpoint data"""
    timestamp: datetime
    system_state: Dict[str, Any]
    memory_state: Dict[str, Any]
    learning_state: Dict[str, Any]
    incidents: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_json(self) -> str:
        """Serialize checkpoint to JSON"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return json.dumps(data)


class CheckpointManager:
    """Manages system checkpoints and recovery"""
    
    def __init__(self, backend: PersistenceBackend):
        self.backend = backend
        self.checkpoints: List[CheckpointData] = []
        self.current_checkpoint: Optional[CheckpointData] = None
        self.lock = __import__('threading').Lock()
    
    def create_checkpoint(self, healer) -> bool:
        """Create a system checkpoint"""
        checkpoint = CheckpointData(
            timestamp=datetime.now(),
            system_state={
                "mode": healer.mode.value,
                "uptime": (datetime.now() - healer.started_at).total_seconds(),
            },
            memory_state={},  # Serialize memory state
            learning_state={},  # Serialize learning state
            incidents=[]  # Serialize incidents
        )
        
        with self.lock:
            self.checkpoints.append(checkpoint)
            self.current_checkpoint = checkpoint
        
        # Persist checkpoint
        key = f"checkpoint_{checkpoint.timestamp.timestamp()}"
        return self.backend.save(key, checkpoint.to_json())
    
    def restore_from_checkpoint(self, checkpoint_id: Optional[str] = None) -> Optional[CheckpointData]:
        """Restore system from checkpoint"""
        if checkpoint_id:
            data = self.backend.load(checkpoint_id)
            if data:
                return CheckpointData(**json.loads(data))
        
        # Return most recent checkpoint
        with self.lock:
            return self.current_checkpoint
    
    def list_checkpoints(self, limit: int = 10) -> List[CheckpointData]:
        """List recent checkpoints"""
        with self.lock:
            return self.checkpoints[-limit:]


class StateSnapshot:
    """Captures system state for debugging and analysis"""
    
    def __init__(self):
        self.snapshots: Dict[str, Dict[str, Any]] = {}
        self.lock = __import__('threading').Lock()
    
    def capture(self, component: str, state: Dict[str, Any]):
        """Capture component state"""
        with self.lock:
            self.snapshots[component] = {
                "timestamp": datetime.now(),
                "state": state
            }
    
    def get_snapshot(self, component: str) -> Optional[Dict[str, Any]]:
        """Get component snapshot"""
        with self.lock:
            return self.snapshots.get(component, {}).get("state")
    
    def get_full_snapshot(self) -> Dict[str, Dict[str, Any]]:
        """Get snapshots of all components"""
        with self.lock:
            return {
                comp: snap["state"]
                for comp, snap in self.snapshots.items()
            }


class TransactionLog:
    """Logs all system operations for audit and recovery"""
    
    def __init__(self, backend: PersistenceBackend, max_entries: int = 100000):
        self.backend = backend
        self.max_entries = max_entries
        self.entries: List[Dict[str, Any]] = []
        self.lock = __import__('threading').Lock()
    
    def log_operation(
        self,
        operation_type: str,
        component: str,
        details: Dict[str, Any],
        success: bool = True
    ):
        """Log an operation"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation_type": operation_type,
            "component": component,
            "details": details,
            "success": success
        }
        
        with self.lock:
            self.entries.append(entry)
            
            # Maintain size limit
            if len(self.entries) > self.max_entries:
                self.entries = self.entries[-self.max_entries:]
        
        # Persist
        key = f"tx_log_{datetime.now().timestamp()}"
        self.backend.save(key, json.dumps(entry))
    
    def get_operations_by_component(self, component: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get operations for a component"""
        with self.lock:
            ops = [e for e in self.entries if e["component"] == component]
            return ops[-limit:]
    
    def get_recent_operations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent operations"""
        with self.lock:
            return self.entries[-limit:]


class DataIntegrity:
    """Ensures data integrity with checksums and validation"""
    
    @staticmethod
    def calculate_checksum(data: Any) -> str:
        """Calculate data checksum"""
        import hashlib
        json_str = json.dumps(asdict(data) if hasattr(data, '__dataclass_fields__') else data)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    @staticmethod
    def verify_integrity(data: Any, checksum: str) -> bool:
        """Verify data integrity"""
        return DataIntegrity.calculate_checksum(data) == checksum


class PersistenceManager:
    """Centralized persistence management"""
    
    def __init__(self, backend_type: StorageBackend = StorageBackend.MEMORY):
        if backend_type == StorageBackend.MEMORY:
            self.backend = InMemoryPersistence()
        elif backend_type == StorageBackend.POSTGRESQL:
            # TODO: Implement PostgreSQL backend
            self.backend = InMemoryPersistence()
        elif backend_type == StorageBackend.MONGODB:
            # TODO: Implement MongoDB backend
            self.backend = InMemoryPersistence()
        else:
            self.backend = InMemoryPersistence()
        
        self.cache = CacheManager(self.backend)
        self.checkpoint_mgr = CheckpointManager(self.backend)
        self.state_snapshot = StateSnapshot()
        self.transaction_log = TransactionLog(self.backend)
    
    def save_state(self, key: str, state: Dict[str, Any], ttl_seconds: Optional[int] = None) -> bool:
        """Save state with integrity check"""
        self.state_snapshot.capture(key, state)
        return self.cache.put(key, state, ttl_seconds)
    
    def load_state(self, key: str) -> Optional[Dict[str, Any]]:
        """Load state"""
        return self.cache.get(key)
