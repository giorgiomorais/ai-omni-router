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
from fastapi.responses import FileResponse
import os
from app.dispatcher.graph_dispatcher import DAGDispatcher, WorkflowDAGResult

class DAGRequest(BaseModel):
    prompt: str
    strategy: Optional[RoutingStrategy] = RoutingStrategy.COST_SAVING

@app.get("/")
def serve_ui():
    """Entrega a interface visual de chat do AI-OmniRouter."""
    ui_path = os.path.join(os.path.dirname(__file__), "ui", "index.html")
    return FileResponse(ui_path)

from app.analytics.duckdb_engine import DuckDBEngine
import pandas as pd

class AnalyticsQueryRequest(BaseModel):
    sql: str

@app.post("/v1/analytics/query")
def execute_analytics_sql(req: AnalyticsQueryRequest):
    """Executa queries analíticas SQL em memória com DuckDB a custo zero."""
    try:
        return DuckDBEngine.execute_query(req.sql)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.post("/v1/analytics/init-sample-data")
def init_sample_commercial_data():
    """Carrega dataset de exemplo de vendas comerciais no DuckDB em memória."""
    sample_data = {
        "id_pedido": [1001, 1002, 1003, 1004, 1005],
        "cliente": ["Tech Corp", "Varejo Brasil", "Alfa Log", "Beta Distribuidora", "Gama Retail"],
        "segmento": ["Enterprise", "SMB", "Logística", "SMB", "Enterprise"],
        "valor_bruto": [15000.0, 3200.0, 8900.0, 1200.0, 45000.0],
        "impostos": [2475.0, 528.0, 1468.5, 198.0, 7425.0],
        "custo_produtos": [6000.0, 1500.0, 3800.0, 600.0, 18000.0],
        "status": ["Faturado", "Faturado", "Cancelado", "Faturado", "Faturado"]
    }
    df = pd.DataFrame(sample_data)
    info = DuckDBEngine.load_dataframe(df, "fato_vendas")
    return {"message": "Tabela fato_vendas carregada com sucesso!", "details": info}

@app.post("/v1/workflow/dag")
async def execute_workflow_dag(req: DAGRequest):
    """Executa decomposição multi-agente em etapas especializadas."""
    try:
        dag_result: WorkflowDAGResult = await DAGDispatcher.execute_dag(
            user_prompt=req.prompt,
            strategy=req.strategy
        )
        return dag_result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

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
