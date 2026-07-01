"""Configuração de rotas principal do módulo IBGE, incluindo o prefixo da API v1."""

from django.urls import include, path

urlpatterns = [
    path("api/v1/", include("ibge.api.urls")),
]
