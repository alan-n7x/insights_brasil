import pandas as pd
import requests
import streamlit as st

from api_client import InsightsAPIClient
from charts.charts import (
    format_number,
    horizontal_bar,
    line_chart,
    metric_card,
    to_number,
)
from config import API_BASE_URL, DEFAULT_INDICATOR

RATIO_INDICATORS = {"PIB_PER_CAPITA"}


def safe_load(label, callback):
    try:
        return callback()
    except requests.RequestException as exc:
        st.error(f"Erro ao carregar {label}: {exc}")
        st.stop()


def normalize_indicator_df(df, value_col, indicador):
    if df.empty or value_col not in df.columns:
        return df

    df = df.copy()

    df[value_col] = to_number(df[value_col])

    df["valor_formatado"] = df[value_col].apply(lambda x: format_number(x, indicador))

    return df


def current_year_value(df, year):
    if df.empty or "ano" not in df.columns or "total" not in df.columns:
        return 0

    current = df[df["ano"] == year]

    if current.empty:
        return 0

    return current.iloc[0]["total"]


client = InsightsAPIClient()

st.set_page_config(
    page_title="Insights Brasil",
    page_icon=":bar_chart:",
    layout="wide",
)

st.title("Insights Brasil")
st.caption("Dashboard de indicadores socioeconômicos por estado e município")

with st.sidebar:
    st.header("Insights Brasil")
    st.caption(f"API: {API_BASE_URL}")

    indicadores = safe_load("indicadores", client.listar_indicadores)

    if not indicadores:
        st.warning(
            "Nenhum indicador encontrado. Rode os comandos de ingestão primeiro."
        )
        st.stop()

    indicador_options = {item["codigo"]: item["nome"] for item in indicadores}
    codigos = list(indicador_options)
    default_index = (
        codigos.index(DEFAULT_INDICATOR) if DEFAULT_INDICATOR in codigos else 0
    )

    indicador = st.selectbox(
        "Indicador",
        options=codigos,
        index=default_index,
        format_func=lambda codigo: f"{codigo} - {indicador_options[codigo]}",
    )

    anos = safe_load("anos", lambda: client.listar_anos(indicador))

    if not anos:
        st.warning("Este indicador ainda não tem anos disponíveis.")
        st.stop()

    ano = st.selectbox(
        "Ano",
        options=sorted(anos),
        index=len(anos) - 1,
    )

    estados = safe_load("estados", client.listar_estados)
    estado_options = {"Todos": None}
    estado_options.update(
        {f"{item['nome']} ({item['sigla']})": item["id"] for item in estados}
    )

    estado_label = st.selectbox(
        "Estado",
        options=list(estado_options),
    )
    estado_id = estado_options[estado_label]

    municipios = safe_load("municípios", client.listar_municipios)
    municipios_filtrados = [
        item
        for item in municipios
        if estado_id is None or item["estado_id"] == estado_id
    ]

    municipio_options = {"Todos": None}
    municipio_options.update(
        {
            f"{item['nome']} ({item['ibge_id']})": item["ibge_id"]
            for item in municipios_filtrados
        }
    )

    municipio_label = st.selectbox(
        "Município",
        options=list(municipio_options),
    )
    municipio_ibge_id = municipio_options[municipio_label]

    top_n = st.slider("Top municípios", min_value=5, max_value=50, value=20, step=5)


ranking_estados = safe_load(
    "ranking por estados",
    lambda: client.ranking_estados(indicador, ano=ano),
)
ranking_municipios = safe_load(
    "ranking por municípios",
    lambda: client.ranking_municipios(
        indicador,
        ano=ano,
        estado_id=estado_id,
        limit=top_n,
    ),
)
evolucao_estado = safe_load(
    "evolução",
    lambda: client.evolucao_estado(indicador, estado_id=estado_id),
)
evolucao_municipio = (
    safe_load(
        "evolução municipal",
        lambda: client.evolucao_municipio(indicador, municipio_ibge_id),
    )
    if municipio_ibge_id
    else []
)

df_estados = normalize_indicator_df(
    pd.DataFrame(ranking_estados),
    "total",
    indicador,
)

df_municipios = normalize_indicator_df(
    pd.DataFrame(ranking_municipios),
    "total",
    indicador,
)

df_evolucao = normalize_indicator_df(
    pd.DataFrame(evolucao_estado),
    "total",
    indicador,
)

df_evolucao_municipio = normalize_indicator_df(
    pd.DataFrame(evolucao_municipio),
    "valor",
    indicador,
)
if not df_estados.empty:
    df_estados = df_estados.sort_values("total", ascending=False)

if not df_municipios.empty:
    df_municipios = df_municipios.sort_values("total", ascending=False)

col1, col2, col3, col4 = st.columns(4)

if indicador in RATIO_INDICATORS:
    valor_principal = current_year_value(df_evolucao, ano)
    valor_principal_label = f"Valor Brasil {ano}"
else:
    valor_principal = df_estados["total"].sum() if not df_estados.empty else 0
    valor_principal_label = f"Total {ano}"

maior_estado = df_estados.iloc[0]["estado"] if not df_estados.empty else "-"
maior_municipio = df_municipios.iloc[0]["municipio"] if not df_municipios.empty else "-"
anos_disponiveis = len(anos)

with col1:
    metric_card(valor_principal_label, valor_principal, indicador)

with col2:
    st.metric("Líder estadual", maior_estado)

with col3:
    st.metric("Líder municipal", maior_municipio)

with col4:
    st.metric("Anos disponíveis", anos_disponiveis)

left, right = st.columns([1.15, 1])

with left:
    horizontal_bar(
        df_estados,
        label_col="estado",
        value_col="total",
        title=f"Ranking por estado - {indicador} ({ano})",
    )

with right:
    if municipio_ibge_id:
        line_chart(
            df_evolucao_municipio,
            x_col="ano",
            y_col="valor",
            title=f"Evolução municipal - {municipio_label}",
        )
    else:
        line_chart(
            df_evolucao,
            x_col="ano",
            y_col="total",
            title=f"Evolução - {indicador}",
        )

st.subheader("Ranking por município")

if df_municipios.empty:
    st.info("Sem municípios para os filtros selecionados.")
else:
    horizontal_bar(
        df_municipios,
        label_col="municipio",
        value_col="total",
        title=f"Top {top_n} municípios - {indicador} ({ano})",
    )

    st.dataframe(
        df_municipios[
            [
                "municipio",
                "municipio_ibge_id",
                "estado",
                "sigla",
                "total",
                "valor_formatado",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


def normalize_municipio_evolucao(data):
    df = pd.DataFrame(data)

    if df.empty:
        return df

    df["ano"] = df["ano"].astype(int)
    df["valor"] = df["valor"].astype(float)

    return df


evolucao_municipio = safe_load(
    "evolução municipal",
    lambda: client.evolucao_municipio(
        indicador, municipio_ibge_id, ano_inicio=2010, ano_fim=2022
    ),
)

if municipio_ibge_id:

    municipio_nome = municipio_label.split(" (")[0]

    municipio_ano_row = df_evolucao_municipio[df_evolucao_municipio["ano"] == ano]

    valor = 0
    if not municipio_ano_row.empty:
        valor = municipio_ano_row.iloc[0]["valor"]

    municipio_row = df_municipios[
        df_municipios["municipio_ibge_id"] == municipio_ibge_id
    ]

    ranking = "-"
    if not municipio_row.empty:
        ranking = municipio_row.iloc[0].name + 1

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Município", municipio_nome)

    with col2:
        st.metric("Ranking", ranking)

    with col3:
        st.metric("Ano", ano)

    with col4:
        st.metric("Valor", format_number(valor, indicador))
