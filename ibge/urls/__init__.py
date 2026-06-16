"""URL configuration for the IBGE API."""

from django.urls import path, include

urlpatterns = [
    path("estados/", include("ibge.urls.estados")),
    path("municipios/", include("ibge.urls.municipios")),
]
