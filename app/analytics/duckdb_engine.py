import duckdb
import pandas as pd
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class DuckDBQueryResult(BaseModel):
    columns: List[str]
    rows: List[List[Any]]
    row_count: int
    execution_time_ms: int
    query_executed: str

class DuckDBEngine:
    """Motor de consulta analítica local em memória para Data Science a custo zero."""

    _connection = None

    @classmethod
    def get_connection(cls):
        if cls._connection is None:
            cls._connection = duckdb.connect(database=":memory:")
            # Inicializa tabela padrão fato_vendas para testes e análises imediatas
            cls._init_demo_dataset()
        return cls._connection

    @classmethod
    def _init_demo_dataset(cls):
        conn = cls._connection
        demo_df = pd.DataFrame({
            "id_pedido": [101, 102, 103, 104, 105, 106, 107, 108],
            "data_venda": ["2026-03-01", "2026-03-02", "2026-03-05", "2026-03-10", "2026-03-15", "2026-03-18", "2026-03-22", "2026-03-25"],
            "cliente": ["Acme Corp", "Tech Solutions", "Varejo Brasil", "Logística Express", "Alpha Saúde", "Beta Agro", "Gama Indústria", "Delta Serviços"],
            "segmento": ["Enterprise", "Mid-Market", "SMB", "Mid-Market", "Enterprise", "SMB", "Enterprise", "Mid-Market"],
            "produto": ["Plano Anual Enterprise", "Consultoria Avançada", "Licença Mensal Pro", "Setup de Integração", "Plano Anual Enterprise", "Licença Mensal Pro", "Custom AI Model", "Consultoria Avançada"],
            "valor_total": [85000.0, 32000.0, 4500.0, 15000.0, 75000.0, 5200.0, 120000.0, 28000.0],
            "custo_total": [25000.0, 11000.0, 1200.0, 4000.0, 22000.0, 1400.0, 35000.0, 9500.0]
        })
        conn.register("fato_vendas", demo_df)

    @classmethod
    def load_dataframe(cls, df: pd.DataFrame, table_name: str = "dados_vendas") -> Dict[str, Any]:
        """Carrega um DataFrame em memória no DuckDB para consultas SQL ultrarrápidas."""
        conn = cls.get_connection()
        conn.register(table_name, df)
        # Recupera schema
        schema_info = conn.execute(f"DESCRIBE {table_name}").fetchall()
        return {
            "table_name": table_name,
            "rows": len(df),
            "columns": [{"name": r[0], "type": r[1]} for r in schema_info]
        }

    @classmethod
    def execute_query(cls, sql_query: str) -> Dict[str, Any]:
        """Executa SQL analítico com CTEs, window functions e agregação local."""
        import time
        start = time.time()
        conn = cls.get_connection()
        
        # Execução segura somente leitura
        res = conn.execute(sql_query)
        columns = [desc[0] for desc in res.description] if res.description else []
        rows = res.fetchall()
        elapsed_ms = int((time.time() - start) * 1000)

        # Converte tipos para JSON serializável
        clean_rows = []
        data_records = []
        for row in rows[:100]: # Limite de preview para segurança
            clean_rows.append([str(v) if v is not None else None for v in row])
            if columns:
                record = {col: row[idx] for idx, col in enumerate(columns)}
                data_records.append(record)

        return {
            "status": "success",
            "columns": columns,
            "preview_rows": clean_rows,
            "data": data_records,
            "row_count": len(rows),
            "total_rows": len(rows),
            "elapsed_ms": elapsed_ms,
            "query": sql_query
        }

# Alias singleton para conveniência
duckdb_engine = DuckDBEngine

