from django.urls import path

from ibge.views.estados import listar_estados_view

urlpatterns = [
    path("", listar_estados_view, name="listar-estados"),
]
