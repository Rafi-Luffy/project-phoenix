"""
Memory-Agent Integration Layer - Phase 1.3
Integrates specialized agents with enhanced memory types
Enables learning, decision-making, and monitoring through memory
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from autonomous_system.core.enhanced_memory import (
    EnhancedMemoryManager, EpisodicMemory, SemanticMemory, ProceduralMemory,
    MemoryDecayFunction
)
from autonomous_system.core.specialized_agents import (
    LearningAgent, DecisionAgent, MonitorAgent
)

logger = logging.getLogger(__name__)


class MemoryAwareAgent:
    """Mixin to make agents memory-aware"""
    
    def __init__(self, memory_manager: EnhancedMemoryManager = None):
        """Initialize memory awareness"""
        self.memory_manager = memory_manager or EnhancedMemoryManager()
        self.agent_experiences: List[Dict[str, Any]] = []
        self.learned_patterns: List[Dict[str, Any]] = []


class EnhancedLearningAgent(MemoryAwareAgent):
    """Learning agent enhanced with episodic and semantic memory"""
    
    def __init__(self, base_agent, memory_manager: EnhancedMemoryManager = None):
        """Initialize enhanced learning agent"""
        super().__init__(memory_manager)
        self.base_agent = base_agent
        self.agent_id = base_agent.agent_id
        self.name = base_agent.name
    
    def store_experience_as_episode(self, action: str, outcome: str, 
                                   confidence: float = 0.8,
                                   agents_involved: List[str] = None,
                                   context: Dict[str, Any] = None) -> str:
        """Store experience as episodic memory"""
        episode_id = self.memory_manager.store_episodic(
            description=f"Agent {self.agent_id} executed {action}",
            agents_involved=agents_involved or [self.agent_id],
            outcome=outcome,
            confidence=confidence,
            tags=[action, outcome, self.agent_id],
            metadata=context or {}
        )
        
        logger.info(f"Stored episode {episode_id} for {self.name}")
        return episode_id
    
    def extract_pattern_as_semantic(self, pattern_name: str, 
                                   pattern_properties: Dict[str, Any],
                                   confidence: float = 0.9) -> str:
        """Extract learned pattern as semantic memory"""
        concept_id = self.memory_manager.store_semantic(
            concept_name=pattern_name,
            properties=pattern_properties,
            source=f"LearningAgent:{self.agent_id}",
            confidence=confidence
        )
        
        logger.info(f"Extracted pattern {pattern_name} as semantic memory")
        return concept_id
    
    def store_strategy_as_procedure(self, strategy_name: str, steps: List[Dict[str, Any]],
                                   parameters: Dict[str, Any] = None) -> str:
        """Store learned strategy as procedural memory"""
        procedure_id = self.memory_manager.store_procedural(
            name=strategy_name,
            steps=steps,
            parameters=parameters or {},
            complexity=5
        )
        
        logger.info(f"Stored strategy {strategy_name} as procedural memory")
        return procedure_id
    
    def recall_similar_episodes(self, description: str, limit: int = 5) -> List[EpisodicMemory]:
        """Recall similar past experiences"""
        return self.memory_manager.similarity_search(description, limit)
    
    def get_learned_patterns(self) -> List[SemanticMemory]:
        """Get all learned semantic patterns"""
        patterns = []
        for concept_id, memory in self.memory_manager.semantic_memories.items():
            if memory.source.startswith(f"LearningAgent:{self.agent_id}"):
                patterns.append(memory)
        return patterns
    
    def get_strategies(self) -> List[ProceduralMemory]:
        """Get all learned strategies"""
        strategies = []
        for proc_id, memory in self.memory_manager.procedural_memories.items():
            if 'source' in memory.parameters and memory.parameters['source'] == self.agent_id:
                strategies.append(memory)
        return strategies
    
    def learn_from_feedback(self, episode_id: str, feedback: str) -> None:
        """Learn from external feedback on an episode"""
        episode = self.memory_manager.retrieve_episodic(episode_id)
        if episode:
            # Boost importance based on feedback
            if 'positive' in feedback.lower() or 'good' in feedback.lower():
                episode.confidence = min(1.0, episode.confidence + 0.1)
            elif 'negative' in feedback.lower() or 'bad' in feedback.lower():
                episode.confidence = max(0.0, episode.confidence - 0.1)
            
            logger.info(f"Updated episode {episode_id} based on feedback: {feedback}")


class EnhancedDecisionAgent(MemoryAwareAgent):
    """Decision agent enhanced with semantic memory and procedural knowledge"""
    
    def __init__(self, base_agent, memory_manager: EnhancedMemoryManager = None):
        """Initialize enhanced decision agent"""
        super().__init__(memory_manager)
        self.base_agent = base_agent
        self.agent_id = base_agent.agent_id
        self.name = base_agent.name
    
    def query_knowledge_base(self, concept: str) -> Optional[SemanticMemory]:
        """Query semantic memory for decision-making"""
        memory = self.memory_manager.retrieve_semantic(concept)
        if memory:
            logger.info(f"Retrieved knowledge for {concept}")
        return memory
    
    def select_strategy(self, task_type: str, min_success_rate: float = 0.6) -> Optional[ProceduralMemory]:
        """Select best strategy for a task"""
        strategies = self.memory_manager.get_procedures_for_task(task_type, min_success_rate)
        if strategies:
            best = strategies[0]  # Already sorted by success rate
            logger.info(f"Selected strategy {best.name} for {task_type} (success: {best.success_rate:.2%})")
            return best
        return None
    
    def make_informed_decision(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """Make decision informed by past experiences"""
        # Query relevant knowledge
        decision_type = decision_context.get('type', 'unknown')
        knowledge = self.query_knowledge_base(decision_type)
        
        # Look for similar past situations
        description = decision_context.get('description', '')
        similar_episodes = self.memory_manager.similarity_search(description, limit=3)
        
        # Select strategy
        task_type = decision_context.get('task_type')
        strategy = self.select_strategy(task_type) if task_type else None
        
        # Make decision
        decision = {
            'decision_id': self.agent_id,
            'type': decision_type,
            'timestamp': datetime.now().isoformat(),
            'informed_by_knowledge': knowledge is not None,
            'similar_precedents': len(similar_episodes),
            'recommended_strategy': strategy.name if strategy else None,
            'confidence': knowledge.confidence if knowledge else 0.5
        }
        
        # Log successful decisions as precedents
        for episode in similar_episodes:
            if episode.outcome == 'success':
                decision['success_precedents'] = decision.get('success_precedents', 0) + 1
        
        logger.info(f"Made informed decision: {decision_type}")
        return decision
    
    def record_decision_outcome(self, decision_context: Dict[str, Any], outcome: str,
                               success: bool) -> None:
        """Record decision outcome for future learning"""
        self.memory_manager.store_episodic(
            description=f"Decision: {decision_context.get('type', 'unknown')}",
            agents_involved=[self.agent_id],
            outcome=outcome,
            confidence=0.95 if success else 0.5,
            tags=['decision', decision_context.get('type', 'unknown')],
            metadata=decision_context
        )
        
        # Update strategy success rate if applicable
        if 'strategy_id' in decision_context:
            self.memory_manager.record_procedure_execution(
                decision_context['strategy_id'],
                success
            )


class EnhancedMonitorAgent(MemoryAwareAgent):
    """Monitor agent enhanced with anomaly memory and pattern recognition"""
    
    def __init__(self, base_agent, memory_manager: EnhancedMemoryManager = None):
        """Initialize enhanced monitor agent"""
        super().__init__(memory_manager)
        self.base_agent = base_agent
        self.agent_id = base_agent.agent_id
        self.name = base_agent.name
        self.anomaly_patterns: Dict[str, List[Dict[str, Any]]] = {}
    
    def record_anomaly(self, metric_name: str, value: float, threshold: float,
                      agents_affected: List[str] = None) -> str:
        """Record anomaly as episodic memory"""
        episode_id = self.memory_manager.store_episodic(
            description=f"Anomaly: {metric_name} = {value} (threshold: {threshold})",
            agents_involved=agents_affected or [self.agent_id],
            outcome='anomaly_detected',
            confidence=0.95,
            tags=['anomaly', metric_name],
            metadata={
                'metric': metric_name,
                'value': value,
                'threshold': threshold,
                'deviation': (value - threshold) / threshold if threshold > 0 else 0
            }
        )
        
        # Track pattern
        if metric_name not in self.anomaly_patterns:
            self.anomaly_patterns[metric_name] = []
        self.anomaly_patterns[metric_name].append({
            'timestamp': datetime.now().isoformat(),
            'value': value,
            'episode_id': episode_id
        })
        
        logger.info(f"Recorded anomaly {metric_name}: {value}")
        return episode_id
    
    def detect_recurring_anomalies(self, metric_name: str, 
                                  recent_days: int = 7) -> Dict[str, Any]:
        """Detect patterns in recurring anomalies"""
        patterns = self.anomaly_patterns.get(metric_name, [])
        
        if len(patterns) < 2:
            return {'pattern_detected': False, 'occurrences': len(patterns)}
        
        # Simple pattern detection
        recent_count = sum(1 for p in patterns if p['timestamp'])  # Would filter by date
        
        # Store pattern as semantic memory
        if recent_count >= 3:
            pattern_name = f"{metric_name}_recurring_anomaly"
            self.memory_manager.store_semantic(
                concept_name=pattern_name,
                properties={
                    'metric': metric_name,
                    'occurrences': recent_count,
                    'pattern_type': 'recurring_anomaly'
                },
                source=f"MonitorAgent:{self.agent_id}",
                confidence=min(1.0, recent_count * 0.2)
            )
            
            return {
                'pattern_detected': True,
                'metric': metric_name,
                'occurrences': recent_count,
                'pattern_id': pattern_name
            }
        
        return {'pattern_detected': False, 'occurrences': recent_count}
    
    def get_recent_anomalies(self, agent_id: str = None, days_back: int = 7) -> List[EpisodicMemory]:
        """Get recent anomalies"""
        anomalies = self.memory_manager.temporal_search(agent_id or self.agent_id, days_back)
        return [a for a in anomalies if a.outcome == 'anomaly_detected']
    
    def get_anomaly_patterns(self) -> List[SemanticMemory]:
        """Get stored anomaly patterns"""
        patterns = []
        for concept_id, memory in self.memory_manager.semantic_memories.items():
            if 'anomaly' in memory.concept_name:
                patterns.append(memory)
        return patterns


class MemoryIntegrationManager:
    """Manages integration between all agents and memory system"""
    
    def __init__(self, memory_manager: EnhancedMemoryManager = None):
        """Initialize integration manager"""
        self.memory_manager = memory_manager or EnhancedMemoryManager()
        self.enhanced_agents: Dict[str, MemoryAwareAgent] = {}
    
    def enhance_learning_agent(self, base_agent: LearningAgent) -> EnhancedLearningAgent:
        """Enhance learning agent with memory capabilities"""
        enhanced = EnhancedLearningAgent(base_agent, self.memory_manager)
        self.enhanced_agents[base_agent.agent_id] = enhanced
        logger.info(f"Enhanced LearningAgent: {base_agent.name}")
        return enhanced
    
    def enhance_decision_agent(self, base_agent: DecisionAgent) -> EnhancedDecisionAgent:
        """Enhance decision agent with memory capabilities"""
        enhanced = EnhancedDecisionAgent(base_agent, self.memory_manager)
        self.enhanced_agents[base_agent.agent_id] = enhanced
        logger.info(f"Enhanced DecisionAgent: {base_agent.name}")
        return enhanced
    
    def enhance_monitor_agent(self, base_agent: MonitorAgent) -> EnhancedMonitorAgent:
        """Enhance monitor agent with memory capabilities"""
        enhanced = EnhancedMonitorAgent(base_agent, self.memory_manager)
        self.enhanced_agents[base_agent.agent_id] = enhanced
        logger.info(f"Enhanced MonitorAgent: {base_agent.name}")
        return enhanced
    
    def get_agent_memory_context(self, agent_id: str) -> Dict[str, Any]:
        """Get memory context for an agent"""
        agent = self.enhanced_agents.get(agent_id)
        if not agent:
            return {}
        
        context = {
            'agent_id': agent_id,
            'agent_name': agent.name,
            'type': type(agent).__name__
        }
        
        if isinstance(agent, EnhancedLearningAgent):
            context['patterns'] = len(agent.get_learned_patterns())
            context['strategies'] = len(agent.get_strategies())
        elif isinstance(agent, EnhancedDecisionAgent):
            context['knowledge_base_size'] = len(self.memory_manager.semantic_memories)
        elif isinstance(agent, EnhancedMonitorAgent):
            context['anomalies'] = len(agent.get_recent_anomalies())
            context['patterns'] = len(agent.get_anomaly_patterns())
        
        return context
    
    def get_system_memory_stats(self) -> Dict[str, Any]:
        """Get system-wide memory statistics"""
        stats = self.memory_manager.get_memory_stats()
        stats['enhanced_agents'] = len(self.enhanced_agents)
        
        # Breakdown by agent type
        stats['learning_agents'] = sum(1 for a in self.enhanced_agents.values() 
                                      if isinstance(a, EnhancedLearningAgent))
        stats['decision_agents'] = sum(1 for a in self.enhanced_agents.values() 
                                      if isinstance(a, EnhancedDecisionAgent))
        stats['monitor_agents'] = sum(1 for a in self.enhanced_agents.values() 
                                     if isinstance(a, EnhancedMonitorAgent))
        
        return stats
