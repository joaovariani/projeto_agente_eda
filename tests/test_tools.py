"""
Testes unitários das ferramentas do agente.

Uso:
    python -m pytest tests/
"""

import pytest
import pandas as pd
from tools.base import state
from tools import inspect_tools, filter_tools, stats_tools


@pytest.fixture(autouse=True)
def carregar_dataset():
    """Carrega o dataset antes de cada teste."""
    state.load("data/spotify.csv")


# ========================================================
# Testes: inspect_tools
# ========================================================

def test_listar_colunas():
    resultado = inspect_tools.listar_colunas()
    assert "colunas" in resultado
    assert resultado["total_linhas"] == 114000
    assert resultado["total_colunas"] == 21
    nomes = [c["nome"] for c in resultado["colunas"]]
    assert "track_name" in nomes
    assert "popularity" in nomes
    assert "track_genre" in nomes


def test_descrever_dados():
    resultado = inspect_tools.descrever_dados()
    assert "numericas" in resultado
    assert "categoricas" in resultado
    assert "popularity" in resultado["numericas"]
    assert "track_genre" in resultado["categoricas"]


def test_contar_valores_valido():
    resultado = inspect_tools.contar_valores("track_genre")
    assert "distribuicao" in resultado
    assert resultado["total_unicos"] == 114
    assert len(resultado["distribuicao"]) > 0


def test_contar_valores_coluna_invalida():
    resultado = inspect_tools.contar_valores("coluna_inexistente")
    assert "erro" in resultado


def test_buscar_registros_valido():
    resultado = inspect_tools.buscar_registros("popularity == 100")
    assert "registros" in resultado
    assert resultado["total_encontrados"] > 0
    assert "track_name" in resultado["registros"][0]


def test_buscar_registros_sem_resultado():
    resultado = inspect_tools.buscar_registros("popularity > 200")
    assert "aviso" in resultado


# ========================================================
# Testes: filter_tools
# ========================================================

def test_filtrar_valido():
    resultado = filter_tools.filtrar("popularity > 90")
    assert "total_registros" in resultado
    assert resultado["total_registros"] > 0
    assert "percentual_do_total" in resultado


def test_filtrar_condicao_invalida():
    resultado = filter_tools.filtrar("coluna_xyz > 10")
    assert "erro" in resultado


def test_filtrar_sem_resultado():
    resultado = filter_tools.filtrar("popularity > 200")
    assert "aviso" in resultado


def test_agrupar_e_agregar_valido():
    resultado = filter_tools.agrupar_e_agregar("track_genre", "popularity", "mean")
    assert "resultado" in resultado
    assert len(resultado["resultado"]) > 0
    assert resultado["resultado"][0]["grupo"] == "pop-film"


def test_agrupar_e_agregar_funcao_invalida():
    resultado = filter_tools.agrupar_e_agregar("track_genre", "popularity", "soma")
    assert "erro" in resultado


def test_agrupar_e_agregar_coluna_invalida():
    resultado = filter_tools.agrupar_e_agregar("track_genre", "coluna_xyz", "mean")
    assert "erro" in resultado


# ========================================================
# Testes: stats_tools
# ========================================================

def test_correlacao_valida():
    resultado = stats_tools.correlacao("energy", "danceability")
    assert "pearson" in resultado
    assert "spearman" in resultado
    assert resultado["pearson"] == 0.1343


def test_correlacao_coluna_invalida():
    resultado = stats_tools.correlacao("energy", "coluna_xyz")
    assert "erro" in resultado


def test_correlacao_coluna_nao_numerica():
    resultado = stats_tools.correlacao("track_name", "popularity")
    assert "erro" in resultado


def test_detectar_outliers_valido():
    resultado = stats_tools.detectar_outliers("popularity")
    assert "iqr" in resultado
    assert "zscore" in resultado
    assert resultado["iqr"]["total_outliers"] > 0


def test_detectar_outliers_coluna_invalida():
    resultado = stats_tools.detectar_outliers("coluna_xyz")
    assert "erro" in resultado


def test_detectar_outliers_coluna_nao_numerica():
    resultado = stats_tools.detectar_outliers("track_name")
    assert "erro" in resultado