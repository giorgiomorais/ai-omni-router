import pytest
from app.router.classifier import SemanticClassifier
from app.router.selector import ModelSelector
from app.core.registry import TaskCategory
from app.core.config import RoutingStrategy

def test_code_classification():
    prompt = "Escreva uma função em Python para calcular o Fibonacci com memoization e async/await"
    cat, conf = SemanticClassifier.classify(prompt)
    assert cat == TaskCategory.CODE
    assert conf > 0.6

def test_reasoning_classification():
    prompt = "Analise criticamente o impacto da inflação no poder de compra e deduza o passo a passo da causalidade"
    cat, conf = SemanticClassifier.classify(prompt)
    assert cat == TaskCategory.REASONING

def test_fast_factual_classification():
    prompt = "Qual é a capital da França?"
    cat, conf = SemanticClassifier.classify(prompt)
    assert cat == TaskCategory.FAST_FACTUAL

def test_data_extraction_classification():
    prompt = "Extraia as informações do texto e converta em json organizado com schema de colunas"
    cat, conf = SemanticClassifier.classify(prompt)
    assert cat == TaskCategory.DATA_EXTRACTION

def test_model_selection_cost_saving():
    # Com estratégia de economia de custos, deve selecionar modelos gratuitos (local ou tier free)
    model, fallback = ModelSelector.select_best_model(
        category=TaskCategory.CODE,
        strategy=RoutingStrategy.COST_SAVING
    )
    assert model.cost_per_million_input == 0.0 or model.is_local
