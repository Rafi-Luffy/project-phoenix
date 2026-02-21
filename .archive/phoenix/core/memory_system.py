"""
Memory System - Module 1.3: Memory System
Short-term, long-term, episodic memory implementation
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from collections import deque
from enum import Enum
import uuid
import math


class MemoryPriority(Enum):
    LOW = 1
    MEDIUM = 5
    HIGH = 10


class ShortTermMemory:
    """Temporary working memory for current context"""

    def __init__(self, max_items: int = 100):
        self.max_items = max_items
        self.memory: deque = deque(maxlen=max_items)
        self.access_patterns: Dict[str, int] = {}

    def store(self, key: str, value: Any, context: Dict[str, Any] = None):
        """Store item in short-term memory"""
        item = {
            'key': key,
            'value': value,
            'context': context or {},
            'timestamp': datetime.now(),
            'access_count': 0
        }
        self.memory.append(item)
        self.access_patterns[key] = 0

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve item from short-term memory"""
        for item in self.memory:
            if item['key'] == key:
                item['access_count'] += 1
                self.access_patterns[key] = item['access_count']
                return item['value']
        return None

    def search(self, pattern: str) -> List[Dict[str, Any]]:
        """Search for items matching pattern"""
        results = []
        for item in self.memory:
            if pattern.lower() in item['key'].lower():
                results.append(item)
        return results

    def clear_old(self, older_than_seconds: int = 300):
        """Remove items older than specified duration"""
        cutoff_time = datetime.now() - timedelta(seconds=older_than_seconds)
        items_to_keep = []
        for item in self.memory:
            if item['timestamp'] > cutoff_time:
                items_to_keep.append(item)
        self.memory = deque(items_to_keep, maxlen=self.max_items)

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all items in memory"""
        return list(self.memory)

    def size(self) -> int:
        """Get current memory size"""
        return len(self.memory)


class LongTermMemory:
    """Persistent memory for learned patterns and historical data"""

    def __init__(self, max_items: int = 10000):
        self.max_items = max_items
        self.memory: Dict[str, Dict[str, Any]] = {}
        self.index: Dict[str, Set[str]] = {}  # Tag-based indexing
        self.created_at = datetime.now()

    def store(self, key: str, value: Any, tags: List[str] = None, 
              priority: MemoryPriority = MemoryPriority.MEDIUM,
              metadata: Dict[str, Any] = None):
        """Store item in long-term memory"""
        if len(self.memory) >= self.max_items:
            self._remove_lowest_priority_item()

        item = {
            'key': key,
            'value': value,
            'tags': tags or [],
            'priority': priority.value,
            'metadata': metadata or {},
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'access_count': 0,
            'relevance_score': 1.0
        }
        
        self.memory[key] = item

        # Update index
        for tag in tags or []:
            if tag not in self.index:
                self.index[tag] = set()
            self.index[tag].add(key)

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve item from long-term memory"""
        if key in self.memory:
            item = self.memory[key]
            item['access_count'] += 1
            item['updated_at'] = datetime.now()
            return item['value']
        return None

    def search_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Search items by tag"""
        keys = self.index.get(tag, set())
        return [self.memory[k] for k in keys if k in self.memory]

    def search_by_pattern(self, pattern: str) -> List[Dict[str, Any]]:
        """Search items by key pattern"""
        results = []
        for key, item in self.memory.items():
            if pattern.lower() in key.lower():
                results.append(item)
        return results

    def update_relevance(self, key: str, score: float):
        """Update relevance score for an item"""
        if key in self.memory:
            self.memory[key]['relevance_score'] = max(0, min(1, score))

    def _remove_lowest_priority_item(self):
        """Remove item with lowest priority and relevance"""
        if not self.memory:
            return

        lowest_key = None
        lowest_score = float('inf')

        for key, item in self.memory.items():
            score = (item['priority'] * item['relevance_score']) / item['access_count'] if item['access_count'] > 0 else item['priority'] * item['relevance_score']
            if score < lowest_score:
                lowest_score = score
                lowest_key = key

        if lowest_key:
            del self.memory[lowest_key]

    def size(self) -> int:
        """Get current memory size"""
        return len(self.memory)

    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics"""
        if not self.memory:
            return {}

        priorities = [item['priority'] for item in self.memory.values()]
        scores = [item['relevance_score'] for item in self.memory.values()]
        accesses = [item['access_count'] for item in self.memory.values()]

        return {
            'total_items': len(self.memory),
            'avg_priority': sum(priorities) / len(priorities),
            'avg_relevance': sum(scores) / len(scores),
            'total_accesses': sum(accesses),
            'unique_tags': len(self.index)
        }


class EpisodicMemory:
    """Memory of specific events and episodes"""

    def __init__(self, max_episodes: int = 1000):
        self.max_episodes = max_episodes
        self.episodes: deque = deque(maxlen=max_episodes)
        self.episode_index: Dict[str, int] = {}

    def record_episode(self, episode_id: str, episode_type: str, 
                      data: Dict[str, Any], outcome: str) -> str:
        """Record an episode"""
        episode = {
            'episode_id': episode_id,
            'type': episode_type,
            'data': data,
            'outcome': outcome,
            'timestamp': datetime.now(),
            'importance': self._calculate_importance(episode_type, outcome)
        }
        
        self.episodes.append(episode)
        self.episode_index[episode_id] = len(self.episodes) - 1
        
        return episode_id

    def recall_episodes(self, episode_type: str = None, 
                       start_time: datetime = None) -> List[Dict[str, Any]]:
        """Recall episodes matching criteria"""
        episodes = list(self.episodes)
        
        if episode_type:
            episodes = [e for e in episodes if e['type'] == episode_type]

        if start_time:
            episodes = [e for e in episodes if e['timestamp'] >= start_time]

        return sorted(episodes, key=lambda x: x['importance'], reverse=True)

    def _calculate_importance(self, episode_type: str, outcome: str) -> float:
        """Calculate importance of an episode"""
        base_importance = {
            'failure': 0.9,
            'recovery': 0.8,
            'correction': 0.7,
            'learning': 0.6,
            'normal_operation': 0.2
        }.get(episode_type, 0.5)

        outcome_modifier = {
            'success': 1.0,
            'partial_success': 0.7,
            'failure': 1.2,  # Failures are important to remember
            'neutral': 0.5
        }.get(outcome, 0.5)

        return base_importance * outcome_modifier

    def get_recent_episodes(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent episodes"""
        return list(self.episodes)[-limit:]

    def size(self) -> int:
        """Get total number of episodes"""
        return len(self.episodes)


class SemanticMemory:
    """Memory of facts, concepts, and relationships"""

    def __init__(self):
        self.facts: Dict[str, Any] = {}
        self.relationships: Dict[str, Set[str]] = {}
        self.concepts: Dict[str, List[str]] = {}

    def store_fact(self, fact_id: str, fact: str, 
                   related_concept: str = None, confidence: float = 1.0):
        """Store a fact"""
        self.facts[fact_id] = {
            'fact': fact,
            'concept': related_concept,
            'confidence': confidence,
            'created_at': datetime.now()
        }

        if related_concept:
            if related_concept not in self.concepts:
                self.concepts[related_concept] = []
            self.concepts[related_concept].append(fact_id)

    def store_relationship(self, entity1: str, entity2: str, relationship: str):
        """Store a relationship between entities"""
        key = f"{entity1}-{relationship}-{entity2}"
        
        if entity1 not in self.relationships:
            self.relationships[entity1] = set()
        self.relationships[entity1].add(key)

    def query_facts(self, concept: str) -> List[Dict[str, Any]]:
        """Query facts for a concept"""
        fact_ids = self.concepts.get(concept, [])
        return [self.facts[fid] for fid in fact_ids if fid in self.facts]

    def get_related_entities(self, entity: str) -> Set[str]:
        """Get entities related to given entity"""
        return self.relationships.get(entity, set())

    def size(self) -> int:
        """Get total size of semantic memory"""
        return len(self.facts) + len(self.relationships)


class MemoryManager:
    """Central manager for all memory types"""

    def __init__(self, short_term_size: int = 100, 
                 long_term_size: int = 10000, 
                 episodic_size: int = 1000):
        self.short_term = ShortTermMemory(max_items=short_term_size)
        self.long_term = LongTermMemory(max_items=long_term_size)
        self.episodic = EpisodicMemory(max_episodes=episodic_size)
        self.semantic = SemanticMemory()

    def consolidate_memory(self):
        """Move important short-term memories to long-term"""
        items = self.short_term.get_all()
        
        for item in items:
            if item['access_count'] > 2 or item.get('important'):
                self.long_term.store(
                    key=item['key'],
                    value=item['value'],
                    tags=[item['key'].split('_')[0]],  # Use first part as tag
                    priority=MemoryPriority.MEDIUM if item['access_count'] <= 5 else MemoryPriority.HIGH,
                    metadata={'original_key': item['key']}
                )

    def clear_old_short_term(self, older_than_seconds: int = 300):
        """Clear old short-term memories"""
        self.short_term.clear_old(older_than_seconds)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all memory systems"""
        return {
            'short_term': self.short_term.size(),
            'long_term': self.long_term.size(),
            'episodic': self.episodic.size(),
            'semantic': self.semantic.size(),
            'long_term_stats': self.long_term.get_statistics()
        }
