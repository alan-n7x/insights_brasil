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
    path('dashboard/resumo/', views.DashboardResumoView.as_view(), name='dashboard-resumo'),
    path('estados/', views.StateListView.as_view(), name='estado-lista'),
    path('estados/<str:sigla>/', views.StateDetailView.as_view(), name='estado-detalhe'),
    path('municipios/<int:codigo>/', views.MunicipalityDetailView.as_view(), name='municipio-detalhe'),
    # Rota genérica: qualquer indicador pelo código
    path('indicador/<str:codigo>/', views.IndicadorViewSet.as_view({'get': 'list'}), name='indicador-list'),
    path('indicador/<str:codigo>/ranking/', views.IndicadorViewSet.as_view({'get': 'ranking'}), name='indicador-ranking'),
    path('indicador/<str:codigo>/serie/', views.IndicadorViewSet.as_view({'get': 'serie'}), name='indicador-serie'),
]

urlpatterns += router.urls
