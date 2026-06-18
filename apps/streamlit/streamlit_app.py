import pandas as pd
import requests
import streamlit as st

from api_client import InsightsAPIClient
from charts.charts import horizontal_bar, line_chart, metric_card, to_number
from config import API_BASE_URL, DEFAULT_INDICATOR


def safe_load(label, callback):
    try:
        return callback()
    except requests.RequestException as exc:
        st.error(f"Erro ao carregar {label}: {exc}")
        st.stop()


client = InsightsAPIClient()

st.set_page_config(
    page_title="Insights Brasil",
    page_icon=":bar_chart:",
    layout="wide",
)

st.title("Insights Brasil")
st.caption("Dashboard de indicadores socioeconômicos por estado e município")

with st.sidebar:
    st.header("Filtros")
    st.caption(f"API: {API_BASE_URL}")

    indicadores = safe_load("indicadores", client.listar_indicadores)

    if not indicadores:
        st.warning("Nenhum indicador encontrado. Rode os comandos de ingestão primeiro.")
        st.stop()

    indicador_options = {item["codigo"]: item["nome"] for item in indicadores}
    default_index = list(indicador_options).index(DEFAULT_INDICATOR) if DEFAULT_INDICATOR in indicador_options else 0

    indicador = st.selectbox(
        "Indicador",
        options=list(indicador_options),
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
    estado_options.update({f"{item['nome']} ({item['sigla']})": item["id"] for item in estados})

    estado_label = st.selectbox(
        "Estado",
        options=list(estado_options),
    )
    estado_id = estado_options[estado_label]

    municipios = safe_load("municípios", client.listar_municipios)
    municipios_filtrados = [
        item for item in municipios if estado_id is None or item["estado_id"] == estado_id
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

df_estados = pd.DataFrame(ranking_estados)
df_municipios = pd.DataFrame(ranking_municipios)
df_evolucao = pd.DataFrame(evolucao_estado)
df_evolucao_municipio = pd.DataFrame(evolucao_municipio)

for df in (df_estados, df_municipios, df_evolucao, df_evolucao_municipio):
    if not df.empty:
        value_col = "total" if "total" in df.columns else "valor"
        df[value_col] = to_number(df[value_col])

col1, col2, col3, col4 = st.columns(4)

total_brasil = df_estados["total"].sum() if not df_estados.empty else 0
maior_estado = df_estados.iloc[0]["estado"] if not df_estados.empty else "-"
maior_municipio = df_municipios.iloc[0]["municipio"] if not df_municipios.empty else "-"
anos_disponiveis = len(anos)

with col1:
    metric_card(f"Total {ano}", total_brasil)

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
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

st.subheader("Dados por estado")

if df_estados.empty:
    st.info("Sem estados para os filtros selecionados.")
else:
    st.dataframe(
        df_estados,
        use_container_width=True,
        hide_index=True,
    )
