"""Experience store for learning from past remediations."""

from typing import List, Optional
from uuid import UUID

from phoenix.core.logging import get_logger
from phoenix.core.models import ExperienceRecord, FailureType, BugType, RemediationAttempt
from phoenix.db import get_db
from phoenix.db.models import ExperienceRecordDB

logger = get_logger(__name__)


class ExperienceStore:
    """Store and retrieve learned patterns from remediation history."""
    
    def __init__(self):
        """Initialize experience store."""
        self.logger = get_logger(__name__)
    
    def record_experience(
        self,
        remediation_attempt: RemediationAttempt,
        failure_signature: str,
        patch_pattern: str,
    ) -> ExperienceRecord:
        """
        Record a successful remediation as experience.
        
        Args:
            remediation_attempt: The successful remediation
            failure_signature: Normalized failure signature
            patch_pattern: The successful patch pattern
            
        Returns:
            ExperienceRecord
        """
        with get_db() as db:
            # Check if similar experience exists
            existing = (
                db.query(ExperienceRecordDB)
                .filter(ExperienceRecordDB.failure_signature == failure_signature)
                .first()
            )
            
            if existing:
                # Update existing record
                existing.times_encountered = existing.times_encountered + 1  # type: ignore
                if remediation_attempt.is_successful:
                    existing.times_successful = existing.times_successful + 1  # type: ignore
                
                # Update averages
                existing.avg_attempts = (  # type: ignore
                    (existing.avg_attempts * (existing.times_encountered - 1) 
                     + remediation_attempt.attempts_count)
                    / existing.times_encountered
                )
                existing.avg_time_seconds = (  # type: ignore
                    (existing.avg_time_seconds * (existing.times_encountered - 1)
                     + remediation_attempt.total_time_seconds)
                    / existing.times_encountered
                )
                
                db.commit()
                db.refresh(existing)
                
                self.logger.info(
                    "experience_updated",
                    signature=failure_signature,
                    times_encountered=existing.times_encountered,
                )
                
                return self._db_to_model(existing)
            
            else:
                # Create new record
                record = ExperienceRecordDB(
                    failure_signature=failure_signature,
                    failure_type="unknown",  # Extract from attempt
                    bug_type="unknown",
                    error_pattern=failure_signature,
                    successful_patch_pattern=patch_pattern,
                    remediation_strategy="",
                    times_encountered=1,
                    times_successful=1 if remediation_attempt.is_successful else 0,
                    avg_attempts=float(remediation_attempt.attempts_count),
                    avg_time_seconds=remediation_attempt.total_time_seconds,
                )
                
                db.add(record)
                db.commit()
                db.refresh(record)
                
                self.logger.info(
                    "experience_recorded",
                    signature=failure_signature,
                )
                
                return self._db_to_model(record)
    
    def find_similar_experiences(
        self,
        failure_signature: str,
        limit: int = 5,
    ) -> List[ExperienceRecord]:
        """
        Find similar past experiences.
        
        Args:
            failure_signature: The failure to match
            limit: Maximum number of results
            
        Returns:
            List of similar ExperienceRecords
        """
        with get_db() as db:
            # Simple text matching for v1
            # TODO: Implement vector similarity search
            records = (
                db.query(ExperienceRecordDB)
                .filter(ExperienceRecordDB.failure_signature.contains(failure_signature[:50]))
                .order_by(ExperienceRecordDB.times_successful.desc())
                .limit(limit)
                .all()
            )
            
            self.logger.info(
                "similar_experiences_found",
                count=len(records),
                signature=failure_signature[:50],
            )
            
            return [self._db_to_model(r) for r in records]
    
    def get_best_strategies(
        self,
        bug_type: BugType,
        limit: int = 3,
    ) -> List[str]:
        """
        Get best remediation strategies for a bug type.
        
        Args:
            bug_type: The type of bug
            limit: Maximum number of strategies
            
        Returns:
            List of remediation strategies
        """
        with get_db() as db:
            records = (
                db.query(ExperienceRecordDB)
                .filter(ExperienceRecordDB.bug_type == bug_type.value)
                .filter(ExperienceRecordDB.times_successful > 0)
                .order_by(
                    (ExperienceRecordDB.times_successful / ExperienceRecordDB.times_encountered).desc()
                )
                .limit(limit)
                .all()
            )
            
            return [str(r.remediation_strategy) for r in records if r.remediation_strategy is not None]  # type: ignore
    
    def _db_to_model(self, db_record: ExperienceRecordDB) -> ExperienceRecord:
        """Convert database model to Pydantic model."""
        return ExperienceRecord(
            id=UUID(str(db_record.id)),  # type: ignore
            failure_signature=str(db_record.failure_signature),
            failure_type=FailureType(str(db_record.failure_type)),  # type: ignore
            bug_type=BugType(str(db_record.bug_type)),  # type: ignore
            error_pattern=str(db_record.error_pattern),
            file_patterns=list(db_record.file_patterns) if db_record.file_patterns else [],  # type: ignore
            test_patterns=list(db_record.test_patterns) if db_record.test_patterns else [],  # type: ignore
            successful_patch_pattern=str(db_record.successful_patch_pattern),
            remediation_strategy=str(db_record.remediation_strategy),
            times_encountered=int(db_record.times_encountered),  # type: ignore
            times_successful=int(db_record.times_successful),  # type: ignore
            avg_attempts=float(db_record.avg_attempts),  # type: ignore
            avg_time_seconds=float(db_record.avg_time_seconds),  # type: ignore
            failure_embedding=list(db_record.failure_embedding) if db_record.failure_embedding else None,  # type: ignore
            patch_embedding=list(db_record.patch_embedding) if db_record.patch_embedding else None,  # type: ignore
            created_at=db_record.created_at,  # type: ignore
            updated_at=db_record.updated_at,  # type: ignore
        )
