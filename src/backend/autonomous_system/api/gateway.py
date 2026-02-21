"""
API Gateway for Autonomous Self-Healing System
Provides REST and GraphQL endpoints for all entity types and operations
Built with FastAPI for high performance and async support
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
from pydantic import BaseModel, Field
import asyncio
from enum import Enum

from ..core.database import (
    PostgreSQLDatabase, Agent, Incident, Correction, LearningRecord,
    MemoryEntry, Communication, Task, EntityType
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models for request/response validation
class AgentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    LEARNING = "learning"
    COORDINATING = "coordinating"


class AgentCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    agent_type: str = Field(..., min_length=1, max_length=100)
    capabilities: List[str] = Field(default_factory=list)
    configuration: Dict[str, Any] = Field(default_factory=dict)


class AgentUpdateRequest(BaseModel):
    status: Optional[AgentStatus] = None
    configuration: Optional[Dict[str, Any]] = None
    capabilities: Optional[List[str]] = None


class AgentResponse(BaseModel):
    agent_id: str
    name: str
    agent_type: str
    status: str
    capabilities: List[str]
    created_at: str
    last_heartbeat: str
    configuration: Dict[str, Any]

    @staticmethod
    def from_agent(agent: Agent) -> "AgentResponse":
        return AgentResponse(
            agent_id=agent.agent_id,
            name=agent.name,
            agent_type=agent.agent_type,
            status=agent.status,
            capabilities=agent.capabilities,
            created_at=agent.created_at,
            last_heartbeat=agent.last_heartbeat,
            configuration=agent.configuration
        )


class IncidentSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentCreateRequest(BaseModel):
    incident_type: str = Field(..., min_length=1, max_length=100)
    severity: IncidentSeverity
    component: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    error_message: Optional[str] = None
    error_stack_trace: Optional[str] = None
    detected_by_agent_id: Optional[str] = None


class IncidentUpdateRequest(BaseModel):
    status: Optional[IncidentStatus] = None
    resolution_notes: Optional[str] = None
    severity: Optional[IncidentSeverity] = None


class IncidentResponse(BaseModel):
    incident_id: str
    incident_type: str
    severity: str
    component: str
    description: str
    status: str
    created_at: str
    detected_by_agent_id: Optional[str]
    error_message: Optional[str]
    error_stack_trace: Optional[str]
    resolution_notes: Optional[str]

    @staticmethod
    def from_incident(incident: Incident) -> "IncidentResponse":
        return IncidentResponse(
            incident_id=incident.incident_id,
            incident_type=incident.incident_type,
            severity=incident.severity,
            component=incident.component,
            description=incident.description,
            status=incident.status,
            created_at=incident.created_at,
            detected_by_agent_id=incident.detected_by_agent_id,
            error_message=incident.error_message,
            error_stack_trace=incident.error_stack_trace,
            resolution_notes=incident.resolution_notes
        )


class CorrectionCreateRequest(BaseModel):
    incident_id: str
    applied_by_agent_id: str
    correction_type: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    changes_made: Dict[str, Any] = Field(default_factory=dict)


class CorrectionResponse(BaseModel):
    correction_id: str
    incident_id: str
    applied_by_agent_id: str
    correction_type: str
    description: str
    created_at: str
    changes_made: Dict[str, Any]
    outcome: str
    effectiveness_score: float

    @staticmethod
    def from_correction(correction: Correction) -> "CorrectionResponse":
        return CorrectionResponse(
            correction_id=correction.correction_id,
            incident_id=correction.incident_id,
            applied_by_agent_id=correction.applied_by_agent_id,
            correction_type=correction.correction_type,
            description=correction.description,
            created_at=correction.created_at,
            changes_made=correction.changes_made,
            outcome=correction.outcome,
            effectiveness_score=correction.effectiveness_score
        )


class LearningRecordCreateRequest(BaseModel):
    agent_id: str
    pattern: str = Field(..., min_length=1)
    context: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(..., ge=0.0, le=1.0)


class LearningRecordResponse(BaseModel):
    learning_id: str
    agent_id: str
    pattern: str
    context: Dict[str, Any]
    confidence: float
    created_at: str
    extracted_rule: Optional[str]

    @staticmethod
    def from_learning_record(record: LearningRecord) -> "LearningRecordResponse":
        return LearningRecordResponse(
            learning_id=record.learning_id,
            agent_id=record.agent_id,
            pattern=record.pattern,
            context=record.context,
            confidence=record.confidence,
            created_at=record.created_at,
            extracted_rule=record.extracted_rule
        )


class MemoryEntryCreateRequest(BaseModel):
    agent_id: str
    content: str = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)


class MemoryEntryResponse(BaseModel):
    memory_id: str
    agent_id: str
    content: str
    tags: List[str]
    importance: float
    created_at: str
    access_count: int
    relevance_score: float

    @staticmethod
    def from_memory_entry(entry: MemoryEntry) -> "MemoryEntryResponse":
        return MemoryEntryResponse(
            memory_id=entry.memory_id,
            agent_id=entry.agent_id,
            content=entry.content,
            tags=entry.tags,
            importance=entry.importance,
            created_at=entry.created_at,
            access_count=entry.access_count,
            relevance_score=entry.relevance_score
        )


class CommunicationCreateRequest(BaseModel):
    from_agent_id: str
    to_agent_id: str
    message_type: str = Field(..., min_length=1, max_length=100)
    content: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=1, ge=0, le=10)


class CommunicationResponse(BaseModel):
    communication_id: str
    from_agent_id: str
    to_agent_id: str
    message_type: str
    content: Dict[str, Any]
    priority: int
    status: str
    created_at: str

    @staticmethod
    def from_communication(comm: Communication) -> "CommunicationResponse":
        return CommunicationResponse(
            communication_id=comm.communication_id,
            from_agent_id=comm.from_agent_id,
            to_agent_id=comm.to_agent_id,
            message_type=comm.message_type,
            content=comm.content,
            priority=comm.priority,
            status=comm.status,
            created_at=comm.created_at
        )


class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskCreateRequest(BaseModel):
    task_type: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    assigned_to_agent_id: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    priority: int = Field(default=1, ge=0, le=10)
    parameters: Dict[str, Any] = Field(default_factory=dict)


class TaskUpdateRequest(BaseModel):
    status: Optional[TaskStatus] = None
    assigned_to_agent_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class TaskResponse(BaseModel):
    task_id: str
    task_type: str
    description: str
    status: str
    assigned_to_agent_id: Optional[str]
    created_at: str
    dependencies: List[str]
    priority: int
    parameters: Dict[str, Any]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]

    @staticmethod
    def from_task(task: Task) -> "TaskResponse":
        return TaskResponse(
            task_id=task.task_id,
            task_type=task.task_type,
            description=task.description,
            status=task.status,
            assigned_to_agent_id=task.assigned_to_agent_id,
            created_at=task.created_at,
            dependencies=task.dependencies,
            priority=task.priority,
            parameters=task.parameters,
            result=task.result,
            error_message=task.error_message
        )


# Health response model
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str


# Error response model
class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
    timestamp: str


# Global database instance
db = PostgreSQLDatabase()


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Autonomous Self-Healing System API Gateway Starting")
    yield
    logger.info("Autonomous Self-Healing System API Gateway Shutting Down")


# Create FastAPI application
app = FastAPI(
    title="Autonomous Self-Healing System API",
    description="REST API for autonomous agent coordination and self-correction",
    version="1.0.0",
    lifespan=lifespan
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoints
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """System health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )


@app.get("/health/detailed", response_model=Dict[str, Any], tags=["Health"])
async def detailed_health_check():
    """Detailed system health metrics"""
    total_agents = len(db.agents)
    active_agents = len([a for a in db.agents.values() if a.status == "active"])
    total_incidents = len(db.incidents)
    open_incidents = len([i for i in db.incidents.values() if i.status == "open"])
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "agents": {"total": total_agents, "active": active_agents},
        "incidents": {"total": total_incidents, "open": open_incidents},
        "tasks": len(db.tasks),
        "memory_entries": len(db.memory_entries),
        "communications": len(db.communications)
    }


# Agent endpoints
@app.post("/agents", response_model=AgentResponse, status_code=201, tags=["Agents"])
async def create_agent(request: AgentCreateRequest):
    """Create a new autonomous agent"""
    agent = db.save_agent(
        name=request.name,
        agent_type=request.agent_type,
        capabilities=request.capabilities,
        configuration=request.configuration
    )
    logger.info(f"Agent created: {agent.agent_id}")
    return AgentResponse.from_agent(agent)


@app.get("/agents", response_model=List[AgentResponse], tags=["Agents"])
async def list_agents(
    status: Optional[str] = Query(None),
    agent_type: Optional[str] = Query(None)
):
    """List all agents with optional filtering"""
    agents = db.get_all_agents()
    
    if status:
        agents = [a for a in agents if a.status == status]
    if agent_type:
        agents = [a for a in agents if a.agent_type == agent_type]
    
    return [AgentResponse.from_agent(a) for a in agents]


@app.get("/agents/{agent_id}", response_model=AgentResponse, tags=["Agents"])
async def get_agent(agent_id: str):
    """Get specific agent details"""
    agent = db.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    return AgentResponse.from_agent(agent)


@app.patch("/agents/{agent_id}", response_model=AgentResponse, tags=["Agents"])
async def update_agent(agent_id: str, request: AgentUpdateRequest):
    """Update agent configuration and status"""
    agent = db.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    if request.status:
        agent.status = request.status
    if request.configuration:
        agent.configuration.update(request.configuration)
    if request.capabilities is not None:
        agent.capabilities = request.capabilities
    
    agent.last_heartbeat = datetime.utcnow().isoformat()
    logger.info(f"Agent updated: {agent_id}")
    return AgentResponse.from_agent(agent)


@app.post("/agents/{agent_id}/heartbeat", response_model=Dict[str, str], tags=["Agents"])
async def agent_heartbeat(agent_id: str):
    """Record agent heartbeat for monitoring"""
    agent = db.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    agent.last_heartbeat = datetime.utcnow().isoformat()
    logger.debug(f"Heartbeat received from agent: {agent_id}")
    return {"status": "heartbeat_recorded", "agent_id": agent_id}


# Incident endpoints
@app.post("/incidents", response_model=IncidentResponse, status_code=201, tags=["Incidents"])
async def create_incident(request: IncidentCreateRequest):
    """Report a new incident"""
    incident = db.save_incident(
        incident_type=request.incident_type,
        severity=request.severity,
        component=request.component,
        description=request.description,
        error_message=request.error_message,
        error_stack_trace=request.error_stack_trace,
        detected_by_agent_id=request.detected_by_agent_id
    )
    logger.warning(f"Incident created: {incident.incident_id} (severity: {incident.severity})")
    return IncidentResponse.from_incident(incident)


@app.get("/incidents", response_model=List[IncidentResponse], tags=["Incidents"])
async def list_incidents(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    component: Optional[str] = Query(None)
):
    """List all incidents with optional filtering"""
    incidents = list(db.incidents.values())
    
    if status:
        incidents = [i for i in incidents if i.status == status]
    if severity:
        incidents = [i for i in incidents if i.severity == severity]
    if component:
        incidents = [i for i in incidents if i.component == component]
    
    return [IncidentResponse.from_incident(i) for i in incidents]


@app.get("/incidents/{incident_id}", response_model=IncidentResponse, tags=["Incidents"])
async def get_incident(incident_id: str):
    """Get specific incident details"""
    incident = db.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return IncidentResponse.from_incident(incident)


@app.patch("/incidents/{incident_id}", response_model=IncidentResponse, tags=["Incidents"])
async def update_incident(incident_id: str, request: IncidentUpdateRequest):
    """Update incident status and notes"""
    incident = db.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    
    if request.status:
        incident.status = request.status
    if request.resolution_notes:
        incident.resolution_notes = request.resolution_notes
    if request.severity:
        incident.severity = request.severity
    
    logger.info(f"Incident updated: {incident_id}, new status: {incident.status}")
    return IncidentResponse.from_incident(incident)


# Correction endpoints
@app.post("/corrections", response_model=CorrectionResponse, status_code=201, tags=["Corrections"])
async def create_correction(request: CorrectionCreateRequest):
    """Record a correction applied to an incident"""
    correction = db.save_correction(
        incident_id=request.incident_id,
        applied_by_agent_id=request.applied_by_agent_id,
        correction_type=request.correction_type,
        description=request.description,
        changes_made=request.changes_made
    )
    logger.info(f"Correction created: {correction.correction_id}")
    return CorrectionResponse.from_correction(correction)


@app.get("/corrections", response_model=List[CorrectionResponse], tags=["Corrections"])
async def list_corrections(incident_id: Optional[str] = Query(None)):
    """List all corrections, optionally filtered by incident"""
    if incident_id:
        corrections = db.get_corrections_by_incident(incident_id)
    else:
        corrections = list(db.corrections.values())
    
    return [CorrectionResponse.from_correction(c) for c in corrections]


@app.get("/incidents/{incident_id}/corrections", response_model=List[CorrectionResponse], tags=["Corrections"])
async def get_incident_corrections(incident_id: str):
    """Get all corrections for a specific incident"""
    incident = db.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    
    corrections = db.get_corrections_by_incident(incident_id)
    return [CorrectionResponse.from_correction(c) for c in corrections]


# Learning record endpoints
@app.post("/learning-records", response_model=LearningRecordResponse, status_code=201, tags=["Learning"])
async def create_learning_record(request: LearningRecordCreateRequest):
    """Record a learned pattern or rule"""
    agent = db.get_agent(request.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {request.agent_id} not found")
    
    record = db.save_learning_record(
        agent_id=request.agent_id,
        pattern=request.pattern,
        context=request.context,
        confidence=request.confidence
    )
    logger.info(f"Learning record created: {record.learning_id}")
    return LearningRecordResponse.from_learning_record(record)


@app.get("/learning-records", response_model=List[LearningRecordResponse], tags=["Learning"])
async def list_learning_records(agent_id: Optional[str] = Query(None)):
    """List learning records, optionally filtered by agent"""
    records = list(db.learning_records.values())
    
    if agent_id:
        records = [r for r in records if r.agent_id == agent_id]
    
    return [LearningRecordResponse.from_learning_record(r) for r in records]


@app.get("/agents/{agent_id}/learning", response_model=List[LearningRecordResponse], tags=["Learning"])
async def get_agent_learning(agent_id: str):
    """Get learning records for a specific agent"""
    agent = db.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    records = [r for r in db.learning_records.values() if r.agent_id == agent_id]
    return [LearningRecordResponse.from_learning_record(r) for r in records]


# Memory endpoints
@app.post("/memory", response_model=MemoryEntryResponse, status_code=201, tags=["Memory"])
async def create_memory_entry(request: MemoryEntryCreateRequest):
    """Store a memory entry for an agent"""
    agent = db.get_agent(request.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {request.agent_id} not found")
    
    entry = db.save_memory_entry(
        agent_id=request.agent_id,
        content=request.content,
        tags=request.tags,
        importance=request.importance
    )
    logger.info(f"Memory entry created: {entry.memory_id}")
    return MemoryEntryResponse.from_memory_entry(entry)


@app.get("/memory", response_model=List[MemoryEntryResponse], tags=["Memory"])
async def query_memory(
    agent_id: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None)
):
    """Query memory entries"""
    if tags:
        entries = db.get_memory_by_tags(tags)
    else:
        entries = list(db.memory_entries.values())
    
    if agent_id:
        entries = [e for e in entries if e.agent_id == agent_id]
    
    return [MemoryEntryResponse.from_memory_entry(e) for e in entries]


@app.get("/agents/{agent_id}/memory", response_model=List[MemoryEntryResponse], tags=["Memory"])
async def get_agent_memory(agent_id: str):
    """Get memory entries for a specific agent"""
    agent = db.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    entries = [e for e in db.memory_entries.values() if e.agent_id == agent_id]
    return [MemoryEntryResponse.from_memory_entry(e) for e in entries]


# Communication endpoints
@app.post("/communications", response_model=CommunicationResponse, status_code=201, tags=["Communication"])
async def send_message(request: CommunicationCreateRequest):
    """Send a message between agents"""
    from_agent = db.get_agent(request.from_agent_id)
    to_agent = db.get_agent(request.to_agent_id)
    
    if not from_agent:
        raise HTTPException(status_code=404, detail=f"From agent {request.from_agent_id} not found")
    if not to_agent:
        raise HTTPException(status_code=404, detail=f"To agent {request.to_agent_id} not found")
    
    comm = db.save_communication(
        from_agent_id=request.from_agent_id,
        to_agent_id=request.to_agent_id,
        message_type=request.message_type,
        content=request.content,
        priority=request.priority
    )
    logger.info(f"Communication sent: {comm.communication_id} from {request.from_agent_id} to {request.to_agent_id}")
    return CommunicationResponse.from_communication(comm)


@app.get("/communications", response_model=List[CommunicationResponse], tags=["Communication"])
async def list_communications(
    agent_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """List communications"""
    communications = list(db.communications.values())
    
    if agent_id:
        communications = [c for c in communications if c.from_agent_id == agent_id or c.to_agent_id == agent_id]
    if status:
        communications = [c for c in communications if c.status == status]
    
    return [CommunicationResponse.from_communication(c) for c in communications]


@app.get("/agents/{agent_id}/communications", response_model=List[CommunicationResponse], tags=["Communication"])
async def get_agent_communications(agent_id: str, unread_only: bool = Query(False)):
    """Get communications for a specific agent"""
    agent = db.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    comms = db.get_communications_for_agent(agent_id)
    
    if unread_only:
        comms = [c for c in comms if c.status == "pending"]
    
    return [CommunicationResponse.from_communication(c) for c in comms]


# Task endpoints
@app.post("/tasks", response_model=TaskResponse, status_code=201, tags=["Tasks"])
async def create_task(request: TaskCreateRequest):
    """Create a new task"""
    if request.assigned_to_agent_id:
        agent = db.get_agent(request.assigned_to_agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {request.assigned_to_agent_id} not found")
    
    task = db.save_task(
        task_type=request.task_type,
        description=request.description,
        assigned_to_agent_id=request.assigned_to_agent_id,
        dependencies=request.dependencies,
        priority=request.priority,
        parameters=request.parameters
    )
    logger.info(f"Task created: {task.task_id}")
    return TaskResponse.from_task(task)


@app.get("/tasks", response_model=List[TaskResponse], tags=["Tasks"])
async def list_tasks(
    status: Optional[str] = Query(None),
    agent_id: Optional[str] = Query(None)
):
    """List all tasks with optional filtering"""
    tasks = list(db.tasks.values())
    
    if status:
        tasks = [t for t in tasks if t.status == status]
    if agent_id:
        tasks = [t for t in tasks if t.assigned_to_agent_id == agent_id]
    
    return [TaskResponse.from_task(t) for t in tasks]


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def get_task(task_id: str):
    """Get specific task details"""
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return TaskResponse.from_task(task)


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def update_task(task_id: str, request: TaskUpdateRequest):
    """Update task status and results"""
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    if request.status:
        task.status = request.status
    if request.assigned_to_agent_id:
        agent = db.get_agent(request.assigned_to_agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {request.assigned_to_agent_id} not found")
        task.assigned_to_agent_id = request.assigned_to_agent_id
    if request.result:
        task.result = request.result
    if request.error_message:
        task.error_message = request.error_message
    
    logger.info(f"Task updated: {task_id}, new status: {task.status}")
    return TaskResponse.from_task(task)


@app.get("/agents/{agent_id}/tasks", response_model=List[TaskResponse], tags=["Tasks"])
async def get_agent_tasks(agent_id: str, status: Optional[str] = Query(None)):
    """Get tasks assigned to a specific agent"""
    agent = db.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    tasks = db.get_tasks_for_agent(agent_id)
    
    if status:
        tasks = [t for t in tasks if t.status == status]
    
    return [TaskResponse.from_task(t) for t in tasks]


# Global error handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            timestamp=datetime.utcnow().isoformat()
        ).model_dump()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
