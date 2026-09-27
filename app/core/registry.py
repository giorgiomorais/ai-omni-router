from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel

class TaskCategory(str, Enum):
    CODE = "code"
    REASONING = "reasoning"
    FAST_FACTUAL = "fast_factual"
    LONG_CONTEXT = "long_context"
    CREATIVE = "creative"
    DATA_EXTRACTION = "data_extraction"

class ProviderType(str, Enum):
    OLLAMA = "ollama"
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"

class ModelProfile(BaseModel):
    id: str
    provider: ProviderType
    display_name: str
    cost_per_million_input: float    # USD (0.0 para local/free tiers)
    cost_per_million_output: float   # USD
    context_window: int              # Em tokens
    specialties: List[TaskCategory]
    is_local: bool = False
    is_free_tier_available: bool = False
    average_latency_ms: int = 1000

# Catálogo Unificado de Modelos
MODEL_CATALOG: Dict[str, ModelProfile] = {
    # --- MODELOS LOCAIS (100% CUSTO ZERO) ---
    "ollama/qwen2.5-coder:1.5b": ModelProfile(
        id="qwen2.5-coder:1.5b",
        provider=ProviderType.OLLAMA,
        display_name="Qwen 2.5 Coder 1.5B (Local)",
        cost_per_million_input=0.0,
        cost_per_million_output=0.0,
        context_window=32768,
        specialties=[TaskCategory.CODE],
        is_local=True,
        average_latency_ms=800
    ),
    "ollama/llama3.2:1b": ModelProfile(
        id="llama3.2:1b",
        provider=ProviderType.OLLAMA,
        display_name="Llama 3.2 1B (Local)",
        cost_per_million_input=0.0,
        cost_per_million_output=0.0,
        context_window=131072,
        specialties=[TaskCategory.FAST_FACTUAL, TaskCategory.DATA_EXTRACTION],
        is_local=True,
        average_latency_ms=500
    ),
    "ollama/deepseek-r1:1.5b": ModelProfile(
        id="deepseek-r1:1.5b",
        provider=ProviderType.OLLAMA,
        display_name="DeepSeek R1 1.5B (Local Reasoning)",
        cost_per_million_input=0.0,
        cost_per_million_output=0.0,
        context_window=32768,
        specialties=[TaskCategory.REASONING],
        is_local=True,
        average_latency_ms=1200
    ),

    # --- GOOGLE GEMINI (Tier Gratuito / Alta Janela) ---
    "gemini/gemini-2.5-flash": ModelProfile(
        id="gemini-2.5-flash",
        provider=ProviderType.GEMINI,
        display_name="Google Gemini 2.5 Flash",
        cost_per_million_input=0.075,
        cost_per_million_output=0.30,
        context_window=1048576,
        specialties=[TaskCategory.FAST_FACTUAL, TaskCategory.LONG_CONTEXT, TaskCategory.DATA_EXTRACTION],
        is_free_tier_available=True,
        average_latency_ms=600
    ),
    "gemini/gemini-2.5-pro": ModelProfile(
        id="gemini-2.5-pro",
        provider=ProviderType.GEMINI,
        display_name="Google Gemini 2.5 Pro",
        cost_per_million_input=1.25,
        cost_per_million_output=5.00,
        context_window=2097152,
        specialties=[TaskCategory.LONG_CONTEXT, TaskCategory.REASONING, TaskCategory.CODE, TaskCategory.CREATIVE],
        is_free_tier_available=True,
        average_latency_ms=1500
    ),

    # --- ANTHROPIC CLAUDE (Engenharia & Raciocínio de Ponta) ---
    "anthropic/claude-3-5-sonnet": ModelProfile(
        id="claude-3-5-sonnet-20241022",
        provider=ProviderType.ANTHROPIC,
        display_name="Claude 3.5 Sonnet",
        cost_per_million_input=3.00,
        cost_per_million_output=15.00,
        context_window=200000,
        specialties=[TaskCategory.CODE, TaskCategory.REASONING, TaskCategory.CREATIVE],
        average_latency_ms=1200
    ),
    "anthropic/claude-3-5-haiku": ModelProfile(
        id="claude-3-5-haiku-20241022",
        provider=ProviderType.ANTHROPIC,
        display_name="Claude 3.5 Haiku",
        cost_per_million_input=0.80,
        cost_per_million_output=4.00,
        context_window=200000,
        specialties=[TaskCategory.FAST_FACTUAL, TaskCategory.CODE],
        average_latency_ms=500
    ),

    # --- OPENAI (Referência de Mercado) ---
    "openai/gpt-4o": ModelProfile(
        id="gpt-4o",
        provider=ProviderType.OPENAI,
        display_name="OpenAI GPT-4o",
        cost_per_million_input=2.50,
        cost_per_million_output=10.00,
        context_window=128000,
        specialties=[TaskCategory.CODE, TaskCategory.REASONING, TaskCategory.CREATIVE],
        average_latency_ms=1000
    ),
    "openai/gpt-4o-mini": ModelProfile(
        id="gpt-4o-mini",
        provider=ProviderType.OPENAI,
        display_name="OpenAI GPT-4o Mini",
        cost_per_million_input=0.15,
        cost_per_million_output=0.60,
        context_window=128000,
        specialties=[TaskCategory.FAST_FACTUAL, TaskCategory.DATA_EXTRACTION],
        average_latency_ms=500
    ),

    # --- GROQ (Tier Gratuito / Latência Ultra Baixa) ---
    "groq/llama-3.3-70b-versatile": ModelProfile(
        id="llama-3.3-70b-versatile",
        provider=ProviderType.GROQ,
        display_name="Llama 3.3 70B (Groq Free Tier)",
        cost_per_million_input=0.0,
        cost_per_million_output=0.0,
        context_window=128000,
        specialties=[TaskCategory.CODE, TaskCategory.REASONING, TaskCategory.FAST_FACTUAL],
        is_free_tier_available=True,
        average_latency_ms=250
    )
}
