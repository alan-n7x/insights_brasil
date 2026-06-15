from django.urls import path

from ibge.views.anos_view import anos_view

urlpatterns = [
    path("", anos_view, name="listar-anos"),
]
