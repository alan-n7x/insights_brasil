import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def population_by_region_chart(data):
    """
    Create a bar chart for population by region.

    Args:
        data (dict): Dictionary with region names and population values.
                    Expected format: {'Regiao': [...], 'Populacao': [...]}
                    or any format that can be converted to a DataFrame.

    Returns:
        plotly.graph_objs._figure.Figure: A Plotly bar chart figure.
    """
    # Convert to DataFrame if needed
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    else:
        df = data

    # Assuming columns are named appropriately; adjust as needed
    # For now, using placeholder column names
    fig = px.bar(df, x='Regiao', y='Populacao',
                 title='População por Região',
                 labels={'Populacao': 'População (milhões)', 'Regiao': 'Região'})
    fig.update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    return fig


def state_ranking_chart(data):
    """
    Create a bar chart for state ranking by population.

    Args:
        data (dict): Dictionary with state names and population values.
                    Expected format: {'Estado': [...], 'Populacao': [...]}

    Returns:
        plotly.graph_objs._figure.Figure: A Plotly bar chart figure.
    """
    # Convert to DataFrame if needed
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    else:
        df = data

    # Sort by population descending for ranking
    df = df.sort_values('Populacao', ascending=False)

    fig = px.bar(df, x='Estado', y='Populacao',
                 title='Ranking dos Estados por População',
                 labels={'Populacao': 'População (milhões)', 'Estado': 'Estado'})
    fig.update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    return fig