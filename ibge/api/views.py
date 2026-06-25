from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from ibge.models import Indicador, FatoIndicador, Estado, Municipio, Tempo
from .serializers import (
    IndicadorSerializer,
    EstadoSerializer,
    MunicipioSerializer,
    TempoSerializer,
    FatoIndicadorSerializer,
)


class IndicadorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Indicador.objects.all()
    serializer_class = IndicadorSerializer


class EstadoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["sigla", "nome"]


class MunicipioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Municipio.objects.all()
    serializer_class = MunicipioSerializer


class TempoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tempo.objects.all()
    serializer_class = TempoSerializer


class FatoIndicadorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FatoIndicador.objects.all()
    serializer_class = FatoIndicadorSerializer
