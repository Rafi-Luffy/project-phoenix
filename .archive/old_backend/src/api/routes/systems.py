"""
Systems management endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from datetime import datetime
from models import SystemRegister, SystemResponse, SystemStatus
import uuid

router = APIRouter()

# In-memory storage for demo (TODO: Replace with database)
systems_db: dict = {}


@router.post("", response_model=SystemResponse)
async def register_system(system: SystemRegister):
    """
    Register a new system to monitor
    """
    system_id = str(uuid.uuid4())
    
    response = SystemResponse(
        id=system_id,
        name=system.name,
        type=system.type,
        endpoint=system.endpoint,
        description=system.description,
        tags=system.tags,
        metadata=system.metadata,
        status=SystemStatus.HEALTHY,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    systems_db[system_id] = response.model_dump()
    
    return response


@router.get("", response_model=List[SystemResponse])
async def list_systems(
    status: SystemStatus = Query(None),
    type: str = Query(None),
    tag: str = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    List all registered systems with optional filtering
    """
    results = list(systems_db.values())
    
    # Apply filters
    if status:
        results = [s for s in results if s["status"] == status]
    if type:
        results = [s for s in results if s["type"] == type]
    if tag:
        results = [s for s in results if tag in s.get("tags", [])]
    
    # Apply pagination
    results = results[offset:offset + limit]
    
    return [SystemResponse(**s) for s in results]


@router.get("/{system_id}", response_model=SystemResponse)
async def get_system(system_id: str):
    """
    Get a specific system by ID
    """
    if system_id not in systems_db:
        raise HTTPException(status_code=404, detail="System not found")
    
    return SystemResponse(**systems_db[system_id])


@router.put("/{system_id}", response_model=SystemResponse)
async def update_system(system_id: str, system: SystemRegister):
    """
    Update a system configuration
    """
    if system_id not in systems_db:
        raise HTTPException(status_code=404, detail="System not found")
    
    existing = systems_db[system_id]
    existing.update(system.model_dump(exclude_unset=True))
    existing["updated_at"] = datetime.utcnow()
    
    systems_db[system_id] = existing
    
    return SystemResponse(**existing)


@router.delete("/{system_id}")
async def delete_system(system_id: str):
    """
    Unregister a system from monitoring
    """
    if system_id not in systems_db:
        raise HTTPException(status_code=404, detail="System not found")
    
    del systems_db[system_id]
    
    return {"message": f"System {system_id} deleted", "id": system_id}


@router.get("/{system_id}/status", response_model=dict)
async def get_system_status(system_id: str):
    """
    Get detailed status of a specific system
    """
    if system_id not in systems_db:
        raise HTTPException(status_code=404, detail="System not found")
    
    system = systems_db[system_id]
    
    return {
        "id": system_id,
        "name": system["name"],
        "status": system.get("status", "unknown"),
        "last_seen": system.get("last_seen"),
        "health_score": 0.95,  # TODO: Calculate from metrics
        "error_rate": 0.02,
        "uptime_percentage": 99.95,
        "active_events": 0,  # TODO: Count from events
        "active_corrections": 0,  # TODO: Count from corrections
        "checked_at": datetime.utcnow()
    }


@router.post("/{system_id}/ping")
async def ping_system(system_id: str):
    """
    Ping a system to verify connectivity
    """
    if system_id not in systems_db:
        raise HTTPException(status_code=404, detail="System not found")
    
    system = systems_db[system_id]
    
    # TODO: Implement actual connectivity check
    
    return {
        "id": system_id,
        "name": system["name"],
        "reachable": True,
        "response_time_ms": 12.5,
        "timestamp": datetime.utcnow()
    }
