"""
Learning System Orchestrator

This module coordinates all learning components (pattern extraction, strategy learning,
knowledge synthesis) to create a complete self-learning system.

Based on: Self-Refine framework for continuous improvement
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import json

from autonomous_system.core.pattern_extraction import PatternExtractionEngine, ExtractedPattern
from autonomous_system.core.strategy_learning import StrategyLearningEngine, StrategyRecommendation
from autonomous_system.core.knowledge_synthesis import KnowledgeSynthesisEngine, KnowledgeRule
from autonomous_system.core.error_detection import ErrorType
from autonomous_system.core.correction_strategy import CorrectionStrategy


@dataclass
class LearningSession:
    """A learning session tracking"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    correction_sessions_processed: int = 0
    patterns_extracted: int = 0
    rules_synthesized: int = 0
    recommendations_generated: int = 0
    learning_insights: Dict[str, Any] = field(default_factory=dict)
    
    def duration_seconds(self) -> float:
        """Get session duration in seconds"""
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()


@dataclass
class LearningMetrics:
    """Overall learning system metrics"""
    total_learning_sessions: int = 0
    total_patterns_extracted: int = 0
    total_rules_synthesized: int = 0
    total_recommendations: int = 0
    average_pattern_per_session: float = 0.0
    average_rule_per_session: float = 0.0
    system_improvement_score: float = 0.0
    last_learning_update: datetime = field(default_factory=datetime.now)


class LearningSystemOrchestrator:
    """
    Master orchestrator for the learning system.
    Coordinates pattern extraction, strategy learning, and knowledge synthesis.
    """
    
    def __init__(self):
        """Initialize learning system orchestrator"""
        # Core learning engines
        self.pattern_extractor = PatternExtractionEngine()
        self.strategy_learner = StrategyLearningEngine()
        self.knowledge_synthesizer = KnowledgeSynthesisEngine()
        
        # Session tracking
        self.learning_sessions: Dict[str, LearningSession] = {}
        self.current_session: Optional[LearningSession] = None
        
        # Metrics
        self.metrics = LearningMetrics()
        self.learning_history: List[Dict[str, Any]] = []
        
        # Thresholds
        self.min_sessions_for_synthesis = 10
        self.min_patterns_for_rules = 5
    
    def start_learning_session(self, session_id: str) -> LearningSession:
        """
        Start a new learning session
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            New learning session
        """
        session = LearningSession(
            session_id=session_id,
            start_time=datetime.now()
        )
        
        self.learning_sessions[session_id] = session
        self.current_session = session
        
        return session
    
    def process_correction_session(self, correction_session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a correction session through all learning engines
        
        Args:
            correction_session: Session from self-correction orchestrator
            
        Returns:
            Learning results dictionary
        """
        if not self.current_session:
            self.start_learning_session(f"auto_{datetime.now().timestamp()}")
        
        session = self.current_session
        results = {
            "session_id": session.session_id,
            "timestamp": datetime.now().isoformat(),
            "patterns": [],
            "strategy_recommendations": [],
            "knowledge_rules": [],
            "synthesis_insights": {}
        }
        
        # Step 1: Extract patterns
        extracted_patterns = self.pattern_extractor.extract_from_session(correction_session)
        session.patterns_extracted += len(extracted_patterns)
        results["patterns"] = [p.to_dict() for p in extracted_patterns]
        
        # Step 2: Update strategy learning
        if "error" in correction_session and "correction" in correction_session:
            error_info = correction_session["error"]
            correction_info = correction_session["correction"]
            
            try:
                error_type = ErrorType[error_info.get("error_type", "UNKNOWN").upper()]
                strategy = CorrectionStrategy[correction_info.get("strategy", "ESCALATE").upper()]
                
                self.strategy_learner.update_strategy_performance(
                    strategy=strategy,
                    error_type=error_type,
                    success=correction_session.get("final_success", False),
                    execution_time=correction_info.get("execution_time", 0),
                    resource_usage=correction_info.get("resource_usage", 0)
                )
                
                # Get strategy recommendation
                recommendation = self.strategy_learner.get_best_strategy(error_type)
                if recommendation:
                    results["strategy_recommendations"].append(recommendation.to_dict())
            except (KeyError, ValueError):
                pass
        
        session.correction_sessions_processed += 1
        
        # Step 3: Periodic synthesis (when threshold is reached)
        if session.correction_sessions_processed >= self.min_sessions_for_synthesis:
            synthesis_result = self._perform_synthesis()
            session.rules_synthesized += synthesis_result.get("rules_generated", 0)
            session.recommendations_generated += synthesis_result.get("recommendations_generated", 0)
            results["synthesis_insights"] = synthesis_result
        
        # Update metrics
        self._update_metrics(session)
        
        return results
    
    def _perform_synthesis(self) -> Dict[str, Any]:
        """
        Perform knowledge synthesis based on current learning data
        
        Returns:
            Synthesis results
        """
        # Gather data from engines
        top_patterns = self.pattern_extractor.get_highest_confidence_patterns(limit=50)
        learning_insights = self.strategy_learner.get_learning_insights()
        
        # Prepare learning data
        learning_data = {
            "strategy_matrix": self.strategy_learner.get_strategy_matrix(),
            "learning_insights": learning_insights
        }
        
        # Perform synthesis
        synthesized_rules = self.knowledge_synthesizer.synthesize_from_patterns(
            patterns=[p.to_dict() for p in top_patterns],
            learning_data=learning_data
        )
        
        # Generate recommendations
        recommendations = self.knowledge_synthesizer.generate_recommendations(learning_data)
        
        # Cluster insights
        insight_clusters = self.knowledge_synthesizer.cluster_insights(
            patterns=[p.to_dict() for p in top_patterns]
        )
        
        return {
            "rules_generated": len(synthesized_rules),
            "recommendations_generated": len(recommendations),
            "insight_clusters": len(insight_clusters),
            "top_rules": [r.to_dict() for r in synthesized_rules[:5]],
            "top_recommendations": [r.to_dict() for r in recommendations[:3]],
            "synthesis_timestamp": datetime.now().isoformat()
        }
    
    def end_learning_session(self) -> Optional[LearningSession]:
        """
        End the current learning session
        
        Returns:
            Completed session or None
        """
        if not self.current_session:
            return None
        
        session = self.current_session
        session.end_time = datetime.now()
        
        # Generate session insights
        session.learning_insights = {
            "patterns_extracted": session.patterns_extracted,
            "rules_synthesized": session.rules_synthesized,
            "recommendations_generated": session.recommendations_generated,
            "session_duration": session.duration_seconds()
        }
        
        # Store in history
        self.learning_history.append({
            "session_id": session.session_id,
            "insights": session.learning_insights,
            "timestamp": datetime.now().isoformat()
        })
        
        self.current_session = None
        return session
    
    def _update_metrics(self, session: LearningSession) -> None:
        """Update overall learning metrics"""
        self.metrics.total_learning_sessions = len(self.learning_sessions)
        self.metrics.total_patterns_extracted = self.pattern_extractor.pattern_discovery_count
        self.metrics.total_rules_synthesized = self.knowledge_synthesizer.rule_discovery_count
        self.metrics.total_recommendations = len(self.knowledge_synthesizer.recommendations)
        
        if self.metrics.total_learning_sessions > 0:
            self.metrics.average_pattern_per_session = (
                self.metrics.total_patterns_extracted / self.metrics.total_learning_sessions
            )
            self.metrics.average_rule_per_session = (
                self.metrics.total_rules_synthesized / self.metrics.total_learning_sessions
            )
        
        # Calculate improvement score
        self._calculate_improvement_score()
        self.metrics.last_learning_update = datetime.now()
    
    def _calculate_improvement_score(self) -> None:
        """Calculate system improvement score based on learning"""
        score = 0.0
        
        # Factor 1: Pattern discovery (0-0.3)
        pattern_diversity = len(self.pattern_extractor.extracted_patterns) / 100.0
        score += min(pattern_diversity * 0.3, 0.3)
        
        # Factor 2: Rule effectiveness (0-0.3)
        if self.knowledge_synthesizer.rules:
            avg_success = sum(
                r.success_rate for r in self.knowledge_synthesizer.rules.values()
            ) / len(self.knowledge_synthesizer.rules)
            score += avg_success * 0.3
        
        # Factor 3: Learning phase progress (0-0.2)
        phase_value = {
            "exploration": 0.05,
            "exploitation": 0.1,
            "optimization": 0.15,
            "prediction": 0.2
        }
        score += phase_value.get(self.strategy_learner.learning_phase.value, 0)
        
        # Factor 4: Recommendation quality (0-0.2)
        rec_count = min(len(self.knowledge_synthesizer.recommendations) / 20.0, 1.0)
        score += rec_count * 0.2
        
        self.metrics.system_improvement_score = min(score, 1.0)
    
    def get_learning_status(self) -> Dict[str, Any]:
        """Get comprehensive learning system status"""
        return {
            "active_session": self.current_session.session_id if self.current_session else None,
            "total_sessions": len(self.learning_sessions),
            "pattern_extraction": self.pattern_extractor.get_stats(),
            "strategy_learning": self.strategy_learner.get_stats(),
            "knowledge_synthesis": self.knowledge_synthesizer.get_stats(),
            "overall_metrics": {
                "total_patterns": self.metrics.total_patterns_extracted,
                "total_rules": self.metrics.total_rules_synthesized,
                "total_recommendations": self.metrics.total_recommendations,
                "improvement_score": self.metrics.system_improvement_score
            }
        }
    
    def get_strategy_recommendation(self, error_type: ErrorType) -> Optional[StrategyRecommendation]:
        """
        Get strategy recommendation for an error type
        
        Args:
            error_type: Type of error
            
        Returns:
            Strategy recommendation or None
        """
        return self.strategy_learner.get_best_strategy(error_type)
    
    def get_applicable_rules(self, error_type: ErrorType, limit: int = 5) -> List[KnowledgeRule]:
        """
        Get applicable knowledge rules for an error type
        
        Args:
            error_type: Type of error
            limit: Maximum rules to return
            
        Returns:
            List of applicable rules
        """
        applicable = [
            r for r in self.knowledge_synthesizer.rules.values()
            if error_type in r.error_types
        ]
        
        # Sort by priority and success rate
        applicable.sort(
            key=lambda r: (r.priority, r.success_rate),
            reverse=True
        )
        
        return applicable[:limit]
    
    def get_knowledge_base_summary(self) -> Dict[str, Any]:
        """Get summary of knowledge base"""
        kb = self.knowledge_synthesizer.get_knowledge_base()
        
        return {
            "total_rules": len(kb["rules"]),
            "total_recommendations": len(kb["recommendations"]),
            "total_insight_clusters": len(kb["insight_clusters"]),
            "rule_types": list(set(r["type"] for r in kb["rules"].values())),
            "covered_error_types": list(set(
                et for r in kb["rules"].values()
                for et in r.get("error_types", [])
            )),
            "top_rules": self.knowledge_synthesizer.get_top_rules(limit=5),
            "learning_history_size": len(self.learning_history)
        }
    
    def export_learning_state(self) -> Dict[str, Any]:
        """Export complete learning system state"""
        return {
            "timestamp": datetime.now().isoformat(),
            "pattern_extractor_stats": self.pattern_extractor.get_stats(),
            "strategy_learner_stats": self.strategy_learner.get_stats(),
            "knowledge_synthesis_stats": self.knowledge_synthesizer.get_stats(),
            "metrics": {
                "total_learning_sessions": self.metrics.total_learning_sessions,
                "total_patterns_extracted": self.metrics.total_patterns_extracted,
                "total_rules_synthesized": self.metrics.total_rules_synthesized,
                "system_improvement_score": self.metrics.system_improvement_score
            },
            "knowledge_base": self.knowledge_synthesizer.get_knowledge_base()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get learning system statistics"""
        return {
            "learning_sessions": len(self.learning_sessions),
            "patterns_extracted": self.metrics.total_patterns_extracted,
            "rules_discovered": self.metrics.total_rules_synthesized,
            "recommendations_generated": self.metrics.total_recommendations,
            "improvement_score": self.metrics.system_improvement_score,
            "learning_history_entries": len(self.learning_history)
        }
