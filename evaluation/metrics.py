"""
Cálculo de métricas de avaliação do agente.
"""

import re


def calcular_acuracia(resposta_agente: str, resposta_referencia: str) -> bool:
    """
    Verifica se a resposta do agente contém a informação de referência.
    Para perguntas ambíguas, verifica se o agente recusou ou pediu esclarecimento.
    """
    if resposta_referencia.startswith("AMBIGUA") or resposta_referencia.startswith("INVALIDA"):
        # O agente deve ter reconhecido o problema
        palavras_chave = [
            "não existe", "nao existe", "não encontrei", "nao encontrei",
            "subjetivo", "não é possível", "nao e possivel", "ambíguo",
            "ambiguo", "esclarecimento", "não tenho", "nao tenho",
            "coluna", "disponível", "disponivel", "sugerir", "poderia"
        ]
        resposta_lower = resposta_agente.lower()
        return any(p in resposta_lower for p in palavras_chave)

    # Extrai números da resposta de referência
    numeros_ref = re.findall(r"-?\d+\.?\d*", resposta_referencia)

    if numeros_ref:
        # Verifica se algum número da referência aparece na resposta
        for num in numeros_ref:
            if num in resposta_agente:
                return True
        return False

    # Para respostas textuais, verifica se palavras-chave aparecem
    palavras = [p.lower().strip() for p in resposta_referencia.split() if len(p) > 3]
    resposta_lower = resposta_agente.lower()
    matches = sum(1 for p in palavras if p in resposta_lower)
    return matches >= max(1, len(palavras) // 2)


def calcular_custo_usd(tokens_input: int, tokens_output: int) -> float:
    """
    Estima o custo em USD para Claude Haiku.
    Preços: $0.80/MTok input, $4.00/MTok output (junho 2026)
    """
    custo_input = (tokens_input / 1_000_000) * 0.80
    custo_output = (tokens_output / 1_000_000) * 4.00
    return round(custo_input + custo_output, 6)


def gerar_relatorio(resultados: list[dict]) -> dict:
    """
    Gera o relatório completo de métricas a partir dos resultados do benchmark.
    """
    total = len(resultados)
    if total == 0:
        return {"erro": "Nenhum resultado para calcular métricas."}

    # Acurácia
    corretas = sum(1 for r in resultados if r.get("correto", False))
    acuracia = round(corretas / total * 100, 2)

    # Taxa de execução bem-sucedida
    sucessos = sum(1 for r in resultados if not r.get("erro", False))
    taxa_execucao = round(sucessos / total * 100, 2)

    # Média de tool calls
    tool_calls = [r.get("tool_calls", 0) for r in resultados]
    media_tool_calls = round(sum(tool_calls) / total, 2)

    # Latência média
    latencias = [r.get("latencia_segundos", 0) for r in resultados]
    latencia_media = round(sum(latencias) / total, 2)

    # Custo total e médio
    custo_total = sum(r.get("custo_usd", 0) for r in resultados)
    custo_medio = round(custo_total / total, 6)

    # Tokens totais
    tokens_input = sum(r.get("tokens", {}).get("input", 0) for r in resultados)
    tokens_output = sum(r.get("tokens", {}).get("output", 0) for r in resultados)

    # Por tipo de pergunta
    por_tipo = {}
    for tipo in ["simples", "analitica", "ambigua"]:
        subset = [r for r in resultados if r.get("tipo") == tipo]
        if subset:
            corretas_tipo = sum(1 for r in subset if r.get("correto", False))
            por_tipo[tipo] = {
                "total": len(subset),
                "corretas": corretas_tipo,
                "acuracia": round(corretas_tipo / len(subset) * 100, 2),
            }

    return {
        "total_perguntas": total,
        "acuracia_geral": acuracia,
        "taxa_execucao_sucesso": taxa_execucao,
        "media_tool_calls": media_tool_calls,
        "latencia_media_segundos": latencia_media,
        "custo_total_usd": round(custo_total, 4),
        "custo_medio_por_pergunta_usd": custo_medio,
        "tokens_totais": {
            "input": tokens_input,
            "output": tokens_output,
        },
        "acuracia_por_tipo": por_tipo,
    }