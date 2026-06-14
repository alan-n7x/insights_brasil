from django.urls import path, include

urlpatterns = [
    path("estados/", include("ibge.urls.estados")),
    path("municipios/", include("ibge.urls.municipios")),
    path("ranking/", include("ibge.urls.ranking")),
    # path("sync/", include("ibge.urls.sync")),
]