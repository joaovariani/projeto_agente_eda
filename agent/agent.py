"""
Loop principal do agente EDA.

Implementa o ciclo: pensar → agir → observar
até o LLM produzir uma resposta final ao usuário.
"""

import json
import time
import logging
from datetime import datetime

import config
import tools as tool_module
from .llm_client import chamar_llm

logger = logging.getLogger(__name__)


class Agent:
    def __init__(self):
        self.historico: list[dict] = []
        self.logs: list[dict] = []

    def _log(self, evento: str, dados: dict):
        entrada = {
            "timestamp": datetime.now().isoformat(),
            "evento": evento,
            **dados,
        }
        self.logs.append(entrada)
        logger.debug(json.dumps(entrada, ensure_ascii=False, default=str))

    def resetar(self):
        """Limpa o histórico e os logs para uma nova sessão."""
        self.historico = []
        self.logs = []

    def perguntar(self, pergunta: str) -> dict:
        """
        Processa uma pergunta do usuário e retorna a resposta final.

        Returns:
            dict com 'resposta', 'tool_calls', 'latencia_segundos', 'tokens'
        """
        inicio = time.time()
        tool_calls_count = 0

        # Adiciona a pergunta do usuário ao histórico
        self.historico.append({"role": "user", "content": pergunta})
        self._log("pergunta_recebida", {"pergunta": pergunta})

        tools = tool_module.get_tools()

        for iteracao in range(config.MAX_AGENT_ITERATIONS):
            response = chamar_llm(self.historico, tools)

            self._log("resposta_llm", {
                "iteracao": iteracao,
                "stop_reason": response.stop_reason,
                "uso_tokens": {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens,
                },
            })

            # Resposta final — sem mais tool calls
            if response.stop_reason == "end_turn":
                texto = ""
                for bloco in response.content:
                    if hasattr(bloco, "text"):
                        texto += bloco.text

                self.historico.append({
                    "role": "assistant",
                    "content": response.content,
                })

                latencia = round(time.time() - inicio, 2)
                self._log("resposta_final", {
                    "latencia_segundos": latencia,
                    "tool_calls_total": tool_calls_count,
                })

                return {
                    "resposta": texto,
                    "tool_calls": tool_calls_count,
                    "latencia_segundos": latencia,
                    "tokens": {
                        "input": response.usage.input_tokens,
                        "output": response.usage.output_tokens,
                    },
                }

            # O agente quer usar tools
            if response.stop_reason == "tool_use":
                tool_results = []

                for bloco in response.content:
                    if bloco.type != "tool_use":
                        continue

                    tool_calls_count += 1
                    nome = bloco.name
                    argumentos = bloco.input

                    self._log("tool_chamada", {
                        "tool": nome,
                        "argumentos": argumentos,
                    })

                    resultado = tool_module.call_tool(nome, argumentos)

                    self._log("tool_resultado", {
                        "tool": nome,
                        "resultado": resultado,
                    })

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": bloco.id,
                        "content": json.dumps(resultado, ensure_ascii=False, default=str),
                    })

                # Adiciona resposta do assistente + resultados das tools ao histórico
                self.historico.append({
                    "role": "assistant",
                    "content": response.content,
                })
                self.historico.append({
                    "role": "user",
                    "content": tool_results,
                })

            else:
                # Stop reason inesperado
                break

        # Limite de iterações atingido
        latencia = round(time.time() - inicio, 2)
        return {
            "resposta": "Limite de iterações atingido sem resposta final.",
            "tool_calls": tool_calls_count,
            "latencia_segundos": latencia,
            "tokens": {},
        }