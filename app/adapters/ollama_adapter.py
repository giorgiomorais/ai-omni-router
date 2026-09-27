import time
import httpx
from typing import List, Optional
from app.adapters.base import BaseProviderAdapter, ChatMessage, CompletionResponse
from app.core.config import settings

class OllamaAdapter(BaseProviderAdapter):
    """Adaptador para modelos locais rodando no Ollama (Custo R$ 0,00)."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")

    async def generate_completion(
        self,
        model_id: str,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> CompletionResponse:
        start_time = time.time()
        url = f"{self.base_url}/api/chat"

        payload = {
            "model": model_id,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        latency_ms = int((time.time() - start_time) * 1000)
        content = data.get("message", {}).get("content", "")
        tokens_in = data.get("prompt_eval_count", 0)
        tokens_out = data.get("eval_count", 0)

        return CompletionResponse(
            content=content,
            model_used=model_id,
            provider="ollama",
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            cost_usd=0.0, # 100% gratuito
            latency_ms=latency_ms
        )
