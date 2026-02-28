"""
Free LLM Integration using Ollama
Zero-cost, open-source reasoning engine for autonomous self-healing

This module integrates Mistral-7B via Ollama for:
- Root cause analysis
- Decision explanation
- Complex reasoning
- Client-specific learning
- No API costs, no setup required
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import aiohttp
import subprocess
import os
import platform

logger = logging.getLogger(__name__)


class OllamaConfig:
    """Configuration for Ollama integration"""
    
    # Ollama server endpoint
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
    # Model selection (all free, no API costs)
    # Options: mistral, llama2, neural-chat, zephyr, dolphin-mixtral
    MODEL = os.getenv("OLLAMA_MODEL", "mistral")
    
    # Model parameters for minimal resource usage
    NUM_PREDICT = 500  # Max tokens (keep responses brief)
    TEMPERATURE = 0.7  # Balanced creativity vs consistency
    TOP_P = 0.9  # Nucleus sampling
    TOP_K = 40  # Diversity
    
    # Request timeout
    REQUEST_TIMEOUT = 60  # seconds
    
    @staticmethod
    def get_model_info(model: str) -> Dict[str, Any]:
        """Get info about available free models"""
        models = {
            "mistral": {
                "name": "Mistral 7B",
                "size": "4.1GB",
                "speed": "Fast",
                "quality": "Excellent",
                "recommended": True,
                "description": "Fast, accurate, best for reasoning"
            },
            "llama2": {
                "name": "LLaMA 2 7B",
                "size": "3.8GB",
                "speed": "Fast",
                "quality": "Excellent",
                "description": "Well-trained, great reasoning"
            },
            "neural-chat": {
                "name": "Neural Chat 7B",
                "size": "4.1GB",
                "speed": "Fast",
                "quality": "Good",
                "description": "Specialized for conversations"
            },
            "zephyr": {
                "name": "Zephyr 7B",
                "size": "4.2GB",
                "speed": "Very Fast",
                "quality": "Excellent",
                "description": "Optimized, lightweight, fastest"
            }
        }
        return models.get(model, models["mistral"])


class OllamaClient:
    """Client for interacting with Ollama local LLM"""
    
    def __init__(self, host: str = None, model: str = None):
        """
        Initialize Ollama client
        
        Args:
            host: Ollama server host (default: localhost:11434)
            model: Model name (default: mistral)
        """
        self.host = host or OllamaConfig.OLLAMA_HOST
        self.model = model or OllamaConfig.MODEL
        self.session = None
        self.available = False
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> bool:
        """
        Initialize connection and check Ollama availability
        
        Returns:
            True if Ollama is available and ready
        """
        try:
            self.session = aiohttp.ClientSession()
            
            # Check if Ollama is running
            async with self.session.get(
                f"{self.host}/api/tags",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    self.available = True
                    self.logger.info(f" Ollama connected at {self.host}")
                    
                    # List available models
                    models = await resp.json()
                    self.logger.info(f"Available models: {models}")
                    return True
                    
        except Exception as e:
            self.logger.warning(f" Ollama not available: {e}")
            self.available = False
            return False
    
    async def pull_model(self) -> bool:
        """
        Download model if not already present
        
        Returns:
            True if model is available
        """
        if not self.session:
            await self.initialize()
        
        try:
            self.logger.info(f" Downloading {self.model} model...")
            async with self.session.post(
                f"{self.host}/api/pull",
                json={"name": self.model},
                timeout=aiohttp.ClientTimeout(total=600)  # 10 min timeout
            ) as resp:
                if resp.status == 200:
                    self.logger.info(f" Model {self.model} ready")
                    return True
        except Exception as e:
            self.logger.error(f" Failed to pull model: {e}")
        
        return False
    
    async def health_check(self) -> bool:
        """
        Check health of Ollama service
        
        Returns:
            True if Ollama is healthy and responsive
        """
        if not self.available:
            return False
        
        try:
            async with self.session.get(
                f"{self.host}/api/tags",
                timeout=aiohttp.ClientTimeout(total=2)
            ) as resp:
                return resp.status == 200
        except Exception as e:
            self.logger.debug(f"Health check failed: {e}")
            return False
    
    async def generate_reasoning(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate reasoning using local LLM
        
        Args:
            prompt: Question/prompt for the model
            context: Additional context information
            
        Returns:
            Generated reasoning text
        """
        if not self.available:
            self.logger.warning("Ollama not available, returning placeholder")
            return "[Reasoning would go here]"
        
        try:
            # Build context-aware prompt
            full_prompt = self._build_prompt(prompt, context)
            
            async with self.session.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": OllamaConfig.TEMPERATURE,
                        "top_p": OllamaConfig.TOP_P,
                        "top_k": OllamaConfig.TOP_K,
                        "num_predict": OllamaConfig.NUM_PREDICT,
                    }
                },
                timeout=aiohttp.ClientTimeout(total=OllamaConfig.REQUEST_TIMEOUT)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    response = data.get("response", "").strip()
                    self.logger.info(f" Generated reasoning ({len(response)} chars)")
                    return response
                    
        except asyncio.TimeoutError:
            self.logger.error("⏱ LLM request timeout")
            return "[Reasoning generation timed out]"
        except Exception as e:
            self.logger.error(f" LLM error: {e}")
            return "[Error generating reasoning]"
    
    async def analyze_error(
        self,
        error_type: str,
        error_message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze error using LLM for root cause
        
        Args:
            error_type: Type of error
            error_message: Error message
            context: System context (logs, metrics, etc.)
            
        Returns:
            Analysis with root cause and recommendations
        """
        prompt = f"""
Analyze this infrastructure error:

Error Type: {error_type}
Error Message: {error_message}

System Context:
{json.dumps(context, indent=2)}

Provide:
1. Root cause analysis (1-2 sentences)
2. Why this happened
3. Best fix strategy
4. Prevention for future

Be concise and technical."""

        response = await self.generate_reasoning(prompt)
        
        return {
            "error_type": error_type,
            "analysis": response,
            "timestamp": datetime.now().isoformat(),
            "model": self.model
        }
    
    async def explain_correction(
        self,
        error: str,
        correction_strategy: str,
        outcome: str
    ) -> str:
        """
        Explain why a correction was chosen and its outcome
        
        Args:
            error: The error that occurred
            correction_strategy: Strategy used to fix it
            outcome: Result of the correction
            
        Returns:
            Natural language explanation
        """
        prompt = f"""
Explain this infrastructure correction:

Problem: {error}
Solution Applied: {correction_strategy}
Outcome: {outcome}

In 2-3 sentences, explain:
- Why this solution was appropriate
- What it fixed
- Expected impact

Be clear for technical audience."""

        return await self.generate_reasoning(prompt)
    
    async def identify_pattern(
        self,
        errors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Identify patterns across multiple errors
        
        Args:
            errors: List of error events
            
        Returns:
            Pattern analysis and insights
        """
        error_summary = json.dumps(errors[:5], indent=2)  # Last 5 errors
        
        prompt = f"""
Analyze these recurring errors:

{error_summary}

Identify:
1. Common pattern or root cause
2. Trigger conditions
3. Preventive measures

Format as bullet points."""

        response = await self.generate_reasoning(prompt)
        
        return {
            "error_count": len(errors),
            "pattern_analysis": response,
            "identified_at": datetime.now().isoformat()
        }
    
    async def recommend_optimization(
        self,
        system_state: Dict[str, Any],
        performance_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Recommend system optimizations based on state and metrics
        
        Args:
            system_state: Current system state
            performance_metrics: Performance metrics
            
        Returns:
            Optimization recommendations
        """
        prompt = f"""
System Performance Analysis:

State:
{json.dumps(system_state, indent=2)[:500]}

Metrics:
{json.dumps(performance_metrics, indent=2)}

Recommend 2-3 optimizations:
1. Priority optimization
2. Secondary optimization
3. Long-term improvement

Be specific and actionable."""

        response = await self.generate_reasoning(prompt)
        
        return {
            "recommendations": response,
            "timestamp": datetime.now().isoformat()
        }
    
    def _build_prompt(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Build context-aware prompt"""
        if not context:
            return prompt
        
        context_str = json.dumps(context, indent=2)[:1000]  # Limit context
        return f"""You are an expert infrastructure and autonomous system engineer.

Context:
{context_str}

Request:
{prompt}

Response:"""
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()


class FreeOllamaSetup:
    """Setup helper for Ollama installation"""
    
    @staticmethod
    async def check_ollama_installed() -> bool:
        """Check if Ollama is installed"""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def get_install_command() -> str:
        """Get install command for current OS"""
        system = platform.system()
        
        if system == "Darwin":  # macOS
            return """
# Install Ollama on macOS:
curl -fsSL https://ollama.ai/install.sh | sh

# Or download from: https://ollama.ai/download/mac

# Then start Ollama:
ollama serve
"""
        elif system == "Linux":
            return """
# Install Ollama on Linux:
curl -fsSL https://ollama.ai/install.sh | sh

# Or use package manager:
# Ubuntu: sudo apt-get install ollama
# Fedora: sudo dnf install ollama

# Then start:
ollama serve
"""
        elif system == "Windows":
            return """
# Install Ollama on Windows:
# Download from: https://ollama.ai/download/windows

# Or use Chocolatey:
choco install ollama

# Then start Ollama from Start menu
"""
        else:
            return "Visit https://ollama.ai/download"
    
    @staticmethod
    async def setup_for_deployment() -> str:
        """Get setup instructions for Oracle Cloud deployment"""
        return """
# For Oracle Cloud Always Free Deployment:

# 1. SSH into instance
ssh -i ~/.ssh/phoenix_oracle ubuntu@<instance-ip>

# 2. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 3. Start Ollama (background)
nohup ollama serve &

# 4. Download model (one time)
ollama pull mistral

# 5. Verify running
curl http://localhost:11434/api/tags

# Done! Model will be available at http://localhost:11434
"""


# Export main class
__all__ = ["OllamaClient", "OllamaConfig", "FreeOllamaSetup"]
