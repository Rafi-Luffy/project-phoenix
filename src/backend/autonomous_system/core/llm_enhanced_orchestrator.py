"""
LLM-Enhanced Self-Healing Orchestrator
Integrates free Ollama LLM for intelligent decision making

This layer adds:
- LLM-powered root cause analysis
- Natural language explanations
- Intelligent strategy selection
- Client-specific learning
- Decision reasoning
"""

import asyncio
import logging
from typing import Any, Dict, Optional, List
from datetime import datetime

from autonomous_system.core.llm_reasoning import OllamaClient
from autonomous_system.core.self_correction import SelfCorrectionOrchestrator


logger = logging.getLogger(__name__)


class LLMEnhancedOrchestrator(SelfCorrectionOrchestrator):
    """
    Self-correction orchestrator enhanced with free LLM reasoning
    Uses Ollama + Mistral (completely free, zero cost)
    """
    
    def __init__(self, memory_manager: Optional[Any] = None):
        """Initialize with LLM support"""
        super().__init__(memory_manager)
        
        self.llm_client = OllamaClient()
        self.llm_enabled = False
        self.llm_explanations = {}
        self.reasoning_cache = {}
        
    async def initialize(self) -> bool:
        """Initialize LLM client"""
        logger.info(" Initializing free LLM reasoning...")
        
        try:
            # Try to connect to Ollama
            if await self.llm_client.initialize():
                self.llm_enabled = True
                logger.info(" Ollama LLM ready (FREE - no API costs!)")
                
                # Pull model if needed
                await self.llm_client.pull_model()
                return True
            else:
                logger.warning(" Ollama not available, running without LLM reasoning")
                self.llm_enabled = False
                return True  # Still works without LLM
                
        except Exception as e:
            logger.error(f"LLM init error: {e}")
            self.llm_enabled = False
            return True  # Graceful degradation
    
    async def analyze_error_with_reasoning(
        self,
        error_type: str,
        error_message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze error with LLM reasoning
        
        Returns root cause and explanation
        """
        if not self.llm_enabled:
            return {
                "error_type": error_type,
                "root_cause": "Error analysis unavailable",
                "explanation": "LLM not running",
                "recommendations": []
            }
        
        try:
            # Use LLM to analyze
            analysis = await self.llm_client.analyze_error(
                error_type, error_message, context
            )
            
            logger.info(f" LLM analysis: {error_type}")
            return analysis
            
        except Exception as e:
            logger.error(f"LLM analysis error: {e}")
            return {
                "error_type": error_type,
                "root_cause": "Analysis failed",
                "explanation": str(e),
                "recommendations": []
            }
    
    async def select_correction_with_reasoning(
        self,
        error: str,
        available_strategies: List[str],
        success_rates: Dict[str, float],
        system_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use LLM to select best correction strategy
        
        Args:
            error: Error description
            available_strategies: Available correction strategies
            success_rates: Historical success rates per strategy
            system_context: Current system state
            
        Returns:
            Selected strategy with reasoning
        """
        # Check cache first
        cache_key = f"{error}_{str(available_strategies)}"
        if cache_key in self.reasoning_cache:
            return self.reasoning_cache[cache_key]
        
        if not self.llm_enabled:
            # Fallback: use highest success rate
            best = max(success_rates.items(), key=lambda x: x[1])
            return {
                "strategy": best[0],
                "confidence": best[1],
                "reasoning": "No LLM available, using historical success rates",
                "alternative_strategies": list(success_rates.keys())
            }
        
        try:
            prompt = f"""
Error: {error}

Available strategies and success rates:
{chr(10).join([f"- {s}: {success_rates.get(s, 0):.1%} success" for s in available_strategies])}

System state: {str(system_context)[:500]}

Which strategy should we use? Explain why."""

            reasoning = await self.llm_client.generate_reasoning(
                prompt,
                context={"system_state": system_context}
            )
            
            # Parse response to extract strategy
            selected = available_strategies[0]  # Default
            for strategy in available_strategies:
                if strategy.lower() in reasoning.lower():
                    selected = strategy
                    break
            
            result = {
                "strategy": selected,
                "confidence": success_rates.get(selected, 0.5),
                "reasoning": reasoning,
                "alternative_strategies": [s for s in available_strategies if s != selected]
            }
            
            # Cache result
            self.reasoning_cache[cache_key] = result
            
            logger.info(f" Strategy selected: {selected}")
            return result
            
        except Exception as e:
            logger.error(f"Strategy selection error: {e}")
            best = max(success_rates.items(), key=lambda x: x[1])
            return {
                "strategy": best[0],
                "confidence": best[1],
                "reasoning": f"Error in LLM reasoning: {e}",
                "alternative_strategies": list(success_rates.keys())
            }
    
    async def explain_correction_decision(
        self,
        error: str,
        strategy_selected: str,
        strategy_rationale: str,
        outcome: str
    ) -> str:
        """
        Generate natural language explanation of correction decision
        
        For users, dashboards, logs
        """
        if not self.llm_enabled:
            return f"Applied {strategy_selected}: {outcome}"
        
        try:
            explanation = await self.llm_client.explain_correction(
                error, strategy_selected, outcome
            )
            
            logger.info(" Correction explanation generated")
            return explanation
            
        except Exception as e:
            logger.error(f"Explanation error: {e}")
            return f"Applied {strategy_selected}: {outcome}"
    
    async def find_error_patterns(
        self,
        recent_errors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Use LLM to identify patterns across errors
        
        Helps predict future issues
        """
        if not self.llm_enabled or len(recent_errors) < 2:
            return {
                "pattern_found": False,
                "pattern_description": "Insufficient data",
                "confidence": 0
            }
        
        try:
            pattern = await self.llm_client.identify_pattern(recent_errors)
            
            logger.info(" Error pattern identified")
            return {
                "pattern_found": True,
                "pattern_description": pattern.get("pattern_analysis", ""),
                "confidence": 0.75,  # Moderate confidence
                "error_count": pattern.get("error_count", 0)
            }
            
        except Exception as e:
            logger.error(f"Pattern detection error: {e}")
            return {
                "pattern_found": False,
                "pattern_description": str(e),
                "confidence": 0
            }
    
    async def recommend_optimizations(
        self,
        system_metrics: Dict[str, float],
        error_history: List[str],
        performance_issues: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Use LLM to recommend system optimizations
        
        Proactive improvements
        """
        if not self.llm_enabled:
            return []
        
        try:
            recommendations = await self.llm_client.recommend_optimization(
                {
                    "errors": error_history[-5:],
                    "issues": performance_issues
                },
                system_metrics
            )
            
            logger.info(" Optimization recommendations generated")
            return [{
                "recommendation": recommendations.get("recommendations", ""),
                "category": "general",
                "priority": "medium",
                "timestamp": datetime.now().isoformat()
            }]
            
        except Exception as e:
            logger.error(f"Optimization error: {e}")
            return []
    
    async def close(self):
        """Cleanup LLM resources"""
        if self.llm_client:
            await self.llm_client.close()


class AsyncLLMEnhancedOrchestrator:
    """
    Async wrapper for sync code to use LLM features
    """
    
    def __init__(self, orchestrator: LLMEnhancedOrchestrator):
        self.orchestrator = orchestrator
        self.loop = None
    
    def analyze_error(
        self,
        error_type: str,
        error_message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Sync wrapper for async error analysis"""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                self.orchestrator.analyze_error_with_reasoning(
                    error_type, error_message, context
                )
            )
        finally:
            loop.close()
    
    def select_strategy(
        self,
        error: str,
        strategies: List[str],
        rates: Dict[str, float],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Sync wrapper for async strategy selection"""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                self.orchestrator.select_correction_with_reasoning(
                    error, strategies, rates, context
                )
            )
        finally:
            loop.close()
    
    def explain_decision(
        self,
        error: str,
        strategy: str,
        rationale: str,
        outcome: str
    ) -> str:
        """Sync wrapper for async explanation"""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                self.orchestrator.explain_correction_decision(
                    error, strategy, rationale, outcome
                )
            )
        finally:
            loop.close()


__all__ = ["LLMEnhancedOrchestrator", "AsyncLLMEnhancedOrchestrator"]
