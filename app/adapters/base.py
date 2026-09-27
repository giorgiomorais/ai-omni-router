from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: str # "system" | "user" | "assistant"
    content: str

class CompletionResponse(BaseModel):
    content: str
    model_used: str
    provider: str
    tokens_input: int
    tokens_output: int
    cost_usd: float
    latency_ms: int
    fallback_triggered: bool = False

class BaseProviderAdapter(ABC):
    """Contrato abstrato para adaptadores de modelos."""

    @abstractmethod
    async def generate_completion(
        self,
        model_id: str,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> CompletionResponse:
        pass
