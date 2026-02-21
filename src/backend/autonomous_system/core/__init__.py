"""
Core system components
"""

from autonomous_system.core.database import PostgreSQLDatabase
from autonomous_system.core.auth import AuthenticationManager, UserRole, PermissionLevel
from autonomous_system.core.monitoring import (
    EventTracker, StructuredLogger, MetricsCollector, AlertManager,
    EventType, MetricType, SeverityLevel
)
from autonomous_system.core.agent_framework import (
    BaseAgent, AgentRegistry, MessageBus, StateManager,
    AgentConfig, AgentState, Message, MessageType
)
from autonomous_system.core.memory_system import (
    MemoryManager, MemoryType, MemoryPriority, ContextWindow
)
from autonomous_system.core.orchestrator import CoreOrchestrator, get_orchestrator

# Phase 1.2: Agent Framework Expansion
from autonomous_system.core.specialized_agents import (
    SupervisorAgent, WorkerAgent, MonitorAgent, LearningAgent, DecisionAgent
)
from autonomous_system.core.message_protocol import (
    MessageProtocol, MessageProtocolHandler, ConversationManager,
    AcknowledgmentStatus, ProtocolEndpoint
)
from autonomous_system.core.state_coordination import (
    StateCoordinator, ConsensusManager, DistributedLockManager,
    CoordinationMode, ConsensusStrategy
)

# Phase 1.3: Memory System
from autonomous_system.core.enhanced_memory import (
    EpisodicMemory, SemanticMemory, ProceduralMemory,
    EnhancedMemoryManager, MemoryIndex
)
from autonomous_system.core.memory_integration import (
    MemoryAwareAgent, EnhancedLearningAgent, EnhancedDecisionAgent,
    EnhancedMonitorAgent, MemoryIntegrationManager
)

# Phase 2: Self-Correction Engine
from autonomous_system.core.error_detection import (
    ErrorDetectionManager, ErrorDetector, ErrorContext, ErrorPattern,
    ErrorAnalysis, ErrorType, ErrorSeverity, ErrorSignature,
    ExceptionDetector, OutcomeDetector, PerformanceDetector
)
from autonomous_system.core.correction_strategy import (
    CorrectionStrategyEngine, Corrector, CorrectionResult,
    CorrectionStrategy, StrategyConfig,
    RetryCorrector, FallbackCorrector, RollbackCorrector, SkipCorrector,
    ModifyParametersCorrector, CacheCorrector, EscalateCorrector
)
from autonomous_system.core.adaptive_improvement import (
    AdaptiveImprovementSystem, ImprovementSuggestion, ImprovementLevel,
    StrategyAdaptation, LearningMetric
)
from autonomous_system.core.self_correction import (
    SelfCorrectionOrchestrator, SelfCorrectionSession, SystemHealthReport
)

# Phase 3: Learning System
from autonomous_system.core.pattern_extraction import (
    PatternExtractionEngine, ExtractedPattern, PatternType
)
from autonomous_system.core.strategy_learning import (
    StrategyLearningEngine, StrategyPerformance
)
from autonomous_system.core.knowledge_synthesis import (
    KnowledgeSynthesisEngine, KnowledgeRule, KnowledgeType
)
from autonomous_system.core.learning_orchestrator import (
    LearningSystemOrchestrator, LearningSession, LearningMetrics
)

# Phase 4: Decision Optimization
from autonomous_system.core.decision_tree import (
    DecisionNodeType, DecisionCondition, DecisionNode, DecisionTree,
    DecisionTreeBuilder
)
from autonomous_system.core.resource_optimizer import (
    ResourceType, ResourceCost, ResourceBudget, OptimizationResult,
    ResourceOptimizationEngine
)
from autonomous_system.core.decision_optimization import (
    DecisionContext, Decision, DecisionOptimizationOrchestrator
)

# Phase 5: Tree of Thoughts Integration
from autonomous_system.core.thought_node import (
    ThoughtType, ThoughtStatus, Evaluation, ThoughtNode, ThoughtPath
)
from autonomous_system.core.outcome_prediction import (
    OutcomePrediction, OutcomePredictionEngine
)
from autonomous_system.core.tree_of_thoughts import (
    TreeOfThoughtsOrchestrator, ToTExplorationConfig, ExplorationResult
)

# Phase 6: Advanced Autonomous Features
from autonomous_system.core.system_optimizer import (
    SystemOptimizer, OptimizationTarget, OptimizationMetrics,
    ParameterRange, SystemConfiguration
)
from autonomous_system.core.meta_learning import (
    MetaLearningEngine, MetaLearningMetrics, LearningPhase,
    StrategyMetaProfile
)

# Phase 7: Free LLM Integration (Ollama)
from autonomous_system.core.llm_reasoning import (
    OllamaClient, OllamaConfig, FreeOllamaSetup
)
from autonomous_system.core.llm_enhanced_orchestrator import (
    LLMEnhancedOrchestrator, AsyncLLMEnhancedOrchestrator
)
from autonomous_system.core.predictive_maintenance import (
    PredictiveMaintenanceEngine, MaintenanceLevel, HealthIndicator,
    ComponentHealth
)
from autonomous_system.core.autonomous_resource_allocation import (
    ResourceAllocator, ResourceType, AllocationStrategy,
    AllocationRequest, AllocationResult, ResourcePool
)
from autonomous_system.core.advanced_autonomous_orchestrator import (
    AdvancedAutonomousOrchestrator, AdvancedAutonomousConfig
)

# Universal Agent Healer - Autonomous self-healing for ANY agent system
from autonomous_system.core.universal_agent_healer import (
    UniversalAgentHealer, AgentSystemType, AgentSystemFailure, AgentHealing,
    register_agent_system, heal_agent_system, get_system_health,
    global_agent_healer
)

__all__ = [
    # Phase 1.1 Components
    'DatabaseManager',
    'app',
    'AuthenticationManager', 'UserRole', 'PermissionLevel',
    'EventTracker', 'StructuredLogger', 'MetricsCollector', 'AlertManager',
    'EventType', 'MetricType', 'SeverityLevel',
    'BaseAgent', 'AgentRegistry', 'MessageBus', 'StateManager',
    'AgentConfig', 'AgentState', 'Message', 'MessageType',
    'MemoryManager', 'MemoryType', 'MemoryPriority', 'ContextWindow',
    'CoreOrchestrator', 'get_orchestrator',
    
    # Phase 1.2 Components
    'SupervisorAgent', 'WorkerAgent', 'MonitorAgent', 'LearningAgent', 'DecisionAgent',
    'MessageProtocol', 'MessageProtocolHandler', 'ConversationManager',
    'AcknowledgmentStatus', 'ProtocolEndpoint',
    'StateCoordinator', 'ConsensusManager', 'DistributedLockManager',
    'CoordinationMode', 'ConsensusStrategy',
    
    # Phase 1.3 Components - Memory System
    'EpisodicMemory', 'SemanticMemory', 'ProceduralMemory',
    'EnhancedMemoryManager', 'MemoryIndex',
    'MemoryAwareAgent', 'EnhancedLearningAgent', 'EnhancedDecisionAgent',
    'EnhancedMonitorAgent', 'MemoryIntegrationManager',
    
    # Phase 2 Components - Self-Correction Engine
    'ErrorDetectionManager', 'ErrorDetector', 'ErrorContext', 'ErrorPattern',
    'ErrorAnalysis', 'ErrorType', 'ErrorSeverity', 'ErrorSignature',
    'ExceptionDetector', 'OutcomeDetector', 'PerformanceDetector',
    'CorrectionStrategyEngine', 'Corrector', 'CorrectionResult',
    'CorrectionStrategy', 'StrategyConfig',
    'RetryCorrector', 'FallbackCorrector', 'RollbackCorrector', 'SkipCorrector',
    'ModifyParametersCorrector', 'CacheCorrector', 'EscalateCorrector',
    'AdaptiveImprovementSystem', 'ImprovementSuggestion', 'ImprovementLevel',
    'StrategyAdaptation', 'LearningMetric',
    'SelfCorrectionOrchestrator', 'SelfCorrectionSession', 'SystemHealthReport',
    
    # Phase 3 Components - Learning System
    'PatternExtractionEngine', 'ExtractedPattern', 'PatternType',
    'StrategyLearningEngine', 'StrategyPerformance',
    'KnowledgeSynthesisEngine', 'KnowledgeRule', 'KnowledgeType',
    'LearningSystemOrchestrator', 'LearningSession', 'LearningMetrics',
    
    # Phase 4 Components - Decision Optimization
    'DecisionNodeType', 'DecisionCondition', 'DecisionNode', 'DecisionTree',
    'DecisionTreeBuilder',
    'ResourceType', 'ResourceCost', 'ResourceBudget', 'OptimizationResult',
    'ResourceOptimizationEngine',
    'DecisionContext', 'Decision', 'DecisionOptimizationOrchestrator',
    
    # Phase 5 Components - Tree of Thoughts Integration
    'ThoughtType', 'ThoughtStatus', 'Evaluation', 'ThoughtNode', 'ThoughtPath',
    'OutcomePrediction', 'OutcomePredictionEngine',
    'TreeOfThoughtsOrchestrator', 'ToTExplorationConfig', 'ExplorationResult',
    
    # Phase 6 Components - Advanced Autonomous Features
    'SystemOptimizer', 'OptimizationTarget', 'OptimizationMetrics',
    'ParameterRange', 'SystemConfiguration',
    'MetaLearningEngine', 'MetaLearningMetrics', 'LearningPhase',
    'StrategyMetaProfile',
    
    # Phase 7 Components - Free LLM Integration (Ollama)
    'OllamaClient', 'OllamaConfig', 'FreeOllamaSetup',
    'LLMEnhancedOrchestrator', 'AsyncLLMEnhancedOrchestrator',
    'PredictiveMaintenanceEngine', 'MaintenanceLevel', 'HealthIndicator',
    'ComponentHealth',
    'ResourceAllocator', 'AllocationStrategy',
    'AllocationRequest', 'AllocationResult', 'ResourcePool',
    'AdvancedAutonomousOrchestrator', 'AdvancedAutonomousConfig',
    
    # Universal Agent Healer - Autonomous self-healing for any system
    'UniversalAgentHealer', 'AgentSystemType', 'AgentSystemFailure', 'AgentHealing',
    'register_agent_system', 'heal_agent_system', 'get_system_health',
    'global_agent_healer'
]

