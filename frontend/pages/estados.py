"""Página de listagem e ranking dos estados brasileiros."""
import logging
import streamlit as st
import pandas as pd
from api.client import get_estados, get_ranking

logger = logging.getLogger(__name__)

st.title("Estados")

with st.spinner("Carregando estados..."):
    try:
        estados = get_estados()
        df = pd.DataFrame(estados)
        st.dataframe(df, hide_index=True, width='stretch')
        logger.info("Estados carregados: %s", len(df))
    except Exception as e:
        st.error(f"Erro ao carregar estados: {e}")
        logger.exception("Falha ao carregar estados")

st.divider()

st.subheader("Ranking Populacional")

with st.spinner("Carregando ranking..."):
    try:
        ranking = get_ranking("populacao", limit=27)
        itens = ranking if isinstance(ranking, list) else []
        if itens:
            df_rank = pd.DataFrame(itens)
            st.dataframe(df_rank, hide_index=True, width='stretch')
            logger.info("Ranking carregado: %s estados", len(df_rank))
    except Exception as e:
        st.error(f"Erro ao carregar ranking: {e}")
        logger.exception("Falha ao carregar ranking")
