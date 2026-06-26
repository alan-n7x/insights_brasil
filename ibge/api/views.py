from django.db.models import Sum
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from ibge.models import Indicador, FatoIndicador, Estado, Municipio, Tempo
from .serializers import (
    IndicadorSerializer,
    EstadoSerializer,
    MunicipioSerializer,
    TempoSerializer,
    FatoIndicadorSerializer,
    FatoIndicadorDetailSerializer,
    KpiQuerySerializer,
)
from .services.kpi_service import KPIService


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

    queryset = FatoIndicador.objects.select_related(
        "indicador",
        "municipio",
        "tempo",
    )

    def get_serializer_class(self):
        # Se for GET /fatos/
        if self.action == "list":
            return FatoIndicadorSerializer

        # Se for GET /fatos/10/
        return FatoIndicadorDetailSerializer


class KpiViewSet(viewsets.ViewSet):
    def list(self, request):
        """
        Retorna os valores dos KPIs solicitados após validação dos parâmetros de consulta.
        Utiliza o serializer KpiQuerySerializer para validar e normalizar os parâmetros
        (indicadores e ano) antes de delegar o cálculo ao serviço KPIService.
        Adiciona um campo '_warnings' caso algum indicador solicitado não seja encontrado.
        """
        # Usa o serializer para validar os parâmetros de consulta
        serializer = KpiQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        codigos = validated.get("indicadores", ["POPULACAO"])
        ano = validated.get("ano")

        # Obtém os dados dos indicadores utilizando o serviço de KPI
        data = KPIService.get_indicators(codigos=codigos, ano=ano)

        # Detecta indicadores não encontrados (valor None) e adiciona aviso
        unknown = [code for code, info in data.items() if info.get('valor') is None]
        if unknown:
            data['_warnings'] = f'Indicadores não encontrados: {", ".join(sorted(unknown))}'

        # Retorna os dados (já formatados como dicionário mapeando código para dicionário do indicador)
        return Response(data)