# client.py

import requests

BASE_URL = "http://127.0.0.1:8000/ibge/api"


def api_get(endpoint):
    response = requests.get(f"{BASE_URL}/{endpoint}/")

    response.raise_for_status()

    return response.json()


def get_estados():
    return api_get("estados")


def get_municipios():
    return api_get("municipios")


def get_indicadores():
    return api_get("indicadores")
