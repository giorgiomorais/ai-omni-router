"""
Skills Base Framework - Tool definitions, registries, and JSON schema generators.
Compatible with standard OpenAI / Groq / Ollama / Gemini tool calling specs.
"""
from typing import Callable, Any, Dict, List, Optional
import inspect

class SkillRegistry:
    """Registry to manage and discover executable skills (tools)."""
    
    def __init__(self):
        self._skills: Dict[str, Callable] = {}
        self._schemas: Dict[str, Dict[str, Any]] = {}
        self._descriptions: Dict[str, str] = {}

    def register(self, name: str, func: Callable, description: str, parameters: Dict[str, Any]):
        """Registers a function as a skill with JSON schema for function calling."""
        self._skills[name] = func
        self._descriptions[name] = description
        self._schemas[name] = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        }

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Returns tools list formatted for OpenAI/Groq/Ollama API function calling."""
        return list(self._schemas.values())

    def execute(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Executes a registered skill with given arguments safely."""
        if name not in self._skills:
            return {"error": f"Skill '{name}' não encontrada no registro."}
        func = self._skills[name]
        try:
            return func(**arguments)
        except Exception as e:
            return {"error": f"Erro ao executar skill '{name}': {str(e)}"}

skill_registry = SkillRegistry()
