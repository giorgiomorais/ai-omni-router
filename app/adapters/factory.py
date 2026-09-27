from typing import Dict
from app.adapters.base import BaseProviderAdapter
from app.adapters.ollama_adapter import OllamaAdapter
from app.adapters.openai_adapter import OpenAICompatibleAdapter
from app.adapters.gemini_adapter import GeminiAdapter
from app.core.config import settings
from app.core.registry import ProviderType

ADAPTER_POOL: Dict[ProviderType, BaseProviderAdapter] = {
    ProviderType.OLLAMA: OllamaAdapter(),
}

def get_adapter_for_provider(provider: ProviderType) -> BaseProviderAdapter:
    if provider == ProviderType.OLLAMA:
        return ADAPTER_POOL[ProviderType.OLLAMA]

    if provider == ProviderType.GEMINI:
        return GeminiAdapter()

    if provider == ProviderType.OPENAI:
        return OpenAICompatibleAdapter(
            api_key=settings.OPENAI_API_KEY or "",
            base_url="https://api.openai.com/v1",
            provider_name="openai"
        )

    if provider == ProviderType.GROQ:
        return OpenAICompatibleAdapter(
            api_key=settings.GROQ_API_KEY or "",
            base_url="https://api.groq.com/openai/v1",
            provider_name="groq"
        )

    # Fallback padrão
    return ADAPTER_POOL[ProviderType.OLLAMA]
