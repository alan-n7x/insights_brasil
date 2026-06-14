import streamlit as st
import plotly.express as px


def format_number(n: int) -> str:
    # formata número com separador de milhar como ponto
    return f"{n:,}".replace(",", ".")


def bar_ranking(
    # gráfico de barras para ranking
    df,
    x: str,
    y: str,
    title: str = "",
    top_n: int | None = None
):
    if top_n:
        df = df.head(top_n)

    fig = px.bar(
        df,
        x=x,
        y=y,
        text=y,
        title=title
    )

    fig.update_traces(texttemplate='%{text:,}', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)


def metric_card(label: str, value: str):
    # card para exibir métrica
    st.metric(label, value)