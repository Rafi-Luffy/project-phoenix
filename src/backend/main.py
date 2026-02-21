"""
Main entry point for the autonomous self-healing system
FastAPI application with integrated orchestrator
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List, Dict
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
import uvicorn

from autonomous_system.core import (
    CoreOrchestrator, get_orchestrator,
    AuthenticationManager, PermissionLevel,
    EventType, MetricType, MemoryType, MemoryPriority,
    MessageType
)
from autonomous_system.core.llm_system_integration import (
    initialize_llm_integration, get_llm_integrator,
    initialize_all_llm, shutdown_all_llm
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting Autonomous Self-Healing System...")
    orchestrator = get_orchestrator()
    initialized = await orchestrator.initialize()
    
    if not initialized:
        logger.error("Failed to initialize system")
        raise RuntimeError("System initialization failed")
    
    # Initialize LLM integration (graceful degradation if unavailable)
    logger.info("🤖 Initializing LLM integration layer...")
    initialize_llm_integration(orchestrator)
    await initialize_all_llm()
    
    yield
    
    # Shutdown
    logger.info("Shutting down system...")
    await shutdown_all_llm()
    await orchestrator.shutdown()


# Create FastAPI app with lifecycle
app = FastAPI(
    title="Autonomous Self-Healing System",
    description="Distributed system with self-correction, learning, and adaptation",
    version="0.1.0",
    lifespan=lifespan
)


# --- Dependency Injection ---

async def get_token(authorization: str = Header(None)) -> str:
    """Extract and validate token from header"""
    # Allow health checks without auth for testing
    # In production, uncomment the validation below
    if not authorization:
        return "guest"  # Default guest token for testing
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return "guest"  # Default guest token for testing
    
    return parts[1]


# --- Health & Status Endpoints ---

@app.get("/health")
async def health_check():
    """System health check including LLM status"""
    orchestrator = get_orchestrator()
    health = await orchestrator.health_check()
    
    # Add LLM integration health
    llm_integrator = get_llm_integrator()
    if llm_integrator:
        llm_health = await llm_integrator.get_health_status()
        health["llm"] = llm_health
    
    return health


@app.get("/status")
async def system_status():
    """Get system status"""
    orchestrator = get_orchestrator()
    return orchestrator.get_system_status()


# --- Authentication Endpoints ---

@app.post("/auth/login")
async def login(username: str, password: str):
    """User login"""
    orchestrator = get_orchestrator()
    token = orchestrator.authenticate_user(username, password)
    
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"token": token, "type": "bearer"}


# --- Agent Management Endpoints ---

@app.post("/agents")
async def create_agent(
    agent_type: str,
    name: str,
    description: str = "",
    token: str = Depends(get_token)
):
    """Create a new agent"""
    orchestrator = get_orchestrator()
    
    # Verify permission
    if not orchestrator.verify_user_permission(token, PermissionLevel.CREATE):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    agent_id = orchestrator.create_agent(agent_type, name, description)
    
    if not agent_id:
        raise HTTPException(status_code=500, detail="Failed to create agent")
    
    return {
        "agent_id": agent_id,
        "agent_type": agent_type,
        "name": name,
        "status": "created"
    }


@app.get("/agents")
async def list_agents(token: str = Depends(get_token)):
    """List all agents"""
    orchestrator = get_orchestrator()
    
    if not orchestrator.verify_user_permission(token, PermissionLevel.READ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    agents = orchestrator.get_all_agents_status()
    return {"agents": agents, "count": len(agents)}


@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str, token: str = Depends(get_token)):
    """Get agent details"""
    orchestrator = get_orchestrator()
    
    if not orchestrator.verify_user_permission(token, PermissionLevel.READ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    status = orchestrator.get_agent_status(agent_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return status


# --- Task Execution Endpoints ---

@app.post("/agents/{agent_id}/tasks")
async def execute_task(
    agent_id: str,
    task_data: dict,
    token: str = Depends(get_token)
):
    """Execute task on agent"""
    orchestrator = get_orchestrator()
    
    if not orchestrator.verify_user_permission(token, PermissionLevel.EXECUTE):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    result = await orchestrator.execute_task(agent_id, task_data)
    return result


# --- Memory Management Endpoints ---

@app.post("/memory")
async def store_memory(
    content: dict,
    memory_type: str,
    agent_id: str = None,
    tags: list = None,
    token: str = Depends(get_token)
):
    """Store memory"""
    orchestrator = get_orchestrator()
    
    if not orchestrator.verify_user_permission(token, PermissionLevel.CREATE):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        mt = MemoryType[memory_type.upper()]
        memory_id = orchestrator.store_memory(
            content=content,
            memory_type=mt,
            agent_id=agent_id,
            tags=tags or []
        )
        return {"memory_id": memory_id, "status": "stored"}
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid memory type")


@app.get("/memory/{memory_id}")
async def retrieve_memory(
    memory_id: str,
    token: str = Depends(get_token)
):
    """Retrieve memory"""
    orchestrator = get_orchestrator()
    
    if not orchestrator.verify_user_permission(token, PermissionLevel.READ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    memory = orchestrator.retrieve_memory(memory_id)
    
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    return memory


@app.get("/memory/search")
async def search_memories(
    query: str = None,
    agent_id: str = None,
    memory_type: str = None,
    token: str = Depends(get_token)
):
    """Search memories"""
    orchestrator = get_orchestrator()
    
    if not orchestrator.verify_user_permission(token, PermissionLevel.READ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        mt = MemoryType[memory_type.upper()] if memory_type else None
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid memory type")
    
    memories = orchestrator.search_memories(
        query=query,
        agent_id=agent_id,
        memory_type=mt
    )
    
    return {"memories": memories, "count": len(memories)}


# --- Monitoring & Logging Endpoints ---

@app.get("/metrics")
async def get_metrics(
    metric_type: str = None,
    token: str = Depends(get_token)
):
    """Get system metrics"""
    orchestrator = get_orchestrator()
    
    if not orchestrator.verify_user_permission(token, PermissionLevel.READ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        mt = MetricType[metric_type.upper()] if metric_type else None
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid metric type")
    
    metrics = orchestrator.get_system_metrics(mt)
    return {"metrics": metrics, "count": len(metrics)}


@app.get("/alerts")
async def get_alerts(token: str = Depends(get_token)):
    """Get active alerts"""
    orchestrator = get_orchestrator()
    
    if not orchestrator.verify_user_permission(token, PermissionLevel.READ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    alerts = orchestrator.get_active_alerts()
    return {"alerts": alerts, "count": len(alerts)}


@app.get("/logs")
async def get_logs(
    limit: int = 100,
    token: str = Depends(get_token)
):
    """Get system logs"""
    orchestrator = get_orchestrator()
    
    if not orchestrator.verify_user_permission(token, PermissionLevel.READ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    logs = orchestrator.get_system_logs(limit)
    return {"logs": logs, "count": len(logs)}


@app.get("/events")
async def get_events(
    event_type: str = None,
    limit: int = 100,
    token: str = Depends(get_token)
):
    """Get event history"""
    orchestrator = get_orchestrator()
    
    if not orchestrator.verify_user_permission(token, PermissionLevel.READ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        et = EventType[event_type.upper()] if event_type else None
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid event type")
    
    events = orchestrator.get_event_history(et, limit)
    return {"events": events, "count": len(events)}


# --- Message Passing Endpoints ---

@app.post("/messages")
async def send_message(
    sender_id: str,
    receiver_id: str,
    message_type: str,
    content: dict,
    token: str = Depends(get_token)
):
    """Send message between agents"""
    orchestrator = get_orchestrator()
    
    if not orchestrator.verify_user_permission(token, PermissionLevel.EXECUTE):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        mt = MessageType[message_type.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid message type")
    
    message_id = orchestrator.send_message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        message_type=mt,
        content=content
    )
    
    return {"message_id": message_id, "status": "sent"}


@app.get("/messages/{agent_id}")
async def get_messages(
    agent_id: str,
    token: str = Depends(get_token)
):
    """Get pending messages for agent"""
    orchestrator = get_orchestrator()
    
    if not orchestrator.verify_user_permission(token, PermissionLevel.READ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    messages = orchestrator.get_pending_messages(agent_id)
    return {"messages": messages, "count": len(messages)}


# --- LLM Integration Endpoints ---

@app.get("/llm/health")
async def llm_health_check(token: str = Depends(get_token)):
    """Get LLM integration health status"""
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    llm_integrator = get_llm_integrator()
    if not llm_integrator:
        return {"status": "not_initialized", "llm_available": False}
    
    health = await llm_integrator.get_health_status()
    return health


@app.post("/llm/analyze_error")
async def llm_analyze_error(
    payload: dict,
    token: str = Depends(get_token)
):
    """
    Analyze error with LLM reasoning
    Provides root cause analysis and recommendations
    """
    llm_integrator = get_llm_integrator()
    if not llm_integrator:
        return {"error": "LLM not initialized"}
    
    try:
        # Create error context for LLM analysis
        from autonomous_system.core.error_detection import ErrorContext, ErrorSeverity, ErrorType
        from datetime import datetime
        
        error_type_str = payload.get("error_type", "UNKNOWN_ERROR")
        error_message = payload.get("error_message", "Unknown error")
        context = payload.get("context", {})
        
        # Map string to ErrorType enum
        try:
            error_type = ErrorType[error_type_str]
        except KeyError:
            error_type = ErrorType.UNKNOWN_ERROR
        
        error_ctx = ErrorContext(
            agent_id="api-request",
            operation="error_analysis",
            timestamp=datetime.now(),
            error_type=error_type,
            severity=ErrorSeverity.MODERATE,
            message=error_message,
            stack_trace="",
            metadata=context
        )
        
        result = await llm_integrator.analyze_error_with_reasoning(error_ctx)
        return result
    except Exception as e:
        logger.error(f"Error in LLM analysis endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"LLM analysis failed: {str(e)}")


@app.post("/llm/explain_correction")
async def llm_explain_correction(
    error_message: str,
    strategy: str,
    result: str = None,
    token: str = Depends(get_token)
):
    """
    Generate natural language explanation for correction decision
    """
    llm_integrator = get_llm_integrator()
    if not llm_integrator or not llm_integrator.llm_enabled:
        return {"explanation": f"Applied strategy: {strategy}"}
    
    try:
        explanation = await llm_integrator.explain_correction_decision(
            error_message,
            strategy,
            result
        )
        return {"explanation": explanation, "strategy": strategy}
    except Exception as e:
        logger.error(f"Error in LLM explanation endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Explanation generation failed: {str(e)}")


@app.post("/llm/detect_patterns")
async def llm_detect_patterns(
    errors: List[Dict] = None,
    token: str = Depends(get_token)
):
    """
    Use LLM to detect patterns across multiple errors
    """
    llm_integrator = get_llm_integrator()
    if not llm_integrator or not llm_integrator.llm_enabled:
        return {"patterns_found": 0, "patterns": []}
    
    if not errors:
        return {"error": "No errors provided"}
    
    try:
        patterns = await llm_integrator.detect_error_patterns(errors)
        return patterns
    except Exception as e:
        logger.error(f"Error in pattern detection endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Pattern detection failed: {str(e)}")


@app.post("/llm/optimize")
async def llm_optimize_system(
    system_state: Dict = None,
    metrics: Dict = None,
    token: str = Depends(get_token)
):
    """
    Get LLM recommendations for system optimization
    """
    llm_integrator = get_llm_integrator()
    if not llm_integrator or not llm_integrator.llm_enabled:
        return {"recommendations": []}
    
    if not system_state or not metrics:
        return {"error": "system_state and metrics required"}
    
    try:
        recommendations = await llm_integrator.recommend_optimizations(
            system_state,
            metrics
        )
        return {"recommendations": recommendations, "count": len(recommendations)}
    except Exception as e:
        logger.error(f"Error in optimization endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


# --- Agent Management Endpoints ---

@app.patch("/agents/{agent_id}")
async def update_agent(
    agent_id: str,
    updates: Dict = None,
    token: str = Depends(get_token)
):
    """
    Update an agent with new configuration or parameters
    """
    orchestrator = get_orchestrator()
    if not updates:
        raise HTTPException(status_code=400, detail="Updates required")
    
    try:
        agent = orchestrator.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        # Update agent properties
        for key, value in updates.items():
            if hasattr(agent, key):
                setattr(agent, key, value)
        
        return {"status": "updated", "agent_id": agent_id, "updates": updates}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent: {e}")
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")


@app.delete("/agents/{agent_id}")
async def delete_agent(
    agent_id: str,
    token: str = Depends(get_token)
):
    """
    Delete an agent and clean up its resources
    """
    orchestrator = get_orchestrator()
    
    try:
        agent = orchestrator.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        # Remove agent from orchestrator
        orchestrator.remove_agent(agent_id)
        
        return {"status": "deleted", "agent_id": agent_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting agent: {e}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")


@app.post("/agents/{agent_id}/start")
async def start_agent(
    agent_id: str,
    token: str = Depends(get_token)
):
    """
    Start an agent and begin its execution
    """
    orchestrator = get_orchestrator()
    
    try:
        agent = orchestrator.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        await agent.start()
        
        return {"status": "started", "agent_id": agent_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting agent: {e}")
        raise HTTPException(status_code=500, detail=f"Start failed: {str(e)}")


@app.post("/agents/{agent_id}/stop")
async def stop_agent(
    agent_id: str,
    token: str = Depends(get_token)
):
    """
    Stop an agent and halt its execution
    """
    orchestrator = get_orchestrator()
    
    try:
        agent = orchestrator.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        await agent.stop()
        
        return {"status": "stopped", "agent_id": agent_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping agent: {e}")
        raise HTTPException(status_code=500, detail=f"Stop failed: {str(e)}")


# --- Memory Management Endpoints ---

@app.delete("/memory/{memory_id}")
async def delete_memory(
    memory_id: str,
    token: str = Depends(get_token)
):
    """
    Delete a memory entry and clear associated data
    """
    orchestrator = get_orchestrator()
    
    try:
        # Delete from memory system
        success = await orchestrator.delete_memory(memory_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Memory {memory_id} not found")
        
        return {"status": "deleted", "memory_id": memory_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting memory: {e}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")


# --- Corrections Management Endpoints ---

@app.get("/corrections")
async def list_corrections(
    agent_id: str = None,
    limit: int = 50,
    token: str = Depends(get_token)
):
    """
    List all corrections or corrections for a specific agent
    """
    orchestrator = get_orchestrator()
    
    try:
        corrections = await orchestrator.get_corrections(agent_id, limit)
        return {
            "corrections": corrections,
            "count": len(corrections),
            "agent_id": agent_id
        }
    except Exception as e:
        logger.error(f"Error listing corrections: {e}")
        raise HTTPException(status_code=500, detail=f"Listing failed: {str(e)}")


@app.get("/corrections/{correction_id}")
async def get_correction(
    correction_id: str,
    token: str = Depends(get_token)
):
    """
    Get detailed information about a specific correction
    """
    orchestrator = get_orchestrator()
    
    try:
        correction = await orchestrator.get_correction(correction_id)
        
        if not correction:
            raise HTTPException(status_code=404, detail=f"Correction {correction_id} not found")
        
        return correction
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting correction: {e}")
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")


@app.post("/corrections/{correction_id}/replay")
async def replay_correction(
    correction_id: str,
    token: str = Depends(get_token)
):
    """
    Replay a correction to reapply its changes
    """
    orchestrator = get_orchestrator()
    
    try:
        correction = await orchestrator.get_correction(correction_id)
        
        if not correction:
            raise HTTPException(status_code=404, detail=f"Correction {correction_id} not found")
        
        # Replay the correction
        result = await orchestrator.replay_correction(correction_id)
        
        return {
            "status": "replayed",
            "correction_id": correction_id,
            "result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error replaying correction: {e}")
        raise HTTPException(status_code=500, detail=f"Replay failed: {str(e)}")


# --- Authentication Token Endpoints ---

@app.post("/auth/token")
async def generate_token(
    username: str = None,
    password: str = None
):
    """
    Generate a new API token for authentication
    """
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
    
    try:
        auth_manager = AuthenticationManager()
        token = await auth_manager.generate_token(username, password)
        
        if not token:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 3600
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating token: {e}")
        raise HTTPException(status_code=500, detail=f"Token generation failed: {str(e)}")


@app.post("/auth/refresh")
async def refresh_token(
    token: str = Depends(get_token)
):
    """
    Refresh an existing API token
    """
    if token == "guest":
        raise HTTPException(status_code=401, detail="Cannot refresh guest token")
    
    try:
        auth_manager = AuthenticationManager()
        new_token = await auth_manager.refresh_token(token)
        
        if not new_token:
            raise HTTPException(status_code=401, detail="Token refresh failed")
        
        return {
            "access_token": new_token,
            "token_type": "bearer",
            "expires_in": 3600
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}")


@app.delete("/auth/revoke")
async def revoke_token(
    token: str = Depends(get_token)
):
    """
    Revoke an API token and invalidate it
    """
    if token == "guest":
        return {"status": "guest token cannot be revoked"}
    
    try:
        auth_manager = AuthenticationManager()
        success = await auth_manager.revoke_token(token)
        
        return {
            "status": "revoked" if success else "revocation failed",
            "token_revoked": success
        }
    except Exception as e:
        logger.error(f"Error revoking token: {e}")
        raise HTTPException(status_code=500, detail=f"Token revocation failed: {str(e)}")


# --- Error Handlers ---

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
