"""
Extended LLM Provider Integration

Adds support for additional LLM providers:
- Mistral AI
- Perplexity AI
- Together AI
- Replicate
- Local LLM endpoints
- Custom model endpoints
"""

import aiohttp
import asyncio
from typing import Dict, Any, List, Optional, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import json
from abc import ABC, abstractmethod


class ProviderType(Enum):
    """Supported LLM providers"""
    MISTRAL = "mistral"
    PERPLEXITY = "perplexity"
    TOGETHER = "together"
    REPLICATE = "replicate"
    LOCAL = "local"
    CUSTOM = "custom"


@dataclass
class ProviderConfig:
    """Configuration for LLM provider"""
    provider_type: ProviderType
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = ""
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 30
    retry_count: int = 3
    custom_headers: Optional[Dict[str, str]] = None


class ExtendedLLMProvider(ABC):
    """Base class for extended LLM providers"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self._costs = {
            "input_tokens": 0.0,
            "output_tokens": 0.0,
            "total_cost": 0.0
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate completion for prompt"""
        pass
    
    @abstractmethod
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream completion for prompt"""
        pass
    
    @abstractmethod
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost of request"""
        pass


class MistralAIProvider(ExtendedLLMProvider):
    """Mistral AI provider integration"""
    
    BASE_URL = "https://api.mistral.ai/v1"
    
    PRICING = {
        "mistral-small": {"input": 0.14, "output": 0.42},  # per 1M tokens
        "mistral-medium": {"input": 0.81, "output": 2.43},
        "mistral-large": {"input": 2.7, "output": 8.1},
    }
    
    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate completion using Mistral"""
        url = f"{self.BASE_URL}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "response_format": {"type": "text"}
        }
        
        async with self.session.post(url, json=payload, headers=headers, timeout=self.config.timeout) as resp:
            if resp.status != 200:
                raise Exception(f"Mistral API error: {resp.status}")
            data = await resp.json()
            
            completion = data["choices"][0]["message"]["content"]
            tokens = data["usage"]
            cost = self.calculate_cost(tokens["prompt_tokens"], tokens["completion_tokens"])
            
            return completion
    
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream completion from Mistral"""
        url = f"{self.BASE_URL}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": True
        }
        
        async with self.session.post(url, json=payload, headers=headers, timeout=self.config.timeout) as resp:
            if resp.status != 200:
                raise Exception(f"Mistral API error: {resp.status}")
            
            async for line in resp.content:
                if line:
                    line = line.decode('utf-8').strip()
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        if "choices" in data and data["choices"]:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for Mistral request"""
        pricing = self.PRICING.get(self.config.model, self.PRICING["mistral-small"])
        cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
        self._costs["total_cost"] += cost
        return cost


class PerplexityAIProvider(ExtendedLLMProvider):
    """Perplexity AI provider integration"""
    
    BASE_URL = "https://api.perplexity.ai"
    
    PRICING = {
        "pplx-7b-online": {"input": 0.02, "output": 0.02},
        "pplx-70b-online": {"input": 0.07, "output": 0.07},
        "llama-2-70b-chat": {"input": 0.02, "output": 0.02},
    }
    
    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate completion using Perplexity"""
        url = f"{self.BASE_URL}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        
        async with self.session.post(url, json=payload, headers=headers, timeout=self.config.timeout) as resp:
            if resp.status != 200:
                raise Exception(f"Perplexity API error: {resp.status}")
            data = await resp.json()
            
            completion = data["choices"][0]["message"]["content"]
            tokens = data["usage"]
            cost = self.calculate_cost(tokens["prompt_tokens"], tokens["completion_tokens"])
            
            return completion
    
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream completion from Perplexity"""
        url = f"{self.BASE_URL}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": True
        }
        
        async with self.session.post(url, json=payload, headers=headers, timeout=self.config.timeout) as resp:
            if resp.status != 200:
                raise Exception(f"Perplexity API error: {resp.status}")
            
            async for line in resp.content:
                if line:
                    line = line.decode('utf-8').strip()
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        if "choices" in data and data["choices"]:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for Perplexity request"""
        pricing = self.PRICING.get(self.config.model, self.PRICING["pplx-7b-online"])
        cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
        self._costs["total_cost"] += cost
        return cost


class TogetherAIProvider(ExtendedLLMProvider):
    """Together AI provider integration"""
    
    BASE_URL = "https://api.together.xyz/v1"
    
    PRICING = {
        "meta-llama/Llama-2-70b-chat-hf": {"input": 0.875, "output": 0.875},
        "mistralai/Mistral-7B-Instruct-v0.2": {"input": 0.1, "output": 0.1},
        "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO": {"input": 0.6, "output": 0.6},
    }
    
    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate completion using Together AI"""
        url = f"{self.BASE_URL}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        
        async with self.session.post(url, json=payload, headers=headers, timeout=self.config.timeout) as resp:
            if resp.status != 200:
                raise Exception(f"Together AI error: {resp.status}")
            data = await resp.json()
            
            completion = data["choices"][0]["message"]["content"]
            tokens = data["usage"]
            cost = self.calculate_cost(tokens["prompt_tokens"], tokens["completion_tokens"])
            
            return completion
    
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream completion from Together AI"""
        url = f"{self.BASE_URL}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": True
        }
        
        async with self.session.post(url, json=payload, headers=headers, timeout=self.config.timeout) as resp:
            if resp.status != 200:
                raise Exception(f"Together AI error: {resp.status}")
            
            async for line in resp.content:
                if line:
                    line = line.decode('utf-8').strip()
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            if "choices" in data and data["choices"]:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for Together AI request"""
        pricing = self.PRICING.get(self.config.model, {"input": 0.1, "output": 0.1})
        cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
        self._costs["total_cost"] += cost
        return cost


class ReplicateProvider(ExtendedLLMProvider):
    """Replicate provider integration for open-source models"""
    
    BASE_URL = "https://api.replicate.com/v1"
    
    PRICING = {
        "meta/llama-2-70b-chat": {"input": 0.65, "output": 1.95},
        "mistralai/mistral-7b-instruct-v0.2": {"input": 0.05, "output": 0.15},
    }
    
    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate completion using Replicate"""
        url = f"{self.BASE_URL}/predictions"
        
        headers = {
            "Authorization": f"Token {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "version": self.config.model,
            "input": {"prompt": prompt}
        }
        
        async with self.session.post(url, json=payload, headers=headers, timeout=self.config.timeout) as resp:
            if resp.status not in [201, 200]:
                raise Exception(f"Replicate error: {resp.status}")
            data = await resp.json()
            
            # Poll for completion
            prediction_url = data["urls"]["get"]
            while True:
                async with self.session.get(prediction_url, headers=headers) as poll_resp:
                    poll_data = await poll_resp.json()
                    if poll_data["status"] == "succeeded":
                        output = "".join(poll_data["output"]) if isinstance(poll_data["output"], list) else poll_data["output"]
                        return output
                    elif poll_data["status"] == "failed":
                        raise Exception(f"Replicate prediction failed: {poll_data.get('error')}")
                    await asyncio.sleep(1)
    
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream completion from Replicate"""
        url = f"{self.BASE_URL}/predictions"
        
        headers = {
            "Authorization": f"Token {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "version": self.config.model,
            "input": {"prompt": prompt},
            "stream": True
        }
        
        async with self.session.post(url, json=payload, headers=headers, timeout=self.config.timeout) as resp:
            if resp.status not in [201, 200]:
                raise Exception(f"Replicate error: {resp.status}")
            
            async for line in resp.content:
                if line:
                    line = line.decode('utf-8').strip()
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            if "output" in data:
                                yield data["output"]
                        except json.JSONDecodeError:
                            continue
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for Replicate request"""
        pricing = self.PRICING.get(self.config.model, {"input": 0.1, "output": 0.3})
        cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
        self._costs["total_cost"] += cost
        return cost


class LocalLLMProvider(ExtendedLLMProvider):
    """Local LLM provider (Ollama, vLLM, etc.)"""
    
    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate completion from local LLM"""
        url = f"{self.config.base_url}/v1/chat/completions"
        
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        
        async with self.session.post(url, json=payload, headers=headers, timeout=self.config.timeout) as resp:
            if resp.status != 200:
                raise Exception(f"Local LLM error: {resp.status}")
            data = await resp.json()
            
            completion = data["choices"][0]["message"]["content"]
            return completion
    
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream completion from local LLM"""
        url = f"{self.config.base_url}/v1/chat/completions"
        
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": True
        }
        
        async with self.session.post(url, json=payload, headers=headers, timeout=self.config.timeout) as resp:
            if resp.status != 200:
                raise Exception(f"Local LLM error: {resp.status}")
            
            async for line in resp.content:
                if line:
                    line = line.decode('utf-8').strip()
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            if "choices" in data and data["choices"]:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Local models have no cost"""
        return 0.0


class CustomEndpointProvider(ExtendedLLMProvider):
    """Custom LLM endpoint provider"""
    
    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate completion from custom endpoint"""
        headers = {
            "Content-Type": "application/json",
            **(self.config.custom_headers or {})
        }
        
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        
        payload = {
            "prompt": prompt,
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            **kwargs
        }
        
        async with self.session.post(self.config.base_url, json=payload, headers=headers, timeout=self.config.timeout) as resp:
            if resp.status != 200:
                raise Exception(f"Custom endpoint error: {resp.status}")
            data = await resp.json()
            
            return data.get("result") or data.get("output") or data.get("text") or str(data)
    
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream completion from custom endpoint"""
        headers = {
            "Content-Type": "application/json",
            **(self.config.custom_headers or {})
        }
        
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        
        payload = {
            "prompt": prompt,
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": True,
            **kwargs
        }
        
        async with self.session.post(self.config.base_url, json=payload, headers=headers, timeout=self.config.timeout) as resp:
            if resp.status != 200:
                raise Exception(f"Custom endpoint error: {resp.status}")
            
            async for line in resp.content:
                if line:
                    yield line.decode('utf-8')
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Custom endpoints require custom pricing"""
        return 0.0


class ExtendedLLMProviderFactory:
    """Factory for creating extended LLM providers"""
    
    PROVIDERS = {
        ProviderType.MISTRAL: MistralAIProvider,
        ProviderType.PERPLEXITY: PerplexityAIProvider,
        ProviderType.TOGETHER: TogetherAIProvider,
        ProviderType.REPLICATE: ReplicateProvider,
        ProviderType.LOCAL: LocalLLMProvider,
        ProviderType.CUSTOM: CustomEndpointProvider,
    }
    
    @staticmethod
    def create(config: ProviderConfig) -> ExtendedLLMProvider:
        """Create provider instance"""
        provider_class = ExtendedLLMProviderFactory.PROVIDERS.get(config.provider_type)
        if not provider_class:
            raise ValueError(f"Unknown provider: {config.provider_type}")
        return provider_class(config)
    
    @staticmethod
    def supports(provider_type: ProviderType) -> bool:
        """Check if provider is supported"""
        return provider_type in ExtendedLLMProviderFactory.PROVIDERS


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test():
        # Mistral
        config = ProviderConfig(
            provider_type=ProviderType.MISTRAL,
            api_key="your-key",
            model="mistral-large"
        )
        
        async with ExtendedLLMProviderFactory.create(config) as provider:
            result = await provider.complete("What is AI?")
            print(result)
    
    asyncio.run(test())
