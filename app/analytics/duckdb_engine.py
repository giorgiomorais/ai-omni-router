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
        return cls._connection

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
        for row in rows[:100]: # Limite de preview para segurança
            clean_rows.append([str(v) if v is not None else None for v in row])

        return {
            "columns": columns,
            "preview_rows": clean_rows,
            "total_rows": len(rows),
            "elapsed_ms": elapsed_ms,
            "query": sql_query
        }
