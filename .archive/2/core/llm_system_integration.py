"""
LLM System Integration
Seamlessly integrates Ollama LLM with Project Phoenix autonomous system

This module:
1. Extends CoreOrchestrator with LLM reasoning
2. Manages LLM lifecycle (initialization, health checks)
3. Provides unified interface for error analysis with LLM
4. Maintains backward compatibility (works without LLM)
5. Handles graceful degradation if Ollama unavailable
"""

import asyncio
import logging
from typing import Dict, Optional, Any, List, Tuple
from datetime import datetime

from autonomous_system.core.orchestrator import CoreOrchestrator
from autonomous_system.core.llm_reasoning import OllamaClient, OllamaConfig
from autonomous_system.core.error_detection import ErrorContext, ErrorAnalysis
from autonomous_system.core.correction_strategy import CorrectionResult


logger = logging.getLogger(__name__)


class LLMSystemIntegrator:
    """
    Integrates LLM with the complete Project Phoenix system
    Provides unified interface for all LLM-assisted operations
    """

    def __init__(self, orchestrator: CoreOrchestrator):
        """
        Initialize LLM integration with existing orchestrator
        
        Args:
            orchestrator: Reference to CoreOrchestrator instance
        """
        self.orchestrator = orchestrator
        self.llm_client = OllamaClient()
        self.llm_enabled = False
        self.llm_health = "unknown"
        self.llm_model = OllamaConfig.MODEL
        self.reasoning_cache: Dict[str, Dict[str, Any]] = {}
        self.max_cache_size = 1000
        self.init_time = None
        self.request_count = 0
        self.error_count = 0
        
        logger.info("🤖 LLM System Integrator initialized")

    async def initialize(self) -> bool:
        """
        Initialize LLM integration
        Gracefully handles if Ollama not available
        """
        try:
            logger.info("🚀 Initializing LLM integration with project...")
            self.init_time = datetime.now()
            
            # Try to connect to Ollama
            if await self.llm_client.initialize():
                self.llm_enabled = True
                self.llm_health = "healthy"
                
                # Verify model availability
                model_info = OllamaConfig.get_model_info(self.llm_model)
                logger.info(
                    f"✅ LLM Ready: {model_info['name']} "
                    f"({model_info['size']}) - {model_info['description']}"
                )
                logger.info("💰 Cost: $0 (Ollama local, zero API charges)")
                
                # Track initialization in metrics
                if hasattr(self.orchestrator, 'metrics_collector'):
                    self.orchestrator.metrics_collector.record_metric(
                        "llm_initialization_success", 1
                    )
                
                return True
            else:
                self.llm_enabled = False
                self.llm_health = "unavailable"
                logger.warning(
                    "⚠️  Ollama not available - running in rule-based mode"
                )
                logger.info(
                    "💡 To enable LLM reasoning, install Ollama: https://ollama.ai"
                )
                return True  # Still operational without LLM
                
        except Exception as e:
            logger.error(f"❌ LLM initialization error: {e}")
            self.llm_enabled = False
            self.llm_health = "error"
            self.error_count += 1
            return True  # Graceful degradation

    async def analyze_error_with_reasoning(
        self,
        error: ErrorContext,
        error_analysis: Optional[ErrorAnalysis] = None
    ) -> Dict[str, Any]:
        """
        Analyze error with LLM reasoning
        Provides intelligent root cause analysis and recommendations
        
        Args:
            error: ErrorContext from error detection
            error_analysis: Optional pre-computed error analysis
            
        Returns:
            Dict with LLM analysis, recommendations, and reasoning
        """
        if not self.llm_enabled:
            return {
                "llm_enabled": False,
                "status": "LLM not available",
                "reasoning": "Running in rule-based mode",
                "recommendations": []
            }

        try:
            self.request_count += 1
            
            # Create cache key for this error
            cache_key = f"{error.error_type}_{error.message}"
            
            # Check if we have cached reasoning
            if cache_key in self.reasoning_cache:
                logger.debug("📦 Using cached reasoning analysis")
                return self.reasoning_cache[cache_key]
            
            # Prepare context for LLM
            error_context = {
                "error_type": error.error_type.value,
                "message": error.message,
                "timestamp": error.timestamp.isoformat() if error.timestamp else None,
                "metadata": error.metadata if hasattr(error, 'metadata') else {},
                "severity": error.severity.name if hasattr(error, 'severity') else "unknown"
            }
            
            # Get LLM analysis
            logger.info(f"🧠 Analyzing with LLM: {error.error_type}")
            llm_result = await self.llm_client.analyze_error(
                error.error_type.value,
                error.message,
                error_context
            )
            
            # Enrich with additional LLM insights
            enriched_result = {
                "llm_enabled": True,
                "error_type": error.error_type.value,
                "root_cause": llm_result.get("root_cause", "Unknown"),
                "analysis": llm_result.get("analysis", ""),
                "severity": llm_result.get("severity", "medium"),
                "recommendations": llm_result.get("recommendations", []),
                "confidence": llm_result.get("confidence", 0.7),
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache result (with limit)
            if len(self.reasoning_cache) < self.max_cache_size:
                self.reasoning_cache[cache_key] = enriched_result
            
            # Track in metrics
            if hasattr(self.orchestrator, 'metrics_collector'):
                self.orchestrator.metrics_collector.record_metric(
                    "llm_error_analysis_success", 1
                )
            
            logger.info(f"✅ LLM analysis complete for {error.error_type}")
            return enriched_result
            
        except Exception as e:
            logger.error(f"❌ LLM analysis error: {e}")
            self.error_count += 1
            
            if hasattr(self.orchestrator, 'metrics_collector'):
                self.orchestrator.metrics_collector.record_metric(
                    "llm_error_analysis_failure", 1
                )
            
            # Fallback to basic analysis
            return {
                "llm_enabled": False,
                "error_type": error.error_type,
                "status": "analysis_error",
                "fallback": True,
                "recommendations": []
            }

    async def explain_correction_decision(
        self,
        error_message: str,
        selected_strategy: str,
        correction_result: Optional[CorrectionResult] = None,
        reasoning: Optional[str] = None
    ) -> str:
        """
        Generate natural language explanation for correction decision
        
        Args:
            error_message: Description of the error
            selected_strategy: Name of selected correction strategy
            correction_result: Result of the correction attempt
            reasoning: Optional reasoning about why strategy selected
            
        Returns:
            Natural language explanation of the decision
        """
        if not self.llm_enabled:
            return (
                f"Applied strategy: {selected_strategy} "
                f"(running without LLM explanations)"
            )

        try:
            explanation = await self.llm_client.explain_correction(
                error_message,
                selected_strategy,
                str(correction_result) if correction_result else "No result"
            )
            
            logger.debug(f"📝 Generated explanation: {explanation[:100]}...")
            return explanation
            
        except Exception as e:
            logger.error(f"❌ Explanation generation error: {e}")
            return f"Strategy {selected_strategy} applied"

    async def detect_error_patterns(
        self,
        recent_errors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Use LLM to detect patterns across multiple errors
        
        Args:
            recent_errors: List of recent error contexts
            
        Returns:
            Pattern analysis with detected patterns and root causes
        """
        if not self.llm_enabled or not recent_errors:
            return {
                "patterns_found": 0,
                "patterns": []
            }

        try:
            pattern_analysis = await self.llm_client.identify_pattern(
                recent_errors
            )
            
            logger.info(
                f"🔍 Detected {pattern_analysis.get('error_count', 0)} "
                f"error patterns"
            )
            
            if hasattr(self.orchestrator, 'metrics_collector'):
                self.orchestrator.metrics_collector.record_metric(
                    "llm_pattern_detection", 1
                )
            
            return pattern_analysis
            
        except Exception as e:
            logger.error(f"❌ Pattern detection error: {e}")
            return {"patterns_found": 0, "patterns": []}

    async def recommend_optimizations(
        self,
        system_state: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> List[str]:
        """
        Use LLM to recommend system optimizations
        
        Args:
            system_state: Current system configuration and state
            metrics: Current system metrics (CPU, memory, etc.)
            
        Returns:
            List of optimization recommendations
        """
        if not self.llm_enabled:
            return []

        try:
            recommendations = await self.llm_client.recommend_optimization(
                system_state,
                metrics
            )
            
            recs = recommendations.get("recommendations", "")
            if isinstance(recs, str) and recs:
                rec_list = [r.strip() for r in recs.split("\n") if r.strip()]
                logger.info(f"💡 Generated {len(rec_list)} optimization suggestions")
                return rec_list
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Optimization recommendation error: {e}")
            return []

    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status of LLM integration"""
        try:
            is_healthy = await self.llm_client.health_check() if self.llm_enabled else False
            
            uptime_seconds = 0
            if self.init_time:
                uptime_seconds = (datetime.now() - self.init_time).total_seconds()
            
            return {
                "llm_enabled": self.llm_enabled,
                "health": self.llm_health if is_healthy else "unhealthy",
                "model": self.llm_model if self.llm_enabled else "none",
                "requests": self.request_count,
                "errors": self.error_count,
                "cache_size": len(self.reasoning_cache),
                "uptime_seconds": uptime_seconds,
                "status": "operational" if self.llm_enabled else "degraded"
            }
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {
                "llm_enabled": False,
                "health": "error",
                "status": "failed"
            }

    async def shutdown(self):
        """Shutdown LLM integration"""
        try:
            await self.llm_client.close()
            logger.info("🛑 LLM integration shutdown complete")
        except Exception as e:
            logger.error(f"Error during LLM shutdown: {e}")


# Global LLM integrator instance
_global_llm_integrator: Optional[LLMSystemIntegrator] = None


def initialize_llm_integration(orchestrator: CoreOrchestrator) -> LLMSystemIntegrator:
    """
    Initialize global LLM integrator with orchestrator
    
    Args:
        orchestrator: CoreOrchestrator instance
        
    Returns:
        LLMSystemIntegrator instance
    """
    global _global_llm_integrator
    _global_llm_integrator = LLMSystemIntegrator(orchestrator)
    return _global_llm_integrator


def get_llm_integrator() -> Optional[LLMSystemIntegrator]:
    """Get the global LLM integrator instance"""
    return _global_llm_integrator


async def initialize_all_llm() -> bool:
    """Initialize all LLM components"""
    integrator = get_llm_integrator()
    if integrator:
        return await integrator.initialize()
    return False


async def shutdown_all_llm():
    """Shutdown all LLM components"""
    integrator = get_llm_integrator()
    if integrator:
        await integrator.shutdown()
