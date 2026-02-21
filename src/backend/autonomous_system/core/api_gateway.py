"""
API Gateway Layer
Central entry point for all system requests using FastAPI
Handles routing, request validation, and response formatting
"""

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from enum import Enum

from autonomous_system.core.database import (
    Agent, Incident, Correction, LearningRecord,
    MemoryEntry, Communication, Task, PostgreSQLDatabase
)
from autonomous_system.core.auth import AuthenticationManager, TokenData
from autonomous_system.core.message_protocol import MessageProtocol
from autonomous_system.core.state_coordination import CoordinationMode


logger = logging.getLogger(__name__)


class APIRequest(BaseModel):
    request_id: str
    timestamp: datetime
    endpoint: str
    method: str
    user_id: Optional[str] = None
    payload: Dict[str, Any] = {}


class APIResponse(BaseModel):
    status: str
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = None
    request_id: str = ""
    
    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now()
        super().__init__(**data)


class APIGateway:
    """API Gateway managing all HTTP endpoints and request routing"""
    
    def __init__(self, database: PostgreSQLDatabase):
        self.app = FastAPI(
            title="Autonomous Self-Healing System",
            version="1.0.0",
            description="Enterprise-grade self-correcting multi-agent system"
        )
        self.database = database
        self.auth_manager = AuthenticationManager()
        self.request_log = []
        
        self._configure_middleware()
        self._configure_routes()
    
    def _configure_middleware(self):
        """Configure middleware for security, logging, and CORS"""
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @self.app.middleware("http")
        async def request_logging_middleware(request: Request, call_next):
            import uuid
            request_id = str(uuid.uuid4())
            
            request.state.request_id = request_id
            start_time = datetime.now()
            
            response = await call_next(request)
            
            process_time = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"Request {request_id} | {request.method} {request.url.path} | "
                f"Status: {response.status_code} | Duration: {process_time:.3f}s"
            )
            
            response.headers["X-Request-ID"] = request_id
            return response
    
    def _configure_routes(self):
        """Configure all API endpoints"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return APIResponse(
                status="healthy",
                data={
                    "timestamp": datetime.now(),
                    "agents": len(self.database.get_all_agents()),
                    "incidents": len(self.database.get_all_incidents()),
                    "memory_entries": len(self.database.memory_entries)
                }
            )
        
        @self.app.post("/agents/register")
        async def register_agent(agent_data: Dict[str, Any]):
            """Register a new agent in the system"""
            try:
                agent = Agent(
                    name=agent_data.get("name"),
                    agent_type=agent_data.get("agent_type"),
                    capabilities=agent_data.get("capabilities", []),
                    configuration=agent_data.get("configuration", {})
                )
                agent_id = self.database.save_agent(agent)
                logger.info(f"Agent registered: {agent_id}")
                return APIResponse(
                    status="success",
                    data={"agent_id": agent_id}
                )
            except Exception as e:
                logger.error(f"Failed to register agent: {str(e)}")
                return APIResponse(
                    status="error",
                    error=str(e)
                )
        
        @self.app.get("/agents/{agent_id}")
        async def get_agent(agent_id: str):
            """Retrieve agent details"""
            agent = self.database.get_agent(agent_id)
            if not agent:
                return APIResponse(
                    status="error",
                    error="Agent not found"
                )
            return APIResponse(
                status="success",
                data=agent.to_dict()
            )
        
        @self.app.get("/agents")
        async def list_agents():
            """List all registered agents"""
            agents = self.database.get_all_agents()
            return APIResponse(
                status="success",
                data=[agent.to_dict() for agent in agents]
            )
        
        @self.app.post("/incidents/report")
        async def report_incident(incident_data: Dict[str, Any]):
            """Report a new incident"""
            try:
                incident = Incident(
                    type=incident_data.get("type"),
                    severity=incident_data.get("severity", "medium"),
                    description=incident_data.get("description"),
                    component=incident_data.get("component"),
                    detected_by=incident_data.get("detected_by"),
                    error_trace=incident_data.get("error_trace", "")
                )
                incident_id = self.database.save_incident(incident)
                logger.info(f"Incident reported: {incident_id} ({incident.severity})")
                return APIResponse(
                    status="success",
                    data={"incident_id": incident_id}
                )
            except Exception as e:
                logger.error(f"Failed to report incident: {str(e)}")
                return APIResponse(
                    status="error",
                    error=str(e)
                )
        
        @self.app.get("/incidents/{incident_id}")
        async def get_incident(incident_id: str):
            """Retrieve incident details"""
            incident = self.database.get_incident(incident_id)
            if not incident:
                return APIResponse(
                    status="error",
                    error="Incident not found"
                )
            corrections = self.database.get_corrections_by_incident(incident_id)
            return APIResponse(
                status="success",
                data={
                    "incident": incident.to_dict(),
                    "corrections": [cor.to_dict() for cor in corrections]
                }
            )
        
        @self.app.get("/incidents")
        async def list_incidents(status: Optional[str] = None):
            """List incidents, optionally filtered by status"""
            if status:
                incidents = self.database.get_incidents_by_status(status)
            else:
                incidents = self.database.get_all_incidents()
            return APIResponse(
                status="success",
                data=[incident.to_dict() for incident in incidents]
            )
        
        @self.app.post("/corrections/apply")
        async def apply_correction(correction_data: Dict[str, Any]):
            """Apply a correction to an incident"""
            try:
                correction = Correction(
                    incident_id=correction_data.get("incident_id"),
                    correction_type=correction_data.get("correction_type"),
                    applied_by=correction_data.get("applied_by"),
                    details=correction_data.get("details", {})
                )
                correction_id = self.database.save_correction(correction)
                logger.info(f"Correction applied: {correction_id}")
                return APIResponse(
                    status="success",
                    data={"correction_id": correction_id}
                )
            except Exception as e:
                logger.error(f"Failed to apply correction: {str(e)}")
                return APIResponse(
                    status="error",
                    error=str(e)
                )
        
        @self.app.post("/tasks/create")
        async def create_task(task_data: Dict[str, Any]):
            """Create a new task"""
            try:
                task = Task(
                    name=task_data.get("name"),
                    task_type=task_data.get("task_type"),
                    assigned_to=task_data.get("assigned_to"),
                    priority=task_data.get("priority", 5),
                    dependencies=task_data.get("dependencies", []),
                    payload=task_data.get("payload", {})
                )
                task_id = self.database.save_task(task)
                logger.info(f"Task created: {task_id}")
                return APIResponse(
                    status="success",
                    data={"task_id": task_id}
                )
            except Exception as e:
                logger.error(f"Failed to create task: {str(e)}")
                return APIResponse(
                    status="error",
                    error=str(e)
                )
        
        @self.app.get("/tasks/{task_id}")
        async def get_task(task_id: str):
            """Retrieve task details"""
            task = self.database.get_task(task_id)
            if not task:
                return APIResponse(
                    status="error",
                    error="Task not found"
                )
            return APIResponse(
                status="success",
                data=task.to_dict()
            )
        
        @self.app.get("/tasks")
        async def list_tasks(status: Optional[str] = None):
            """List tasks, optionally filtered by status"""
            if status:
                tasks = self.database.get_tasks_by_status(status)
            else:
                tasks = list(self.database.tasks.values())
            return APIResponse(
                status="success",
                data=[task.to_dict() for task in tasks]
            )
        
        @self.app.post("/memory/store")
        async def store_memory(memory_data: Dict[str, Any]):
            """Store an entry in long-term memory"""
            try:
                entry = MemoryEntry(
                    memory_type=memory_data.get("memory_type"),
                    content=memory_data.get("content"),
                    tags=memory_data.get("tags", [])
                )
                entry_id = self.database.save_memory_entry(entry)
                logger.info(f"Memory entry stored: {entry_id}")
                return APIResponse(
                    status="success",
                    data={"entry_id": entry_id}
                )
            except Exception as e:
                logger.error(f"Failed to store memory: {str(e)}")
                return APIResponse(
                    status="error",
                    error=str(e)
                )
        
        @self.app.get("/memory/search")
        async def search_memory(tags: List[str]):
            """Search memory by tags"""
            entries = self.database.get_memory_by_tags(tags)
            return APIResponse(
                status="success",
                data=[entry.to_dict() for entry in entries]
            )
        
        @self.app.post("/communication/send")
        async def send_communication(comm_data: Dict[str, Any]):
            """Send message between agents"""
            try:
                comm = Communication(
                    sender_id=comm_data.get("sender_id"),
                    recipient_id=comm_data.get("recipient_id"),
                    message_type=comm_data.get("message_type"),
                    content=comm_data.get("content"),
                    priority=comm_data.get("priority", 5),
                    payload=comm_data.get("payload", {})
                )
                comm_id = self.database.save_communication(comm)
                logger.info(f"Communication sent: {comm_id}")
                return APIResponse(
                    status="success",
                    data={"communication_id": comm_id}
                )
            except Exception as e:
                logger.error(f"Failed to send communication: {str(e)}")
                return APIResponse(
                    status="error",
                    error=str(e)
                )
        
        @self.app.get("/communications/{agent_id}")
        async def get_communications(agent_id: str):
            """Get communications for an agent"""
            communications = self.database.get_communications_for_agent(agent_id)
            return APIResponse(
                status="success",
                data=[comm.to_dict() for comm in communications]
            )
        
        @self.app.get("/system/status")
        async def system_status():
            """Get comprehensive system status"""
            return APIResponse(
                status="success",
                data={
                    "timestamp": datetime.now(),
                    "total_agents": len(self.database.get_all_agents()),
                    "active_incidents": len(self.database.get_incidents_by_status("open")),
                    "resolved_incidents": len(self.database.get_incidents_by_status("resolved")),
                    "total_corrections": len(self.database.corrections),
                    "total_learning_records": len(self.database.learning_records),
                    "total_memory_entries": len(self.database.memory_entries),
                    "pending_tasks": len(self.database.get_tasks_by_status("pending"))
                }
            )
        
        # --- Phase 1.2: Advanced Agent Framework Endpoints ---
        
        @self.app.post("/agents/specialized/create")
        async def create_specialized_agent(request: Dict[str, Any]):
            """Create a specialized agent (Supervisor, Worker, Monitor, Learning, Decision)"""
            try:
                from autonomous_system.core.orchestrator import get_orchestrator
                orchestrator = get_orchestrator()
                
                agent_type = request.get("agent_type")
                agent_name = request.get("agent_name")
                description = request.get("description", "")
                config_data = request.get("config_data", {})
                
                agent_id = orchestrator.create_specialized_agent(
                    agent_type=agent_type,
                    agent_name=agent_name,
                    description=description,
                    config_data=config_data
                )
                
                if agent_id:
                    return APIResponse(
                        status="success",
                        data={"agent_id": agent_id, "agent_type": agent_type}
                    )
                else:
                    return APIResponse(
                        status="error",
                        error=f"Failed to create {agent_type} agent"
                    )
                    
            except Exception as e:
                logger.error(f"Specialized agent creation failed: {str(e)}")
                return APIResponse(status="error", error=str(e))
        
        @self.app.get("/agents/specialized/{agent_id}/status")
        async def get_specialized_agent_status(agent_id: str):
            """Get specialized agent status"""
            try:
                from autonomous_system.core.orchestrator import get_orchestrator
                orchestrator = get_orchestrator()
                
                status = orchestrator.get_agent_status(agent_id)
                if status:
                    return APIResponse(status="success", data=status)
                else:
                    return APIResponse(status="error", error="Agent not found")
                    
            except Exception as e:
                logger.error(f"Failed to get agent status: {str(e)}")
                return APIResponse(status="error", error=str(e))
        
        @self.app.post("/messages/protocol/send")
        async def send_protocol_message(request: Dict[str, Any]):
            """Send message with specific protocol"""
            try:
                from autonomous_system.core.orchestrator import get_orchestrator
                orchestrator = get_orchestrator()
                
                sender_id = request.get("sender_id")
                receiver_id = request.get("receiver_id")
                protocol = MessageProtocol[request.get("protocol", "REQUEST_REPLY").upper()]
                content = request.get("content", {})
                
                message_id = orchestrator.send_protocol_message(
                    sender_id=sender_id,
                    receiver_id=receiver_id,
                    protocol=protocol,
                    content=content
                )
                
                if message_id:
                    return APIResponse(
                        status="success",
                        data={"message_id": message_id, "protocol": protocol.value}
                    )
                else:
                    return APIResponse(
                        status="error",
                        error="Failed to send message"
                    )
                    
            except Exception as e:
                logger.error(f"Protocol message failed: {str(e)}")
                return APIResponse(status="error", error=str(e))
        
        @self.app.get("/agents/{agent_id}/state")
        async def get_agent_state(agent_id: str):
            """Get agent state from coordinator"""
            try:
                from autonomous_system.core.orchestrator import get_orchestrator
                orchestrator = get_orchestrator()
                
                state = orchestrator.get_agent_state(agent_id)
                if state is not None:
                    return APIResponse(status="success", data=state)
                else:
                    return APIResponse(status="error", error="Agent state not found")
                    
            except Exception as e:
                logger.error(f"Failed to get agent state: {str(e)}")
                return APIResponse(status="error", error=str(e))
        
        @self.app.put("/agents/{agent_id}/state")
        async def update_agent_state(agent_id: str, request: Dict[str, Any]):
            """Update agent state in coordinator"""
            try:
                from autonomous_system.core.orchestrator import get_orchestrator
                orchestrator = get_orchestrator()
                
                new_state = request.get("state", {})
                success = orchestrator.update_agent_state(agent_id, new_state)
                
                if success:
                    return APIResponse(
                        status="success",
                        data={"agent_id": agent_id, "updated_state": new_state}
                    )
                else:
                    return APIResponse(
                        status="error",
                        error="Failed to update agent state"
                    )
                    
            except Exception as e:
                logger.error(f"State update failed: {str(e)}")
                return APIResponse(status="error", error=str(e))
        
        @self.app.post("/coordination/locks/acquire")
        async def acquire_lock(request: Dict[str, Any]):
            """Acquire distributed lock"""
            try:
                from autonomous_system.core.orchestrator import get_orchestrator
                orchestrator = get_orchestrator()
                
                resource_id = request.get("resource_id")
                agent_id = request.get("agent_id")
                timeout = request.get("timeout", 300)
                
                success = orchestrator.acquire_distributed_lock(resource_id, agent_id, timeout)
                
                if success:
                    return APIResponse(
                        status="success",
                        data={"resource_id": resource_id, "holder": agent_id}
                    )
                else:
                    return APIResponse(
                        status="error",
                        error="Failed to acquire lock"
                    )
                    
            except Exception as e:
                logger.error(f"Lock acquisition failed: {str(e)}")
                return APIResponse(status="error", error=str(e))
        
        @self.app.post("/coordination/locks/release")
        async def release_lock(request: Dict[str, Any]):
            """Release distributed lock"""
            try:
                from autonomous_system.core.orchestrator import get_orchestrator
                orchestrator = get_orchestrator()
                
                resource_id = request.get("resource_id")
                agent_id = request.get("agent_id")
                
                success = orchestrator.release_distributed_lock(resource_id, agent_id)
                
                if success:
                    return APIResponse(
                        status="success",
                        data={"resource_id": resource_id, "released_by": agent_id}
                    )
                else:
                    return APIResponse(
                        status="error",
                        error="Failed to release lock"
                    )
                    
            except Exception as e:
                logger.error(f"Lock release failed: {str(e)}")
                return APIResponse(status="error", error=str(e))
        
        @self.app.post("/coordination/consensus/start")
        async def start_consensus_vote(request: Dict[str, Any]):
            """Start consensus voting round"""
            try:
                from autonomous_system.core.orchestrator import get_orchestrator
                orchestrator = get_orchestrator()
                
                proposal = request.get("proposal", {})
                required_agents = request.get("required_agents")
                
                vote_id = orchestrator.start_consensus_vote(proposal, required_agents)
                
                if vote_id:
                    return APIResponse(
                        status="success",
                        data={"vote_id": vote_id, "proposal": proposal}
                    )
                else:
                    return APIResponse(
                        status="error",
                        error="Failed to start consensus vote"
                    )
                    
            except Exception as e:
                logger.error(f"Consensus vote failed: {str(e)}")
                return APIResponse(status="error", error=str(e))
        
        @self.app.post("/coordination/consensus/vote")
        async def cast_vote(request: Dict[str, Any]):
            """Cast vote in consensus round"""
            try:
                from autonomous_system.core.orchestrator import get_orchestrator
                orchestrator = get_orchestrator()
                
                vote_id = request.get("vote_id")
                agent_id = request.get("agent_id")
                vote = request.get("vote", False)
                
                success = orchestrator.cast_consensus_vote(vote_id, agent_id, vote)
                
                if success:
                    return APIResponse(
                        status="success",
                        data={"vote_id": vote_id, "voter": agent_id, "vote": vote}
                    )
                else:
                    return APIResponse(
                        status="error",
                        error="Failed to cast vote"
                    )
                    
            except Exception as e:
                logger.error(f"Vote casting failed: {str(e)}")
                return APIResponse(status="error", error=str(e))
        
        @self.app.get("/system/phase-1-2/status")
        async def get_phase_1_2_status():
            """Get Phase 1.2 component status"""
            try:
                from autonomous_system.core.orchestrator import get_orchestrator
                orchestrator = get_orchestrator()
                
                phase_status = orchestrator.get_phase_1_2_status()
                return APIResponse(status="success", data=phase_status)
                    
            except Exception as e:
                logger.error(f"Failed to get Phase 1.2 status: {str(e)}")
                return APIResponse(status="error", error=str(e))
    
    def get_app(self) -> FastAPI:
        """Return FastAPI application instance"""
        return self.app
