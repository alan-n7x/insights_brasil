
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'indicadores', views.IndicadorViewSet, basename='indicador')
router.register(r'estados', views.EstadoViewSet, basename='estado')
router.register(r'municipios', views.MunicipioViewSet, basename='municipio')
router.register(r'tempos', views.TempoViewSet, basename='tempo')
router.register(r'fatos', views.FatoIndicadorViewSet, basename='fato')

urlpatterns = [
    path('', include(router.urls)),
]

