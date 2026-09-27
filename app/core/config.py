from enum import Enum
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class RoutingStrategy(str, Enum):
    BALANCED = "balanced"
    COST_SAVING = "cost_saving"
    QUALITY_FIRST = "quality_first"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PORT: int = 8000
    HOST: str = "0.0.0.0"
    DEFAULT_ROUTING_STRATEGY: RoutingStrategy = RoutingStrategy.BALANCED

    # Provedor Local (Zero Custo)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LOCAL_MODEL_CODE: str = "qwen2.5-coder:1.5b"
    LOCAL_MODEL_FAST: str = "llama3.2:1b"
    LOCAL_MODEL_REASONING: str = "deepseek-r1:1.5b"

    # Nuvem
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None

settings = Settings()
