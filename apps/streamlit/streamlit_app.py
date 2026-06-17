import os

import altair as alt
import pandas as pd
import requests
import streamlit as st


API_BASE_URL = os.getenv("INSIGHTS_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_ANOS = f"{API_BASE_URL}/api/ibge/populacao/anos/"
API_RANKING = f"{API_BASE_URL}/api/ibge/populacao/ranking-estados/"


st.title("IBGE Dashboard - População")


# =========================
# ANOS DISPONÍVEIS
# =========================

response = requests.get(API_ANOS, timeout=10)

if response.status_code != 200:
    st.error("Erro ao buscar anos da API")
    st.stop()


anos = response.json()

if not anos:
    st.warning("Nenhum ano disponível")
    st.stop()


ano = st.selectbox(
    "Selecione o ano",
    sorted(anos),
    index=len(anos) - 1,
)


# =========================
# RANKING
# =========================

response = requests.get(
    API_RANKING,
    params={
        "ano": ano,
    },
    timeout=10,
)

if response.status_code != 200:
    st.error("Erro ao buscar ranking")
    st.stop()


data = response.json()

df = pd.DataFrame(data)


if df.empty:
    st.warning("Sem dados")
    st.stop()


df = df.rename(
    columns={
        "estado": "Estado",
        "total": "População",
    }
)


df["População"] = pd.to_numeric(df["População"])


df = df.sort_values(
    "População",
    ascending=False,
)


# =========================
# TABELA
# =========================

st.subheader(f"Ranking Populacional - {ano}")

st.dataframe(
    df,
    use_container_width=True,
)


# =========================
# GRÁFICO
# =========================

chart = (
    alt.Chart(df)
    .mark_bar()
    .encode(
        x=alt.X(
            "População:Q",
            title="População",
        ),
        y=alt.Y(
            "Estado:N",
            sort="-x",
            title="Estado",
        ),
        tooltip=[
            "Estado",
            "População",
        ],
    )
)

st.altair_chart(
    chart,
    use_container_width=True,
)
