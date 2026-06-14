from django.urls import path
from ibge.views.ranking import ranking_estados_view

urlpatterns = [
    path("estados/", ranking_estados_view, name="ranking-estados"),
]