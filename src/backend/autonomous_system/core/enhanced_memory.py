"""
Enhanced Memory System - Phase 1.3
Specialized memory types: Episodic, Semantic, Procedural
Advanced retrieval patterns and memory optimization
"""

from typing import Dict, List, Optional, Any, Callable, Set
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json
import logging
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)


class MemoryDecayFunction(Enum):
    """Decay functions for memory importance over time"""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    LOGARITHMIC = "logarithmic"
    NONE = "none"


class RetrievalStrategy(Enum):
    """Strategies for memory retrieval"""
    TEMPORAL = "temporal"
    SEMANTIC = "semantic"
    SIMILARITY = "similarity"
    RELEVANCE = "relevance"
    FREQUENCY = "frequency"


@dataclass
class EpisodicMemory:
    """Store specific events and experiences"""
    
    episode_id: str
    description: str
    timestamp: datetime
    agents_involved: List[str]
    outcome: str  # success, failure, mixed
    confidence: float  # 0.0 - 1.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Importance and decay
    importance: float = 1.0  # Initial importance
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    
    def update_importance(self, decay_function: MemoryDecayFunction = MemoryDecayFunction.EXPONENTIAL) -> float:
        """Update importance based on age and access patterns"""
        age_seconds = (datetime.now() - self.timestamp).total_seconds()
        age_days = age_seconds / (24 * 3600)
        
        if decay_function == MemoryDecayFunction.EXPONENTIAL:
            decay = 0.95 ** age_days
        elif decay_function == MemoryDecayFunction.LINEAR:
            decay = max(0.0, 1.0 - (age_days / 90))  # Decay over 90 days
        elif decay_function == MemoryDecayFunction.LOGARITHMIC:
            decay = 1.0 / (1.0 + (age_days / 30))
        else:
            decay = 1.0
        
        # Boost importance based on access frequency
        access_boost = min(1.0, self.access_count * 0.05)
        
        self.importance = max(0.0, (self.confidence * decay) + access_boost)
        self.access_count += 1
        self.last_accessed = datetime.now()
        
        return self.importance
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'episode_id': self.episode_id,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'agents_involved': self.agents_involved,
            'outcome': self.outcome,
            'confidence': self.confidence,
            'tags': self.tags,
            'importance': self.importance,
            'access_count': self.access_count,
            'metadata': self.metadata
        }


@dataclass
class SemanticMemory:
    """Store knowledge, concepts, and relationships"""
    
    concept_id: str
    concept_name: str
    properties: Dict[str, Any]  # Key-value properties of concept
    relationships: List[Dict[str, str]]  # [{related_concept, relationship_type}]
    confidence: float  # 0.0 - 1.0
    source: str  # Where this knowledge came from
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Tracking
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    
    def add_relationship(self, related_concept: str, relationship_type: str) -> None:
        """Add relationship to another concept"""
        self.relationships.append({
            'related_concept': related_concept,
            'relationship_type': relationship_type
        })
    
    def update_confidence(self, evidence_count: int) -> float:
        """Update confidence based on evidence accumulation"""
        self.confidence = min(1.0, self.confidence + (evidence_count * 0.1))
        self.access_count += 1
        self.last_accessed = datetime.now()
        return self.confidence
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'concept_id': self.concept_id,
            'concept_name': self.concept_name,
            'properties': self.properties,
            'relationships': self.relationships,
            'confidence': self.confidence,
            'source': self.source,
            'timestamp': self.timestamp.isoformat(),
            'access_count': self.access_count
        }


@dataclass
class ProceduralMemory:
    """Store skills, procedures, and strategies"""
    
    procedure_id: str
    name: str
    steps: List[Dict[str, Any]]  # [{action, parameters, condition, result}]
    parameters: Dict[str, Any]  # Configurable parameters
    success_rate: float  # 0.0 - 1.0
    complexity: int  # 1-10 complexity level
    
    last_used: Optional[datetime] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Performance tracking
    executions: int = 0
    successes: int = 0
    failures: int = 0
    avg_execution_time_ms: float = 0.0
    
    def record_execution(self, success: bool, execution_time_ms: float = 0.0) -> None:
        """Record execution of procedure"""
        self.executions += 1
        if success:
            self.successes += 1
            self.success_rate = self.successes / self.executions
        else:
            self.failures += 1
        
        # Update average execution time
        if self.avg_execution_time_ms == 0:
            self.avg_execution_time_ms = execution_time_ms
        else:
            self.avg_execution_time_ms = (self.avg_execution_time_ms + execution_time_ms) / 2
        
        self.last_used = datetime.now()
    
    def improve_procedure(self, new_steps: List[Dict[str, Any]]) -> None:
        """Improve procedure with new steps"""
        self.steps = new_steps
        # Reset performance metrics for new version
        self.executions = 0
        self.successes = 0
        self.failures = 0
        self.success_rate = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'procedure_id': self.procedure_id,
            'name': self.name,
            'steps': self.steps,
            'parameters': self.parameters,
            'success_rate': self.success_rate,
            'complexity': self.complexity,
            'timestamp': self.timestamp.isoformat(),
            'executions': self.executions,
            'successes': self.successes,
            'failures': self.failures,
            'avg_execution_time_ms': self.avg_execution_time_ms
        }


class MemoryIndex:
    """Multi-dimensional indexing for fast retrieval"""
    
    def __init__(self):
        self.time_index: Dict[str, List[str]] = defaultdict(list)  # date -> memory_ids
        self.agent_index: Dict[str, List[str]] = defaultdict(list)  # agent_id -> memory_ids
        self.tag_index: Dict[str, List[str]] = defaultdict(list)  # tag -> memory_ids
        self.type_index: Dict[str, List[str]] = defaultdict(list)  # memory_type -> memory_ids
        self.concept_index: Dict[str, List[str]] = defaultdict(list)  # concept -> memory_ids
    
    def index_episodic(self, memory: EpisodicMemory) -> None:
        """Index episodic memory"""
        date_key = memory.timestamp.date().isoformat()
        self.time_index[date_key].append(memory.episode_id)
        
        for agent_id in memory.agents_involved:
            self.agent_index[agent_id].append(memory.episode_id)
        
        for tag in memory.tags:
            self.tag_index[tag].append(memory.episode_id)
        
        self.type_index['episodic'].append(memory.episode_id)
    
    def index_semantic(self, memory: SemanticMemory) -> None:
        """Index semantic memory"""
        self.type_index['semantic'].append(memory.concept_id)
        self.concept_index[memory.concept_name].append(memory.concept_id)
        
        for rel in memory.relationships:
            self.concept_index[rel['related_concept']].append(memory.concept_id)
    
    def index_procedural(self, memory: ProceduralMemory) -> None:
        """Index procedural memory"""
        self.type_index['procedural'].append(memory.procedure_id)
        self.tag_index[memory.name].append(memory.procedure_id)
    
    def remove_from_index(self, memory_id: str, index_type: str = None) -> None:
        """Remove memory from indices"""
        if index_type is None or index_type == 'episodic':
            for key_list in self.time_index.values():
                if memory_id in key_list:
                    key_list.remove(memory_id)
            for key_list in self.agent_index.values():
                if memory_id in key_list:
                    key_list.remove(memory_id)
        
        for key_list in self.tag_index.values():
            if memory_id in key_list:
                key_list.remove(memory_id)
        
        for key_list in self.type_index.values():
            if memory_id in key_list:
                key_list.remove(memory_id)
        
        for key_list in self.concept_index.values():
            if memory_id in key_list:
                key_list.remove(memory_id)


class EnhancedMemoryManager:
    """Manages all specialized memory types with optimization"""
    
    def __init__(self, max_episodic: int = 5000, max_semantic: int = 10000, max_procedural: int = 1000):
        """Initialize enhanced memory manager"""
        # Memory stores
        self.episodic_memories: Dict[str, EpisodicMemory] = {}
        self.semantic_memories: Dict[str, SemanticMemory] = {}
        self.procedural_memories: Dict[str, ProceduralMemory] = {}
        
        # Limits
        self.max_episodic = max_episodic
        self.max_semantic = max_semantic
        self.max_procedural = max_procedural
        
        # Indexing
        self.index = MemoryIndex()
        
        # Statistics
        self.total_retrievals = 0
        self.total_stores = 0
    
    # --- Episodic Memory Operations ---
    
    def store_episodic(self, description: str, agents_involved: List[str],
                      outcome: str, confidence: float = 0.8, tags: List[str] = None,
                      metadata: Dict[str, Any] = None) -> str:
        """Store episodic memory"""
        import uuid
        episode_id = str(uuid.uuid4())
        
        memory = EpisodicMemory(
            episode_id=episode_id,
            description=description,
            timestamp=datetime.now(),
            agents_involved=agents_involved,
            outcome=outcome,
            confidence=confidence,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        self.episodic_memories[episode_id] = memory
        self.index.index_episodic(memory)
        self.total_stores += 1
        
        # Check if over limit and prune if needed
        if len(self.episodic_memories) > self.max_episodic:
            self._prune_episodic()
        
        logger.info(f"Stored episodic memory: {episode_id}")
        return episode_id
    
    def retrieve_episodic(self, episode_id: str) -> Optional[EpisodicMemory]:
        """Retrieve episodic memory by ID"""
        if episode_id in self.episodic_memories:
            memory = self.episodic_memories[episode_id]
            memory.update_importance()
            self.total_retrievals += 1
            return memory
        return None
    
    def search_episodic_by_agent(self, agent_id: str, limit: int = 50) -> List[EpisodicMemory]:
        """Search episodic memories by agent"""
        memory_ids = self.index.agent_index.get(agent_id, [])
        memories = [self.episodic_memories[mid] for mid in memory_ids[:limit]]
        return memories
    
    def search_episodic_by_time(self, start_date: datetime, end_date: datetime) -> List[EpisodicMemory]:
        """Search episodic memories by time range"""
        memories = []
        current = start_date
        while current <= end_date:
            date_key = current.date().isoformat()
            memory_ids = self.index.time_index.get(date_key, [])
            memories.extend([self.episodic_memories[mid] for mid in memory_ids])
            current += timedelta(days=1)
        return memories
    
    def search_episodic_by_tag(self, tag: str) -> List[EpisodicMemory]:
        """Search episodic memories by tag"""
        memory_ids = self.index.tag_index.get(tag, [])
        memories = [self.episodic_memories[mid] for mid in memory_ids]
        return sorted(memories, key=lambda m: m.importance, reverse=True)
    
    # --- Semantic Memory Operations ---
    
    def store_semantic(self, concept_name: str, properties: Dict[str, Any],
                      source: str, confidence: float = 0.8) -> str:
        """Store semantic memory"""
        import uuid
        concept_id = str(uuid.uuid4())
        
        memory = SemanticMemory(
            concept_id=concept_id,
            concept_name=concept_name,
            properties=properties,
            relationships=[],
            confidence=confidence,
            source=source
        )
        
        self.semantic_memories[concept_id] = memory
        self.index.index_semantic(memory)
        self.total_stores += 1
        
        if len(self.semantic_memories) > self.max_semantic:
            self._prune_semantic()
        
        logger.info(f"Stored semantic memory: {concept_name}")
        return concept_id
    
    def retrieve_semantic(self, concept_name: str) -> Optional[SemanticMemory]:
        """Retrieve semantic memory by concept name"""
        concept_ids = self.index.concept_index.get(concept_name, [])
        if concept_ids:
            memory = self.semantic_memories.get(concept_ids[0])
            if memory:
                memory.access_count += 1
                memory.last_accessed = datetime.now()
                self.total_retrievals += 1
                return memory
        return None
    
    def get_related_concepts(self, concept_name: str) -> List[Dict[str, Any]]:
        """Get related concepts"""
        memory = self.retrieve_semantic(concept_name)
        if memory:
            return memory.relationships
        return []
    
    def add_semantic_relationship(self, concept_name: str, related_concept: str,
                                relationship_type: str) -> bool:
        """Add relationship between concepts"""
        memory = self.retrieve_semantic(concept_name)
        if memory:
            memory.add_relationship(related_concept, relationship_type)
            return True
        return False
    
    # --- Procedural Memory Operations ---
    
    def store_procedural(self, name: str, steps: List[Dict[str, Any]] = None,
                        parameters: Dict[str, Any] = None,
                        complexity: int = 5) -> str:
        """Store procedural memory"""
        import uuid
        procedure_id = str(uuid.uuid4())
        
        memory = ProceduralMemory(
            procedure_id=procedure_id,
            name=name,
            steps=steps or [],
            parameters=parameters or {},
            success_rate=0.5,
            complexity=complexity
        )
        
        self.procedural_memories[procedure_id] = memory
        self.index.index_procedural(memory)
        self.total_stores += 1
        
        if len(self.procedural_memories) > self.max_procedural:
            self._prune_procedural()
        
        logger.info(f"Stored procedural memory: {name}")
        return procedure_id
    
    def retrieve_procedural(self, name: str) -> Optional[ProceduralMemory]:
        """Retrieve procedural memory by name"""
        procedure_ids = self.index.tag_index.get(name, [])
        if procedure_ids:
            return self.procedural_memories.get(procedure_ids[0])
        return None
    
    def get_procedures_for_task(self, task_type: str, min_success_rate: float = 0.5) -> List[ProceduralMemory]:
        """Get procedures applicable for a task"""
        applicable = []
        for proc in self.procedural_memories.values():
            if 'task_type' in proc.parameters and proc.parameters['task_type'] == task_type:
                if proc.success_rate >= min_success_rate:
                    applicable.append(proc)
        return sorted(applicable, key=lambda p: p.success_rate, reverse=True)
    
    def record_procedure_execution(self, procedure_id: str, success: bool,
                                  execution_time_ms: float = 0.0) -> bool:
        """Record execution of procedure"""
        if procedure_id in self.procedural_memories:
            self.procedural_memories[procedure_id].record_execution(success, execution_time_ms)
            return True
        return False
    
    # --- Memory Optimization ---
    
    def _prune_episodic(self, retention_factor: float = 0.8) -> int:
        """Prune low-importance episodic memories"""
        count = int(self.max_episodic * (1 - retention_factor))
        
        # Sort by importance
        sorted_memories = sorted(
            self.episodic_memories.values(),
            key=lambda m: m.importance
        )
        
        # Remove lowest importance
        removed = 0
        for memory in sorted_memories[:count]:
            del self.episodic_memories[memory.episode_id]
            self.index.remove_from_index(memory.episode_id, 'episodic')
            removed += 1
        
        logger.info(f"Pruned {removed} episodic memories")
        return removed
    
    def _prune_semantic(self, retention_factor: float = 0.9) -> int:
        """Prune low-confidence semantic memories"""
        count = int(self.max_semantic * (1 - retention_factor))
        
        sorted_memories = sorted(
            self.semantic_memories.values(),
            key=lambda m: m.confidence
        )
        
        removed = 0
        for memory in sorted_memories[:count]:
            del self.semantic_memories[memory.concept_id]
            self.index.remove_from_index(memory.concept_id)
            removed += 1
        
        logger.info(f"Pruned {removed} semantic memories")
        return removed
    
    def _prune_procedural(self, retention_factor: float = 0.85) -> int:
        """Prune low-success procedural memories"""
        count = int(self.max_procedural * (1 - retention_factor))
        
        sorted_memories = sorted(
            self.procedural_memories.values(),
            key=lambda m: m.success_rate
        )
        
        removed = 0
        for memory in sorted_memories[:count]:
            del self.procedural_memories[memory.procedure_id]
            self.index.remove_from_index(memory.procedure_id)
            removed += 1
        
        logger.info(f"Pruned {removed} procedural memories")
        return removed
    
    def optimize_all(self) -> Dict[str, int]:
        """Run full optimization"""
        results = {
            'episodic_pruned': self._prune_episodic() if len(self.episodic_memories) > self.max_episodic else 0,
            'semantic_pruned': self._prune_semantic() if len(self.semantic_memories) > self.max_semantic else 0,
            'procedural_pruned': self._prune_procedural() if len(self.procedural_memories) > self.max_procedural else 0
        }
        
        logger.info(f"Memory optimization complete: {results}")
        return results
    
    # --- Advanced Retrieval ---
    
    def semantic_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search semantically similar concepts"""
        results = []
        
        # Simple string matching for now (can be enhanced with embeddings)
        query_lower = query.lower()
        for concept_id, memory in self.semantic_memories.items():
            if query_lower in memory.concept_name.lower() or \
               any(query_lower in str(v).lower() for v in memory.properties.values()):
                results.append({
                    'concept': memory.concept_name,
                    'confidence': memory.confidence,
                    'properties': memory.properties,
                    'score': memory.confidence
                })
        
        return sorted(results, key=lambda r: r['score'], reverse=True)[:limit]
    
    def temporal_search(self, agent_id: str, days_back: int = 30) -> List[EpisodicMemory]:
        """Search recent memories for agent"""
        start_date = datetime.now() - timedelta(days=days_back)
        all_memories = self.search_episodic_by_agent(agent_id)
        return [m for m in all_memories if m.timestamp >= start_date]
    
    def similarity_search(self, description: str, limit: int = 10) -> List[EpisodicMemory]:
        """Find similar past episodes"""
        results = []
        query_words = set(description.lower().split())
        
        for memory in self.episodic_memories.values():
            memory_words = set(memory.description.lower().split())
            similarity = len(query_words & memory_words) / max(len(query_words), 1)
            if similarity > 0.3:
                results.append((memory, similarity))
        
        return [m[0] for m in sorted(results, key=lambda x: x[1], reverse=True)[:limit]]
    
    # --- Statistics ---
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            'episodic_count': len(self.episodic_memories),
            'semantic_count': len(self.semantic_memories),
            'procedural_count': len(self.procedural_memories),
            'total_memories': len(self.episodic_memories) + len(self.semantic_memories) + len(self.procedural_memories),
            'total_stores': self.total_stores,
            'total_retrievals': self.total_retrievals,
            'episodic_max': self.max_episodic,
            'semantic_max': self.max_semantic,
            'procedural_max': self.max_procedural
        }
    
    def clear_all(self) -> None:
        """Clear all memories"""
        self.episodic_memories.clear()
        self.semantic_memories.clear()
        self.procedural_memories.clear()
        self.index = MemoryIndex()
        logger.info("Cleared all memories")
