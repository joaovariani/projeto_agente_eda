"""
Executor do benchmark de avaliação do agente.

Uso:
    python -m evaluation.benchmark
"""

import json
import time
from datetime import datetime

import config
from agent import Agent
from tools import state
from .metrics import calcular_acuracia, calcular_custo_usd, gerar_relatorio


def executar_benchmark(verbose: bool = True) -> dict:
    """
    Executa todas as perguntas do benchmark e retorna o relatório completo.
    """
    # Carrega o benchmark
    with open(config.BENCHMARK_FILE, "r", encoding="utf-8") as f:
        benchmark = json.load(f)

    perguntas = benchmark["perguntas"]
    total = len(perguntas)

    if verbose:
        print("=" * 60)
        print("  Executando Benchmark do Agente EDA")
        print(f"  Dataset: {config.DATASET_PATH.name}")
        print(f"  Total de perguntas: {total}")
        print("=" * 60)

    # Carrega o dataset
    resultado_carga = state.load(config.DATASET_PATH)
    if "erro" in resultado_carga:
        print(f"Erro ao carregar dataset: {resultado_carga['erro']}")
        return {}

    agente = Agent()
    resultados = []

    for i, item in enumerate(perguntas, 1):
        if verbose:
            print(f"\n[{i}/{total}] {item['pergunta']}")

        agente.resetar()

        erro = False
        try:
            resultado = agente.perguntar(item["pergunta"])
            resposta = resultado["resposta"]
            tool_calls = resultado["tool_calls"]
            latencia = resultado["latencia_segundos"]
            tokens = resultado.get("tokens", {})
        except Exception as e:
            resposta = f"ERRO: {e}"
            tool_calls = 0
            latencia = 0
            tokens = {}
            erro = True

        correto = calcular_acuracia(resposta, item["resposta_referencia"])
        custo = calcular_custo_usd(
            tokens.get("input", 0),
            tokens.get("output", 0),
        )

        resultado_item = {
            "id": item["id"],
            "tipo": item["tipo"],
            "pergunta": item["pergunta"],
            "resposta_referencia": item["resposta_referencia"],
            "resposta_agente": resposta,
            "correto": correto,
            "erro": erro,
            "tool_calls": tool_calls,
            "latencia_segundos": latencia,
            "tokens": tokens,
            "custo_usd": custo,
        }
        resultados.append(resultado_item)

        if verbose:
            status = "✓" if correto else "✗"
            print(f"  {status} | {latencia}s | {tool_calls} tools | ${custo}")

        # Pausa pequena para não sobrecarregar a API
        time.sleep(1)

    # Gera relatório
    relatorio = gerar_relatorio(resultados)

    saida = {
        "timestamp": datetime.now().isoformat(),
        "dataset": str(config.DATASET_PATH),
        "modelo": config.LLM_MODEL,
        "relatorio": relatorio,
        "resultados": resultados,
    }

    # Salva o log
    caminho_log = config.LOGS_DIR / f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(caminho_log, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2, default=str)

    if verbose:
        print("\n" + "=" * 60)
        print("  RESULTADO FINAL")
        print("=" * 60)
        print(f"  Acurácia geral:        {relatorio['acuracia_geral']}%")
        print(f"  Taxa de execução:      {relatorio['taxa_execucao_sucesso']}%")
        print(f"  Média tool calls:      {relatorio['media_tool_calls']}")
        print(f"  Latência média:        {relatorio['latencia_media_segundos']}s")
        print(f"  Custo total:           ${relatorio['custo_total_usd']}")
        print(f"\n  Log salvo em: {caminho_log}")
        print("=" * 60)

    return saida


if __name__ == "__main__":
    executar_benchmark()