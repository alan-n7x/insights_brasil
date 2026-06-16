# ibge/urls/populacao.py
from django.urls import path
from ibge.views.populacao import (
    ranking_estados_view,
    evolucao_populacao_view,
    listar_anos_populacao_view
)

urlpatterns = [
    path("ranking-estados/", ranking_estados_view),
    path("evolucao/", evolucao_populacao_view),
    path("anos/", listar_anos_populacao_view),
]
