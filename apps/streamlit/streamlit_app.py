from charts.charts import bar_ranking

import streamlit as st
import requests
import pandas as pd


API_ANOS = "http://127.0.0.1:8000/api/ibge/anos/"
API_RANKING = "http://127.0.0.1:8000/api/ibge/ranking/estados/"


# anos disponíveis

anos = requests.get(API_ANOS).json()

ano = st.selectbox(
    "Selecione o ano",
    anos,
    index=len(anos) - 1
)


# ranking do ano selecionado

data = requests.get(
    API_RANKING,
    params={"ano": ano}
).json()


df = pd.DataFrame(data)


df = df.rename(
    columns={
        "estado": "estado",
        "total": "populacao"
    }
)


df = df.sort_values(
    "populacao",
    ascending=False
)


st.title("Ranking Populacional IBGE")


bar_ranking(
    df,
    x="estado",
    y="populacao",
    title=f"Estados mais populosos - {ano}"
)