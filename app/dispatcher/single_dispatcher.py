import logging
from typing import List, Optional
from pydantic import BaseModel

from app.adapters.base import ChatMessage, CompletionResponse
from app.adapters.factory import get_adapter_for_provider
from app.core.config import settings, RoutingStrategy
from app.core.registry import TaskCategory, ModelProfile
from app.router.classifier import SemanticClassifier
from app.router.selector import ModelSelector

logger = logging.getLogger("ai_omni_router")

class OrchestrationResult(BaseModel):
    category_detected: TaskCategory
    confidence: float
    primary_model: ModelProfile
    fallback_model: Optional[ModelProfile] = None
    response: CompletionResponse

class Dispatcher:
    """Orquestrador principal responsável por receber o prompt, rotear e executar com failover."""

    @classmethod
    async def dispatch(
        cls,
        messages: List[ChatMessage],
        strategy: RoutingStrategy = RoutingStrategy.BALANCED,
        preferred_provider: Optional[str] = None
    ) -> OrchestrationResult:
        # 1. Pega a última mensagem do usuário para classificar a intenção
        user_prompt = ""
        for m in reversed(messages):
            if m.role == "user":
                user_prompt = m.content
                break

        # 2. Classificação semântica com custo ZERO de tokens
        category, confidence = SemanticClassifier.classify(user_prompt)

        # 3. Seleção do melhor modelo especialista e fallback
        primary_model, fallback_model = ModelSelector.select_best_model(
            category=category,
            strategy=strategy,
            preferred_provider=preferred_provider
        )

        logger.info(f"Tarefa: {category.value} | Confiança: {confidence:.2f} | Roteando para: {primary_model.id} ({primary_model.provider})")

        # 4. Injeção de Prompt Especialista e Anonimização LGPD Shield
        from app.core.data_masker import DataMasker
        from app.core.expert_prompts import get_expert_prompt_for_category

        expert_prompt = get_expert_prompt_for_category(category)
        
        # Prepara mensagens com prompt de sistema especialista e máscara de dados
        processed_messages: List[ChatMessage] = []
        reverse_maps: List[dict] = []
        
        # Adiciona prompt de sistema especialista se não existir
        has_system = any(m.role == "system" for m in messages)
        if not has_system:
            processed_messages.append(ChatMessage(role="system", content=expert_prompt))

        for m in messages:
            if m.role == "user" and not primary_model.is_local:
                masked_content, rev_map = DataMasker.mask(m.content)
                reverse_maps.append(rev_map)
                processed_messages.append(ChatMessage(role=m.role, content=masked_content))
            else:
                processed_messages.append(m)

        # 5. Tentativa de execução no modelo primário
        adapter = get_adapter_for_provider(primary_model.provider)
        try:
            completion = await adapter.generate_completion(
                model_id=primary_model.id,
                messages=processed_messages
            )
            # Desmascara resposta se aplicável
            for r_map in reverse_maps:
                completion.content = DataMasker.unmask(completion.content, r_map)

            return OrchestrationResult(
                category_detected=category,
                confidence=confidence,
                primary_model=primary_model,
                fallback_model=fallback_model,
                response=completion
            )
        except Exception as exc:
            logger.warning(f"Falha no modelo primário {primary_model.id}: {str(exc)}. Acionando failover...")
            
            # Se houver fallback configurado, executa o circuito de resiliência
            if fallback_model:
                fb_adapter = get_adapter_for_provider(fallback_model.provider)
                fallback_completion = await fb_adapter.generate_completion(
                    model_id=fallback_model.id,
                    messages=messages
                )
                fallback_completion.fallback_triggered = True
                return OrchestrationResult(
                    category_detected=category,
                    confidence=confidence,
                    primary_model=primary_model,
                    fallback_model=fallback_model,
                    response=fallback_completion
                )
            raise exc
