from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.adapters.base import ChatMessage, CompletionResponse
from app.adapters.factory import get_adapter_for_provider
from app.core.config import RoutingStrategy
from app.core.registry import TaskCategory, ModelProfile, ProviderType
from app.router.classifier import SemanticClassifier
from app.router.selector import ModelSelector

class WorkflowStep(BaseModel):
    step_id: str
    name: str
    category: TaskCategory
    instruction_prompt: str
    model_profile: ModelProfile
    result: Optional[str] = None
    cost_usd: float = 0.0
    latency_ms: int = 0

class WorkflowDAGResult(BaseModel):
    is_composite: bool
    total_steps: int
    steps: List[WorkflowStep]
    final_output: str
    total_cost_usd: float
    total_latency_ms: int

class DAGDispatcher:
    """Decompositor em Grafo Acíclico Dirigido (DAG) para requisições complexas."""

    @classmethod
    def should_decompose(cls, prompt: str) -> bool:
        """Identifica se a requisição é composta (ex: analise dados E crie código E faça relatório)."""
        prompt_lower = prompt.lower()
        complex_triggers = [
            " e depois ", " em seguida ", " passo a passo ", " e crie ",
            " analise e ", " gere o codigo e explique ", " planeje e execute "
        ]
        return any(t in prompt_lower for t in complex_triggers) and len(prompt) > 80

    @classmethod
    async def execute_dag(
        cls,
        user_prompt: str,
        strategy: RoutingStrategy = RoutingStrategy.COST_SAVING
    ) -> WorkflowDAGResult:
        """Executa um fluxo encadeado de 3 etapas com especialistas distintos: Planejamento -> Execução -> Síntese."""
        steps: List[WorkflowStep] = []
        total_cost = 0.0
        total_latency = 0

        # Etapa 1: Planejamento / Raciocínio (DeepSeek R1 ou Llama 3.2)
        p1_model, _ = ModelSelector.select_best_model(TaskCategory.REASONING, strategy)
        steps.append(WorkflowStep(
            step_id="step_1",
            name="Planejamento e Arquitetura",
            category=TaskCategory.REASONING,
            instruction_prompt=f"Planeje e estruture a melhor abordagem para atender à solicitação: '{user_prompt}'. Seja conciso.",
            model_profile=p1_model
        ))

        # Etapa 2: Execução / Código Técnico (Qwen Coder)
        p2_model, _ = ModelSelector.select_best_model(TaskCategory.CODE, strategy)
        steps.append(WorkflowStep(
            step_id="step_2",
            name="Implementação Técnica / Código",
            category=TaskCategory.CODE,
            instruction_prompt=f"Com base na solicitação original '{user_prompt}', forneça a solução prática e o código necessário.",
            model_profile=p2_model
        ))

        # Etapa 3: Revisão e Resumo Executivo (Llama 3.2 / Fast)
        p3_model, _ = ModelSelector.select_best_model(TaskCategory.FAST_FACTUAL, strategy)
        steps.append(WorkflowStep(
            step_id="step_3",
            name="Revisão e Sumário Executivo",
            category=TaskCategory.FAST_FACTUAL,
            instruction_prompt="Revise os passos anteriores e forneça um resumo claro, acionável e executivo.",
            model_profile=p3_model
        ))

        accumulated_context = f"Solicitação do Usuário: {user_prompt}\n\n"

        for step in steps:
            adapter = get_adapter_for_provider(step.model_profile.provider)
            resp = None
            try:
                resp = await adapter.generate_completion(
                    model_id=step.model_profile.id,
                    messages=[
                        ChatMessage(role="system", content="Você é um especialista analítico sênior em sua fase do pipeline."),
                        ChatMessage(role="user", content=accumulated_context + "\nSua Tarefa:\n" + step.instruction_prompt)
                    ]
                )
            except Exception as e:
                # Fallover resiliente para modelos locais garantidos do Ollama
                local_fallback_id = "qwen2.5-coder:1.5b" if step.category == TaskCategory.CODE else "llama3.2:1b"
                fb_adapter = get_adapter_for_provider(ProviderType.OLLAMA)
                resp = await fb_adapter.generate_completion(
                    model_id=local_fallback_id,
                    messages=[ChatMessage(role="user", content=accumulated_context + "\n" + step.instruction_prompt)]
                )
                resp.fallback_triggered = True

            step.result = resp.content
            step.cost_usd = resp.cost_usd
            step.latency_ms = resp.latency_ms
            total_cost += resp.cost_usd
            total_latency += resp.latency_ms

            accumulated_context += f"--- Resultado de [{step.name}] ---\n{resp.content}\n\n"

        return WorkflowDAGResult(
            is_composite=True,
            total_steps=len(steps),
            steps=steps,
            final_output=accumulated_context,
            total_cost_usd=round(total_cost, 6),
            total_latency_ms=total_latency
        )
