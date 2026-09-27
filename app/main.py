from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from app.adapters.base import ChatMessage
from app.core.config import settings, RoutingStrategy
from app.core.registry import MODEL_CATALOG
from app.dispatcher.single_dispatcher import Dispatcher, OrchestrationResult
from app.router.classifier import SemanticClassifier
from app.router.selector import ModelSelector

app = FastAPI(
    title="AI-OmniRouter API",
    description="Orquestrador Inteligente Multi-Modelos de IA com Custo Operacional Zero",
    version="1.0.0"
)

# Modelos de requisição e resposta padrão OpenAI
class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage]
    strategy: Optional[RoutingStrategy] = RoutingStrategy.BALANCED
    preferred_provider: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None

class RoutePreviewRequest(BaseModel):
    prompt: str
    strategy: Optional[RoutingStrategy] = RoutingStrategy.BALANCED

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "models_registered": len(MODEL_CATALOG),
        "available_models": [m.id for m in ModelSelector.get_available_models()]
    }

@app.get("/v1/models")
def list_models():
    """Lista todos os modelos cadastrados no catálogo com suas matrizes de custo e habilidades."""
    return {"data": list(MODEL_CATALOG.values())}

@app.post("/v1/router/preview")
def preview_routing(req: RoutePreviewRequest):
    """Permite testar e inspecionar a classificação e o modelo escolhido SEM disparar a chamada de LLM."""
    category, confidence = SemanticClassifier.classify(req.prompt)
    primary, fallback = ModelSelector.select_best_model(
        category=category,
        strategy=req.strategy
    )
    return {
        "prompt_analyzed": req.prompt,
        "category_detected": category,
        "confidence": confidence,
        "selected_model": primary,
        "fallback_model": fallback,
        "classification_cost_usd": 0.0 # Zero custo
    }

@app.post("/v1/chat/completions")
async def chat_completion(req: ChatCompletionRequest):
    """Endpoint principal de orquestração com despacho inteligente."""
    try:
        result: OrchestrationResult = await Dispatcher.dispatch(
            messages=req.messages,
            strategy=req.strategy,
            preferred_provider=req.preferred_provider
        )
        return {
            "id": f"omni-{result.response.model_used}",
            "object": "chat.completion",
            "routing_telemetry": {
                "category_detected": result.category_detected,
                "confidence": result.confidence,
                "model_selected": result.primary_model.id,
                "provider": result.primary_model.provider,
                "fallback_triggered": result.response.fallback_triggered,
                "cost_usd": result.response.cost_usd,
                "latency_ms": result.response.latency_ms
            },
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": result.response.content
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": result.response.tokens_input,
                "completion_tokens": result.response.tokens_output,
                "total_tokens": result.response.tokens_input + result.response.tokens_output
            }
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
