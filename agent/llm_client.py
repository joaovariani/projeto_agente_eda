"""
Cliente da API do Claude (Anthropic).

Responsável por enviar mensagens e tools para o LLM
e retornar a resposta bruta para o loop do agente.
"""

import anthropic
import config


_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


def chamar_llm(mensagens: list[dict], tools: list[dict]) -> object:
    """
    Envia o histórico de mensagens e as tools disponíveis para o Claude.

    Args:
        mensagens: lista de dicts com 'role' e 'content'
        tools: lista de tools no formato Anthropic

    Returns:
        Objeto de resposta da API do Claude
    """
    response = _client.messages.create(
        model=config.LLM_MODEL,
        max_tokens=config.MAX_TOKENS_PER_RESPONSE,
        system=(
            "Você é um agente especialista em análise exploratória de dados. "
            "Responda sempre em português brasileiro. "
            "Você tem acesso a ferramentas Python para analisar um dataset CSV carregado em memória. "
            "Sempre que precisar de informações sobre os dados, use as ferramentas disponíveis. "
            "Nunca invente dados ou resultados — sempre execute as ferramentas para obter os valores reais. "
            "Ao final, apresente a resposta de forma clara e objetiva para o usuário."
        ),
        messages=mensagens,
        tools=tools,
    )
    return response