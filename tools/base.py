"""
Base comum para todas as ferramentas do agente.

Define o decorador @tool e o objeto de estado global (state)
que carrega e mantém o DataFrame em memória.
"""

import pandas as pd
from pathlib import Path


# ========================================================
# Registro global de tools
# ========================================================

_registry: list[dict] = []
_functions: dict[str, callable] = {}


def tool(description: str, parameters: dict):
    """
    Decorador que registra uma função como tool disponível para o agente.
    Armazena a descrição e os parâmetros no formato da API Anthropic.
    """
    def decorator(func):
        _registry.append({
            "name": func.__name__,
            "description": description,
            "input_schema": parameters,
        })
        _functions[func.__name__] = func
        return func
    return decorator


def get_tools() -> list[dict]:
    """Retorna a lista de tools no formato esperado pela API do Claude."""
    return _registry


def call_tool(name: str, arguments: dict):
    """Executa uma tool pelo nome com os argumentos fornecidos pelo LLM."""
    if name not in _functions:
        return {"erro": f"Tool '{name}' não encontrada."}
    try:
        return _functions[name](**arguments)
    except TypeError as e:
        return {"erro": f"Argumentos inválidos para '{name}': {e}"}
    except Exception as e:
        return {"erro": f"Erro ao executar '{name}': {e}"}


# ========================================================
# Estado global — DataFrame carregado
# ========================================================

class _State:
    def __init__(self):
        self._df: pd.DataFrame | None = None
        self._path: str = ""

    def load(self, path: str | Path) -> dict:
        """Carrega um CSV no estado global."""
        try:
            self._df = pd.read_csv(path)
            self._path = str(path)
            return {
                "mensagem": f"Dataset carregado: {self._path}",
                "linhas": len(self._df),
                "colunas": len(self._df.columns),
            }
        except Exception as e:
            return {"erro": f"Não foi possível carregar o arquivo: {e}"}

    def require_loaded(self) -> pd.DataFrame:
        """Retorna o DataFrame ou lança erro se não estiver carregado."""
        if self._df is None:
            raise RuntimeError(
                "Nenhum dataset carregado. "
                "Carregue um CSV antes de usar as tools."
            )
        return self._df

    @property
    def is_loaded(self) -> bool:
        return self._df is not None

    @property
    def path(self) -> str:
        return self._path


state = _State()