import streamlit as st
import pandas as pd
from api.client import get_estados


st.title("Estados")


estados = get_estados()

df = pd.DataFrame(estados)


st.dataframe(
    df[["nome", "sigla", "ibge_id"]]
)