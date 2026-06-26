import streamlit as st
from components.cards import metric_card
from components.charts import population_by_region_chart, state_ranking_chart
import plotly.express as px
import pandas as pd

from api.client import get_kpis

st.subheader("Indicadores Principais")
col1, col2, col3, col4 = st.columns(4)
kpis = get_kpis(["populacao"], ano=2021)

populacao_raw = kpis.get("POPULACAO", {}).get("valor", 0)

# 🔥 força inteiro (remove .0)
populacao = int(populacao_raw)

populacao_formatada = f"{populacao:,}".replace(",", ".")

st.subheader("Indicadores Principais")
col1, col2, col3, col4 = st.columns(4)

with col1:
    metric_card(
        label="População Total do Brasil", value=f"{populacao:,}".replace(",", ".")
    )

with col2:
    metric_card(label="Quantidade de Estados", value="26 estados + DF")
with col3:
    metric_card(label="Região Mais Populosa", value="Sudeste")
with col4:
    metric_card(label="Estado Mais Populoso", value="São Paulo")

st.divider()

st.subheader("Visão Geral")

# Mock data for charts
region_population_data = {
    "Regiao": ["Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"],
    "Populacao": [20, 55, 90, 15, 30],
}

state_population_data = {
    "Estado": ["SP", "MG", "RJ", "BA", "PR", "RS", "PE", "CE", "PA", "SC"],
    "Populacao": [46, 21, 17, 15, 11, 11, 9, 9, 8, 7],
}

col1, col2 = st.columns(2)

with col1:
    fig_region = population_by_region_chart(region_population_data)
    st.plotly_chart(fig_region, width="stretch")

with col2:
    fig_state = state_ranking_chart(state_population_data)
    st.plotly_chart(fig_state, width="stretch")
