"""
Ferramentas de visualização: geração de gráficos salvos como imagem.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from .base import tool, state
from config import OUTPUTS_DIR


# ========================================================
# gerar_grafico
# ========================================================

@tool(
    description=(
        "Gera e salva um gráfico como imagem na pasta outputs/. "
        "Tipos disponíveis: histograma, boxplot, scatter, barplot. "
        "Retorna o caminho do arquivo salvo."
    ),
    parameters={
        "type": "object",
        "properties": {
            "tipo": {
                "type": "string",
                "description": "Tipo do gráfico: histograma, boxplot, scatter, barplot.",
            },
            "colunas": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "Lista de colunas a usar. "
                    "histograma/boxplot: 1 coluna. "
                    "scatter: 2 colunas [x, y]. "
                    "barplot: 2 colunas [categoria, valor]."
                ),
            },
            "titulo": {
                "type": "string",
                "description": "Título opcional do gráfico.",
            },
        },
        "required": ["tipo", "colunas"],
    },
)
def gerar_grafico(tipo: str, colunas: list, titulo: str = "") -> dict:
    df = state.require_loaded()

    tipos_validos = ["histograma", "boxplot", "scatter", "barplot"]
    if tipo not in tipos_validos:
        return {"erro": f"Tipo '{tipo}' inválido. Use: {tipos_validos}"}

    for col in colunas:
        if col not in df.columns:
            return {"erro": f"Coluna '{col}' não existe. Use listar_colunas() para ver as disponíveis."}

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.set_theme(style="whitegrid")

    try:
        if tipo == "histograma":
            sns.histplot(data=df, x=colunas[0], kde=True, ax=ax)
            ax.set_xlabel(colunas[0])

        elif tipo == "boxplot":
            sns.boxplot(data=df, y=colunas[0], ax=ax)

        elif tipo == "scatter":
            if len(colunas) < 2:
                return {"erro": "scatter requer 2 colunas: [x, y]."}
            sns.scatterplot(data=df, x=colunas[0], y=colunas[1], alpha=0.3, ax=ax)

        elif tipo == "barplot":
            if len(colunas) < 2:
                return {"erro": "barplot requer 2 colunas: [categoria, valor]."}
            dados = (
                df.groupby(colunas[0])[colunas[1]]
                .mean()
                .sort_values(ascending=False)
                .head(15)
                .reset_index()
            )
            sns.barplot(data=dados, x=colunas[1], y=colunas[0], ax=ax)

        ax.set_title(titulo or f"{tipo} — {', '.join(colunas)}")
        plt.tight_layout()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"{tipo}_{'_'.join(colunas)}_{timestamp}.png"
        caminho = OUTPUTS_DIR / nome_arquivo
        fig.savefig(caminho, dpi=100)
        plt.close(fig)

        return {
            "arquivo": str(caminho),
            "tipo": tipo,
            "colunas": colunas,
            "mensagem": f"Gráfico salvo em {caminho}",
        }

    except Exception as e:
        plt.close(fig)
        return {"erro": f"Erro ao gerar gráfico: {e}"}