"""
Ferramentas de filtragem e agrupamento do dataset.
"""

from .base import tool, state


# ========================================================
# filtrar
# ========================================================

@tool(
    description=(
        "Filtra o dataset por uma condição e retorna estatísticas do "
        "subconjunto resultante. Use expressões pandas válidas, ex: "
        "\"popularity > 80\", \"track_genre == 'pop'\", "
        "\"energy > 0.8 and danceability > 0.7\"."
    ),
    parameters={
        "type": "object",
        "properties": {
            "condicao": {
                "type": "string",
                "description": "Expressão de filtro válida para df.query().",
            },
        },
        "required": ["condicao"],
    },
)
def filtrar(condicao: str) -> dict:
    df = state.require_loaded()
    try:
        df_filtrado = df.query(condicao)
    except Exception as e:
        return {"erro": f"Condição inválida: {e}"}

    if df_filtrado.empty:
        return {"aviso": "Nenhum registro encontrado com essa condição.", "total": 0}

    num_cols = df_filtrado.select_dtypes(include="number").columns.tolist()
    estatisticas = {}
    if num_cols:
        estatisticas = df_filtrado[num_cols].describe().round(4).to_dict()

    return {
        "condicao": condicao,
        "total_registros": len(df_filtrado),
        "percentual_do_total": round(len(df_filtrado) / len(df) * 100, 2),
        "estatisticas": estatisticas,
    }


# ========================================================
# agrupar_e_agregar
# ========================================================

@tool(
    description=(
        "Agrupa o dataset por uma coluna e aplica uma função de agregação "
        "em outra coluna. Exemplo: média de popularity por track_genre. "
        "Funções disponíveis: mean, median, sum, min, max, count, std."
    ),
    parameters={
        "type": "object",
        "properties": {
            "grupo": {
                "type": "string",
                "description": "Nome da coluna para agrupar (ex: 'track_genre').",
            },
            "coluna": {
                "type": "string",
                "description": "Nome da coluna numérica para agregar (ex: 'popularity').",
            },
            "funcao": {
                "type": "string",
                "description": "Função de agregação: mean, median, sum, min, max, count, std.",
            },
            "top_n": {
                "type": "integer",
                "description": "Quantos grupos retornar ordenados pelo resultado (padrão: 10).",
            },
        },
        "required": ["grupo", "coluna", "funcao"],
    },
)
def agrupar_e_agregar(grupo: str, coluna: str, funcao: str, top_n: int = 10) -> dict:
    df = state.require_loaded()

    funcoes_validas = ["mean", "median", "sum", "min", "max", "count", "std"]
    if funcao not in funcoes_validas:
        return {"erro": f"Função '{funcao}' inválida. Use uma de: {funcoes_validas}"}

    for col in [grupo, coluna]:
        if col not in df.columns:
            return {"erro": f"Coluna '{col}' não existe. Use listar_colunas() para ver as disponíveis."}

    resultado = (
        df.groupby(grupo)[coluna]
        .agg(funcao)
        .round(4)
        .sort_values(ascending=False)
        .head(top_n)
    )

    return {
        "grupo": grupo,
        "coluna": coluna,
        "funcao": funcao,
        "resultado": [
            {"grupo": str(k), "valor": float(v)}
            for k, v in resultado.items()
        ],
    }