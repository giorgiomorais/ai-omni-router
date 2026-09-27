import time
import httpx
from typing import List, Optional
from app.adapters.base import BaseProviderAdapter, ChatMessage, CompletionResponse
from app.core.config import settings

class OpenAICompatibleAdapter(BaseProviderAdapter):
    """Adaptador universal para endpoints compatíveis com a API da OpenAI (OpenAI, Groq, OpenRouter)."""

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1", provider_name: str = "openai"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.provider_name = provider_name

    async def generate_completion(
        self,
        model_id: str,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> CompletionResponse:
        start_time = time.time()
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model_id,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        latency_ms = int((time.time() - start_time) * 1000)
        choice = data.get("choices", [{}])[0]
        content = choice.get("message", {}).get("content", "")
        usage = data.get("usage", {})
        tokens_in = usage.get("prompt_tokens", 0)
        tokens_out = usage.get("completion_tokens", 0)

        # Custo aproximado baseado na tabela
        cost_usd = 0.0
        if "gpt-4o-mini" in model_id:
            cost_usd = (tokens_in * 0.15 + tokens_out * 0.60) / 1_000_000
        elif "gpt-4o" in model_id:
            cost_usd = (tokens_in * 2.50 + tokens_out * 10.00) / 1_000_000

        return CompletionResponse(
            content=content,
            model_used=model_id,
            provider=self.provider_name,
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            cost_usd=round(cost_usd, 6),
            latency_ms=latency_ms
        )
