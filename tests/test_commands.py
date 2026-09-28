"""
Tests for Slash Commands Handler.
"""
from app.commands.handler import CommandHandler

def test_is_command():
    assert CommandHandler.is_command("/dre") is True
    assert CommandHandler.is_command("  /sql SELECT 1") is True
    assert CommandHandler.is_command("Qual a receita de hoje?") is False

def test_help_command():
    res = CommandHandler.handle_command("/help")
    assert res["is_command"] is True
    assert "/dre" in res["response"]
    assert "/sql" in res["response"]

def test_sql_command():
    res = CommandHandler.handle_command("/sql SELECT count(*) as qtd FROM fato_vendas")
    assert res["is_command"] is True
    assert "Resultado da Query SQL" in res["response"]
    assert len(res["raw_data"]) == 1

def test_dre_command():
    res = CommandHandler.handle_command("/dre")
    assert res["is_command"] is True
    assert "Demonstração de Resultado do Exercício" in res["response"]
    assert "Margem de Contribuição" in res["response"]

def test_curva_abc_command():
    res = CommandHandler.handle_command("/curva-abc")
    assert res["is_command"] is True
    assert "Análise de Pareto" in res["response"]
    assert "Classe A" in res["response"]

def test_grafico_command():
    res = CommandHandler.handle_command("/grafico")
    assert res["is_command"] is True
    assert "chart" in res
    assert res["chart"]["type"] == "bar"
