"""Página inicial do dashboard com indicadores principais, ranking e gráficos."""
import logging
import streamlit as st
from components.cards import metric_card
from components.charts import population_by_region_chart, state_ranking_chart
from services.dashboard import carregar_resumo, carregar_ranking_estados, carregar_dados_por_regiao
from utils.formatting import format_int, format_brl

logger = logging.getLogger(__name__)

st.subheader("Indicadores Principais")

with st.spinner("Carregando indicadores..."):
    try:
        resumo = carregar_resumo()
        logger.info("Resumo carregado: pop=%s pib=%s pc=%s", resumo["populacao"], resumo["pib"], resumo["pib_per_capita"])
    except Exception as e:
        st.error(f"Erro ao carregar resumo: {e}")
        logger.exception("Falha ao carregar resumo")
        resumo = {"populacao": 0, "pib": 0, "pib_per_capita": 0}

col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card(label="População Total", value=format_int(resumo["populacao"]))
with col2:
    metric_card(label="PIB Total", value=format_brl(resumo["pib"]))
with col3:
    metric_card(label="PIB per Capita", value=format_brl(resumo["pib_per_capita"]))
with col4:
    metric_card(label="Ano de Referência", value=str(resumo["ano"]))

st.divider()
st.subheader("Visão Geral")

with st.spinner("Carregando ranking..."):
    try:
        state_data = carregar_ranking_estados(limit=10)
        logger.info("Ranking carregado: %s estados", len(state_data["Estado"]))
    except Exception as e:
        st.error(f"Erro ao carregar ranking: {e}")
        logger.exception("Falha ao carregar ranking")
        state_data = {"Estado": [], "Populacao": []}

with st.spinner("Carregando dados por região..."):
    try:
        region_data = carregar_dados_por_regiao()
        logger.info("Regiões carregadas")
    except Exception as e:
        st.error(f"Erro ao carregar dados regionais: {e}")
        logger.exception("Falha ao carregar dados regionais")
        region_data = {"Regiao": [], "Populacao": []}

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(population_by_region_chart(region_data), width='stretch')
with col2:
    st.plotly_chart(state_ranking_chart(state_data), width='stretch')
