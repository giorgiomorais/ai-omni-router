"""
Data & Analytics Skills - DuckDB query execution, Pareto ABC classification.
"""
from typing import Dict, Any, List
import pandas as pd
from app.skills.base import skill_registry
from app.analytics.duckdb_engine import duckdb_engine

def execute_sql_query(query: str) -> Dict[str, Any]:
    """
    Executa uma consulta SQL analítica no DuckDB em memória com as tabelas carregadas.
    """
    return duckdb_engine.execute_query(query)

def classify_pareto_abc(itens: List[str], valores: List[float]) -> Dict[str, Any]:
    """
    Classifica itens segundo o Princípio de Pareto (Curva ABC):
    - Classe A: Representam ~80% do valor total acumulado.
    - Classe B: Representam os próximos ~15% (80% a 95%).
    - Classe C: Representam os últimos ~5% (95% a 100%).
    """
    if not itens or not valores or len(itens) != len(valores):
        return {"error": "As listas de itens e valores devem ser válidas e de mesmo tamanho."}
    
    df = pd.DataFrame({"item": itens, "valor": valores})
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0.0)
    df = df.sort_values(by="valor", ascending=False).reset_index(drop=True)
    
    total_acumulado = df["valor"].sum()
    if total_acumulado == 0:
        return {"error": "Soma dos valores é zero."}

    df["share_pct"] = (df["valor"] / total_acumulado) * 100.0
    df["acumulado_pct"] = df["share_pct"].cumsum()

    classes = []
    for acum in df["acumulado_pct"]:
        if acum <= 80.0001:
            classes.append("A")
        elif acum <= 95.0001:
            classes.append("B")
        else:
            classes.append("C")

    df["classe"] = classes

    resumo_classes = {
        "A": {"count": int((df["classe"] == "A").sum()), "total_valor": round(float(df[df["classe"] == "A"]["valor"].sum()), 2)},
        "B": {"count": int((df["classe"] == "B").sum()), "total_valor": round(float(df[df["classe"] == "B"]["valor"].sum()), 2)},
        "C": {"count": int((df["classe"] == "C").sum()), "total_valor": round(float(df[df["classe"] == "C"]["valor"].sum()), 2)}
    }

    return {
        "status": "success",
        "total_itens": len(df),
        "total_faturamento": round(float(total_acumulado), 2),
        "resumo_classes": resumo_classes,
        "detalhes": df.to_dict(orient="records")[:20]  # Retorna top 20 para resumo
    }

# Register skills
skill_registry.register(
    name="execute_sql_query",
    func=execute_sql_query,
    description="Executa consulta SQL no DuckDB sobre a base de dados analítica em memória (tabelas: fato_vendas ou arquivos importados).",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Query SQL (SELECT) para executar no DuckDB"}
        },
        "required": ["query"]
    }
)

skill_registry.register(
    name="classify_pareto_abc",
    func=classify_pareto_abc,
    description="Aplica classificação de Pareto (Curva ABC) sobre produtos ou clientes por volume financeiro.",
    parameters={
        "type": "object",
        "properties": {
            "itens": {"type": "array", "items": {"type": "string"}, "description": "Lista com nomes dos itens/produtos/clientes"},
            "valores": {"type": "array", "items": {"type": "number"}, "description": "Lista com valores financeiros correspondentes"}
        },
        "required": ["itens", "valores"]
    }
)
