"""Ponto de entrada do dashboard Streamlit Insight Brasil.

Exibe indicadores socioeconômicos do Brasil usando dados do IBGE,
com painéis interativos, gráficos por região e ranking de estados.
"""
import logging
from pathlib import Path
import streamlit as st
from PIL import Image

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent


def load_css(file_name):
    """Carrega e injeta um arquivo CSS no Streamlit.

    Args:
        file_name: Nome do arquivo CSS dentro do diretório assets.
    """
    css_path = BASE_DIR / "assets" / file_name
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


st.set_page_config(page_title="Insight Brasil", page_icon="📊", layout="wide")

load_css("style.css")

logo_path = BASE_DIR / "assets" / "logo.png"
logo = Image.open(logo_path)
st.logo(logo, size="large")

st.title("Insight Brasil")
st.caption("Indicadores socioeconômicos do Brasil usando dados do IBGE")

pages = [
    st.Page("pages/home.py", title="Dashboard", icon="🏠"),
    st.Page("pages/estados.py", title="Estados", icon="🗺️"),
]

pg = st.navigation(pages)
pg.run()