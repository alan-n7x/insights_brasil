import streamlit as st
import requests
import pandas as pd

API_ANOS = "http://127.0.0.1:8000/api/ibge/populacao/anos/"
API_RANKING = "http://127.0.0.1:8000/api/ibge/populacao/ranking-estados/"


st.title("📊 IBGE Dashboard - População")

# =========================
# ANOS
# =========================
response = requests.get(API_ANOS)

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
    index=len(anos) - 1
)

# =========================
# RANKING
# =========================
response = requests.get(
    API_RANKING,
    params={"ano": ano}
)

if response.status_code != 200:
    st.error("Erro ao buscar ranking")
    st.stop()

data = response.json()

df = pd.DataFrame(data)

if df.empty:
    st.warning("Sem dados para esse ano")
    st.stop()

df = df.rename(columns={
    "estado": "Estado",
    "total": "População"
})

df = df.sort_values("População", ascending=False)

# =========================
# VISUALIZAÇÃO
# =========================
st.subheader(f"🏆 Ranking Populacional - {ano}")

st.dataframe(df)

st.bar_chart(df.set_index("Estado"))