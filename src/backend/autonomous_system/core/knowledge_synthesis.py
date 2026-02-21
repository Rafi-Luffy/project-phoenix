"""
Knowledge Synthesis Engine for Learning System

This module synthesizes learnings from corrections into actionable knowledge.
Generates rules, recommendations, and insights for system improvement.

Based on: Self-Refine framework for knowledge synthesis
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum
import json
from collections import defaultdict

from autonomous_system.core.error_detection import ErrorType, ErrorSeverity
from autonomous_system.core.correction_strategy import CorrectionStrategy


class KnowledgeType(Enum):
    """Types of knowledge that can be synthesized"""
    PREVENTION_RULE = "prevention_rule"      # How to prevent errors
    DETECTION_RULE = "detection_rule"        # How to detect errors early
    RECOVERY_RULE = "recovery_rule"          # How to recover from errors
    OPTIMIZATION_RULE = "optimization_rule"  # How to optimize operations
    PATTERN_RULE = "pattern_rule"            # Pattern-based rules


@dataclass
class KnowledgeRule:
    """A synthesized knowledge rule"""
    rule_type: KnowledgeType
    rule_id: str
    name: str
    description: str
    condition: str  # When this rule applies
    action: str     # What to do
    priority: int   # 1-100, higher = more important
    confidence: float  # 0.0-1.0
    error_types: List[ErrorType] = field(default_factory=list)
    success_rate: float = 0.0
    application_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_applied: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": self.rule_type.value,
            "id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "condition": self.condition,
            "action": self.action,
            "priority": self.priority,
            "confidence": self.confidence,
            "success_rate": self.success_rate,
            "applications": self.application_count,
            "error_types": [e.value for e in self.error_types],
            "created": self.created_at.isoformat()
        }


@dataclass
class Recommendation:
    """A system improvement recommendation"""
    recommendation_id: str
    title: str
    description: str
    rationale: str
    targeted_issue: str
    expected_improvement: str
    difficulty: str  # Easy, Medium, Hard
    estimated_impact: float  # 0.0-1.0
    priority: int  # 1-100
    based_on_rules: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, implemented, verified
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.recommendation_id,
            "title": self.title,
            "description": self.description,
            "rationale": self.rationale,
            "issue": self.targeted_issue,
            "expected_improvement": self.expected_improvement,
            "difficulty": self.difficulty,
            "estimated_impact": self.estimated_impact,
            "priority": self.priority,
            "status": self.status
        }


@dataclass
class InsightCluster:
    """A cluster of related insights"""
    cluster_id: str
    theme: str
    insights: List[str]
    related_errors: List[ErrorType]
    confidence: float
    frequency: int  # How often this pattern appears
    actionability: str  # High, Medium, Low
    

class KnowledgeSynthesisEngine:
    """
    Synthesizes learnings into actionable knowledge rules and recommendations.
    Discovers patterns, generates rules, creates improvement suggestions.
    """
    
    def __init__(self):
        """Initialize knowledge synthesis engine"""
        self.rules: Dict[str, KnowledgeRule] = {}
        self.recommendations: Dict[str, Recommendation] = {}
        self.insight_clusters: Dict[str, InsightCluster] = {}
        
        self.total_syntheses = 0
        self.rule_discovery_count = 0
        self.recommendation_count = 0
        
        # Knowledge base
        self.error_recovery_knowledge: Dict[str, List[str]] = defaultdict(list)
    
    def synthesize_from_patterns(self, 
                                 patterns: List[Dict[str, Any]],
                                 learning_data: Dict[str, Any]) -> List[KnowledgeRule]:
        """
        Synthesize knowledge from extracted patterns
        
        Args:
            patterns: Extracted patterns from pattern extraction engine
            learning_data: Learning data from strategy learning engine
            
        Returns:
            List of synthesized knowledge rules
        """
        self.total_syntheses += 1
        synthesized_rules = []
        
        # Synthesize prevention rules from high-frequency error patterns
        prevention_rules = self._synthesize_prevention_rules(patterns)
        synthesized_rules.extend(prevention_rules)
        
        # Synthesize recovery rules from successful corrections
        recovery_rules = self._synthesize_recovery_rules(patterns, learning_data)
        synthesized_rules.extend(recovery_rules)
        
        # Synthesize optimization rules from performance data
        optimization_rules = self._synthesize_optimization_rules(learning_data)
        synthesized_rules.extend(optimization_rules)
        
        # Synthesize detection rules for early error identification
        detection_rules = self._synthesize_detection_rules(patterns)
        synthesized_rules.extend(detection_rules)
        
        return synthesized_rules
    
    def _synthesize_prevention_rules(self, patterns: List[Dict[str, Any]]) -> List[KnowledgeRule]:
        """Synthesize rules for error prevention"""
        rules = []
        
        # Group patterns by error type and frequency
        error_pattern_map = defaultdict(list)
        for pattern in patterns:
            if pattern.get("type") == "error_sequence":
                error_type = pattern.get("metadata", {}).get("error_type")
                if error_type:
                    error_pattern_map[error_type].append(pattern)
        
        # Create prevention rules for frequent errors
        for error_type_str, pattern_list in error_pattern_map.items():
            if len(pattern_list) >= 2:  # At least 2 occurrences
                try:
                    error_type = ErrorType[error_type_str.upper()]
                except:
                    continue
                
                rule_id = f"prevent_{error_type_str}_{len(self.rules)}"
                
                if rule_id not in self.rules:
                    rule = KnowledgeRule(
                        rule_type=KnowledgeType.PREVENTION_RULE,
                        rule_id=rule_id,
                        name=f"Prevent {error_type_str}",
                        description=f"Prevention rule for {error_type_str} errors",
                        condition=f"When executing operations prone to {error_type_str}",
                        action=f"Validate inputs and state before operation",
                        priority=70,
                        confidence=0.7,
                        error_types=[error_type],
                        success_rate=0.75,
                        metadata={
                            "error_type": error_type_str,
                            "pattern_count": len(pattern_list)
                        }
                    )
                    self.rules[rule_id] = rule
                    self.rule_discovery_count += 1
                    rules.append(rule)
        
        return rules
    
    def _synthesize_recovery_rules(self, patterns: List[Dict[str, Any]], 
                                  learning_data: Dict[str, Any]) -> List[KnowledgeRule]:
        """Synthesize rules for error recovery"""
        rules = []
        
        # Extract successful recovery patterns
        recovery_patterns = [
            p for p in patterns
            if p.get("type") == "recovery_pattern"
        ]
        
        for pattern in recovery_patterns[:10]:  # Limit to top 10
            strategy = pattern.get("metadata", {}).get("strategy")
            error_type_str = pattern.get("metadata", {}).get("error_type")
            
            if strategy and error_type_str:
                try:
                    error_type = ErrorType[error_type_str.upper()]
                except:
                    continue
                
                rule_id = f"recover_{error_type_str}_{strategy}"
                
                if rule_id not in self.rules:
                    rule = KnowledgeRule(
                        rule_type=KnowledgeType.RECOVERY_RULE,
                        rule_id=rule_id,
                        name=f"Recover {error_type_str} with {strategy}",
                        description=f"Recovery strategy for {error_type_str}",
                        condition=f"When {error_type_str} is detected",
                        action=f"Apply {strategy} correction strategy",
                        priority=80,
                        confidence=0.8,
                        error_types=[error_type],
                        success_rate=0.85,
                        metadata={
                            "error_type": error_type_str,
                            "strategy": strategy
                        }
                    )
                    self.rules[rule_id] = rule
                    self.rule_discovery_count += 1
                    rules.append(rule)
        
        return rules
    
    def _synthesize_optimization_rules(self, learning_data: Dict[str, Any]) -> List[KnowledgeRule]:
        """Synthesize rules for operation optimization"""
        rules = []
        
        # Extract insights from strategy performance
        strategy_matrix = learning_data.get("strategy_matrix", {})
        
        for error_type_str, strategies in strategy_matrix.items():
            # Find most efficient strategy
            best_efficiency = 0
            best_strategy = None
            
            for strategy_name, metrics in strategies.items():
                efficiency = metrics.get("efficiency", 0)
                if efficiency > best_efficiency:
                    best_efficiency = efficiency
                    best_strategy = strategy_name
            
            if best_strategy and best_efficiency > 0.6:
                rule_id = f"optimize_{error_type_str}_{best_strategy}"
                
                if rule_id not in self.rules:
                    rule = KnowledgeRule(
                        rule_type=KnowledgeType.OPTIMIZATION_RULE,
                        rule_id=rule_id,
                        name=f"Optimize {error_type_str} handling",
                        description=f"Use efficient {best_strategy} for {error_type_str}",
                        condition=f"When handling {error_type_str}",
                        action=f"Use {best_strategy} as primary strategy",
                        priority=60,
                        confidence=0.75,
                        success_rate=0.8,
                        metadata={
                            "error_type": error_type_str,
                            "best_strategy": best_strategy,
                            "efficiency": best_efficiency
                        }
                    )
                    self.rules[rule_id] = rule
                    self.rule_discovery_count += 1
                    rules.append(rule)
        
        return rules
    
    def _synthesize_detection_rules(self, patterns: List[Dict[str, Any]]) -> List[KnowledgeRule]:
        """Synthesize rules for early error detection"""
        rules = []
        
        # Extract context patterns for detection rules
        context_patterns = [
            p for p in patterns
            if p.get("type") == "context_pattern"
        ]
        
        for pattern in context_patterns[:5]:  # Limit to top 5
            operation = pattern.get("metadata", {}).get("operation")
            error_type_str = pattern.get("metadata", {}).get("error_type")
            
            if operation and error_type_str:
                try:
                    error_type = ErrorType[error_type_str.upper()]
                except:
                    continue
                
                rule_id = f"detect_{error_type_str}_{operation}"
                
                if rule_id not in self.rules:
                    rule = KnowledgeRule(
                        rule_type=KnowledgeType.DETECTION_RULE,
                        rule_id=rule_id,
                        name=f"Detect {error_type_str} in {operation}",
                        description=f"Early detection for {error_type_str}",
                        condition=f"Before executing {operation}",
                        action=f"Monitor for {error_type_str} indicators",
                        priority=75,
                        confidence=0.7,
                        error_types=[error_type],
                        success_rate=0.72,
                        metadata={
                            "operation": operation,
                            "error_type": error_type_str
                        }
                    )
                    self.rules[rule_id] = rule
                    self.rule_discovery_count += 1
                    rules.append(rule)
        
        return rules
    
    def apply_rule(self, rule_id: str, context: Dict[str, Any]) -> bool:
        """
        Apply a rule in a given context
        
        Args:
            rule_id: ID of the rule to apply
            context: Context information
            
        Returns:
            Whether rule was successfully applied
        """
        if rule_id not in self.rules:
            return False
        
        rule = self.rules[rule_id]
        rule.application_count += 1
        rule.last_applied = datetime.now()
        return True
    
    def record_rule_success(self, rule_id: str, success: bool) -> None:
        """Record success/failure of rule application"""
        if rule_id not in self.rules:
            return
        
        rule = self.rules[rule_id]
        if success:
            rule.success_rate = (
                (rule.success_rate * (rule.application_count - 1) + 1) /
                rule.application_count
            )
    
    def generate_recommendations(self, learning_data: Dict[str, Any]) -> List[Recommendation]:
        """
        Generate improvement recommendations from learning data
        
        Args:
            learning_data: Data from learning engines
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Analyze error type insights
        error_insights = learning_data.get("error_type_insights", {})
        
        for error_type, insight in error_insights.items():
            success_rate = insight.get("success_rate", 0)
            attempts = insight.get("attempts", 0)
            
            # If low success rate, recommend improvement
            if success_rate < 0.6 and attempts > 5:
                rec_id = f"improve_{error_type}_{len(self.recommendations)}"
                
                if rec_id not in self.recommendations:
                    rec = Recommendation(
                        recommendation_id=rec_id,
                        title=f"Improve {error_type} handling",
                        description=f"Success rate for {error_type} is {success_rate:.1%}",
                        rationale="Low success rate indicates room for improvement",
                        targeted_issue=f"{error_type} errors",
                        expected_improvement="Increase success rate to 80%+",
                        difficulty="Medium",
                        estimated_impact=0.7,
                        priority=80,
                        based_on_rules=[r.rule_id for r in self.rules.values()
                                       if error_type in str(r.metadata)]
                    )
                    self.recommendations[rec_id] = rec
                    self.recommendation_count += 1
                    recommendations.append(rec)
        
        return recommendations
    
    def cluster_insights(self, patterns: List[Dict[str, Any]]) -> List[InsightCluster]:
        """
        Cluster related insights for better understanding
        
        Args:
            patterns: Extracted patterns
            
        Returns:
            List of insight clusters
        """
        clusters = []
        clustered_patterns = defaultdict(list)
        
        # Group by pattern type
        for pattern in patterns:
            pattern_type = pattern.get("type", "unknown")
            clustered_patterns[pattern_type].append(pattern)
        
        # Create clusters for each pattern type
        for pattern_type, pattern_list in clustered_patterns.items():
            if pattern_list:
                cluster_id = f"cluster_{pattern_type}_{len(self.insight_clusters)}"
                
                error_types = []
                for pattern in pattern_list:
                    error_type = pattern.get("metadata", {}).get("error_type")
                    if error_type:
                        try:
                            error_types.append(ErrorType[error_type.upper()])
                        except:
                            pass
                
                cluster = InsightCluster(
                    cluster_id=cluster_id,
                    theme=f"{pattern_type} patterns",
                    insights=[p.get("name", "") for p in pattern_list[:5]],
                    related_errors=list(set(error_types)),
                    confidence=0.7,
                    frequency=len(pattern_list),
                    actionability="High" if len(pattern_list) > 5 else "Medium"
                )
                
                self.insight_clusters[cluster_id] = cluster
                clusters.append(cluster)
        
        return clusters
    
    def get_knowledge_base(self) -> Dict[str, Any]:
        """Get current knowledge base"""
        return {
            "rules": {
                rule_id: rule.to_dict()
                for rule_id, rule in self.rules.items()
            },
            "recommendations": {
                rec_id: rec.to_dict()
                for rec_id, rec in self.recommendations.items()
            },
            "insight_clusters": {
                cluster_id: {
                    "theme": cluster.theme,
                    "insights": cluster.insights,
                    "frequency": cluster.frequency,
                    "actionability": cluster.actionability
                }
                for cluster_id, cluster in self.insight_clusters.items()
            }
        }
    
    def get_top_rules(self, limit: int = 10) -> List[KnowledgeRule]:
        """Get top performing rules by priority and success rate"""
        sorted_rules = sorted(
            self.rules.values(),
            key=lambda r: (r.priority, r.success_rate),
            reverse=True
        )
        return sorted_rules[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge synthesis statistics"""
        return {
            "total_syntheses": self.total_syntheses,
            "total_rules": len(self.rules),
            "rules_discovered": self.rule_discovery_count,
            "rules_by_type": {
                kt.value: len([r for r in self.rules.values() if r.rule_type == kt])
                for kt in KnowledgeType
            },
            "total_recommendations": len(self.recommendations),
            "recommendations_generated": self.recommendation_count,
            "insight_clusters": len(self.insight_clusters)
        }
