import altair as alt
import pandas as pd
import streamlit as st
from decimal import Decimal


# -----------------------------
# NORMALIZAÇÃO DE DADOS
# -----------------------------
def to_number(series):
    """
    Converte números BR/EN para float seguro.
    Aceita:
    - "1.234,56"
    - "1234.56"
    - 1234
    """
    if series is None:
        return pd.Series(dtype="float64")

    normalized = series.astype(str).str.strip()

    # detecta formato brasileiro
    br_mask = normalized.str.contains(",", regex=False)

    normalized = normalized.where(
        ~br_mask,
        normalized.str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
    )

    return pd.to_numeric(normalized, errors="coerce").fillna(0.0).astype(float)


# -----------------------------
# FORMATAÇÃO VISUAL
# -----------------------------
import math


import math


def format_number(value, indicador=None):
    if value is None:
        return "0"

    try:
        value = float(value)
    except (TypeError, ValueError):
        return "0"

    if math.isnan(value):
        return "0"

    # -----------------------
    # PIB (vem em milhares do IBGE)
    # -----------------------
    if indicador in {"PIB", "PIB_TOTAL"}:
        value *= 1000

        if abs(value) >= 1_000_000_000_000:
            return f"{value / 1_000_000_000_000:.2f} tri"

        if abs(value) >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f} bi"

        if abs(value) >= 1_000_000:
            return f"{value / 1_000_000:.2f} mi"

        if abs(value) >= 1_000:
            return f"{value / 1_000:.2f} mil"

        return f"{value:.2f}"

    # -----------------------
    # POPULAÇÃO (inteiro)
    # -----------------------
    elif indicador == "POPULACAO":
        return f"{int(value):,}".replace(",", ".")

    # -----------------------
    # PIB PER CAPITA (moeda com escala)
    # -----------------------
    elif indicador == "PIB_PER_CAPITA":

        if abs(value) >= 1_000_000_000_000:
            return f"R$ {value / 1_000_000_000_000:.2f} tri"

        if abs(value) >= 1_000_000_000:
            return f"R$ {value / 1_000_000_000:.2f} bi"

        if abs(value) >= 1_000_000:
            return f"R$ {value / 1_000_000:.2f} mi"

        if abs(value) >= 1_000:
            return f"R$ {value / 1_000:.2f} mil"

        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # -----------------------
    # fallback (IDH, taxas, etc.)
    # -----------------------
    return f"{value:.2f}"


def metric_card(label, value, indicador=None):
    st.metric(label, format_number(value, indicador))


# -----------------------------
# GRÁFICO: BARRAS HORIZONTAIS
# -----------------------------
def horizontal_bar(df, label_col, value_col, title):
    if df is None or df.empty:
        st.info("Sem dados para exibir.")
        return

    df = df.copy()
    df[value_col] = to_number(df[value_col])

    df = df.sort_values(value_col, ascending=False)

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(f"{value_col}:Q", title="Valor"),
            y=alt.Y(f"{label_col}:N", sort=None, title=""),
            tooltip=[
                alt.Tooltip(f"{label_col}:N"),
                alt.Tooltip(f"{value_col}:Q", format=",.2f"),
            ],
        )
        .properties(
            title=title,
            height=max(260, min(520, len(df) * 28)),
        )
    )

    st.altair_chart(chart, use_container_width=True)


# -----------------------------
# GRÁFICO: LINHA TEMPORAL
# -----------------------------
def line_chart(df, x_col, y_col, title):

    if df is None or df.empty:
        st.info("Sem dados para exibir.")
        return

    df = df.copy()

    # garante tipos corretos
    df[x_col] = pd.to_numeric(df[x_col], errors="coerce").fillna(0).astype(int)

    df[y_col] = to_number(df[y_col])

    # ordena pelos anos
    df = df.sort_values(x_col)

    # converte para string para evitar 2,006
    df[x_col] = df[x_col].astype(str)

    chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                f"{x_col}:N",
                title="Ano",
                sort=df[x_col].tolist(),
            ),
            y=alt.Y(
                f"{y_col}:Q",
                title="Valor",
            ),
            tooltip=[
                alt.Tooltip(
                    f"{x_col}:N",
                    title="Ano",
                ),
                alt.Tooltip(
                    f"{y_col}:Q",
                    title="Valor",
                    format=",.2f",
                ),
            ],
        )
        .properties(
            title=title,
            height=320,
        )
    )

    st.altair_chart(chart, use_container_width=True)
