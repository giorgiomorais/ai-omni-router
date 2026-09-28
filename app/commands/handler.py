"""
Slash Commands Handler - Intercepts user inputs starting with `/`
Executes deterministically without AI hallucination or costs.
Supported commands:
- /sql <query>: Runs directly on DuckDB
- /dre: Calculates DRE on current DuckDB table or defaults
- /curva-abc: Computes Pareto 80/20 on current data
- /grafico: Plots sales or custom dataset
- /pdf: Triggers executive PDF download
- /help ou /ajuda: Lists all commands
"""
from typing import Dict, Any, Optional
import json
from app.analytics.duckdb_engine import duckdb_engine
from app.skills.finance_skills import calculate_dre
from app.skills.data_skills import classify_pareto_abc
from app.skills.chart_skills import generate_chart

class CommandHandler:
    """Interprets and executes slash commands directly."""

    @staticmethod
    def is_command(text: str) -> bool:
        return text.strip().startswith("/")

    @classmethod
    def handle_command(cls, text: str) -> Dict[str, Any]:
        parts = text.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1].strip() if len(parts) > 1 else ""

        if cmd in ["/help", "/ajuda"]:
            return cls._help_command()
        elif cmd == "/sql":
            return cls._sql_command(args)
        elif cmd == "/dre":
            return cls._dre_command(args)
        elif cmd in ["/curva-abc", "/abc", "/pareto"]:
            return cls._curva_abc_command(args)
        elif cmd in ["/grafico", "/chart"]:
            return cls._grafico_command(args)
        elif cmd == "/pdf":
            return {
                "is_command": True,
                "command": cmd,
                "response": "Para baixar o relatório executivo em PDF, utilize o botão **Exportar PDF** no cabeçalho ou faça uma requisição a `/v1/reports/export-pdf`.",
                "action": "export_pdf"
            }
        else:
            return {
                "is_command": True,
                "command": cmd,
                "response": f"Comando `{cmd}` desconhecido. Digite `/help` para listar os comandos suportados."
            }

    @staticmethod
    def _help_command() -> Dict[str, Any]:
        help_text = (
            "### ⚡ Comandos Rápidos Disponíveis (Slash Commands)\n\n"
            "| Comando | Descrição | Exemplo |\n"
            "| :--- | :--- | :--- |\n"
            "| `/sql <query>` | Executa consulta SQL direta no DuckDB sem custo de LLM | `/sql SELECT segmento, sum(valor_total) FROM fato_vendas GROUP BY 1` |\n"
            "| `/dre` | Gera a Demonstração de Resultado do Exercício gerencial sobre os dados | `/dre` |\n"
            "| `/curva-abc` | Aplica a classificação de Pareto (80/20) nos produtos faturados | `/curva-abc` |\n"
            "| `/grafico` | Gera gráfico instantâneo das vendas por segmento | `/grafico` |\n"
            "| `/pdf` | Exporta relatório executivo em PDF | `/pdf` |\n"
            "| `/help` | Exibe esta listagem | `/help` |\n"
        )
        return {
            "is_command": True,
            "command": "/help",
            "response": help_text
        }

    @staticmethod
    def _sql_command(query: str) -> Dict[str, Any]:
        if not query:
            return {
                "is_command": True,
                "command": "/sql",
                "response": "Por favor, especifique a consulta SQL. Exemplo: `/sql SELECT * FROM fato_vendas LIMIT 5`"
            }
        result = duckdb_engine.execute_query(query)
        if result.get("status") == "error":
            return {
                "is_command": True,
                "command": "/sql",
                "response": f"❌ **Erro na execução SQL:**\n```\n{result.get('error')}\n```"
            }
        
        # Converte resultado em tabela Markdown
        columns = result.get("columns", [])
        data = result.get("data", [])
        row_count = result.get("row_count", 0)

        if not columns or not data:
            return {
                "is_command": True,
                "command": "/sql",
                "response": f"✅ Query executada com sucesso. Nenhuma linha retornada. ({row_count} registros)"
            }

        header = "| " + " | ".join(columns) + " |"
        separator = "| " + " | ".join(["---"] * len(columns)) + " |"
        rows = []
        for r in data[:20]:
            row_str = "| " + " | ".join([str(r.get(col, "")) for col in columns]) + " |"
            rows.append(row_str)

        table_md = "\n".join([header, separator] + rows)
        if len(data) > 20:
            table_md += f"\n\n*(Mostrando primeiras 20 linhas de {row_count})*"

        return {
            "is_command": True,
            "command": "/sql",
            "response": f"### 📊 Resultado da Query SQL ({row_count} linhas)\n\n{table_md}",
            "raw_data": data
        }

    @staticmethod
    def _dre_command(args: str) -> Dict[str, Any]:
        # Busca total faturado no DuckDB
        sql_res = duckdb_engine.execute_query("SELECT SUM(valor_total) as receita, SUM(custo_total) as custo FROM fato_vendas")
        receita_bruta = 150000.0
        custo_variavel = 55000.0
        if sql_res.get("status") == "success" and sql_res.get("data"):
            first_row = sql_res["data"][0]
            receita_bruta = float(first_row.get("receita") or 150000.0)
            custo_variavel = float(first_row.get("custo") or 55000.0)

        dre = calculate_dre(
            receita_bruta=receita_bruta,
            aliquota_impostos_pct=12.0,
            custo_variavel_total=custo_variavel,
            despesas_fixas_total=18000.0,
            investimento_mkt_total=12000.0
        )

        md = (
            f"### 📑 Demonstração de Resultado do Exercício (DRE Gerencial)\n\n"
            f"| Linha da DRE | Valor (R$) | % Rec. Líquida |\n"
            f"| :--- | :--- | :--- |\n"
            f"| **(=) Receita Bruta Total** | **R$ {dre['receita_bruta']:,.2f}** | - |\n"
            f"| (-) Deduções e Impostos sobre Vendas (12%) | R$ {dre['deducoes_impostos']:,.2f} | - |\n"
            f"| **(=) Receita Operacional Líquida** | **R$ {dre['receita_liquida']:,.2f}** | **100,0%** |\n"
            f"| (-) Custos Variáveis (CMV/CPV) | R$ {dre['custos_variaveis']:,.2f} | {dre['custos_variaveis']/dre['receita_liquida']*100:.1f}% |\n"
            f"| **(=) Margem de Contribuição** | **R$ {dre['margem_contribuicao_valor']:,.2f}** | **{dre['margem_contribuicao_pct']:.1f}%** |\n"
            f"| (-) Despesas Fixas (Adm/Op) | R$ {dre['despesas_fixas']:,.2f} | {dre['despesas_fixas']/dre['receita_liquida']*100:.1f}% |\n"
            f"| (-) Despesas Comerciais & Marketing | R$ {dre['investimento_marketing']:,.2f} | {dre['investimento_marketing']/dre['receita_liquida']*100:.1f}% |\n"
            f"| **(=) Resultado Operacional (EBITDA)** | **R$ {dre['resultado_operacional_ebitda']:,.2f}** | **{dre['margem_operacional_pct']:.1f}%** |\n\n"
            f"🎯 **Ponto de Equilíbrio Operacional:** R$ {dre['ponto_equilibrio_faturamento']:,.2f}/mês\n"
        )
        return {
            "is_command": True,
            "command": "/dre",
            "response": md,
            "data": dre
        }

    @staticmethod
    def _curva_abc_command(args: str) -> Dict[str, Any]:
        sql_res = duckdb_engine.execute_query("SELECT produto, SUM(valor_total) as total FROM fato_vendas GROUP BY 1 ORDER BY 2 DESC")
        if sql_res.get("status") != "success" or not sql_res.get("data"):
            return {
                "is_command": True,
                "command": "/curva-abc",
                "response": "Base de dados vazia para cálculo de Curva ABC."
            }
        
        itens = [r["produto"] for r in sql_res["data"]]
        valores = [float(r["total"]) for r in sql_res["data"]]
        abc = classify_pareto_abc(itens, valores)

        resumo = abc["resumo_classes"]
        md = (
            f"### 📈 Análise de Pareto (Curva ABC de Produtos)\n\n"
            f"- **Faturamento Total Analisado:** R$ {abc['total_faturamento']:,.2f}\n"
            f"- **Classe A (80% da Receita):** {resumo['A']['count']} produtos | R$ {resumo['A']['total_valor']:,.2f}\n"
            f"- **Classe B (15% da Receita):** {resumo['B']['count']} produtos | R$ {resumo['B']['total_valor']:,.2f}\n"
            f"- **Classe C (5% da Receita):** {resumo['C']['count']} produtos | R$ {resumo['C']['total_valor']:,.2f}\n\n"
            f"| Produto | Classe | Faturamento (R$) | Share % | Acumulado % |\n"
            f"| :--- | :---: | :--- | :--- | :--- |\n"
        )
        for d in abc["detalhes"][:10]:
            md += f"| {d['item']} | **{d['classe']}** | R$ {d['valor']:,.2f} | {d['share_pct']:.1f}% | {d['acumulado_pct']:.1f}% |\n"

        return {
            "is_command": True,
            "command": "/curva-abc",
            "response": md,
            "data": abc
        }

    @staticmethod
    def _grafico_command(args: str) -> Dict[str, Any]:
        # Busca faturamento por segmento
        sql_res = duckdb_engine.execute_query("SELECT segmento, ROUND(SUM(valor_total), 2) as total FROM fato_vendas GROUP BY 1 ORDER BY 2 DESC")
        if sql_res.get("status") != "success" or not sql_res.get("data"):
            labels = ["Enterprise", "Mid-Market", "SMB"]
            values = [85000.0, 42000.0, 18500.0]
        else:
            labels = [r["segmento"] for r in sql_res["data"]]
            values = [float(r["total"]) for r in sql_res["data"]]

        chart_payload = generate_chart(
            chart_type="bar",
            title="Faturamento por Segmento de Clientes (R$)",
            labels=labels,
            values=values,
            dataset_label="Receita Bruta"
        )

        return {
            "is_command": True,
            "command": "/grafico",
            "response": "📊 **Gráfico de Vendas por Segmento gerado:**",
            "chart": chart_payload["chart_config"]
        }
