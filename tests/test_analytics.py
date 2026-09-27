import pytest
from app.core.data_masker import DataMasker
from app.analytics.duckdb_engine import DuckDBEngine
import pandas as pd

def test_data_masker():
    text = "O cliente com CPF 123.456.789-00 e CNPJ 12.345.678/0001-90 enviou o email financeiro@empresa.com"
    masked, rev_map = DataMasker.mask(text)
    
    # Valida que dados sensíveis foram mascarados
    assert "123.456.789-00" not in masked
    assert "12.345.678/0001-90" not in masked
    assert "financeiro@empresa.com" not in masked
    assert "[CPF_OCULTO_1]" in masked
    assert "[CNPJ_OCULTO_1]" in masked
    
    # Valida restauração
    restored = DataMasker.unmask(masked, rev_map)
    assert restored == text

def test_duckdb_engine():
    df = pd.DataFrame({
        "venda": [100.0, 200.0, 300.0],
        "imposto": [10.0, 20.0, 30.0]
    })
    DuckDBEngine.load_dataframe(df, "teste_vendas")
    result = DuckDBEngine.execute_query("SELECT SUM(venda) as total_vendas, SUM(venda - imposto) as receita_liquida FROM teste_vendas")
    
    assert result["total_rows"] == 1
    assert result["columns"] == ["total_vendas", "receita_liquida"]
    assert float(result["preview_rows"][0][0]) == 600.0
    assert float(result["preview_rows"][0][1]) == 540.0
