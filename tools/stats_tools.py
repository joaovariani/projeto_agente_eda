"""
Ferramentas estatísticas do dataset.

Correlação entre colunas e detecção de outliers.
"""

import pandas as pd
from .base import tool, state


# ========================================================
# correlacao
# ========================================================

@tool(
    description=(
        "Calcula a correlação entre duas colunas numéricas. "
        "Retorna os coeficientes de Pearson e Spearman. "
        "Útil para identificar relações lineares e monotônicas entre variáveis."
    ),
    parameters={
        "type": "object",
        "properties": {
            "coluna1": {
                "type": "string",
                "description": "Nome da primeira coluna numérica.",
            },
            "coluna2": {
                "type": "string",
                "description": "Nome da segunda coluna numérica.",
            },
        },
        "required": ["coluna1", "coluna2"],
    },
)
def correlacao(coluna1: str, coluna2: str) -> dict:
    df = state.require_loaded()

    for col in [coluna1, coluna2]:
        if col not in df.columns:
            return {"erro": f"Coluna '{col}' não existe. Use listar_colunas() para ver as disponíveis."}

    for col in [coluna1, coluna2]:
        if not pd.api.types.is_numeric_dtype(df[col]):
            return {"erro": f"Coluna '{col}' não é numérica."}

    pearson = float(f"{df[coluna1].corr(df[coluna2], method='pearson'):.4f}")
    # Spearman = Pearson dos ranks (não requer scipy)
    spearman = float(f"{df[coluna1].rank().corr(df[coluna2].rank()):.4f}")

    return {
        "coluna1": coluna1,
        "coluna2": coluna2,
        "pearson": pearson,
        "spearman": spearman,
    }


# ========================================================
# detectar_outliers
# ========================================================

@tool(
    description=(
        "Detecta outliers em uma coluna numérica usando os métodos IQR e Z-score. "
        "Retorna os limites, total de outliers e estatísticas descritivas."
    ),
    parameters={
        "type": "object",
        "properties": {
            "coluna": {
                "type": "string",
                "description": "Nome da coluna numérica para detectar outliers.",
            },
        },
        "required": ["coluna"],
    },
)
def detectar_outliers(coluna: str) -> dict:
    df = state.require_loaded()

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não existe. Use listar_colunas() para ver as disponíveis."}

    if not pd.api.types.is_numeric_dtype(df[coluna]):
        return {"erro": f"Coluna '{coluna}' não é numérica."}

    serie = df[coluna].dropna()

    q1 = float(serie.quantile(0.25))
    q3 = float(serie.quantile(0.75))
    iqr = q3 - q1
    limite_inf = q1 - 1.5 * iqr
    limite_sup = q3 + 1.5 * iqr
    outliers_iqr = serie[(serie < limite_inf) | (serie > limite_sup)]

    std = serie.std()
    if std == 0:
        outliers_zscore = serie[serie != serie.mean()]
    else:
        z_scores = (serie - serie.mean()) / std
        outliers_zscore = serie[abs(z_scores) > 3]

    return {
        "coluna": coluna,
        "iqr": {
            "q1": round(q1, 4),
            "q3": round(q3, 4),
            "iqr": round(iqr, 4),
            "limite_inferior": round(limite_inf, 4),
            "limite_superior": round(limite_sup, 4),
            "total_outliers": len(outliers_iqr),
            "percentual": round(len(outliers_iqr) / len(serie) * 100, 2),
        },
        "zscore": {
            "total_outliers": len(outliers_zscore),
            "percentual": round(len(outliers_zscore) / len(serie) * 100, 2),
        },
        "estatisticas": {
            "min": round(float(serie.min()), 4),
            "max": round(float(serie.max()), 4),
            "media": round(float(serie.mean()), 4),
            "desvio_padrao": round(float(serie.std()), 4),
        },
    }
