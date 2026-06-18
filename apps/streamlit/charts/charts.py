import altair as alt
import pandas as pd
import streamlit as st


def to_number(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)


def format_number(value):
    value = float(value or 0)

    if abs(value) >= 1_000_000_000_000:
        return f"{value / 1_000_000_000_000:.2f} tri"

    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f} bi"

    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f} mi"

    if abs(value) >= 1_000:
        return f"{value / 1_000:.2f} mil"

    return f"{value:.2f}"


def metric_card(label, value):
    st.metric(label, format_number(value))


def horizontal_bar(df, label_col, value_col, title):
    if df.empty:
        st.info("Sem dados para exibir.")
        return

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(f"{value_col}:Q", title="Valor"),
            y=alt.Y(f"{label_col}:N", sort="-x", title=""),
            tooltip=[label_col, value_col],
        )
        .properties(title=title, height=max(260, min(520, len(df) * 28)))
    )

    st.altair_chart(chart, use_container_width=True)


def line_chart(df, x_col, y_col, title):
    if df.empty:
        st.info("Sem dados para exibir.")
        return

    chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X(f"{x_col}:O", title="Ano"),
            y=alt.Y(f"{y_col}:Q", title="Valor"),
            tooltip=[x_col, y_col],
        )
        .properties(title=title, height=320)
    )

    st.altair_chart(chart, use_container_width=True)
