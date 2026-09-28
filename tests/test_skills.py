"""
Tests for Financial, Data and Chart Skills.
"""
from app.skills.base import skill_registry
from app.skills.finance_skills import calculate_dre, calculate_unit_economics
from app.skills.data_skills import classify_pareto_abc
from app.skills.chart_skills import generate_chart

def test_calculate_dre():
    res = calculate_dre(
        receita_bruta=100000.0,
        aliquota_impostos_pct=10.0,
        custo_variavel_total=30000.0,
        despesas_fixas_total=20000.0,
        investimento_mkt_total=10000.0
    )
    assert res["status"] == "success"
    assert res["receita_liquida"] == 90000.0
    assert res["margem_contribuicao_valor"] == 60000.0
    assert round(res["margem_contribuicao_pct"], 2) == 66.67
    assert res["resultado_operacional_ebitda"] == 30000.0

def test_calculate_unit_economics():
    res = calculate_unit_economics(
        novos_clientes=10,
        investimento_marketing_vendas=5000.0,
        ticket_medio=250.0,
        churn_rate_mensal_pct=5.0,
        margem_contribuicao_pct=60.0
    )
    assert res["status"] == "success"
    assert res["cac"] == 500.0
    assert res["tempo_vida_medio_meses"] == 20.0
    assert res["ltv"] == 3000.0
    assert res["ltv_cac_ratio"] == 6.0
    assert res["saude_comercial"] == "Excelente"

def test_classify_pareto_abc():
    itens = ["Prod A", "Prod B", "Prod C", "Prod D"]
    valores = [8000.0, 1500.0, 400.0, 100.0]
    res = classify_pareto_abc(itens, valores)
    
    assert res["status"] == "success"
    assert res["total_itens"] == 4
    assert res["total_faturamento"] == 10000.0
    assert res["resumo_classes"]["A"]["count"] == 1
    assert res["resumo_classes"]["B"]["count"] == 1
    assert res["resumo_classes"]["C"]["count"] == 2

def test_generate_chart():
    res = generate_chart(
        chart_type="bar",
        title="Receita por Segmento",
        labels=["Enterprise", "SMB"],
        values=[80000.0, 20000.0]
    )
    assert res["status"] == "success"
    config = res["chart_config"]
    assert config["type"] == "bar"
    assert config["data"]["labels"] == ["Enterprise", "SMB"]
    assert config["data"]["datasets"][0]["data"] == [80000.0, 20000.0]

def test_skill_registry_execution():
    tool_schemas = skill_registry.get_tool_schemas()
    assert len(tool_schemas) >= 4
    
    # Executa skill através do registro
    res = skill_registry.execute("calculate_dre", {"receita_bruta": 50000.0})
    assert res["status"] == "success"
    assert res["receita_bruta"] == 50000.0
