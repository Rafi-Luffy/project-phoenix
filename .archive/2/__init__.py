"""
Autonomous Self-Healing System
Foundation for building self-correcting, learning, and adaptive systems
Based on Self-Refine and Tree of Thoughts papers
Phase 3: Learning System
"""

__version__ = "0.4.0"
__author__ = "Autonomous Systems Team"

# Phase 1.1: Core Components
from autonomous_system.core.orchestrator import CoreOrchestrator, get_orchestrator
from autonomous_system.core.database import PostgreSQLDatabase
from autonomous_system.core.auth import AuthenticationManager
from autonomous_system.core.monitoring import EventTracker, MetricsCollector, AlertManager

# Phase 1.2: Agent Framework
from autonomous_system.core.specialized_agents import (
    LearningAgent,
    DecisionAgent,
    MonitorAgent,
    SupervisorAgent,
    WorkerAgent
)
from autonomous_system.core.message_protocol import MessageProtocol, MessageProtocolHandler
from autonomous_system.core.state_coordination import (
    StateCoordinator,
    ConsensusManager,
    DistributedLockManager
)

# Phase 1.3: Enhanced Memory System
from autonomous_system.core.enhanced_memory import (
    EnhancedMemoryManager,
    EpisodicMemory,
    SemanticMemory,
    ProceduralMemory,
    MemoryDecayFunction,
    RetrievalStrategy
)
from autonomous_system.core.memory_integration import (
    MemoryAwareAgent,
    EnhancedLearningAgent,
    EnhancedDecisionAgent,
    EnhancedMonitorAgent,
    MemoryIntegrationManager
)
from autonomous_system.core.memory_api import create_memory_router

# Phase 2: Self-Correction Engine
from autonomous_system.core.error_detection import (
    ErrorDetectionManager, ErrorType, ErrorSeverity,
    ErrorContext, ErrorAnalysis
)
from autonomous_system.core.correction_strategy import (
    CorrectionStrategyEngine, CorrectionStrategy, CorrectionResult
)
from autonomous_system.core.adaptive_improvement import (
    AdaptiveImprovementSystem, ImprovementLevel, ImprovementSuggestion
)
from autonomous_system.core.self_correction import (
    SelfCorrectionOrchestrator, SystemHealthReport
)

# Phase 3: Learning System
from autonomous_system.core.pattern_extraction import (
    PatternExtractionEngine, PatternType, ExtractedPattern
)
from autonomous_system.core.strategy_learning import (
    StrategyLearningEngine, LearningPhase, StrategyPerformance, StrategyRecommendation
)
from autonomous_system.core.knowledge_synthesis import (
    KnowledgeSynthesisEngine, KnowledgeType, KnowledgeRule, Recommendation
)
from autonomous_system.core.learning_orchestrator import (
    LearningSystemOrchestrator, LearningSession, LearningMetrics
)

__all__ = [
    # Core Components
    'CoreOrchestrator', 'get_orchestrator',
    'PostgreSQLDatabase', 'AuthenticationManager',
    'EventTracker', 'MetricsCollector', 'AlertManager',
    
    # Agent Framework
    'LearningAgent', 'DecisionAgent', 'MonitorAgent',
    'SupervisorAgent', 'WorkerAgent',
    'MessageProtocol', 'MessageProtocolHandler',
    'StateCoordinator', 'ConsensusManager', 'DistributedLockManager',
    
    # Memory System
    'EnhancedMemoryManager',
    'EpisodicMemory', 'SemanticMemory', 'ProceduralMemory',
    'MemoryDecayFunction', 'RetrievalStrategy',
    'MemoryAwareAgent',
    'EnhancedLearningAgent', 'EnhancedDecisionAgent', 'EnhancedMonitorAgent',
    'MemoryIntegrationManager',
    'create_memory_router',
    
    # Self-Correction Engine
    'ErrorDetectionManager', 'ErrorType', 'ErrorSeverity',
    'ErrorContext', 'ErrorAnalysis',
    'CorrectionStrategyEngine', 'CorrectionStrategy', 'CorrectionResult',
    'AdaptiveImprovementSystem', 'ImprovementLevel', 'ImprovementSuggestion',
    'SelfCorrectionOrchestrator', 'SystemHealthReport',
    
    # Learning System
    'PatternExtractionEngine', 'PatternType', 'ExtractedPattern',
    'StrategyLearningEngine', 'LearningPhase', 'StrategyPerformance', 'StrategyRecommendation',
    'KnowledgeSynthesisEngine', 'KnowledgeType', 'KnowledgeRule', 'Recommendation',
    'LearningSystemOrchestrator', 'LearningSession', 'LearningMetrics'
]

