from django.urls import path

from .views import estados, sync_estados, sync_municipios

urlpatterns = [
    path("estados/", estados, name="estados"),
    path("sync-estados/", sync_estados, name="sync-estados"),
    path("sync-municipios/", sync_municipios, name="sync-municipios"),
]
