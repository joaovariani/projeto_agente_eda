"""
Interface de linha de comando do agente EDA.

Uso:
    python cli.py
"""

import logging
import json
from datetime import datetime
from pathlib import Path

import config
from agent import Agent
from tools import state
from tools.base import get_tools

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(
            config.LOGS_DIR / f"sessao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


def salvar_log_sessao(agente: Agent):
    """Salva o log completo da sessão em JSON."""
    caminho = config.LOGS_DIR / f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(agente.logs, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nLog salvo em: {caminho}")


def main():
    print("=" * 60)
    print("  Agente de Análise Exploratória de Dados")
    print("  Dataset: Spotify Tracks")
    print("=" * 60)

    # Carrega o dataset
    resultado = state.load(config.DATASET_PATH)
    if "erro" in resultado:
        print(f"\nErro ao carregar dataset: {resultado['erro']}")
        return
    print(f"\nDataset carregado: {resultado['linhas']:,} linhas × {resultado['colunas']} colunas")
    print("\nDigite sua pergunta em português. Digite 'sair' para encerrar.\n")

    agente = Agent()

    while True:
        try:
            pergunta = input("Você: ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not pergunta:
            continue

        if pergunta.lower() in ["sair", "exit", "quit"]:
            break

        if pergunta.lower() == "resetar":
            agente.resetar()
            print("Histórico resetado.\n")
            continue

        print("\nAgente: processando...\n")
        resultado = agente.perguntar(pergunta)

        print(f"Agente: {resultado['resposta']}")
        print(f"\n[{resultado['latencia_segundos']}s | {resultado['tool_calls']} tool calls]")
        print("-" * 60 + "\n")

    salvar_log_sessao(agente)
    print("\nAté logo!")


if __name__ == "__main__":
    main()