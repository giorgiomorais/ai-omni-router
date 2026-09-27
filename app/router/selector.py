from typing import Optional, List, Tuple
from app.core.config import settings, RoutingStrategy
from app.core.registry import MODEL_CATALOG, ModelProfile, TaskCategory, ProviderType

class ModelSelector:
    """Motor de decisão que escolhe o melhor modelo com base na tarefa e chaves disponíveis."""

    @classmethod
    def get_available_models(cls) -> List[ModelProfile]:
        available = []
        for profile in MODEL_CATALOG.values():
            if profile.provider == ProviderType.OLLAMA:
                available.append(profile)
            elif profile.provider == ProviderType.GEMINI and settings.GEMINI_API_KEY:
                available.append(profile)
            elif profile.provider == ProviderType.OPENAI and settings.OPENAI_API_KEY:
                available.append(profile)
            elif profile.provider == ProviderType.ANTHROPIC and settings.ANTHROPIC_API_KEY:
                available.append(profile)
            elif profile.provider == ProviderType.GROQ and settings.GROQ_API_KEY:
                available.append(profile)
            # Se for tier gratuito disponível sem chave ou com chave pública, entra na lista
            elif profile.is_free_tier_available and profile.cost_per_million_input == 0:
                available.append(profile)
        
        # Fallback de segurança se nenhuma chave de nuvem estiver cadastrada: retorna modelos locais
        if not available:
            available = [m for m in MODEL_CATALOG.values() if m.is_local]

        return available

    @classmethod
    def select_best_model(
        cls,
        category: TaskCategory,
        strategy: RoutingStrategy = RoutingStrategy.BALANCED,
        preferred_provider: Optional[str] = None
    ) -> Tuple[ModelProfile, Optional[ModelProfile]]:
        """Retorna (Modelo Escolhido, Modelo de Fallback)."""
        available = cls.get_available_models()

        if preferred_provider:
            filtered = [m for m in available if m.provider == preferred_provider]
            if filtered:
                available = filtered

        # 1. Candidatos que atendem a especialidade
        specialists = [m for m in available if category in m.specialties]
        candidates = specialists if specialists else available

        # 2. Ordenação por estratégia
        if strategy == RoutingStrategy.COST_SAVING:
            # Prioriza 100% gratuito (local ou free tier), depois menor custo
            sorted_models = sorted(
                candidates,
                key=lambda m: (
                    0 if m.is_local or m.cost_per_million_input == 0 else 1,
                    m.cost_per_million_input + m.cost_per_million_output,
                    m.average_latency_ms
                )
            )
        elif strategy == RoutingStrategy.QUALITY_FIRST:
            # Prioriza modelos especialistas de topo de linha
            sorted_models = sorted(
                candidates,
                key=lambda m: (
                    0 if not m.is_local else 1,
                    -(m.cost_per_million_input + m.cost_per_million_output)
                )
            )
        else: # BALANCED
            # Equilibra custo acessível / tier gratuito com boa latência e qualidade
            sorted_models = sorted(
                candidates,
                key=lambda m: (
                    0 if (m.is_free_tier_available or m.is_local) else 1,
                    m.average_latency_ms,
                    m.cost_per_million_input
                )
            )

        primary = sorted_models[0]
        fallback = sorted_models[1] if len(sorted_models) > 1 else None

        return primary, fallback
