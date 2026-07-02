"""Página inicial do dashboard com indicadores principais, ranking e gráficos."""
import logging
import streamlit as st
from components.cards import metric_card
from components.charts import population_by_region_chart, state_ranking_chart
from api.client import get_dashboard_resumo

logger = logging.getLogger(__name__)


def format_int(value):
    """Formata valor inteiro com abreviação brasileira (mi/bi/tri)."""
    if not value:
        return "---"
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f} bi".replace(".", ",")
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f} mi".replace(".", ",")
    return f"{int(value):,}".replace(",", ".")


def format_brl(value):
    """Formata valor monetário no padrão brasileiro (R$)."""
    if not value:
        return "---"
    if value >= 1_000_000_000_000:
        return f"R$ {value / 1_000_000_000_000:.2f} tri".replace(".", ",").replace(",", "X").replace(".", ",").replace("X", ".")
    if value >= 1_000_000_000:
        return f"R$ {value / 1_000_000_000:.2f} bi".replace(".", ",").replace(",", "X").replace(".", ",").replace("X", ".")
    if value >= 1_000_000:
        return f"R$ {value / 1_000_000:.2f} mi".replace(".", ",").replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


st.subheader("Indicadores Principais")

with st.spinner("Carregando dados..."):
    try:
        data = get_dashboard_resumo()
        logger.info("Dashboard carregado: ano=%s pop=%s", data.get("ano"), data.get("populacao_total"))
    except Exception as e:
        st.error(f"Erro ao carregar dashboard: {e}")
        logger.exception("Falha ao carregar dashboard")
        data = {}

resumo = {
    "ano": data.get("ano", "---"),
    "populacao": data.get("populacao_total", 0),
    "pib": data.get("pib_total", 0),
    "pib_per_capita": data.get("pib_per_capita_medio", 0),
}

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

regioes = data.get("populacao_por_regiao", [])
ranking = data.get("ranking_estados", [])

region_data = {
    "Regiao": [r["regiao"] for r in regioes],
    "Populacao": [int(r["valor"]) for r in regioes],
}

state_data = {
    "Estado": [r["estado"] for r in ranking[:10]],
    "Populacao": [int(r["valor"]) for r in ranking[:10]],
}

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(population_by_region_chart(region_data), width='stretch')
with col2:
    st.plotly_chart(state_ranking_chart(state_data), width='stretch')
