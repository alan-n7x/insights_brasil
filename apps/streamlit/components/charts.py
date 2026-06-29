"""Gráficos Plotly para visualização de indicadores no dashboard."""
import plotly.express as px
import pandas as pd


def population_by_region_chart(data):
    """Gera gráfico de barras da população por região.

    Args:
        data: Dicionário ou DataFrame com colunas Regiao e Populacao.

    Returns:
        Figura Plotly configurada.
    """
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    else:
        df = data

    fig = px.bar(
        df,
        x="Regiao",
        y="Populacao",
        title="População por Região",
        labels={"Populacao": "População", "Regiao": "Região"},
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_yaxes(tickformat=",.0f")
    return fig


def state_ranking_chart(data):
    """Gera gráfico de barras do ranking populacional dos estados.

    Args:
        data: Dicionário ou DataFrame com colunas Estado e Populacao.

    Returns:
        Figura Plotly configurada.
    """
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    else:
        df = data

    df = df.sort_values("Populacao", ascending=False)

    fig = px.bar(
        df,
        x="Estado",
        y="Populacao",
        title="Ranking dos Estados por População",
        labels={"Populacao": "População", "Estado": "Estado"},
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_yaxes(tickformat=",.0f")
    return fig
