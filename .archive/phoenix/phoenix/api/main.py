"""FastAPI application for Phoenix."""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from pathlib import Path

from phoenix.core.config import get_config, ensure_directories
from phoenix.core.logging import setup_logging, get_logger
from phoenix.core.models import Project, FailureEvent, RemediationAttempt, RemediationStatus
from phoenix.db import get_db, init_db
from phoenix.db.models import ProjectDB, FailureEventDB, RemediationAttemptDB
from phoenix.observer.test_runner import TestRunner
from phoenix.observer.failure_detector import FailureDetector
from phoenix.orchestrator.orchestrator import Orchestrator

# Setup
setup_logging()
ensure_directories()
logger = get_logger(__name__)
config = get_config()

# Create FastAPI app
app = FastAPI(
    title="Phoenix",
    description="Self-Healing Agentic AI Framework and Runtime",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class CreateProjectRequest(BaseModel):
    name: str
    local_path: str
    description: Optional[str] = None
    repository_url: Optional[str] = None
    branch: str = "main"
    language: str = "python"
    test_command: str = "pytest"
    auto_remediation_enabled: bool = True
    max_attempts: int = 5


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    local_path: str
    is_healthy: bool
    total_failures: int
    total_remediations: int
    success_rate: float
    last_run_at: Optional[str]
    
    class Config:
        from_attributes = True


class RunRemediationRequest(BaseModel):
    failure_event_id: Optional[UUID] = None
    max_attempts: Optional[int] = None


class RemediationStatusResponse(BaseModel):
    id: UUID
    status: str
    attempts_count: int
    is_successful: bool
    total_time_seconds: float
    failure_reason: Optional[str]
    
    class Config:
        from_attributes = True


# Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("starting_phoenix_api")
    init_db()
    logger.info("database_initialized")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Phoenix",
        "version": "0.1.0",
        "description": "Self-Healing Agentic AI Framework and Runtime",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/projects", response_model=ProjectResponse)
async def create_project(
    request: CreateProjectRequest,
    db: Session = Depends(get_db),
):
    """Register a new project with Phoenix."""
    # Validate path exists
    project_path = Path(request.local_path)
    if not project_path.exists():
        raise HTTPException(status_code=400, detail="Project path does not exist")
    
    # Create project
    project_db = ProjectDB(
        name=request.name,
        description=request.description,
        repository_url=request.repository_url,
        local_path=request.local_path,
        branch=request.branch,
        language=request.language,
        test_command=request.test_command,
        auto_remediation_enabled=request.auto_remediation_enabled,
        max_attempts=request.max_attempts,
    )
    
    db.add(project_db)
    db.commit()
    db.refresh(project_db)
    
    logger.info("project_created", project_id=str(project_db.id), name=request.name)
    
    return project_db


@app.get("/projects", response_model=List[ProjectResponse])
async def list_projects(db: Session = Depends(get_db)):
    """List all registered projects."""
    projects = db.query(ProjectDB).all()
    return projects


@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: UUID, db: Session = Depends(get_db)):
    """Get a specific project."""
    project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.post("/projects/{project_id}/run")
async def run_phoenix(
    project_id: UUID,
    request: RunRemediationRequest = RunRemediationRequest(),
    db: Session = Depends(get_db),
):
    """Trigger Phoenix remediation for a project."""
    # Get project
    project_db = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
    if not project_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_path = Path(str(project_db.local_path))  # type: ignore
    
    logger.info("running_phoenix", project_id=str(project_id))
    
    # Run tests to detect failures
    test_runner = TestRunner(project_path, str(project_db.test_command))  # type: ignore
    test_results = test_runner.run_tests()
    
    # Detect failures
    failure_detector = FailureDetector(project_id, project_path)
    failures = failure_detector.detect_failures(test_results)
    
    if not failures:
        return {
            "message": "No failures detected",
            "tests_run": test_results.total_tests,
            "tests_passed": test_results.passed,
        }
    
    # Save failures to DB
    for failure in failures:
        failure_db = FailureEventDB(
            id=failure.id,
            project_id=project_id,
            failure_type=failure.failure_type.value,
            severity=failure.severity,
            test_name=failure.test_name,
            test_file=failure.test_file,
            error_message=failure.error_message,
            stack_trace=failure.stack_trace,
            error_type=failure.error_type,
            files_implicated=failure.files_implicated,
            lines_implicated=failure.lines_implicated,
        )
        db.add(failure_db)
    
    db.commit()
    
    # Run remediation if auto-remediation enabled
    remediation_results = []
    
    if bool(project_db.auto_remediation_enabled):  # type: ignore
        orchestrator = Orchestrator(
            project_id=project_id,
            project_path=project_path,
            test_command=str(project_db.test_command),  # type: ignore
        )
        
        for failure in failures:
            attempt = orchestrator.remediate(
                failure,
                max_attempts=request.max_attempts or int(project_db.max_attempts),  # type: ignore
            )
            
            # Save to DB
            attempt_db = RemediationAttemptDB(
                id=attempt.id,
                failure_event_id=attempt.failure_event_id,
                project_id=project_id,
                status=attempt.status.value,
                attempts_count=attempt.attempts_count,
                total_time_seconds=attempt.total_time_seconds,
                is_successful=attempt.is_successful,
                failure_reason=attempt.failure_reason,
                completed_at=attempt.completed_at,
            )
            db.add(attempt_db)
            
            remediation_results.append({
                "failure_id": str(failure.id),
                "attempt_id": str(attempt.id),
                "status": attempt.status.value,
                "is_successful": attempt.is_successful,
            })
        
        db.commit()
    
    return {
        "failures_detected": len(failures),
        "remediations_attempted": len(remediation_results),
        "results": remediation_results,
    }


@app.get("/remediations/{attempt_id}", response_model=RemediationStatusResponse)
async def get_remediation(attempt_id: UUID, db: Session = Depends(get_db)):
    """Get status of a remediation attempt."""
    attempt = db.query(RemediationAttemptDB).filter(
        RemediationAttemptDB.id == attempt_id
    ).first()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Remediation attempt not found")
    
    return attempt


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "phoenix.api.main:app",
        host=config.api_host,
        port=config.api_port,
        reload=True,
    )
