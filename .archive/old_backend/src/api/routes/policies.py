"""
Correction policies management endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from datetime import datetime
from models import PolicyCreate, PolicyResponse
import uuid

router = APIRouter()

# In-memory storage for demo (TODO: Replace with database)
policies_db: dict = {}


@router.post("", response_model=PolicyResponse)
async def create_policy(policy: PolicyCreate):
    """
    Create a new correction policy
    """
    policy_id = str(uuid.uuid4())
    
    response = PolicyResponse(
        id=policy_id,
        name=policy.name,
        description=policy.description,
        system_id=policy.system_id,
        enabled=policy.enabled,
        conditions=policy.conditions,
        actions=policy.actions,
        priority=policy.priority,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        executions=0
    )
    
    policies_db[policy_id] = response.model_dump()
    
    return response


@router.get("", response_model=List[PolicyResponse])
async def list_policies(
    system_id: str = Query(None),
    enabled: bool = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    List policies with optional filtering
    """
    results = list(policies_db.values())
    
    # Apply filters
    if system_id:
        results = [p for p in results if p["system_id"] == system_id]
    if enabled is not None:
        results = [p for p in results if p["enabled"] == enabled]
    
    # Sort by priority descending, then by creation time
    results = sorted(results, key=lambda p: (-p["priority"], p["created_at"]), reverse=True)
    
    # Apply pagination
    results = results[offset:offset + limit]
    
    return [PolicyResponse(**p) for p in results]


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(policy_id: str):
    """
    Get a specific policy
    """
    if policy_id not in policies_db:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    return PolicyResponse(**policies_db[policy_id])


@router.put("/{policy_id}", response_model=PolicyResponse)
async def update_policy(policy_id: str, policy: PolicyCreate):
    """
    Update a policy
    """
    if policy_id not in policies_db:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    existing = policies_db[policy_id]
    existing.update(policy.model_dump(exclude_unset=True))
    existing["updated_at"] = datetime.utcnow()
    
    policies_db[policy_id] = existing
    
    return PolicyResponse(**existing)


@router.delete("/{policy_id}")
async def delete_policy(policy_id: str):
    """
    Delete a policy
    """
    if policy_id not in policies_db:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    del policies_db[policy_id]
    
    return {"message": f"Policy {policy_id} deleted", "id": policy_id}


@router.post("/{policy_id}/enable")
async def enable_policy(policy_id: str):
    """
    Enable a policy
    """
    if policy_id not in policies_db:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    policies_db[policy_id]["enabled"] = True
    policies_db[policy_id]["updated_at"] = datetime.utcnow()
    
    return PolicyResponse(**policies_db[policy_id])


@router.post("/{policy_id}/disable")
async def disable_policy(policy_id: str):
    """
    Disable a policy
    """
    if policy_id not in policies_db:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    policies_db[policy_id]["enabled"] = False
    policies_db[policy_id]["updated_at"] = datetime.utcnow()
    
    return PolicyResponse(**policies_db[policy_id])


@router.get("/system/{system_id}/active")
async def get_active_policies(system_id: str):
    """
    Get all active policies for a system
    """
    policies = [
        p for p in policies_db.values()
        if p["system_id"] == system_id and p["enabled"]
    ]
    
    return [PolicyResponse(**p) for p in policies]
