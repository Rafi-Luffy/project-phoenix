"""
Event detection and management endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from datetime import datetime
from models import EventDetected, EventResponse, EventType, EventSeverity
import uuid

router = APIRouter()

# In-memory storage for demo (TODO: Replace with database)
events_db: dict = {}


@router.post("", response_model=EventResponse)
async def create_event(event: EventDetected):
    """
    Record a detected event
    """
    event_id = str(uuid.uuid4())
    
    response = EventResponse(
        id=event_id,
        system_id=event.system_id,
        event_type=event.event_type,
        severity=event.severity,
        title=event.title,
        description=event.description,
        metrics=event.metrics,
        context=event.context,
        tags=event.tags,
        detected_at=datetime.utcnow(),
        created_at=datetime.utcnow()
    )
    
    events_db[event_id] = response.model_dump()
    
    return response


@router.get("", response_model=List[EventResponse])
async def list_events(
    system_id: str = Query(None),
    event_type: EventType = Query(None),
    severity: EventSeverity = Query(None),
    tag: str = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    List events with optional filtering
    """
    results = list(events_db.values())
    
    # Apply filters
    if system_id:
        results = [e for e in results if e["system_id"] == system_id]
    if event_type:
        results = [e for e in results if e["event_type"] == event_type]
    if severity:
        results = [e for e in results if e["severity"] == severity]
    if tag:
        results = [e for e in results if tag in e.get("tags", [])]
    
    # Sort by detected_at descending
    results = sorted(results, key=lambda e: e["detected_at"], reverse=True)
    
    # Apply pagination
    results = results[offset:offset + limit]
    
    return [EventResponse(**e) for e in results]


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str):
    """
    Get a specific event
    """
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return EventResponse(**events_db[event_id])


@router.get("/system/{system_id}/recent")
async def get_recent_events(system_id: str, hours: int = Query(24, ge=1, le=720)):
    """
    Get recent events for a system
    """
    # Filter events for this system
    system_events = [
        e for e in events_db.values() 
        if e["system_id"] == system_id
    ]
    
    if not system_events:
        return []
    
    # Sort by detected_at descending and return top 10
    system_events = sorted(system_events, key=lambda e: e["detected_at"], reverse=True)[:10]
    
    return [EventResponse(**e) for e in system_events]


@router.get("/statistics/summary")
async def event_statistics():
    """
    Get event statistics and summary
    """
    events = list(events_db.values())
    
    if not events:
        return {
            "total_events": 0,
            "by_severity": {},
            "by_type": {},
            "critical_events": 0,
            "timestamp": datetime.utcnow()
        }
    
    # Count by severity
    by_severity = {}
    by_type = {}
    
    for event in events:
        severity = event.get("severity", "unknown")
        event_type = event.get("event_type", "unknown")
        
        by_severity[severity] = by_severity.get(severity, 0) + 1
        by_type[event_type] = by_type.get(event_type, 0) + 1
    
    critical_count = by_severity.get("critical", 0)
    
    return {
        "total_events": len(events),
        "by_severity": by_severity,
        "by_type": by_type,
        "critical_events": critical_count,
        "timestamp": datetime.utcnow()
    }


@router.delete("/{event_id}")
async def delete_event(event_id: str):
    """
    Delete an event
    """
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail="Event not found")
    
    del events_db[event_id]
    
    return {"message": f"Event {event_id} deleted", "id": event_id}
