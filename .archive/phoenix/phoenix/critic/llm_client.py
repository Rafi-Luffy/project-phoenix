"""LLM client abstraction for multiple providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from phoenix.core.config import get_config
from phoenix.core.logging import get_logger

logger = get_logger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers - comprehensive coverage of all major models."""
    
    # Commercial Cloud Providers
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    AI21 = "ai21"
    
    # Azure & Enterprise
    AZURE_OPENAI = "azure_openai"
    AWS_BEDROCK = "aws_bedrock"
    VERTEX_AI = "vertex_ai"
    
    # High-Performance Inference
    GROQ = "groq"
    TOGETHER = "together"
    REPLICATE = "replicate"
    ANYSCALE = "anyscale"
    PERPLEXITY = "perplexity"
    
    # Open Source / Local
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"
    LLAMACPP = "llamacpp"
    VLLM = "vllm"
    
    # Hugging Face
    HUGGINGFACE = "huggingface"
    HUGGINGFACE_INFERENCE = "huggingface_inference"
    
    # Specialized
    MISTRAL = "mistral"
    DEEPINFRA = "deepinfra"
    FIREWORKS = "fireworks"


@dataclass
class LLMConfig:
    """Configuration for LLM client."""
    
    provider: LLMProvider
    model: str
    api_key: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a chat completion."""
        pass


class OpenAIClient(LLMClient):
    """OpenAI API client."""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        """Initialize OpenAI client."""
        from openai import OpenAI
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.logger = get_logger(__name__)
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a chat completion using OpenAI."""
        try:
            # Convert to proper OpenAI format
            formatted_messages = [{"role": m["role"], "content": m["content"]} for m in messages]  # type: ignore
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,  # type: ignore
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            return content if content is not None else ""
        except Exception as e:
            self.logger.error("openai_api_error", error=str(e))
            raise


class GeminiClient(LLMClient):
    """Google Gemini API client."""
    
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        """Initialize Gemini client."""
        try:
            import google.generativeai as genai  # type: ignore
            
            genai.configure(api_key=api_key)  # type: ignore
            self.model = genai.GenerativeModel(model)  # type: ignore
            self.api_key = api_key
            self.logger = get_logger(__name__)
        except ImportError:
            self.logger.warning("google_generativeai_not_installed")
            raise
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a chat completion using Gemini."""
        try:
            # Convert messages to Gemini format
            prompt = self._convert_messages(messages)
            
            # Build generation config
            gen_config = {}
            if temperature is not None:
                gen_config["temperature"] = temperature
            if max_tokens is not None:
                gen_config["max_output_tokens"] = max_tokens
            
            response = self.model.generate_content(  # type: ignore
                prompt,
                generation_config=gen_config if gen_config else None,  # type: ignore
            )
            return str(response.text) if hasattr(response, 'text') else ""
        except Exception as e:
            self.logger.error("gemini_api_error", error=str(e))
            raise
    
    def _convert_messages(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to Gemini prompt."""
        prompt_parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        return "\n\n".join(prompt_parts)


class AnthropicClient(LLMClient):
    """Anthropic Claude API client."""
    
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        """Initialize Anthropic client."""
        from anthropic import Anthropic
        
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.logger = get_logger(__name__)
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a chat completion using Claude."""
        try:
            # Extract system message if present
            system_message = None
            chat_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    chat_messages.append(msg)
            
            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens or 4096,
                "temperature": temperature,
                "messages": chat_messages,  # type: ignore
            }
            
            if system_message:
                kwargs["system"] = system_message  # type: ignore
            
            response = self.client.messages.create(**kwargs)  # type: ignore
            
            # Safely extract text content
            if hasattr(response, 'content') and len(response.content) > 0:
                first_block = response.content[0]
                if hasattr(first_block, 'text'):
                    return str(first_block.text)
            return ""
        except Exception as e:
            self.logger.error("anthropic_api_error", error=str(e))
            raise


class CohereClient(LLMClient):
    """Cohere API client."""
    
    def __init__(self, api_key: str, model: str = "command-r-plus"):
        """Initialize Cohere client."""
        try:
            import cohere
            self.client = cohere.Client(api_key=api_key)
            self.model = model
            self.logger = get_logger(__name__)
        except ImportError:
            raise ImportError("Install cohere: pip install cohere")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a chat completion using Cohere."""
        try:
            # Convert to Cohere format
            chat_history = []
            message = ""
            
            for msg in messages:
                if msg["role"] == "user":
                    message = msg["content"]
                elif msg["role"] == "assistant":
                    chat_history.append({"role": "CHATBOT", "message": msg["content"]})
                elif msg["role"] == "system":
                    # Prepend system message to user message
                    message = f"{msg['content']}\n\n{message}" if message else msg["content"]
            
            response = self.client.chat(
                model=self.model,
                message=message,
                chat_history=chat_history,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return str(response.text) if hasattr(response, 'text') else ""
        except Exception as e:
            self.logger.error("cohere_api_error", error=str(e))
            raise


class AI21Client(LLMClient):
    """AI21 Labs API client."""
    
    def __init__(self, api_key: str, model: str = "jamba-instruct"):
        """Initialize AI21 client."""
        try:
            from ai21 import AI21Client as AI21SDK
            self.client = AI21SDK(api_key=api_key)
            self.model = model
            self.logger = get_logger(__name__)
        except ImportError:
            raise ImportError("Install ai21: pip install ai21")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a chat completion using AI21."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore
                temperature=temperature,
                max_tokens=max_tokens or 4096,
            )
            return str(response.choices[0].message.content) if response.choices else ""
        except Exception as e:
            self.logger.error("ai21_api_error", error=str(e))
            raise


class GroqClient(LLMClient):
    """Groq API client (ultra-fast inference)."""
    
    def __init__(self, api_key: str, model: str = "llama-3.1-70b-versatile"):
        """Initialize Groq client."""
        try:
            from groq import Groq
            self.client = Groq(api_key=api_key)
            self.model = model
            self.logger = get_logger(__name__)
        except ImportError:
            raise ImportError("Install groq: pip install groq")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a chat completion using Groq."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            return content if content is not None else ""
        except Exception as e:
            self.logger.error("groq_api_error", error=str(e))
            raise


class OllamaClient(LLMClient):
    """Ollama local model client."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1"):
        """Initialize Ollama client."""
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.logger = get_logger(__name__)
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a chat completion using Ollama."""
        try:
            import requests
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    }
                },
                timeout=120,
            )
            response.raise_for_status()
            result = response.json()
            return str(result.get("message", {}).get("content", ""))
        except Exception as e:
            self.logger.error("ollama_api_error", error=str(e))
            raise


class TogetherClient(LLMClient):
    """Together AI API client."""
    
    def __init__(self, api_key: str, model: str = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"):
        """Initialize Together client."""
        try:
            from together import Together
            self.client = Together(api_key=api_key)
            self.model = model
            self.logger = get_logger(__name__)
        except ImportError:
            raise ImportError("Install together: pip install together")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a chat completion using Together AI."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore
                temperature=temperature,
                max_tokens=max_tokens or 4096,
            )
            content = response.choices[0].message.content
            return content if content is not None else ""
        except Exception as e:
            self.logger.error("together_api_error", error=str(e))
            raise


class MistralClient(LLMClient):
    """Mistral AI API client."""
    
    def __init__(self, api_key: str, model: str = "mistral-large-latest"):
        """Initialize Mistral client."""
        try:
            from mistralai.client import MistralClient as MistralSDK
            self.client = MistralSDK(api_key=api_key)
            self.model = model
            self.logger = get_logger(__name__)
        except ImportError:
            raise ImportError("Install mistralai: pip install mistralai")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a chat completion using Mistral."""
        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,  # type: ignore
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return str(response.choices[0].message.content) if response.choices else ""
        except Exception as e:
            self.logger.error("mistral_api_error", error=str(e))
            raise


class HuggingFaceClient(LLMClient):
    """Hugging Face Inference API client."""
    
    def __init__(self, api_key: str, model: str = "meta-llama/Meta-Llama-3-70B-Instruct"):
        """Initialize Hugging Face client."""
        try:
            from huggingface_hub import InferenceClient
            self.client = InferenceClient(token=api_key)
            self.model = model
            self.logger = get_logger(__name__)
        except ImportError:
            raise ImportError("Install huggingface_hub: pip install huggingface_hub")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a chat completion using Hugging Face."""
        try:
            response = self.client.chat_completion(
                messages=messages,  # type: ignore
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens or 4096,
            )
            content = response.choices[0].message.content
            return content if content is not None else ""
        except Exception as e:
            self.logger.error("huggingface_api_error", error=str(e))
            raise


class AzureOpenAIClient(LLMClient):
    """Azure OpenAI API client."""
    
    def __init__(self, api_key: str, endpoint: str, model: str = "gpt-4", api_version: str = "2024-02-15-preview"):
        """Initialize Azure OpenAI client."""
        try:
            from openai import AzureOpenAI
            self.client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=endpoint
            )
            self.model = model
            self.logger = get_logger(__name__)
        except ImportError:
            raise ImportError("Install openai: pip install openai")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a chat completion using Azure OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            return content if content is not None else ""
        except Exception as e:
            self.logger.error("azure_openai_api_error", error=str(e))
            raise


class ReplicateClient(LLMClient):
    """Replicate API client."""
    
    def __init__(self, api_key: str, model: str = "meta/meta-llama-3-70b-instruct"):
        """Initialize Replicate client."""
        try:
            import replicate
            self.client = replicate.Client(api_token=api_key)
            self.model = model
            self.logger = get_logger(__name__)
        except ImportError:
            raise ImportError("Install replicate: pip install replicate")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a chat completion using Replicate."""
        try:
            # Convert messages to prompt
            prompt = self._messages_to_prompt(messages)
            
            output = self.client.run(
                self.model,
                input={
                    "prompt": prompt,
                    "temperature": temperature,
                    "max_tokens": max_tokens or 4096,
                }
            )
            return "".join(str(item) for item in output) if output else ""
        except Exception as e:
            self.logger.error("replicate_api_error", error=str(e))
            raise
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert messages to a single prompt."""
        prompt_parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        return "\n\n".join(prompt_parts)


def create_llm_client(
    provider: Optional[LLMProvider] = None,
    model: Optional[str] = None,
) -> LLMClient:
    """
    Create an LLM client based on configuration.
    
    Args:
        provider: LLM provider to use (defaults to config)
        model: Model name (defaults to config)
        
    Returns:
        Initialized LLM client
    """
    config = get_config()
    
    if provider is None:
        provider = LLMProvider(config.default_llm_provider)
    
    if model is None:
        model = config.default_model
    
    # Commercial Cloud Providers
    if provider == LLMProvider.OPENAI:
        if not config.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        return OpenAIClient(config.openai_api_key, model)
    
    elif provider == LLMProvider.GEMINI:
        if not config.gemini_api_key:
            raise ValueError("Gemini API key not configured")
        return GeminiClient(config.gemini_api_key, model)
    
    elif provider == LLMProvider.ANTHROPIC:
        if not config.anthropic_api_key:
            raise ValueError("Anthropic API key not configured")
        return AnthropicClient(config.anthropic_api_key, model)
    
    elif provider == LLMProvider.COHERE:
        if not config.cohere_api_key:
            raise ValueError("Cohere API key not configured")
        return CohereClient(config.cohere_api_key, model)
    
    elif provider == LLMProvider.AI21:
        if not config.ai21_api_key:
            raise ValueError("AI21 API key not configured")
        return AI21Client(config.ai21_api_key, model)
    
    # High-Performance Inference
    elif provider == LLMProvider.GROQ:
        if not config.groq_api_key:
            raise ValueError("Groq API key not configured")
        return GroqClient(config.groq_api_key, model)
    
    elif provider == LLMProvider.TOGETHER:
        if not config.together_api_key:
            raise ValueError("Together AI API key not configured")
        return TogetherClient(config.together_api_key, model)
    
    elif provider == LLMProvider.REPLICATE:
        if not config.replicate_api_key:
            raise ValueError("Replicate API key not configured")
        return ReplicateClient(config.replicate_api_key, model)
    
    # Azure & Enterprise
    elif provider == LLMProvider.AZURE_OPENAI:
        if not config.azure_openai_api_key or not config.azure_openai_endpoint:
            raise ValueError("Azure OpenAI API key and endpoint not configured")
        return AzureOpenAIClient(
            config.azure_openai_api_key,
            config.azure_openai_endpoint,
            model,
            config.azure_openai_api_version
        )
    
    # Open Source / Local
    elif provider == LLMProvider.OLLAMA:
        return OllamaClient(config.ollama_base_url, model)
    
    elif provider == LLMProvider.LM_STUDIO:
        return OllamaClient(config.lm_studio_base_url, model)  # Uses same API
    
    # Hugging Face
    elif provider == LLMProvider.HUGGINGFACE or provider == LLMProvider.HUGGINGFACE_INFERENCE:
        if not config.huggingface_api_key:
            raise ValueError("Hugging Face API key not configured")
        return HuggingFaceClient(config.huggingface_api_key, model)
    
    # Specialized
    elif provider == LLMProvider.MISTRAL:
        if not config.mistral_api_key:
            raise ValueError("Mistral API key not configured")
        return MistralClient(config.mistral_api_key, model)
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def create_llm_client_with_fallback(
    preferred_provider: Optional[LLMProvider] = None,
    model: Optional[str] = None,
) -> LLMClient:
    """
    Create an LLM client with automatic fallback to other providers.
    
    Args:
        preferred_provider: Preferred LLM provider
        model: Model name
        
    Returns:
        Initialized LLM client (may be different provider if fallback occurs)
    """
    config = get_config()
    
    if not config.enable_llm_fallback:
        return create_llm_client(preferred_provider, model)
    
    # Try preferred provider first
    if preferred_provider:
        try:
            return create_llm_client(preferred_provider, model)
        except (ValueError, ImportError) as e:
            logger.warning(
                "llm_provider_unavailable",
                provider=preferred_provider,
                error=str(e)
            )
    
    # Try fallback providers in order
    fallback_order = config.fallback_providers
    for provider_name in fallback_order:
        try:
            provider = LLMProvider(provider_name)
            client = create_llm_client(provider, model)
            logger.info(
                "llm_fallback_success",
                fallback_provider=provider_name,
                preferred_provider=preferred_provider
            )
            return client
        except (ValueError, ImportError) as e:
            logger.warning(
                "llm_fallback_failed",
                provider=provider_name,
                error=str(e)
            )
            continue
    
    # No providers available
    raise ValueError(
        "No LLM providers available. Please configure at least one provider's API key."
    )
