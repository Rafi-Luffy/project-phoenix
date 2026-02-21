"""
Pattern Extraction Engine for Learning System

This module extracts meaningful patterns from error correction sessions
to enable learning and prediction.

Based on: Self-Refine framework (Madaan et al.)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum
import json
from collections import defaultdict, Counter

from autonomous_system.core.error_detection import (
    ErrorContext, ErrorType, ErrorSeverity
)
from autonomous_system.core.correction_strategy import (
    CorrectionResult, CorrectionStrategy
)


class PatternType(Enum):
    """Types of patterns that can be extracted"""
    ERROR_SEQUENCE = "error_sequence"      # Sequential error occurrences
    CONTEXT_PATTERN = "context_pattern"    # Common contexts for errors
    STRATEGY_PATTERN = "strategy_pattern"  # Effective strategy patterns
    TEMPORAL_PATTERN = "temporal_pattern"  # Time-based patterns
    CAUSALITY_PATTERN = "causality_pattern" # Cause-effect relationships
    RECOVERY_PATTERN = "recovery_pattern"  # Successful recovery sequences


@dataclass
class ExtractedPattern:
    """A pattern extracted from correction sessions"""
    pattern_type: PatternType
    name: str
    description: str
    occurrences: int = 0
    contexts: List[Dict[str, Any]] = field(default_factory=list)
    success_rate: float = 0.0
    confidence_score: float = 0.0
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": self.pattern_type.value,
            "name": self.name,
            "description": self.description,
            "occurrences": self.occurrences,
            "success_rate": self.success_rate,
            "confidence": self.confidence_score,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class ErrorSequence:
    """A sequence of related errors"""
    error_types: List[ErrorType]
    frequencies: List[int]
    recovery_strategies: List[CorrectionStrategy]
    success_count: int = 0
    total_count: int = 0
    
    @property
    def recovery_rate(self) -> float:
        """Recovery rate for this sequence"""
        if self.total_count == 0:
            return 0.0
        return self.success_count / self.total_count


@dataclass
class ContextPattern:
    """Common context features for errors"""
    error_type: ErrorType
    common_inputs: Dict[str, Any]
    common_states: Dict[str, Any]
    effective_strategies: List[CorrectionStrategy]
    occurrence_count: int = 0
    success_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "error_type": self.error_type.value,
            "inputs": self.common_inputs,
            "states": self.common_states,
            "strategies": [s.value for s in self.effective_strategies],
            "occurrences": self.occurrence_count,
            "success_rate": self.success_rate
        }


class PatternExtractionEngine:
    """
    Extracts patterns from correction sessions for learning.
    Analyzes sessions to identify recurring patterns and relationships.
    """
    
    def __init__(self, max_patterns: int = 500):
        """
        Initialize pattern extraction engine
        
        Args:
            max_patterns: Maximum patterns to track
        """
        self.extracted_patterns: Dict[str, ExtractedPattern] = {}
        self.error_sequences: Dict[str, ErrorSequence] = {}
        self.context_patterns: Dict[str, ContextPattern] = {}
        self.max_patterns = max_patterns
        
        self.total_sessions_analyzed = 0
        self.pattern_discovery_count = 0
    
    def extract_from_session(self, session: Dict[str, Any]) -> List[ExtractedPattern]:
        """
        Extract patterns from a correction session
        
        Args:
            session: Session data from orchestrator
            
        Returns:
            List of extracted patterns
        """
        patterns = []
        self.total_sessions_analyzed += 1
        
        # Extract error type pattern
        if "error" in session:
            error_type = session["error"].get("error_type")
            if error_type:
                pattern = self._extract_error_pattern(session, error_type)
                if pattern:
                    patterns.append(pattern)
        
        # Extract context pattern
        context_pattern = self._extract_context_pattern(session)
        if context_pattern:
            patterns.append(context_pattern)
        
        # Extract strategy effectiveness pattern
        strategy_pattern = self._extract_strategy_pattern(session)
        if strategy_pattern:
            patterns.append(strategy_pattern)
        
        # Extract temporal pattern
        temporal_pattern = self._extract_temporal_pattern(session)
        if temporal_pattern:
            patterns.append(temporal_pattern)
        
        # Extract recovery pattern
        if session.get("final_success"):
            recovery_pattern = self._extract_recovery_pattern(session)
            if recovery_pattern:
                patterns.append(recovery_pattern)
        
        return patterns
    
    def _extract_error_pattern(self, session: Dict[str, Any], 
                               error_type: str) -> Optional[ExtractedPattern]:
        """Extract error occurrence pattern"""
        pattern_id = f"error_{error_type}"
        
        if pattern_id in self.extracted_patterns:
            pattern = self.extracted_patterns[pattern_id]
            pattern.occurrences += 1
            pattern.last_seen = datetime.now()
            
            # Update success rate
            if session.get("final_success"):
                success_count = pattern.metadata.get("successes", 0) + 1
                pattern.metadata["successes"] = success_count
                pattern.success_rate = success_count / pattern.occurrences
        else:
            if len(self.extracted_patterns) < self.max_patterns:
                pattern = ExtractedPattern(
                    pattern_type=PatternType.ERROR_SEQUENCE,
                    name=f"Error: {error_type}",
                    description=f"Recurring {error_type} error pattern",
                    occurrences=1,
                    success_rate=1.0 if session.get("final_success") else 0.0,
                    metadata={
                        "error_type": error_type,
                        "successes": 1 if session.get("final_success") else 0
                    }
                )
                self.extracted_patterns[pattern_id] = pattern
                self.pattern_discovery_count += 1
                return pattern
        
        return self.extracted_patterns.get(pattern_id)
    
    def _extract_context_pattern(self, session: Dict[str, Any]) -> Optional[ExtractedPattern]:
        """Extract contextual pattern from session"""
        if "error" not in session:
            return None
        
        error_info = session["error"]
        error_type = error_info.get("error_type", "unknown")
        
        # Extract context features
        agent_id = error_info.get("agent_id")
        operation = error_info.get("operation")
        
        pattern_id = f"context_{error_type}_{operation}"
        
        if pattern_id in self.extracted_patterns:
            pattern = self.extracted_patterns[pattern_id]
            pattern.occurrences += 1
            pattern.last_seen = datetime.now()
            
            if session.get("final_success"):
                pattern.metadata["successes"] = pattern.metadata.get("successes", 0) + 1
                pattern.success_rate = pattern.metadata["successes"] / pattern.occurrences
        else:
            if len(self.extracted_patterns) < self.max_patterns:
                pattern = ExtractedPattern(
                    pattern_type=PatternType.CONTEXT_PATTERN,
                    name=f"Context: {operation}",
                    description=f"Error context pattern for {operation} operation",
                    occurrences=1,
                    success_rate=1.0 if session.get("final_success") else 0.0,
                    metadata={
                        "operation": operation,
                        "error_type": error_type,
                        "agent_id": agent_id,
                        "successes": 1 if session.get("final_success") else 0
                    }
                )
                self.extracted_patterns[pattern_id] = pattern
                self.pattern_discovery_count += 1
                return pattern
        
        return self.extracted_patterns.get(pattern_id)
    
    def _extract_strategy_pattern(self, session: Dict[str, Any]) -> Optional[ExtractedPattern]:
        """Extract strategy effectiveness pattern"""
        if not session.get("correction"):
            return None
        
        correction = session["correction"]
        strategy = correction.get("strategy")
        error_type = session.get("error", {}).get("error_type", "unknown")
        
        pattern_id = f"strategy_{strategy}_{error_type}"
        
        if pattern_id in self.extracted_patterns:
            pattern = self.extracted_patterns[pattern_id]
            pattern.occurrences += 1
            pattern.last_seen = datetime.now()
            
            if correction.get("success"):
                pattern.metadata["successes"] = pattern.metadata.get("successes", 0) + 1
                pattern.success_rate = pattern.metadata["successes"] / pattern.occurrences
                pattern.confidence_score = min(pattern.occurrences / 10.0, 1.0)
        else:
            if len(self.extracted_patterns) < self.max_patterns:
                pattern = ExtractedPattern(
                    pattern_type=PatternType.STRATEGY_PATTERN,
                    name=f"Strategy: {strategy}",
                    description=f"Effectiveness of {strategy} for {error_type}",
                    occurrences=1,
                    success_rate=1.0 if correction.get("success") else 0.0,
                    confidence_score=0.1,
                    metadata={
                        "strategy": strategy,
                        "error_type": error_type,
                        "successes": 1 if correction.get("success") else 0
                    }
                )
                self.extracted_patterns[pattern_id] = pattern
                self.pattern_discovery_count += 1
                return pattern
        
        return self.extracted_patterns.get(pattern_id)
    
    def _extract_temporal_pattern(self, session: Dict[str, Any]) -> Optional[ExtractedPattern]:
        """Extract temporal patterns"""
        timestamp = session.get("timestamp", datetime.now().isoformat())
        try:
            dt = datetime.fromisoformat(timestamp) if isinstance(timestamp, str) else timestamp
            hour = dt.hour
            day_of_week = dt.weekday()
        except:
            return None
        
        pattern_id = f"temporal_{hour}_{day_of_week}"
        
        if pattern_id in self.extracted_patterns:
            pattern = self.extracted_patterns[pattern_id]
            pattern.occurrences += 1
        else:
            if len(self.extracted_patterns) < self.max_patterns:
                pattern = ExtractedPattern(
                    pattern_type=PatternType.TEMPORAL_PATTERN,
                    name=f"Temporal: {hour}h Day{day_of_week}",
                    description=f"Pattern at hour {hour}, day {day_of_week}",
                    occurrences=1,
                    metadata={"hour": hour, "day_of_week": day_of_week}
                )
                self.extracted_patterns[pattern_id] = pattern
                self.pattern_discovery_count += 1
                return pattern
        
        return self.extracted_patterns.get(pattern_id)
    
    def _extract_recovery_pattern(self, session: Dict[str, Any]) -> Optional[ExtractedPattern]:
        """Extract successful recovery patterns"""
        if not session.get("final_success"):
            return None
        
        error_type = session.get("error", {}).get("error_type", "unknown")
        strategy = session.get("correction", {}).get("strategy", "unknown")
        
        pattern_id = f"recovery_{error_type}_{strategy}"
        
        if pattern_id in self.extracted_patterns:
            pattern = self.extracted_patterns[pattern_id]
            pattern.occurrences += 1
            pattern.success_rate = 1.0
        else:
            if len(self.extracted_patterns) < self.max_patterns:
                pattern = ExtractedPattern(
                    pattern_type=PatternType.RECOVERY_PATTERN,
                    name=f"Recovery: {strategy} for {error_type}",
                    description=f"Successful recovery using {strategy}",
                    occurrences=1,
                    success_rate=1.0,
                    confidence_score=0.1,
                    metadata={
                        "error_type": error_type,
                        "strategy": strategy
                    }
                )
                self.extracted_patterns[pattern_id] = pattern
                self.pattern_discovery_count += 1
                return pattern
        
        return self.extracted_patterns.get(pattern_id)
    
    def get_most_frequent_patterns(self, limit: int = 20) -> List[ExtractedPattern]:
        """Get most frequent patterns"""
        sorted_patterns = sorted(
            self.extracted_patterns.values(),
            key=lambda p: p.occurrences,
            reverse=True
        )
        return sorted_patterns[:limit]
    
    def get_highest_confidence_patterns(self, limit: int = 20) -> List[ExtractedPattern]:
        """Get patterns with highest confidence"""
        sorted_patterns = sorted(
            self.extracted_patterns.values(),
            key=lambda p: (p.confidence_score, p.occurrences),
            reverse=True
        )
        return sorted_patterns[:limit]
    
    def get_patterns_by_type(self, pattern_type: PatternType) -> List[ExtractedPattern]:
        """Get patterns of a specific type"""
        return [
            p for p in self.extracted_patterns.values()
            if p.pattern_type == pattern_type
        ]
    
    def get_best_strategies_for_error(self, error_type: str) -> List[Tuple[CorrectionStrategy, float]]:
        """Get best strategies for an error type with success rates"""
        strategy_success = defaultdict(lambda: {"successes": 0, "total": 0})
        
        pattern_prefix = f"strategy_"
        for pattern_id, pattern in self.extracted_patterns.items():
            if pattern_id.startswith(pattern_prefix) and error_type in pattern_id:
                strategy = pattern.metadata.get("strategy")
                if strategy:
                    strategy_success[strategy]["total"] += pattern.occurrences
                    strategy_success[strategy]["successes"] += int(
                        pattern.metadata.get("successes", 0)
                    )
        
        # Calculate success rates
        results = []
        for strategy, counts in strategy_success.items():
            if counts["total"] > 0:
                success_rate = counts["successes"] / counts["total"]
                try:
                    results.append((CorrectionStrategy(strategy), success_rate))
                except ValueError:
                    pass
        
        # Sort by success rate
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pattern extraction statistics"""
        pattern_type_counts = defaultdict(int)
        for pattern in self.extracted_patterns.values():
            pattern_type_counts[pattern.pattern_type.value] += 1
        
        return {
            "total_sessions_analyzed": self.total_sessions_analyzed,
            "total_patterns_discovered": self.pattern_discovery_count,
            "active_patterns": len(self.extracted_patterns),
            "patterns_by_type": dict(pattern_type_counts),
            "patterns_at_capacity": len(self.extracted_patterns) >= self.max_patterns
        }
