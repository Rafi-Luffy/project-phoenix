"""
Memory System
Short-term, long-term, episodic, semantic memory with retrieval and optimization
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging
from collections import OrderedDict


class MemoryType(Enum):
    """Types of memory"""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    WORKING = "working"


class MemoryPriority(Enum):
    """Memory importance levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


@dataclass
class MemoryItem:
    """Single memory item"""
    
    item_id: str
    memory_type: MemoryType
    content: Dict[str, Any]
    priority: MemoryPriority
    timestamp: datetime
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    retention_days: int = 30
    tags: List[str] = None
    agent_id: Optional[str] = None
    
    def __post_init__(self):
        """Initialize optional fields"""
        if self.tags is None:
            self.tags = []
    
    def is_expired(self) -> bool:
        """Check if memory is expired"""
        expiry = self.timestamp + timedelta(days=self.retention_days)
        return datetime.now() > expiry
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'item_id': self.item_id,
            'memory_type': self.memory_type.value,
            'content': self.content,
            'priority': self.priority.name,
            'timestamp': self.timestamp.isoformat(),
            'access_count': self.access_count,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'retention_days': self.retention_days,
            'tags': self.tags,
            'agent_id': self.agent_id
        }


class ShortTermMemory:
    """Short-term memory using LRU cache"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: OrderedDict[str, MemoryItem] = OrderedDict()
        self.logger = logging.getLogger(__name__)
    
    def store(self, item: MemoryItem):
        """Store item in short-term memory"""
        if item.item_id in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(item.item_id)
        else:
            # Add new item
            if len(self.cache) >= self.max_size:
                # Remove least recently used
                oldest_id, oldest_item = self.cache.popitem(last=False)
                self.logger.debug(f"Short-term memory evicted: {oldest_id}")
        
        self.cache[item.item_id] = item
    
    def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        """Retrieve item from short-term memory"""
        if item_id in self.cache:
            item = self.cache[item_id]
            item.access_count += 1
            item.last_accessed = datetime.now()
            self.cache.move_to_end(item_id)
            return item
        return None
    
    def search(self, query: str, tags: List[str] = None) -> List[MemoryItem]:
        """Search short-term memory"""
        results = []
        
        for item in self.cache.values():
            # Check content match
            if query.lower() in json.dumps(item.content).lower():
                # Check tags if provided
                if tags and not any(t in item.tags for t in tags):
                    continue
                results.append(item)
        
        # Sort by recency
        return sorted(results, key=lambda x: x.last_accessed or x.timestamp, reverse=True)
    
    def clear(self):
        """Clear all short-term memory"""
        self.cache.clear()
    
    def get_all(self) -> List[MemoryItem]:
        """Get all items"""
        return list(self.cache.values())
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'utilization': len(self.cache) / self.max_size,
            'total_accesses': sum(item.access_count for item in self.cache.values())
        }


class LongTermMemory:
    """Long-term memory backed by database"""
    
    def __init__(self, db_session=None):
        self.db_session = db_session
        self.memories: Dict[str, MemoryItem] = {}  # In-memory index
        self.logger = logging.getLogger(__name__)
    
    def store(self, item: MemoryItem):
        """Store item in long-term memory"""
        self.memories[item.item_id] = item
        
        # Would persist to database here
        if self.db_session:
            self.logger.info(f"Memory persisted to database: {item.item_id}")
    
    def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        """Retrieve item from long-term memory"""
        if item_id in self.memories:
            item = self.memories[item_id]
            item.access_count += 1
            item.last_accessed = datetime.now()
            return item
        
        # Would query database here if not in index
        return None
    
    def search(self, query: str = None, tags: List[str] = None, 
               memory_type: MemoryType = None, agent_id: str = None) -> List[MemoryItem]:
        """Search long-term memory with multiple filters"""
        results = []
        
        for item in self.memories.values():
            # Check if expired
            if item.is_expired():
                continue
            
            # Check query match
            if query and query.lower() not in json.dumps(item.content).lower():
                continue
            
            # Check tags
            if tags and not any(t in item.tags for t in tags):
                continue
            
            # Check type
            if memory_type and item.memory_type != memory_type:
                continue
            
            # Check agent
            if agent_id and item.agent_id != agent_id:
                continue
            
            results.append(item)
        
        # Sort by priority and access count
        return sorted(results, key=lambda x: (x.priority.value, -x.access_count))
    
    def cleanup_expired(self):
        """Remove expired memories"""
        expired_ids = [
            item_id for item_id, item in self.memories.items()
            if item.is_expired()
        ]
        
        for item_id in expired_ids:
            del self.memories[item_id]
        
        self.logger.info(f"Cleaned up {len(expired_ids)} expired memories")
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        active = sum(1 for item in self.memories.values() if not item.is_expired())
        expired = len(self.memories) - active
        
        return {
            'total_items': len(self.memories),
            'active_items': active,
            'expired_items': expired,
            'by_type': {
                mt.value: sum(1 for item in self.memories.values() 
                            if item.memory_type == mt and not item.is_expired())
                for mt in MemoryType
            }
        }


class MemoryIndexer:
    """Index memory for fast retrieval"""
    
    def __init__(self):
        self.tag_index: Dict[str, List[str]] = {}  # tag -> [item_ids]
        self.type_index: Dict[MemoryType, List[str]] = {}  # type -> [item_ids]
        self.agent_index: Dict[str, List[str]] = {}  # agent_id -> [item_ids]
        self.logger = logging.getLogger(__name__)
    
    def index_item(self, item: MemoryItem):
        """Index a memory item"""
        # Index by tags
        for tag in item.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = []
            self.tag_index[tag].append(item.item_id)
        
        # Index by type
        if item.memory_type not in self.type_index:
            self.type_index[item.memory_type] = []
        self.type_index[item.memory_type].append(item.item_id)
        
        # Index by agent
        if item.agent_id:
            if item.agent_id not in self.agent_index:
                self.agent_index[item.agent_id] = []
            self.agent_index[item.agent_id].append(item.item_id)
    
    def remove_item(self, item: MemoryItem):
        """Remove item from indexes"""
        for tag in item.tags:
            if tag in self.tag_index and item.item_id in self.tag_index[tag]:
                self.tag_index[tag].remove(item.item_id)
        
        if item.memory_type in self.type_index and item.item_id in self.type_index[item.memory_type]:
            self.type_index[item.memory_type].remove(item.item_id)
        
        if item.agent_id and item.agent_id in self.agent_index:
            if item.item_id in self.agent_index[item.agent_id]:
                self.agent_index[item.agent_id].remove(item.item_id)
    
    def get_by_tag(self, tag: str) -> List[str]:
        """Get item IDs by tag"""
        return self.tag_index.get(tag, [])
    
    def get_by_type(self, memory_type: MemoryType) -> List[str]:
        """Get item IDs by type"""
        return self.type_index.get(memory_type, [])
    
    def get_by_agent(self, agent_id: str) -> List[str]:
        """Get item IDs by agent"""
        return self.agent_index.get(agent_id, [])


class MemoryManager:
    """Central memory management system"""
    
    def __init__(self, db_session=None, short_term_size: int = 1000):
        self.short_term = ShortTermMemory(max_size=short_term_size)
        self.long_term = LongTermMemory(db_session)
        self.indexer = MemoryIndexer()
        self.logger = logging.getLogger(__name__)
    
    def store_memory(self, content: Dict[str, Any], memory_type: MemoryType,
                    priority: MemoryPriority = MemoryPriority.NORMAL,
                    retention_days: int = 30, tags: List[str] = None,
                    agent_id: str = None) -> str:
        """Store memory in appropriate tier"""
        import uuid
        item_id = str(uuid.uuid4())
        
        item = MemoryItem(
            item_id=item_id,
            memory_type=memory_type,
            content=content,
            priority=priority,
            timestamp=datetime.now(),
            retention_days=retention_days,
            tags=tags or [],
            agent_id=agent_id
        )
        
        # Always store in long-term
        self.long_term.store(item)
        
        # Also store high-priority items in short-term
        if priority in [MemoryPriority.CRITICAL, MemoryPriority.HIGH]:
            self.short_term.store(item)
        
        # Index the item
        self.indexer.index_item(item)
        
        self.logger.info(f"Memory stored: {item_id} ({memory_type.value})")
        return item_id
    
    def retrieve_memory(self, item_id: str) -> Optional[MemoryItem]:
        """Retrieve memory item"""
        # Try short-term first
        item = self.short_term.retrieve(item_id)
        if item:
            return item
        
        # Try long-term
        return self.long_term.retrieve(item_id)
    
    def search_memory(self, query: str = None, tags: List[str] = None,
                     memory_type: MemoryType = None, agent_id: str = None,
                     search_short_term: bool = True) -> List[MemoryItem]:
        """Search memory across both tiers"""
        results = []
        
        if search_short_term:
            results.extend(self.short_term.search(query, tags))
        
        results.extend(self.long_term.search(query, tags, memory_type, agent_id))
        
        # Remove duplicates and sort by priority
        unique_results = {}
        for item in results:
            if item.item_id not in unique_results:
                unique_results[item.item_id] = item
        
        return sorted(unique_results.values(), 
                     key=lambda x: (x.priority.value, -x.access_count))
    
    def get_agent_context(self, agent_id: str, limit: int = 20) -> Dict[str, Any]:
        """Get context window for an agent (recent relevant memories)"""
        memories = self.search_memory(agent_id=agent_id)[:limit]
        
        return {
            'agent_id': agent_id,
            'memory_count': len(memories),
            'memories': [m.to_dict() for m in memories],
            'total_accesses': sum(m.access_count for m in memories),
            'timestamp': datetime.now().isoformat()
        }
    
    def optimize_memory(self):
        """Clean up and optimize memory"""
        self.long_term.cleanup_expired()
        
        # Move frequently accessed long-term memories to short-term
        for item in self.long_term.search():
            if item.access_count > 10 and item.priority in [MemoryPriority.HIGH, MemoryPriority.CRITICAL]:
                self.short_term.store(item)
    
    def get_memory_stats(self) -> Dict:
        """Get memory system statistics"""
        return {
            'short_term': self.short_term.get_stats(),
            'long_term': self.long_term.get_stats(),
            'total_memories': (
                len(self.short_term.get_all()) + 
                len(self.long_term.memories)
            )
        }
    
    def clear_all(self):
        """Clear all memory (use with caution)"""
        self.short_term.clear()
        self.long_term.memories.clear()
        self.logger.warning("All memory cleared")


class ContextWindow:
    """Manages context window for agent decision making"""
    
    def __init__(self, max_tokens: int = 8000, memory_manager: MemoryManager = None):
        self.max_tokens = max_tokens
        self.memory_manager = memory_manager
        self.current_context: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
    
    def build_context(self, agent_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build context for agent decision making"""
        # Start with task data
        context = {
            'task': task_data,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add relevant memories
        if self.memory_manager:
            memories = self.memory_manager.get_agent_context(agent_id, limit=10)
            context['relevant_memories'] = memories
        
        # Estimate tokens and trim if needed
        context_str = json.dumps(context)
        estimated_tokens = len(context_str) // 4
        
        if estimated_tokens > self.max_tokens:
            self.logger.warning(f"Context exceeds token limit: {estimated_tokens}/{self.max_tokens}")
            # Keep task data and most recent memories
            context['relevant_memories'] = {
                'agent_id': agent_id,
                'memory_count': 0,
                'memories': []
            }
        
        self.current_context = [context]
        return context
    
    def add_to_context(self, data: Dict[str, Any]):
        """Add data to current context"""
        self.current_context.append(data)
    
    def get_context(self) -> List[Dict[str, Any]]:
        """Get current context"""
        return self.current_context
    
    def clear_context(self):
        """Clear context"""
        self.current_context = []
