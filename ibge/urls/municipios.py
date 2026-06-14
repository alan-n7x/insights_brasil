from django.urls import path
from ibge.views.views import sync_municipios

urlpatterns = [
    path("", sync_municipios, name="municipios"),
]