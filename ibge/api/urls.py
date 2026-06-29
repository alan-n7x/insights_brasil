"""Padrões de URL (rotas) da API REST do IBGE."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'populacao', views.PopulacaoViewSet, basename='populacao')
router.register(r'pib', views.PIBViewSet, basename='pib')
router.register(r'pib-per-capita', views.PIBPerCapitaViewSet, basename='pib-per-capita')

urlpatterns = [
    path('painel/resumo/', views.SummaryView.as_view(), name='painel-resumo'),
    path('estados/', views.StateListView.as_view(), name='estado-lista'),
    path('estados/<str:sigla>/', views.StateDetailView.as_view(), name='estado-detalhe'),
    path('municipios/<int:codigo>/', views.MunicipalityDetailView.as_view(), name='municipio-detalhe'),
]

urlpatterns += router.urls
