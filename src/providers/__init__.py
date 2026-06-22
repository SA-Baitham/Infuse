from .base import ProviderRegistry, BaseProvider, ConfigField, ProviderMeta
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .gemini_provider import GeminiProvider
from .ollama_provider import OllamaProvider
from .openrouter_provider import OpenRouterProvider
from .nvidia_provider import NVIDIAProvider
from .opencode_provider import OpenCodeZenProvider

ProviderRegistry.register(OpenAIProvider)
ProviderRegistry.register(AnthropicProvider)
ProviderRegistry.register(GeminiProvider)
ProviderRegistry.register(OllamaProvider)
ProviderRegistry.register(OpenRouterProvider)
ProviderRegistry.register(NVIDIAProvider)
ProviderRegistry.register(OpenCodeZenProvider)

__all__ = ["ProviderRegistry", "BaseProvider", "ConfigField", "ProviderMeta"]
