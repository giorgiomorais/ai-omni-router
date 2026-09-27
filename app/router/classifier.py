import re
from typing import Dict, List, Tuple
from app.core.registry import TaskCategory

# Padrões léxico-semânticos sem custo de tokens (execução em <1ms na CPU)
CATEGORY_PATTERNS: Dict[TaskCategory, List[str]] = {
    TaskCategory.CODE: [
        r"\b(def |class |function |import |const |let |var |async |await |select |insert |update |delete |from |where |join |groupby)\b",
        r"\b(python|javascript|typescript|c\#|c\+\+|java|sql|dax|html|css|docker|git|api|endpoint|json|yaml|bug|refactor|script)\b",
        r"```[a-z]*",
        r"\b(corrija o erro|escreva um cdigo|crie uma query|funo|endpoint)\b"
    ],
    TaskCategory.REASONING: [
        r"\b(prove|deduza|calcule|passo a passo|analise criticamente|lgica|previso|otimizao|demonstre|resolva o enigma)\b",
        r"\b(por que|quais so os prs e contras|qual a causa raiz|diagnstico|comparativo aprofundado)\b"
    ],
    TaskCategory.DATA_EXTRACTION: [
        r"\b(extraia|estruture|converta em json|formato csv|tabela|regex|parse|normalize)\b",
        r"\b(organize em colunas|campos:|schema)\b"
    ],
    TaskCategory.CREATIVE: [
        r"\b(escreva uma histria|poema|redija um e-mail|copy|artigo|slogan|roteiro|pitch|marketing)\b"
    ]
}

class SemanticClassifier:
    """Classificador semântico leve com custo zero de execução."""

    @classmethod
    def classify(cls, prompt: str) -> Tuple[TaskCategory, float]:
        text = prompt.lower()
        char_count = len(prompt)

        # Regra de contexto longo (se o prompt tiver mais de 50.000 caracteres)
        if char_count > 50000:
            return TaskCategory.LONG_CONTEXT, 0.95

        scores: Dict[TaskCategory, float] = {cat: 0.0 for cat in TaskCategory}

        # Avaliação de padrões de expressão regular
        for category, patterns in CATEGORY_PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    scores[category] += len(matches) * 1.5

        # Heurísticas de detecção
        best_category = max(scores, key=scores.get)
        confidence = scores[best_category]

        # Se não houver correspondência forte e for pergunta curta, classifica como FAST_FACTUAL
        if confidence < 1.0:
            return TaskCategory.FAST_FACTUAL, 0.70

        # Normalização de confiança (0.5 a 0.99)
        normalized_conf = min(0.99, 0.5 + (confidence * 0.1))
        return best_category, normalized_conf
