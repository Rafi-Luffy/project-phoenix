"""
Correction execution and history endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from datetime import datetime
from models import CorrectionAttempt, CorrectionResponse, CorrectionStatus
import uuid

router = APIRouter()

# In-memory storage for demo (TODO: Replace with database)
corrections_db: dict = {}


@router.post("", response_model=CorrectionResponse)
async def execute_correction(correction: CorrectionAttempt):
    """
    Execute a correction action
    """
    correction_id = str(uuid.uuid4())
    
    response = CorrectionResponse(
        id=correction_id,
        event_id=correction.event_id,
        policy_id=correction.policy_id,
        system_id=correction.system_id,
        action_type=correction.action_type,
        target=correction.target,
        parameters=correction.parameters,
        dry_run=correction.dry_run,
        status=CorrectionStatus.PENDING,
        started_at=datetime.utcnow()
    )
    
    corrections_db[correction_id] = response.model_dump()
    
    # TODO: Execute the correction asynchronously
    # For now, immediately mark as successful
    corrections_db[correction_id]["status"] = CorrectionStatus.SUCCESSFUL
    corrections_db[correction_id]["completed_at"] = datetime.utcnow()
    corrections_db[correction_id]["duration_ms"] = 250
    corrections_db[correction_id]["result"] = {
        "success": True,
        "message": f"Applied {correction.action_type} to {correction.target}"
    }
    
    return CorrectionResponse(**corrections_db[correction_id])


@router.get("", response_model=List[CorrectionResponse])
async def list_corrections(
    system_id: str = Query(None),
    event_id: str = Query(None),
    status: CorrectionStatus = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    List corrections with optional filtering
    """
    results = list(corrections_db.values())
    
    # Apply filters
    if system_id:
        results = [c for c in results if c["system_id"] == system_id]
    if event_id:
        results = [c for c in results if c["event_id"] == event_id]
    if status:
        results = [c for c in results if c["status"] == status]
    
    # Sort by started_at descending
    results = sorted(results, key=lambda c: c["started_at"], reverse=True)
    
    # Apply pagination
    results = results[offset:offset + limit]
    
    return [CorrectionResponse(**c) for c in results]


@router.get("/{correction_id}", response_model=CorrectionResponse)
async def get_correction(correction_id: str):
    """
    Get a specific correction record
    """
    if correction_id not in corrections_db:
        raise HTTPException(status_code=404, detail="Correction not found")
    
    return CorrectionResponse(**corrections_db[correction_id])


@router.get("/system/{system_id}/recent")
async def get_recent_corrections(system_id: str, limit: int = Query(10, ge=1, le=100)):
    """
    Get recent corrections for a system
    """
    system_corrections = [
        c for c in corrections_db.values()
        if c["system_id"] == system_id
    ]
    
    # Sort by started_at descending and apply limit
    system_corrections = sorted(system_corrections, key=lambda c: c["started_at"], reverse=True)[:limit]
    
    return [CorrectionResponse(**c) for c in system_corrections]


@router.get("/statistics/summary")
async def correction_statistics():
    """
    Get correction execution statistics
    """
    corrections = list(corrections_db.values())
    
    if not corrections:
        return {
            "total_corrections": 0,
            "successful": 0,
            "failed": 0,
            "pending": 0,
            "success_rate": 0.0,
            "average_duration_ms": 0,
            "timestamp": datetime.utcnow()
        }
    
    successful = sum(1 for c in corrections if c["status"] == CorrectionStatus.SUCCESSFUL)
    failed = sum(1 for c in corrections if c["status"] == CorrectionStatus.FAILED)
    pending = sum(1 for c in corrections if c["status"] == CorrectionStatus.PENDING)
    
    durations = [c["duration_ms"] for c in corrections if c.get("duration_ms")]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    success_rate = (successful / len(corrections) * 100) if corrections else 0
    
    return {
        "total_corrections": len(corrections),
        "successful": successful,
        "failed": failed,
        "pending": pending,
        "success_rate": round(success_rate, 2),
        "average_duration_ms": round(avg_duration, 2),
        "timestamp": datetime.utcnow()
    }


@router.post("/{correction_id}/rollback")
async def rollback_correction(correction_id: str):
    """
    Rollback a correction
    """
    if correction_id not in corrections_db:
        raise HTTPException(status_code=404, detail="Correction not found")
    
    correction = corrections_db[correction_id]
    
    # Only allow rollback of successful corrections
    if correction["status"] != CorrectionStatus.SUCCESSFUL:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot rollback correction with status: {correction['status']}"
        )
    
    # TODO: Execute rollback logic
    
    correction["status"] = CorrectionStatus.ROLLED_BACK
    correction["updated_at"] = datetime.utcnow()
    
    return CorrectionResponse(**correction)
