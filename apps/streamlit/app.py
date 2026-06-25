from pathlib import Path
import streamlit as st
from PIL import Image


BASE_DIR = Path(__file__).resolve().parent


def load_css(file_name):
    css_path = BASE_DIR / "assets" / file_name
    
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )


st.set_page_config(
    page_title="Insight Brasil",
    page_icon="📊",
    layout="wide"
)


# Carrega CSS
load_css("style.css")


logo_path = BASE_DIR / "assets" / "logo.png"

logo = Image.open(logo_path)

st.logo(
    logo,
    size="large"
)


st.title("Insight Brasil")
st.caption(
    "Indicadores socioeconômicos do Brasil usando dados do IBGE"
)


pages = [
    st.Page(
        "pages/home.py",
        title="Início",
        icon="🏠"
    ),

    st.Page(
        "pages/estados.py",
        title="Estados",
        icon="🗺️"
    ),
]


pg = st.navigation(pages)

pg.run()