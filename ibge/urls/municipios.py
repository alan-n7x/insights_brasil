from django.urls import path

from ibge.views.municipios import listar_municipios_view

urlpatterns = [
    path("", listar_municipios_view, name="listar-municipios"),
]
