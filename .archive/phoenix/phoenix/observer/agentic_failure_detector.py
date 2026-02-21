"""
Agentic AI Failure Detector

Detects failures in AI agent systems automatically. I built this because debugging
agentic AI failures manually was driving me crazy - context overflows, agent deadlocks,
hallucinations... the list goes on.

This detector knows about 30+ different failure patterns that happen in production
when you're running autonomous agents. It catches everything from LLM rate limits
to multi-agent coordination issues to RAG pipeline failures.

The goal: detect failures so we can fix them automatically. No more 3am debugging sessions.
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from pathlib import Path

from phoenix.core.logging import get_logger

logger = get_logger(__name__)


class AgenticFailureType(str, Enum):
    """
    Failure types I've seen happen in production agentic AI systems.
    
    Categorized by what part of the system fails - LLM interactions,
    agent coordination, tool calls, memory, RAG, workflows, etc.
    """
    
    # LLM-Specific Failures (API and model issues)
    HALLUCINATION = "hallucination"  # LLM makes stuff up
    CONTEXT_OVERFLOW = "context_overflow"  # Conversation too long for context window
    RATE_LIMIT = "rate_limit"  # Hit API rate limits
    TOKEN_LIMIT = "token_limit"  # Response exceeded max tokens
    PROMPT_INJECTION = "prompt_injection"  # Security issue - user manipulating prompts
    
    # Agent Coordination Failures (multi-agent systems)
    AGENT_DEADLOCK = "agent_deadlock"  # Circular wait - A waits for B waits for C waits for A
    AGENT_RACE_CONDITION = "agent_race_condition"  # Multiple agents accessing same resource
    AGENT_STATE_DESYNC = "agent_state_desync"  # Agent states got out of sync
    AGENT_COMMUNICATION_FAILURE = "agent_communication_failure"  # Can't talk to other agents
    AGENT_TIMEOUT = "agent_timeout"  # Agent hung and didn't respond
    
    # Tool/Function Calling Failures (when agents use tools)
    TOOL_NOT_FOUND = "tool_not_found"  # Agent tried to call a tool that doesn't exist
    TOOL_SCHEMA_MISMATCH = "tool_schema_mismatch"  # Wrong parameters passed to tool
    TOOL_EXECUTION_FAILURE = "tool_execution_failure"  # Tool code crashed
    TOOL_PERMISSION_DENIED = "tool_permission_denied"  # Agent doesn't have access
    TOOL_TIMEOUT = "tool_timeout"  # Tool took too long to respond
    
    # Memory/Context Failures
    MEMORY_CORRUPTION = "memory_corruption"  # Agent memory corrupted
    MEMORY_LEAK = "memory_leak"  # Memory not being released
    CONTEXT_LOSS = "context_loss"  # Lost conversation context
    STATE_PERSISTENCE_FAILURE = "state_persistence_failure"  # Can't save state
    
    # RAG/Vector Database Failures
    EMBEDDING_FAILURE = "embedding_failure"  # Can't generate embeddings
    VECTOR_SEARCH_FAILURE = "vector_search_failure"  # Search crashed
    INDEX_CORRUPTION = "index_corruption"  # Vector index corrupted
    RETRIEVAL_TIMEOUT = "retrieval_timeout"  # Retrieval too slow
    RELEVANCE_DEGRADATION = "relevance_degradation"  # Retrieved docs not relevant
    
    # Workflow/Orchestration Failures
    WORKFLOW_STUCK = "workflow_stuck"  # Workflow not progressing
    WORKFLOW_CYCLE = "workflow_cycle"  # Infinite loop detected
    WORKFLOW_BRANCH_ERROR = "workflow_branch_error"  # Wrong branch taken
    CALLBACK_FAILURE = "callback_failure"  # Callback didn't execute
    EVENT_LOSS = "event_loss"  # Event not received
    
    # Multi-Modal Failures
    IMAGE_PROCESSING_FAILURE = "image_processing_failure"  # Vision model failed
    AUDIO_TRANSCRIPTION_FAILURE = "audio_transcription_failure"  # Speech-to-text failed
    MODALITY_MISMATCH = "modality_mismatch"  # Wrong input type
    
    # Network/API Failures
    API_UNAVAILABLE = "api_unavailable"  # External API down
    NETWORK_PARTITION = "network_partition"  # Network split
    WEBHOOK_FAILURE = "webhook_failure"  # Webhook not delivered
    AUTH_FAILURE = "auth_failure"  # Authentication failed
    
    # Data/Schema Failures
    SCHEMA_VALIDATION_FAILURE = "schema_validation_failure"  # Invalid data structure
    DATA_CORRUPTION = "data_corruption"  # Data got corrupted
    VERSION_MISMATCH = "version_mismatch"  # Incompatible versions
    
    # Resource Failures
    RESOURCE_EXHAUSTION = "resource_exhaustion"  # Out of memory/CPU
    QUOTA_EXCEEDED = "quota_exceeded"  # Cloud quota hit
    COST_LIMIT_REACHED = "cost_limit_reached"  # Budget exceeded


@dataclass
class FailureContext:
    """Complete context of an agentic AI failure."""
    
    # Identification
    failure_id: str
    failure_type: AgenticFailureType
    timestamp: datetime
    
    # System Context
    agent_name: str
    agent_type: str  # "langchain", "autogen", "crewai", etc.
    language: str
    framework: str
    
    # Failure Details
    error_message: str
    stack_trace: str
    error_location: Dict[str, Any]  # file, line, function
    
    # Agentic Context
    conversation_history: List[Dict[str, str]]
    agent_state: Dict[str, Any]
    tools_available: List[str]
    tools_attempted: List[str]
    llm_calls: List[Dict[str, Any]]  # All LLM interactions
    
    # Environmental Context
    environment_vars: Dict[str, str]
    resource_usage: Dict[str, float]  # CPU, memory, etc.
    network_state: Dict[str, Any]
    
    # Related Context
    related_agents: List[str]  # Other agents involved
    upstream_events: List[Dict[str, Any]]
    downstream_effects: List[str]
    
    # Metadata
    severity: str  # "critical", "high", "medium", "low"
    impact_scope: str  # "single_agent", "multi_agent", "system_wide"
    auto_fixable: bool
    similar_failures: List[str]  # IDs of similar past failures
    
    # Additional context
    custom_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FailureReport:
    """Comprehensive failure report for logging and analysis."""
    
    context: FailureContext
    
    # Analysis
    root_cause: str
    contributing_factors: List[str]
    failure_pattern: str
    confidence: float  # 0-1
    
    # Fix Strategy
    proposed_fix: str
    fix_complexity: str  # "simple", "moderate", "complex"
    fix_risk: str  # "low", "medium", "high"
    estimated_fix_time: int  # seconds
    
    # Validation Plan
    validation_tests: List[str]
    rollback_plan: str
    
    # Reporting
    human_readable_summary: str
    technical_details: Dict[str, Any]
    
    # Timestamp
    generated_at: datetime = field(default_factory=datetime.utcnow)


class AgenticFailureDetector:
    """
    Advanced failure detector for agentic AI systems.
    
    Detects complex failures that only happen in autonomous agent systems:
    - LLM hallucinations and context issues
    - Multi-agent coordination problems
    - Tool calling failures
    - Memory and state issues
    - RAG/vector database problems
    - Workflow orchestration failures
    
    100% AUTONOMOUS - NO HUMAN REQUIRED.
    """
    
    # Pattern signatures for complex failures
    FAILURE_PATTERNS = {
        AgenticFailureType.HALLUCINATION: [
            r"generated.*(?:false|incorrect|invalid).*(?:information|data)",
            r"hallucination.*detected",
            r"fact.*check.*failed",
            r"source.*not.*found",
        ],
        AgenticFailureType.CONTEXT_OVERFLOW: [
            r"context.*(?:length|window|size).*exceeded",
            r"token.*limit.*(?:reached|exceeded)",
            r"maximum.*context.*length",
            r"InvalidRequestError.*context_length_exceeded",
        ],
        AgenticFailureType.AGENT_DEADLOCK: [
            r"agents?.*(?:waiting|blocked|stuck).*on.*each.*other",
            r"circular.*dependency.*detected",
            r"deadlock.*between.*agents",
            r"mutual.*wait.*detected",
        ],
        AgenticFailureType.AGENT_RACE_CONDITION: [
            r"race.*condition.*detected",
            r"concurrent.*(?:modification|access).*conflict",
            r"agents?.*interfering.*with.*each.*other",
            r"state.*modified.*by.*multiple.*agents",
        ],
        AgenticFailureType.TOOL_NOT_FOUND: [
            r"tool.*['\"]([^'\"]+)['\"].*not.*found",
            r"function.*['\"]([^'\"]+)['\"].*(?:does not exist|unavailable)",
            r"no.*tool.*named.*['\"]([^'\"]+)['\"]",
            r"unknown.*(?:tool|function).*['\"]([^'\"]+)['\"]",
        ],
        AgenticFailureType.TOOL_SCHEMA_MISMATCH: [
            r"tool.*(?:parameter|argument).*(?:missing|invalid|incorrect)",
            r"schema.*validation.*failed.*for.*tool",
            r"(?:expected|required).*(?:parameter|argument).*not.*provided",
            r"type.*mismatch.*in.*tool.*call",
        ],
        AgenticFailureType.MEMORY_CORRUPTION: [
            r"agent.*memory.*corrupted",
            r"state.*(?:inconsistent|invalid|corrupted)",
            r"memory.*integrity.*check.*failed",
            r"conversation.*history.*corrupted",
        ],
        AgenticFailureType.CONTEXT_LOSS: [
            r"(?:lost|missing).*(?:context|conversation).*(?:history|state)",
            r"unable.*to.*(?:retrieve|restore).*(?:context|history)",
            r"conversation.*context.*unavailable",
            r"session.*(?:expired|lost|terminated)",
        ],
        AgenticFailureType.EMBEDDING_FAILURE: [
            r"(?:embedding|encode).*(?:failed|error)",
            r"unable.*to.*(?:generate|create).*embedding",
            r"embedding.*model.*(?:unavailable|crashed)",
            r"vector.*encoding.*failed",
        ],
        AgenticFailureType.VECTOR_SEARCH_FAILURE: [
            r"vector.*(?:search|query).*failed",
            r"similarity.*search.*error",
            r"(?:pinecone|weaviate|milvus|qdrant|chroma).*(?:error|failed)",
            r"unable.*to.*query.*vector.*(?:database|store|index)",
        ],
        AgenticFailureType.WORKFLOW_STUCK: [
            r"workflow.*(?:stuck|not.*progressing|stalled)",
            r"no.*progress.*in.*(?:workflow|pipeline)",
            r"step.*(?:waiting|blocked).*indefinitely",
            r"workflow.*timeout.*waiting.*for",
        ],
        AgenticFailureType.WORKFLOW_CYCLE: [
            r"(?:infinite|circular).*(?:loop|cycle).*detected",
            r"workflow.*repeating.*(?:indefinitely|endlessly)",
            r"circular.*dependency.*in.*workflow",
            r"max.*(?:iterations|loops).*exceeded",
        ],
        AgenticFailureType.RATE_LIMIT: [
            r"rate.*limit.*(?:exceeded|reached|hit)",
            r"too.*many.*requests",
            r"429.*(?:too.*many.*requests)",
            r"quota.*exceeded.*for.*API",
        ],
        AgenticFailureType.API_UNAVAILABLE: [
            r"(?:API|service|endpoint).*(?:unavailable|down|unreachable)",
            r"(?:connection|request).*(?:failed|timeout|refused)",
            r"503.*service.*unavailable",
            r"504.*gateway.*timeout",
        ],
    }
    
    def __init__(self):
        """Initialize the advanced failure detector."""
        self.logger = get_logger(__name__)
        self.detected_failures: List[FailureContext] = []
        self.failure_count: Dict[AgenticFailureType, int] = {}
    
    def detect_from_logs(
        self,
        log_output: str,
        agent_context: Dict[str, Any],
    ) -> List[FailureContext]:
        """
        Detect complex agentic failures from logs.
        
        Args:
            log_output: Log output from agent execution
            agent_context: Context about the agent system
            
        Returns:
            List of detected failure contexts
        """
        failures = []
        
        # Check each failure pattern
        for failure_type, patterns in self.FAILURE_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, log_output, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    failure = self._create_failure_context(
                        failure_type=failure_type,
                        error_match=match,
                        log_output=log_output,
                        agent_context=agent_context,
                    )
                    failures.append(failure)
                    
                    self.logger.warning(
                        "agentic_failure_detected",
                        failure_type=failure_type.value,
                        agent=agent_context.get("agent_name"),
                        auto_fixable=failure.auto_fixable,
                    )
        
        # Detect composite failures (multiple issues)
        composite_failures = self._detect_composite_failures(log_output, agent_context)
        failures.extend(composite_failures)
        
        # Store detections
        self.detected_failures.extend(failures)
        for failure in failures:
            self.failure_count[failure.failure_type] = \
                self.failure_count.get(failure.failure_type, 0) + 1
        
        return failures
    
    def _create_failure_context(
        self,
        failure_type: AgenticFailureType,
        error_match: re.Match,
        log_output: str,
        agent_context: Dict[str, Any],
    ) -> FailureContext:
        """Create detailed failure context."""
        
        # Extract error details from match
        error_message = error_match.group(0)
        error_start = max(0, error_match.start() - 200)
        error_end = min(len(log_output), error_match.end() + 200)
        context_snippet = log_output[error_start:error_end]
        
        # Extract stack trace if present
        stack_trace = self._extract_stack_trace(log_output, error_match.start())
        
        # Determine severity and auto-fixability
        severity, auto_fixable = self._assess_failure(failure_type, error_message)
        
        # Find similar past failures
        similar_failures = self._find_similar_failures(failure_type, error_message)
        
        return FailureContext(
            failure_id=f"{failure_type.value}_{datetime.utcnow().timestamp()}",
            failure_type=failure_type,
            timestamp=datetime.utcnow(),
            agent_name=agent_context.get("agent_name", "unknown"),
            agent_type=agent_context.get("agent_type", "unknown"),
            language=agent_context.get("language", "python"),
            framework=agent_context.get("framework", "unknown"),
            error_message=error_message,
            stack_trace=stack_trace,
            error_location=self._extract_error_location(stack_trace),
            conversation_history=agent_context.get("conversation_history", []),
            agent_state=agent_context.get("agent_state", {}),
            tools_available=agent_context.get("tools_available", []),
            tools_attempted=self._extract_tool_calls(context_snippet),
            llm_calls=agent_context.get("llm_calls", []),
            environment_vars=agent_context.get("environment_vars", {}),
            resource_usage=agent_context.get("resource_usage", {}),
            network_state=agent_context.get("network_state", {}),
            related_agents=agent_context.get("related_agents", []),
            upstream_events=agent_context.get("upstream_events", []),
            downstream_effects=self._predict_downstream_effects(failure_type),
            severity=severity,
            impact_scope=self._determine_impact_scope(failure_type, agent_context),
            auto_fixable=auto_fixable,
            similar_failures=similar_failures,
            custom_context={"context_snippet": context_snippet},
        )
    
    def _detect_composite_failures(
        self,
        log_output: str,
        agent_context: Dict[str, Any],
    ) -> List[FailureContext]:
        """
        Detect complex composite failures (multiple simultaneous issues).
        
        Examples:
        - Rate limit + retry exhaustion
        - Context overflow + memory corruption
        - Agent deadlock + timeout
        """
        composite_failures = []
        
        # Composite Pattern 1: Rate Limit Death Spiral
        if (re.search(r"rate.*limit", log_output, re.IGNORECASE) and
            re.search(r"retry.*(?:exhausted|failed)", log_output, re.IGNORECASE)):
            
            composite_failures.append(self._create_composite_failure(
                "rate_limit_death_spiral",
                "Rate limiting triggered retry exhaustion",
                log_output,
                agent_context,
            ))
        
        # Composite Pattern 2: Memory Leak + Context Overflow
        if (re.search(r"memory.*(?:leak|exhausted)", log_output, re.IGNORECASE) and
            re.search(r"context.*(?:overflow|exceeded)", log_output, re.IGNORECASE)):
            
            composite_failures.append(self._create_composite_failure(
                "memory_context_cascade",
                "Memory leak caused context overflow",
                log_output,
                agent_context,
            ))
        
        # Composite Pattern 3: Multi-Agent Deadlock + Timeout
        if (re.search(r"deadlock", log_output, re.IGNORECASE) and
            re.search(r"timeout", log_output, re.IGNORECASE) and
            len(agent_context.get("related_agents", [])) > 1):
            
            composite_failures.append(self._create_composite_failure(
                "multi_agent_deadlock_timeout",
                "Agent deadlock caused system timeout",
                log_output,
                agent_context,
            ))
        
        return composite_failures
    
    def _create_composite_failure(
        self,
        pattern_name: str,
        description: str,
        log_output: str,
        agent_context: Dict[str, Any],
    ) -> FailureContext:
        """Create a composite failure context."""
        return FailureContext(
            failure_id=f"composite_{pattern_name}_{datetime.utcnow().timestamp()}",
            failure_type=AgenticFailureType.AGENT_STATE_DESYNC,  # Generic
            timestamp=datetime.utcnow(),
            agent_name=agent_context.get("agent_name", "unknown"),
            agent_type=agent_context.get("agent_type", "unknown"),
            language=agent_context.get("language", "python"),
            framework=agent_context.get("framework", "unknown"),
            error_message=f"COMPOSITE FAILURE: {description}",
            stack_trace=self._extract_stack_trace(log_output, 0),
            error_location={},
            conversation_history=agent_context.get("conversation_history", []),
            agent_state=agent_context.get("agent_state", {}),
            tools_available=agent_context.get("tools_available", []),
            tools_attempted=[],
            llm_calls=agent_context.get("llm_calls", []),
            environment_vars=agent_context.get("environment_vars", {}),
            resource_usage=agent_context.get("resource_usage", {}),
            network_state=agent_context.get("network_state", {}),
            related_agents=agent_context.get("related_agents", []),
            upstream_events=agent_context.get("upstream_events", []),
            downstream_effects=["cascading_failures", "system_instability"],
            severity="critical",
            impact_scope="multi_agent",
            auto_fixable=True,  # Phoenix can handle composite failures
            similar_failures=[],
            custom_context={"composite_pattern": pattern_name},
        )
    
    def _extract_stack_trace(self, log_output: str, error_pos: int) -> str:
        """Extract stack trace from log output."""
        # Look for traceback after error position
        traceback_patterns = [
            r"Traceback.*?(?=\n\n|\nERROR|\Z)",
            r"Stack trace:.*?(?=\n\n|\Z)",
            r"at .*?:\d+:\d+.*?(?=\n\n|\Z)",
        ]
        
        for pattern in traceback_patterns:
            match = re.search(pattern, log_output[error_pos:], re.DOTALL | re.MULTILINE)
            if match:
                return match.group(0)
        
        return "No stack trace available"
    
    def _extract_error_location(self, stack_trace: str) -> Dict[str, Any]:
        """Extract file, line, function from stack trace."""
        location = {"file": None, "line": None, "function": None}
        
        # Python traceback format
        py_match = re.search(r'File "([^"]+)", line (\d+), in (\w+)', stack_trace)
        if py_match:
            location["file"] = py_match.group(1)
            location["line"] = int(py_match.group(2))
            location["function"] = py_match.group(3)
            return location
        
        # JavaScript stack format
        js_match = re.search(r'at (\w+) \(([^:]+):(\d+):(\d+)\)', stack_trace)
        if js_match:
            location["function"] = js_match.group(1)
            location["file"] = js_match.group(2)
            location["line"] = int(js_match.group(3))
            return location
        
        return location
    
    def _extract_tool_calls(self, context_snippet: str) -> List[str]:
        """Extract tool/function calls from context."""
        tools = []
        
        # LangChain tool format
        lc_tools = re.findall(r'tool[:\s]+["\']([^"\']+)["\']', context_snippet, re.IGNORECASE)
        tools.extend(lc_tools)
        
        # Function call format
        func_calls = re.findall(r'calling function ["\']([^"\']+)["\']', context_snippet, re.IGNORECASE)
        tools.extend(func_calls)
        
        return list(set(tools))
    
    def _predict_downstream_effects(self, failure_type: AgenticFailureType) -> List[str]:
        """Predict cascading effects of this failure."""
        effects_map = {
            AgenticFailureType.AGENT_DEADLOCK: [
                "workflow_stuck",
                "resource_leak",
                "timeout_cascade",
            ],
            AgenticFailureType.CONTEXT_OVERFLOW: [
                "conversation_restart",
                "information_loss",
                "user_experience_degradation",
            ],
            AgenticFailureType.TOOL_NOT_FOUND: [
                "task_failure",
                "agent_confusion",
                "retry_storm",
            ],
            AgenticFailureType.MEMORY_CORRUPTION: [
                "data_loss",
                "incorrect_responses",
                "security_vulnerability",
            ],
            AgenticFailureType.RATE_LIMIT: [
                "cascading_failures",
                "cost_spike",
                "service_degradation",
            ],
        }
        
        return effects_map.get(failure_type, ["unknown_effects"])
    
    def _determine_impact_scope(
        self,
        failure_type: AgenticFailureType,
        agent_context: Dict[str, Any],
    ) -> str:
        """Determine how many agents/systems are affected."""
        related_agents = agent_context.get("related_agents", [])
        
        if len(related_agents) > 5:
            return "system_wide"
        elif len(related_agents) > 0:
            return "multi_agent"
        else:
            return "single_agent"
    
    def _assess_failure(
        self,
        failure_type: AgenticFailureType,
        error_message: str,
    ) -> tuple[str, bool]:
        """Assess severity and auto-fixability."""
        
        # Critical failures
        critical_types = {
            AgenticFailureType.MEMORY_CORRUPTION,
            AgenticFailureType.DATA_CORRUPTION,
            AgenticFailureType.SECURITY_BREACH,
        }
        
        if failure_type in critical_types:
            return "critical", True  # Phoenix MUST fix critical issues
        
        # High severity
        high_severity_types = {
            AgenticFailureType.AGENT_DEADLOCK,
            AgenticFailureType.WORKFLOW_STUCK,
            AgenticFailureType.API_UNAVAILABLE,
        }
        
        if failure_type in high_severity_types:
            return "high", True
        
        # Most agentic failures are auto-fixable by Phoenix
        return "medium", True
    
    def _find_similar_failures(
        self,
        failure_type: AgenticFailureType,
        error_message: str,
    ) -> List[str]:
        """Find IDs of similar past failures for learning."""
        similar = []
        
        for past_failure in self.detected_failures:
            if past_failure.failure_type == failure_type:
                # Simple similarity: check if error messages share keywords
                msg_words = set(re.findall(r'\w+', error_message.lower()))
                past_words = set(re.findall(r'\w+', past_failure.error_message.lower()))
                
                overlap = len(msg_words & past_words)
                if overlap > 3:  # Arbitrary threshold
                    similar.append(past_failure.failure_id)
        
        return similar[:5]  # Top 5 similar
    
    def get_failure_statistics(self) -> Dict[str, Any]:
        """Get comprehensive failure statistics."""
        return {
            "total_failures_detected": len(self.detected_failures),
            "failures_by_type": {
                ft.value: count for ft, count in self.failure_count.items()
            },
            "auto_fixable_percentage": (
                sum(1 for f in self.detected_failures if f.auto_fixable) / 
                len(self.detected_failures) * 100
                if self.detected_failures else 0
            ),
            "severity_distribution": self._get_severity_distribution(),
            "most_common_failures": self._get_top_failures(5),
        }
    
    def _get_severity_distribution(self) -> Dict[str, int]:
        """Get distribution of failure severities."""
        dist = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for failure in self.detected_failures:
            dist[failure.severity] = dist.get(failure.severity, 0) + 1
        return dist
    
    def _get_top_failures(self, n: int) -> List[Dict[str, Any]]:
        """Get top N most common failure types."""
        sorted_failures = sorted(
            self.failure_count.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [
            {"type": ft.value, "count": count}
            for ft, count in sorted_failures[:n]
        ]
