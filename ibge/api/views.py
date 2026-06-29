"""
Views da API REST do IBGE em português, utilizando ViewSets para escalabilidade.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .serializers import (
    SummarySerializer,
    MunicipalityListSerializer,
    RankingItemSerializer,
    SeriesItemSerializer,
    StateSerializer,
    MunicipalityDetailSerializer,
    ParameterSerializer,
    DashboardResumoSerializer,
)
from ..query_engine import DashboardQuery
from ..repositories.indicador_repository import IndicadorRepository
from ..repositories.municipio_repository import MunicipioRepository
from ..models import Estado


class SummaryView(APIView):
    """View que retorna o sumário com população, PIB e PIB per capita para filtros informados."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ano",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name="estado",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name="municipio",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
        ],
        responses={200: SummarySerializer},
    )
    def get(self, request):
        """Retorna o sumário do painel com filtros opcionais de ano, estado e município."""
        params = ParameterSerializer(data=request.GET)
        params.is_valid(raise_exception=True)
        ano = params.validated_data.get("ano")
        estado = params.validated_data.get("estado")
        municipio = params.validated_data.get("municipio")

        if municipio is not None and not MunicipioRepository.get_by_codigo(municipio):
            return Response(
                {"detail": "Município não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = DashboardQuery.summary(
            ano=ano,
            estado=estado,
            municipio=municipio,
        )
        serializer = SummarySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class DashboardResumoView(APIView):
    """Endpoint BFF que retorna todos os dados prontos para o dashboard."""

    @extend_schema(
        summary="Resumo completo do dashboard",
        description="Retorna população total, PIB total, PIB per capita médio, população por região e ranking de estados em uma única chamada.",
        parameters=[
            OpenApiParameter(
                name="ano",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
        ],
        responses={200: DashboardResumoSerializer},
    )
    def get(self, request):
        """Retorna o resumo completo do dashboard para o ano informado."""
        params = ParameterSerializer(data=request.GET)
        params.is_valid(raise_exception=True)
        ano = params.validated_data.get("ano")
        data = DashboardQuery.dashboard_resumo(ano=ano)
        serializer = DashboardResumoSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class StateListView(APIView):
    """View que retorna a lista de todos os estados brasileiros."""

    @extend_schema(
        summary="Listar estados",
        description="Retorna todos os estados brasileiros com sigla, nome e região.",
        responses={200: StateSerializer(many=True)},
    )
    def get(self, request):
        """Retorna a lista de estados com sigla, nome e região."""
        qs = Estado.objects.values("sigla", "nome", "regiao")
        return Response(list(qs))


class StateDetailView(APIView):
    """View que retorna os detalhes de um estado específico pela sigla."""

    @extend_schema(
        summary="Detalhe do estado",
        description="Retorna os dados de um estado específico pela sigla (ex: SP, RJ).",
        parameters=[
            OpenApiParameter(
                name="sigla",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description="Sigla do estado (ex: SP)",
            ),
        ],
        responses={200: StateSerializer, 404: None},
    )
    def get(self, request, sigla):
        """Retorna os dados de um estado filtrado pela sigla."""
        try:
            estado = Estado.objects.get(sigla=sigla.upper())
        except Estado.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        data = {"sigla": estado.sigla, "nome": estado.nome, "regiao": estado.regiao}
        return Response(data)


class MunicipalityDetailView(APIView):
    """View que retorna os detalhes de um município específico pelo código IBGE."""

    @extend_schema(
        summary="Detalhe do município",
        description="Retorna os dados de um município específico pelo código IBGE.",
        parameters=[
            OpenApiParameter(
                name="codigo",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description="Código IBGE do município (ex: 3550308)",
            ),
        ],
        responses={200: MunicipalityDetailSerializer, 404: None},
    )
    def get(self, request, codigo):
        """Retorna os dados de um município filtrado pelo código IBGE."""
        mun = MunicipioRepository.get_by_codigo(codigo)
        if not mun:
            return Response(status=status.HTTP_404_NOT_FOUND)
        data = {
            "codigo": mun.ibge_id,
            "nome": mun.nome,
            "sigla": mun.estado.sigla,
            "nome_estado": mun.estado.nome,
        }
        return Response(data)


class IndicadorViewSet(viewsets.ViewSet):
    """
    ViewSet genérico para indicadores, parametrizado pelo código na URL.

    Fornece:
    - list: lista de municípios com valor do indicador (filtros: ano, estado, municipio)
    - ranking: ranking por estado (soma do indicador)
    - serie: série temporal anual (filtros: estado, municipio)

    Uso: GET /api/v1/indicador/POPULACAO/, /api/v1/indicador/POPULACAO/ranking/, etc.
    """

    serializer_class = MunicipalityListSerializer
    lookup_field = 'codigo'

    def _get_codigo(self):
        """Retorna o código do indicador da URL (self.kwargs ou self.request.GET)."""
        return (self.kwargs.get('codigo') or self.request.GET.get('codigo') or '').upper()

    def _get_indicator(self, codigo):
        """Retorna a instância de Indicador pelo código ou None."""
        return IndicadorRepository.get_by_codigo(codigo)

    @extend_schema(
        summary="Listar indicador por município",
        description="Retorna os valores do indicador para cada município, com filtros opcionais.",
        parameters=[
            OpenApiParameter(
                name="codigo", type=OpenApiTypes.STR, location=OpenApiParameter.PATH, required=True,
                description="Código do indicador (ex: POPULACAO, PIB)",
            ),
            OpenApiParameter(
                name="ano", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False,
            ),
            OpenApiParameter(
                name="estado", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                description="Sigla do estado (ex: SP)",
            ),
            OpenApiParameter(
                name="municipio", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False,
                description="Código IBGE do município",
            ),
            OpenApiParameter(
                name="limit", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False,
                description="Limite de resultados",
            ),
            OpenApiParameter(
                name="nome", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                description="Filtro por nome do município (LIKE)",
            ),
            OpenApiParameter(
                name="order_by", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                description='Ordenação: "valor" para decrescente, "asc" para crescente',
            ),
        ],
        responses={200: MunicipalityListSerializer},
    )
    def list(self, request, codigo=None):
        """Endpoint: GET /<indicador>/ (lista de municípios)"""
        codigo = (codigo or self._get_codigo()).upper()
        params = ParameterSerializer(data=request.GET)
        params.is_valid(raise_exception=True)
        ano = params.validated_data.get("ano")
        estado = params.validated_data.get("estado")
        municipio = params.validated_data.get("municipio")
        nome = params.validated_data.get("nome")
        limite = params.validated_data.get("limit")
        order_by = params.validated_data.get("order_by")

        if municipio:
            mun = MunicipioRepository.get_by_codigo(municipio)
            if not mun:
                return Response([], status=status.HTTP_200_OK)
            val = DashboardQuery._get_value_for_indicator(
                codigo.lower(), municipio=municipio, ano=ano
            )
            data = [
                {
                    "codigo": mun.ibge_id,
                    "nome": mun.nome,
                    "sigla": mun.estado.sigla,
                    "valor": val or 0,
                }
            ]
        else:
            data = DashboardQuery._get_indicator_list(
                codigo.lower(), ano=ano, estado=estado,
                nome=nome, limit=limite, order_by=order_by,
            )
        serializer = MunicipalityListSerializer(data={"items": data})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="ranking")
    @extend_schema(
        summary="Ranking do indicador por estado",
        parameters=[
            OpenApiParameter(
                name="codigo", type=OpenApiTypes.STR, location=OpenApiParameter.PATH, required=True,
                description="Código do indicador (ex: POPULACAO, PIB)",
            ),
            OpenApiParameter(
                name="ano", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False,
            ),
            OpenApiParameter(
                name="estado", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
            ),
            OpenApiParameter(
                name="limit", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False,
                description="Limite máximo de resultados (padrão: 10, mínimo: 1)",
            ),
        ],
        responses={200: RankingItemSerializer(many=True)},
    )
    def ranking(self, request, codigo=None):
        """Endpoint: GET /<indicador>/ranking/"""
        codigo = (codigo or self._get_codigo()).upper()
        params = ParameterSerializer(data=request.GET)
        params.is_valid(raise_exception=True)
        ano = params.validated_data.get("ano")
        limite = params.validated_data.get("limit", 10)
        ind = self._get_indicator(codigo)
        if not ind:
            return Response([])

        if codigo == "PIB_PER_CAPITA":
            summary_data = DashboardQuery.summary(
                ano=ano,
                estado=params.validated_data.get("estado"),
                municipio=params.validated_data.get("municipio"),
            )
            pop = summary_data["populacao"]
            pib = summary_data["pib"]
            per_capita = pib / pop if pop > 0 else 0.0
            result = [{"position": 1, "state": "BR", "value": per_capita}]
            serializer = RankingItemSerializer(data=result, many=True)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        data = DashboardQuery.get_ranking_by_estado(ind, ano, limit=limite)
        result = [
            {
                "position": item["posicao"],
                "state": item["estado"],
                "value": item["valor"],
            }
            for item in data
        ]
        serializer = RankingItemSerializer(data=result, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="serie")
    @extend_schema(
        summary="Série temporal do indicador",
        description="Retorna os valores anuais do indicador, agregados por ano.",
        parameters=[
            OpenApiParameter(
                name="codigo", type=OpenApiTypes.STR, location=OpenApiParameter.PATH, required=True,
                description="Código do indicador (ex: POPULACAO, PIB)",
            ),
            OpenApiParameter(
                name="estado", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False,
                description="Sigla do estado (ex: SP)",
            ),
            OpenApiParameter(
                name="municipio", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False,
                description="Código IBGE do município",
            ),
        ],
        responses={200: SeriesItemSerializer(many=True)},
    )
    def serie(self, request, codigo=None):
        """Endpoint: GET /<indicador>/serie/"""
        codigo = (codigo or self._get_codigo()).upper()
        params = ParameterSerializer(data=request.GET)
        params.is_valid(raise_exception=True)
        estado = params.validated_data.get("estado")
        municipio = params.validated_data.get("municipio")
        data = DashboardQuery.get_time_series(
            indicator_name=codigo.lower(), estado=estado, municipio=municipio
        )
        serializer = SeriesItemSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class PopulacaoViewSet(IndicadorViewSet):
    """ViewSet para compatibilidade retroativa: GET /populacao/ funciona como /indicador/POPULACAO/."""

    def _get_codigo(self):
        return "POPULACAO"


class PIBViewSet(IndicadorViewSet):
    """ViewSet para compatibilidade retroativa: GET /pib/ funciona como /indicador/PIB/."""

    def _get_codigo(self):
        return "PIB"


class PIBPerCapitaViewSet(IndicadorViewSet):
    """ViewSet para compatibilidade retroativa: GET /pib-per-capita/ funciona como /indicador/PIB_PER_CAPITA/."""

    def _get_codigo(self):
        return "PIB_PER_CAPITA"
