"""
Pacote de ferramentas do agente.

Importar este pacote já registra todas as tools automaticamente.
"""

from .base import get_tools, call_tool, state

from . import inspect_tools
from . import filter_tools
from . import stats_tools
from . import plot_tools

__all__ = ["get_tools", "call_tool", "state"]