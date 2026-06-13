from django.urls import path

from .views import estados, sync_estados

urlpatterns = [
    path("estados/", estados, name="estados"),
    path("sync-estados/", sync_estados, name="sync-estados"),
]
