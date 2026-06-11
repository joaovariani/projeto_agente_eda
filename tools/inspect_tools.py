"""
Ferramentas de inspeção do dataset.

Estas tools respondem a perguntas do tipo "o que tem nesse CSV?"
e geralmente são as PRIMEIRAS a serem chamadas pelo agente quando
ele recebe uma pergunta nova.
"""

from .base import tool, state


# ========================================================
# listar_colunas
# ========================================================

@tool(
    description=(
        "Retorna a lista de colunas do dataset com seus tipos. "
        "Use esta tool SEMPRE que precisar saber quais colunas existem "
        "antes de operar sobre elas."
    ),
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    },
)
def listar_colunas() -> dict:
    df = state.require_loaded()
    return {
        "colunas": [
            {"nome": col, "tipo": str(df[col].dtype)}
            for col in df.columns
        ],
        "total_linhas": len(df),
        "total_colunas": len(df.columns),
    }


# ========================================================
# descrever_dados
# ========================================================

@tool(
    description=(
        "Retorna estatísticas descritivas do dataset (média, mediana, "
        "desvio padrão, mín, máx para numéricas; contagem e moda para "
        "categóricas). Equivalente a df.describe() estendido."
    ),
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    },
)
def descrever_dados() -> dict:
    df = state.require_loaded()
    resultado = {}

    # Colunas numéricas
    num_cols = df.select_dtypes(include="number").columns.tolist()
    if num_cols:
        desc = df[num_cols].describe().round(4)
        resultado["numericas"] = desc.to_dict()

    # Colunas categóricas
    cat_cols = df.select_dtypes(include=["object", "bool", "category"]).columns.tolist()
    cat_info = {}
    for col in cat_cols:
        vc = df[col].value_counts()
        cat_info[col] = {
            "total_unicos": int(df[col].nunique()),
            "mais_frequente": str(vc.index[0]) if len(vc) > 0 else None,
            "frequencia_mais_frequente": int(vc.iloc[0]) if len(vc) > 0 else 0,
            "nulos": int(df[col].isna().sum()),
        }
    if cat_info:
        resultado["categoricas"] = cat_info

    return resultado


# ========================================================
# contar_valores
# ========================================================

@tool(
    description=(
        "Retorna a distribuição de valores de uma coluna específica. "
        "Útil para entender categorias, frequências e valores únicos."
    ),
    parameters={
        "type": "object",
        "properties": {
            "coluna": {
                "type": "string",
                "description": "Nome da coluna para contar os valores.",
            },
            "top_n": {
                "type": "integer",
                "description": "Quantos valores retornar (padrão: 20).",
            },
        },
        "required": ["coluna"],
    },
)
def contar_valores(coluna: str, top_n: int = 20) -> dict:
    df = state.require_loaded()
    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não existe. Use listar_colunas() para ver as disponíveis."}

    vc = df[coluna].value_counts().head(top_n)
    return {
        "coluna": coluna,
        "total_unicos": int(df[coluna].nunique()),
        "nulos": int(df[coluna].isna().sum()),
        "distribuicao": [
            {"valor": str(k), "contagem": int(v)}
            for k, v in vc.items()
        ],
    }
# ========================================================
# buscar_registros (tool extra)
# ========================================================

@tool(
    description=(
        "Retorna registros completos do dataset que atendem a uma condição, "
        "incluindo todas as colunas (nome da música, artista, etc). "
        "Use quando precisar saber o nome, artista ou qualquer campo textual "
        "de registros específicos. Ex: músicas com popularity == 100."
    ),
    parameters={
        "type": "object",
        "properties": {
            "condicao": {
                "type": "string",
                "description": "Expressão de filtro válida para df.query(). Ex: \"popularity == 100\"",
            },
            "colunas": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Colunas a retornar (padrão: track_name, artists, track_genre, popularity).",
            },
            "limite": {
                "type": "integer",
                "description": "Número máximo de registros a retornar (padrão: 10).",
            },
        },
        "required": ["condicao"],
    },
)
def buscar_registros(condicao: str, colunas: list = None, limite: int = 10) -> dict:
    df = state.require_loaded()

    try:
        df_filtrado = df.query(condicao)
    except Exception as e:
        return {"erro": f"Condição inválida: {e}"}

    if df_filtrado.empty:
        return {"aviso": "Nenhum registro encontrado.", "total": 0}

    if colunas is None:
        colunas = ["track_name", "artists", "track_genre", "popularity"]

    colunas_validas = [c for c in colunas if c in df.columns]
    if not colunas_validas:
        return {"erro": "Nenhuma das colunas informadas existe no dataset."}

    registros = df_filtrado[colunas_validas].head(limite).to_dict(orient="records")

    return {
        "total_encontrados": len(df_filtrado),
        "retornados": len(registros),
        "registros": registros,
    }