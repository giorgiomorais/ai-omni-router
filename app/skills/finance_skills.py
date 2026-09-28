"""
Financial & Accounting Skills - Exact mathematical calculation without LLM hallucinations.
Focado em rigor contábil (DRE, Margem de Contribuição, Ponto de Equilíbrio, CAC/LTV).
"""
from typing import Dict, Any
from app.skills.base import skill_registry

def calculate_dre(
    receita_bruta: float,
    aliquota_impostos_pct: float = 12.0,
    custo_variavel_total: float = 0.0,
    despesas_fixas_total: float = 0.0,
    investimento_mkt_total: float = 0.0
) -> Dict[str, Any]:
    """
    Calcula a DRE Gerencial analítica com base em faturamento bruto e deduções fiscais e operacionais.
    """
    impostos_vendas = receita_bruta * (aliquota_impostos_pct / 100.0)
    receita_liquida = receita_bruta - impostos_vendas
    margem_contribuicao_valor = receita_liquida - custo_variavel_total
    margem_contribuicao_pct = (margem_contribuicao_valor / receita_liquida * 100.0) if receita_liquida > 0 else 0.0
    
    total_despesas_operacionais = despesas_fixas_total + investimento_mkt_total
    resultado_operacional_ebitda = margem_contribuicao_valor - total_despesas_operacionais
    margem_operacional_pct = (resultado_operacional_ebitda / receita_liquida * 100.0) if receita_liquida > 0 else 0.0

    # Ponto de Equilíbrio Operacional (Break-even point)
    ponto_equilibrio_faturamento = 0.0
    if margem_contribuicao_pct > 0:
        ponto_equilibrio_faturamento = total_despesas_operacionais / (margem_contribuicao_pct / 100.0)

    return {
        "status": "success",
        "receita_bruta": round(receita_bruta, 2),
        "deducoes_impostos": round(impostos_vendas, 2),
        "aliquota_impostos_efetiva_pct": round(aliquota_impostos_pct, 2),
        "receita_liquida": round(receita_liquida, 2),
        "custos_variaveis": round(custo_variavel_total, 2),
        "margem_contribuicao_valor": round(margem_contribuicao_valor, 2),
        "margem_contribuicao_pct": round(margem_contribuicao_pct, 2),
        "despesas_fixas": round(despesas_fixas_total, 2),
        "investimento_marketing": round(investimento_mkt_total, 2),
        "resultado_operacional_ebitda": round(resultado_operacional_ebitda, 2),
        "margem_operacional_pct": round(margem_operacional_pct, 2),
        "ponto_equilibrio_faturamento": round(ponto_equilibrio_faturamento, 2)
    }

def calculate_unit_economics(
    novos_clientes: int,
    investimento_marketing_vendas: float,
    ticket_medio: float,
    churn_rate_mensal_pct: float,
    margem_contribuicao_pct: float = 60.0
) -> Dict[str, Any]:
    """
    Calcula métricas de Unit Economics Comerciais: CAC, LTV e Razão LTV/CAC.
    """
    if novos_clientes <= 0:
        return {"error": "Número de novos clientes deve ser maior que zero."}
    
    cac = investimento_marketing_vendas / novos_clientes
    tempo_vida_medio_meses = (100.0 / churn_rate_mensal_pct) if churn_rate_mensal_pct > 0 else 12.0
    ltv = ticket_medio * (margem_contribuicao_pct / 100.0) * tempo_vida_medio_meses
    ltv_cac_ratio = ltv / cac if cac > 0 else 0.0
    
    # Payback estimado do CAC em meses
    margem_por_cliente_mes = ticket_medio * (margem_contribuicao_pct / 100.0)
    payback_meses = cac / margem_por_cliente_mes if margem_por_cliente_mes > 0 else 0.0

    return {
        "status": "success",
        "cac": round(cac, 2),
        "ltv": round(ltv, 2),
        "ltv_cac_ratio": round(ltv_cac_ratio, 2),
        "tempo_vida_medio_meses": round(tempo_vida_medio_meses, 1),
        "payback_meses": round(payback_meses, 1),
        "saude_comercial": "Excelente" if ltv_cac_ratio >= 3.0 else ("Atenção" if ltv_cac_ratio >= 1.5 else "Crítica")
    }

# Register skills in base registry
skill_registry.register(
    name="calculate_dre",
    func=calculate_dre,
    description="Calcula DRE Gerencial rigorosa (Receita Bruta, Impostos, Receita Líquida, Margem de Contribuição, EBITDA e Ponto de Equilíbrio).",
    parameters={
        "type": "object",
        "properties": {
            "receita_bruta": {"type": "number", "description": "Faturamento bruto total em R$"},
            "aliquota_impostos_pct": {"type": "number", "description": "Alíquota estimada de impostos sobre vendas (%)", "default": 12.0},
            "custo_variavel_total": {"type": "number", "description": "Soma de custos variáveis (CMV/CPV + comissões) em R$", "default": 0.0},
            "despesas_fixas_total": {"type": "number", "description": "Soma de despesas fixas (folha, aluguel, infra) em R$", "default": 0.0},
            "investimento_mkt_total": {"type": "number", "description": "Total investido em marketing e tráfego pago em R$", "default": 0.0}
        },
        "required": ["receita_bruta"]
    }
)

skill_registry.register(
    name="calculate_unit_economics",
    func=calculate_unit_economics,
    description="Calcula Unit Economics comerciais: CAC (Custo de Aquisição de Clientes), LTV (Lifetime Value), razão LTV/CAC e Payback.",
    parameters={
        "type": "object",
        "properties": {
            "novos_clientes": {"type": "integer", "description": "Número de novos clientes adquiridos no período"},
            "investimento_marketing_vendas": {"type": "number", "description": "Investimento total em vendas e marketing em R$"},
            "ticket_medio": {"type": "number", "description": "Ticket médio da mensalidade ou compra em R$"},
            "churn_rate_mensal_pct": {"type": "number", "description": "Taxa de cancelamento mensal (churn) em %"},
            "margem_contribuicao_pct": {"type": "number", "description": "Margem de contribuição média em %", "default": 60.0}
        },
        "required": ["novos_clientes", "investimento_marketing_vendas", "ticket_medio", "churn_rate_mensal_pct"]
    }
)
