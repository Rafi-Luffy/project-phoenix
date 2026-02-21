"""
Memory System API Endpoints - Phase 1.3
REST API for enhanced memory operations, storage, and retrieval
Integrates with all agent types for knowledge management
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import logging

from autonomous_system.core.enhanced_memory import EnhancedMemoryManager
from autonomous_system.core.memory_integration import MemoryIntegrationManager

logger = logging.getLogger(__name__)


# ==================== Request/Response Models ====================

class EpisodicMemoryRequest(BaseModel):
    """Request to store episodic memory"""
    description: str
    agents_involved: List[str] = Field(default_factory=list)
    outcome: str
    confidence: float = Field(0.8, ge=0.0, le=1.0)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EpisodicMemoryResponse(BaseModel):
    """Response with episodic memory"""
    episode_id: str
    description: str
    timestamp: str
    agents_involved: List[str]
    outcome: str
    confidence: float
    importance: float
    tags: List[str]
    access_count: int


class SemanticMemoryRequest(BaseModel):
    """Request to store semantic memory"""
    concept_name: str
    properties: Dict[str, Any]
    source: str
    confidence: float = Field(0.8, ge=0.0, le=1.0)


class SemanticMemoryResponse(BaseModel):
    """Response with semantic memory"""
    concept_id: str
    concept_name: str
    properties: Dict[str, Any]
    relationships: List[Dict[str, str]] = Field(default_factory=list)
    confidence: float
    source: str
    timestamp: str


class ProceduralMemoryRequest(BaseModel):
    """Request to store procedural memory"""
    name: str
    steps: List[Dict[str, Any]]
    parameters: Dict[str, Any] = Field(default_factory=dict)
    complexity: int = Field(5, ge=1, le=10)


class ProceduralMemoryResponse(BaseModel):
    """Response with procedural memory"""
    procedure_id: str
    name: str
    steps: List[Dict[str, Any]]
    parameters: Dict[str, Any]
    success_rate: float
    complexity: int
    executions: int


class SemanticRelationshipRequest(BaseModel):
    """Request to add relationship between concepts"""
    concept: str
    related_concept: str
    relationship_type: str


class ProcedureExecutionRequest(BaseModel):
    """Request to record procedure execution"""
    procedure_id: str
    success: bool
    execution_time_ms: float = Field(0.0, ge=0.0)


class MemorySearchRequest(BaseModel):
    """Request for memory search"""
    query: str
    limit: int = Field(10, ge=1, le=100)


class MemoryStatsResponse(BaseModel):
    """Response with memory statistics"""
    episodic_count: int
    episodic_limit: int
    semantic_count: int
    semantic_limit: int
    procedural_count: int
    procedural_limit: int
    total_memory_usage: str


class MemoryOptimizationResponse(BaseModel):
    """Response after memory optimization"""
    episodic_pruned: int
    semantic_pruned: int
    procedural_pruned: int
    total_removed: int
    optimization_timestamp: str


# ==================== Router Setup ====================

def create_memory_router(memory_manager: EnhancedMemoryManager,
                        integration_manager: MemoryIntegrationManager) -> APIRouter:
    """Create memory API router"""
    router = APIRouter(prefix="/api/v1/memory", tags=["memory"])
    
    # ==================== Health & Info ====================
    
    @router.get("/health")
    async def memory_health() -> Dict[str, str]:
        """Check memory system health"""
        try:
            stats = memory_manager.get_memory_stats()
            return {
                "status": "healthy",
                "episodic_memories": stats['episodic_count'],
                "semantic_memories": stats['semantic_count'],
                "procedural_memories": stats['procedural_count']
            }
        except Exception as e:
            logger.error(f"Memory health check failed: {e}")
            raise HTTPException(status_code=500, detail="Memory system unhealthy")
    
    @router.get("/stats", response_model=MemoryStatsResponse)
    async def get_memory_stats() -> MemoryStatsResponse:
        """Get memory system statistics"""
        try:
            stats = memory_manager.get_memory_stats()
            return MemoryStatsResponse(**stats)
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve memory stats")
    
    # ==================== Episodic Memory ====================
    
    @router.post("/episodic/store", response_model=Dict[str, str])
    async def store_episodic(request: EpisodicMemoryRequest) -> Dict[str, str]:
        """Store episodic memory"""
        try:
            episode_id = memory_manager.store_episodic(
                description=request.description,
                agents_involved=request.agents_involved,
                outcome=request.outcome,
                confidence=request.confidence,
                tags=request.tags,
                metadata=request.metadata
            )
            return {
                "episode_id": episode_id,
                "status": "stored",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to store episodic memory: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.get("/episodic/{episode_id}", response_model=EpisodicMemoryResponse)
    async def retrieve_episodic(episode_id: str) -> EpisodicMemoryResponse:
        """Retrieve episodic memory by ID"""
        try:
            memory = memory_manager.retrieve_episodic(episode_id)
            if not memory:
                raise HTTPException(status_code=404, detail="Episode not found")
            
            return EpisodicMemoryResponse(
                episode_id=episode_id,
                description=memory.description,
                timestamp=memory.timestamp.isoformat(),
                agents_involved=memory.agents_involved,
                outcome=memory.outcome,
                confidence=memory.confidence,
                importance=memory.importance,
                tags=memory.tags,
                access_count=memory.access_count
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve episodic memory: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/episodic/by-agent/{agent_id}")
    async def get_episodic_by_agent(agent_id: str, 
                                    limit: int = Query(50, ge=1, le=100)) -> List[EpisodicMemoryResponse]:
        """Get episodic memories for agent"""
        try:
            memories = memory_manager.search_episodic_by_agent(agent_id, limit)
            return [
                EpisodicMemoryResponse(
                    episode_id=m.episode_id,
                    description=m.description,
                    timestamp=m.timestamp.isoformat(),
                    agents_involved=m.agents_involved,
                    outcome=m.outcome,
                    confidence=m.confidence,
                    importance=m.importance,
                    tags=m.tags,
                    access_count=m.access_count
                )
                for m in memories
            ]
        except Exception as e:
            logger.error(f"Failed to get episodic memories for agent: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/episodic/by-tag/{tag}")
    async def get_episodic_by_tag(tag: str,
                                  limit: int = Query(50, ge=1, le=100)) -> List[EpisodicMemoryResponse]:
        """Get episodic memories by tag"""
        try:
            memories = memory_manager.search_episodic_by_tag(tag, limit)
            return [
                EpisodicMemoryResponse(
                    episode_id=m.episode_id,
                    description=m.description,
                    timestamp=m.timestamp.isoformat(),
                    agents_involved=m.agents_involved,
                    outcome=m.outcome,
                    confidence=m.confidence,
                    importance=m.importance,
                    tags=m.tags,
                    access_count=m.access_count
                )
                for m in memories
            ]
        except Exception as e:
            logger.error(f"Failed to get episodic memories by tag: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/episodic/time-range")
    async def get_episodic_by_time(start_date: date,
                                    end_date: date) -> List[EpisodicMemoryResponse]:
        """Get episodic memories in time range"""
        try:
            memories = memory_manager.search_episodic_by_time(start_date, end_date)
            return [
                EpisodicMemoryResponse(
                    episode_id=m.episode_id,
                    description=m.description,
                    timestamp=m.timestamp.isoformat(),
                    agents_involved=m.agents_involved,
                    outcome=m.outcome,
                    confidence=m.confidence,
                    importance=m.importance,
                    tags=m.tags,
                    access_count=m.access_count
                )
                for m in memories
            ]
        except Exception as e:
            logger.error(f"Failed to get episodic memories by time: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ==================== Semantic Memory ====================
    
    @router.post("/semantic/store", response_model=Dict[str, str])
    async def store_semantic(request: SemanticMemoryRequest) -> Dict[str, str]:
        """Store semantic memory"""
        try:
            concept_id = memory_manager.store_semantic(
                concept_name=request.concept_name,
                properties=request.properties,
                source=request.source,
                confidence=request.confidence
            )
            return {
                "concept_id": concept_id,
                "status": "stored",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to store semantic memory: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.get("/semantic/{concept_name}", response_model=SemanticMemoryResponse)
    async def retrieve_semantic(concept_name: str) -> SemanticMemoryResponse:
        """Retrieve semantic memory by concept name"""
        try:
            memory = memory_manager.retrieve_semantic(concept_name)
            if not memory:
                raise HTTPException(status_code=404, detail="Concept not found")
            
            return SemanticMemoryResponse(
                concept_id=memory.concept_id,
                concept_name=memory.concept_name,
                properties=memory.properties,
                relationships=memory.relationships,
                confidence=memory.confidence,
                source=memory.source,
                timestamp=memory.timestamp.isoformat()
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve semantic memory: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/semantic/relationship")
    async def add_semantic_relationship(request: SemanticRelationshipRequest) -> Dict[str, Any]:
        """Add relationship between concepts"""
        try:
            success = memory_manager.add_semantic_relationship(
                request.concept,
                request.related_concept,
                request.relationship_type
            )
            return {
                "success": success,
                "concept": request.concept,
                "related_concept": request.related_concept,
                "relationship_type": request.relationship_type,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to add semantic relationship: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.get("/semantic/{concept_name}/related")
    async def get_related_concepts(concept_name: str) -> Dict[str, Any]:
        """Get concepts related to given concept"""
        try:
            related = memory_manager.get_related_concepts(concept_name)
            return {
                "concept": concept_name,
                "related_concepts": related,
                "count": len(related)
            }
        except Exception as e:
            logger.error(f"Failed to get related concepts: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ==================== Procedural Memory ====================
    
    @router.post("/procedural/store", response_model=Dict[str, str])
    async def store_procedural(request: ProceduralMemoryRequest) -> Dict[str, str]:
        """Store procedural memory"""
        try:
            procedure_id = memory_manager.store_procedural(
                name=request.name,
                steps=request.steps,
                parameters=request.parameters,
                complexity=request.complexity
            )
            return {
                "procedure_id": procedure_id,
                "status": "stored",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to store procedural memory: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.get("/procedural/{procedure_name}", response_model=ProceduralMemoryResponse)
    async def retrieve_procedural(procedure_name: str) -> ProceduralMemoryResponse:
        """Retrieve procedural memory by name"""
        try:
            memory = memory_manager.retrieve_procedural(procedure_name)
            if not memory:
                raise HTTPException(status_code=404, detail="Procedure not found")
            
            return ProceduralMemoryResponse(
                procedure_id=memory.procedure_id,
                name=memory.name,
                steps=memory.steps,
                parameters=memory.parameters,
                success_rate=memory.success_rate,
                complexity=memory.complexity,
                executions=memory.executions
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve procedural memory: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/procedural/by-task/{task_type}")
    async def get_procedures_for_task(task_type: str,
                                     min_success_rate: float = Query(0.6, ge=0.0, le=1.0)) -> List[ProceduralMemoryResponse]:
        """Get procedures for a task"""
        try:
            procedures = memory_manager.get_procedures_for_task(task_type, min_success_rate)
            return [
                ProceduralMemoryResponse(
                    procedure_id=p.procedure_id,
                    name=p.name,
                    steps=p.steps,
                    parameters=p.parameters,
                    success_rate=p.success_rate,
                    complexity=p.complexity,
                    executions=p.executions
                )
                for p in procedures
            ]
        except Exception as e:
            logger.error(f"Failed to get procedures for task: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/procedural/record-execution")
    async def record_procedure_execution(request: ProcedureExecutionRequest) -> Dict[str, Any]:
        """Record execution of a procedure"""
        try:
            success = memory_manager.record_procedure_execution(
                request.procedure_id,
                request.success,
                request.execution_time_ms
            )
            return {
                "procedure_id": request.procedure_id,
                "success": request.success,
                "recorded": success,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to record procedure execution: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    # ==================== Search & Retrieval ====================
    
    @router.post("/search/semantic")
    async def semantic_search(request: MemorySearchRequest) -> Dict[str, Any]:
        """Semantic search across memories"""
        try:
            results = memory_manager.semantic_search(request.query, request.limit)
            return {
                "query": request.query,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/search/temporal/{agent_id}")
    async def temporal_search(agent_id: str,
                             days_back: int = Query(30, ge=1)) -> Dict[str, Any]:
        """Temporal search for agent memories"""
        try:
            results = memory_manager.temporal_search(agent_id, days_back)
            return {
                "agent_id": agent_id,
                "days_back": days_back,
                "results": [m.to_dict() for m in results],
                "count": len(results)
            }
        except Exception as e:
            logger.error(f"Temporal search failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/search/similarity")
    async def similarity_search(request: MemorySearchRequest) -> Dict[str, Any]:
        """Similarity search across memories"""
        try:
            results = memory_manager.similarity_search(request.query, request.limit)
            return {
                "query": request.query,
                "results": [m.to_dict() for m in results],
                "count": len(results)
            }
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ==================== Optimization ====================
    
    @router.post("/optimize", response_model=MemoryOptimizationResponse)
    async def optimize_memory() -> MemoryOptimizationResponse:
        """Optimize all memory types"""
        try:
            result = memory_manager.optimize_all()
            return MemoryOptimizationResponse(
                episodic_pruned=result.get('episodic_pruned', 0),
                semantic_pruned=result.get('semantic_pruned', 0),
                procedural_pruned=result.get('procedural_pruned', 0),
                total_removed=result.get('total_removed', 0),
                optimization_timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            logger.error(f"Memory optimization failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.delete("/clear")
    async def clear_all_memory() -> Dict[str, str]:
        """Clear all memory"""
        try:
            memory_manager.clear_all()
            return {
                "status": "cleared",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ==================== Integration Manager ====================
    
    @router.get("/integration/stats")
    async def get_integration_stats() -> Dict[str, Any]:
        """Get memory integration statistics"""
        try:
            stats = integration_manager.get_system_memory_stats()
            return stats
        except Exception as e:
            logger.error(f"Failed to get integration stats: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/integration/agent/{agent_id}")
    async def get_agent_memory_context(agent_id: str) -> Dict[str, Any]:
        """Get memory context for an agent"""
        try:
            context = integration_manager.get_agent_memory_context(agent_id)
            if not context:
                raise HTTPException(status_code=404, detail="Agent not found")
            return context
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get agent memory context: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return router
