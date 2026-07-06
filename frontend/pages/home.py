"""Página inicial do dashboard com indicadores principais, ranking e gráficos."""
import logging
from datetime import datetime

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


with st.spinner("Carregando dados..."):
    try:
        dados_recentes = get_dashboard_resumo()
        anos_disponiveis = dados_recentes.get("anos_disponiveis", [])
        if not anos_disponiveis:
            anos_disponiveis = [dados_recentes.get("ano")]

        ano_selecionado = st.selectbox(
            "Ano de referência",
            options=anos_disponiveis,
            index=0,
            help="Somente anos com dados disponíveis no banco são exibidos.",
        )
        data = (
            dados_recentes
            if ano_selecionado == dados_recentes.get("ano")
            else get_dashboard_resumo(ano=ano_selecionado)
        )
        logger.info("Dashboard carregado: ano=%s pop=%s", data.get("ano"), data.get("populacao_total"))
    except Exception as e:
        st.error(f"Erro ao carregar dashboard: {e}")
        logger.exception("Falha ao carregar dashboard")
        data = {}

st.subheader("Indicadores Principais")

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

st.divider()
st.subheader("Qualidade e origem dos dados")

metadados = data.get("metadados", {})
ultima_atualizacao = metadados.get("ultima_atualizacao")
if ultima_atualizacao:
    try:
        atualizado_em = datetime.fromisoformat(ultima_atualizacao).strftime("%d/%m/%Y %H:%M")
    except (TypeError, ValueError):
        atualizado_em = ultima_atualizacao
else:
    atualizado_em = "---"

periodo_inicio = metadados.get("periodo_inicio")
periodo_fim = metadados.get("periodo_fim")
periodo = f"{periodo_inicio}–{periodo_fim}" if periodo_inicio and periodo_fim else "---"
cobertos = metadados.get("municipios_cobertos", 0)
total = metadados.get("municipios_total", 0)
percentual = metadados.get("cobertura_percentual", 0)
fontes = ", ".join(metadados.get("fontes", [])) or "---"

tech1, tech2, tech3, tech4, tech5 = st.columns(5)
with tech1:
    metric_card("Última atualização", atualizado_em, help_text="Registro mais recentemente atualizado no ano selecionado.")
with tech2:
    metric_card("Período disponível", periodo, help_text="Primeiro e último ano encontrados no banco.")
with tech3:
    metric_card("Municípios cobertos", f"{cobertos:,} de {total:,}".replace(",", "."), help_text="Municípios com população e PIB no ano selecionado.")
with tech4:
    metric_card("Registros ausentes", str(metadados.get("registros_ausentes", 0)), delta=f"{percentual:.1f}% coberto".replace(".", ","), help_text="Municípios sem todos os dados necessários aos cards principais.")
with tech5:
    metric_card("Fonte", fontes, help_text="Fonte declarada para população e PIB.")
