from charts.charts import bar_ranking, format_number

import streamlit as st
import requests
import pandas as pd


API_URL = "http://127.0.0.1:8000/api/ibge/ranking/estados/"

data = requests.get(API_URL).json()
df = pd.DataFrame(data)

df = df.rename(columns={
    "municipio__estado__nome": "estado",
    "total": "populacao"
})

df = df.sort_values("populacao", ascending=False)

st.title("Ranking Populacional IBGE")

bar_ranking(
    df,
    x="estado",
    y="populacao",
    title="Estados mais populosos",
    # top_n=27
)