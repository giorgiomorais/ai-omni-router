import time
import httpx
from typing import List, Optional
from app.adapters.base import BaseProviderAdapter, ChatMessage, CompletionResponse
from app.core.config import settings

class GeminiAdapter(BaseProviderAdapter):
    """Adaptador nativo para API REST do Google Gemini."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY

    async def generate_completion(
        self,
        model_id: str,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> CompletionResponse:
        start_time = time.time()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={self.api_key}"

        # Conversão de formato OpenAI para Gemini contents
        contents = []
        for m in messages:
            role = "user" if m.role in ["user", "system"] else "model"
            contents.append({
                "role": role,
                "parts": [{"text": m.content}]
            })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
            }
        }
        if max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        latency_ms = int((time.time() - start_time) * 1000)
        candidates = data.get("candidates", [{}])
        content = ""
        if candidates and "content" in candidates[0]:
            parts = candidates[0]["content"].get("parts", [])
            if parts:
                content = parts[0].get("text", "")

        usage = data.get("usageMetadata", {})
        tokens_in = usage.get("promptTokenCount", 0)
        tokens_out = usage.get("candidatesTokenCount", 0)

        # Gemini Flash tem free tier; se cobrado:
        cost_usd = 0.0
        if "flash" in model_id:
            cost_usd = (tokens_in * 0.075 + tokens_out * 0.30) / 1_000_000
        elif "pro" in model_id:
            cost_usd = (tokens_in * 1.25 + tokens_out * 5.00) / 1_000_000

        return CompletionResponse(
            content=content,
            model_used=model_id,
            provider="gemini",
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            cost_usd=round(cost_usd, 6),
            latency_ms=latency_ms
        )
