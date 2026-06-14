from django.urls import path

from ibge.views.anos import listar_anos_view

urlpatterns = [path("", listar_anos_view, name="listar-anos")]
