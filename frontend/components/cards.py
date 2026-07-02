"""Cartões de métrica para exibição de indicadores no dashboard."""
import streamlit as st


def metric_card(label, value, delta=None, help_text=None):
    """Exibe um cartão de métrica no Streamlit.

    Args:
        label: Rótulo da métrica.
        value: Valor principal a ser exibido.
        delta: Variação opcional a ser destacada.
        help_text: Texto de ajuda opcional exibido ao passar o mouse.
    """
    st.metric(label=label, value=value, delta=delta, help=help_text)