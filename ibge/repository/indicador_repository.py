from django.db.models import Sum, F, Max
from ibge.models import IndicadorMunicipio, Indicador


class IndicadorRepository:

    # -------------------------
    # INDICADORES
    # -------------------------
    def listar_indicadores(self):
        return Indicador.objects.all().values("id", "codigo", "nome").order_by("codigo")

    def ultimo_ano_disponivel(self, indicador):
        return (
            IndicadorMunicipio.objects.filter(indicador__codigo=indicador).aggregate(
                ultimo_ano=Max("ano")
            )
        )["ultimo_ano"]

    def listar_anos(self, indicador):
        return (
            IndicadorMunicipio.objects.filter(indicador__codigo=indicador)
            .values_list("ano", flat=True)
            .distinct()
            .order_by("ano")
        )

    # -------------------------
    # ESTADOS
    # -------------------------
    def ranking_estados(self, indicador, ano):
        return (
            IndicadorMunicipio.objects.filter(indicador__codigo=indicador, ano=ano)
            .values(estado=F("municipio__estado__nome"))
            .annotate(total=Sum("valor"))
            .order_by("-total")
        )

    def evolucao_estado(self, indicador, estado_id=None):
        qs = IndicadorMunicipio.objects.filter(indicador__codigo=indicador)

        if estado_id:
            qs = qs.filter(municipio__estado_id=estado_id)

        return qs.values("ano").annotate(total=Sum("valor")).order_by("ano")

    # -------------------------
    # MUNICÍPIOS
    # -------------------------
    def ranking_municipios(self, indicador, ano, estado_id=None, limit=None):
        qs = IndicadorMunicipio.objects.filter(
            indicador__codigo=indicador,
            ano=ano,
        )

        if estado_id:
            qs = qs.filter(municipio__estado_id=estado_id)

        qs = (
            qs.values(
                municipio_nome=F("municipio__nome"),
                municipio_ibge_id=F("municipio__ibge_id"),
                estado=F("municipio__estado__nome"),
                sigla=F("municipio__estado__sigla"),
            )
            .annotate(total=Sum("valor"))
            .order_by("-total")
        )

        return qs[: int(limit)] if limit else qs

    def evolucao_municipio(
        self, indicador, municipio_ibge_id, ano_inicio=None, ano_fim=None
    ):
        qs = IndicadorMunicipio.objects.filter(
            indicador__codigo=indicador,
            municipio__ibge_id=municipio_ibge_id,
        )

        if ano_inicio:
            qs = qs.filter(ano__gte=ano_inicio)

        if ano_fim:
            qs = qs.filter(ano__lte=ano_fim)

        return qs.values("ano", "valor").order_by("ano")

    # -------------------------
    # PIB / POPULACAO (dados crus)
    # -------------------------
    def pib_por_estado_ano(self, ano):
        return (
            IndicadorMunicipio.objects.filter(indicador__codigo="PIB", ano=ano)
            .values(estado=F("municipio__estado__nome"))
            .annotate(pib_total=Sum("valor"))
        )

    def populacao_por_estado_ano(self, ano):
        return (
            IndicadorMunicipio.objects.filter(indicador__codigo="POPULACAO", ano=ano)
            .values(estado=F("municipio__estado__nome"))
            .annotate(populacao_total=Sum("valor"))
        )

    def pib_por_ano(self, estado_id=None):
        qs = IndicadorMunicipio.objects.filter(indicador__codigo="PIB")

        if estado_id:
            qs = qs.filter(municipio__estado_id=estado_id)

        return qs.values("ano").annotate(pib_total=Sum("valor"))

    def populacao_por_ano(self, estado_id=None):
        qs = IndicadorMunicipio.objects.filter(indicador__codigo="POPULACAO")

        if estado_id:
            qs = qs.filter(municipio__estado_id=estado_id)

        return qs.values("ano").annotate(populacao_total=Sum("valor"))
