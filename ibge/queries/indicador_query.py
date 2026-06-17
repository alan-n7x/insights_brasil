from django.db.models import Sum, F, Max

from ibge.models import IndicadorMunicipio


class IndicadorQuery:

    def ultimo_ano_disponivel(self, indicador):

        return (
            IndicadorMunicipio.objects.filter(indicador__codigo=indicador).aggregate(
                ultimo_ano=Max("ano")
            )
        )["ultimo_ano"]

    def listar_anos(self, indicador):

        return (
            IndicadorMunicipio.objects.filter(indicador__codigo=indicador)
            .values_list(
                "ano",
                flat=True,
            )
            .distinct()
            .order_by("ano")
        )

    def ranking_estados(
        self,
        indicador,
        ano=None,
    ):

        if ano is None:

            ano = self.ultimo_ano_disponivel(indicador)

        return (
            IndicadorMunicipio.objects.filter(
                indicador__codigo=indicador,
                ano=ano,
            )
            .values(estado=F("municipio__estado__nome"))
            .annotate(total=Sum("valor"))
            .order_by("-total")
        )

    def evolucao_municipio(
        self,
        indicador,
        municipio_ibge_id,
        ano_inicio=None,
        ano_fim=None,
    ):

        qs = IndicadorMunicipio.objects.filter(
            indicador__codigo=indicador,
            municipio__ibge_id=municipio_ibge_id,
        )

        if ano_inicio:

            qs = qs.filter(ano__gte=ano_inicio)

        if ano_fim:

            qs = qs.filter(ano__lte=ano_fim)

        return qs.values(
            "ano",
            "valor",
        ).order_by("ano")

    def evolucao_estado(
        self,
        indicador,
        estado_id=None,
    ):

        qs = IndicadorMunicipio.objects.filter(
            indicador__codigo=indicador,
        )

        if estado_id:

            qs = qs.filter(
                municipio__estado_id=estado_id,
            )

        return (
            qs.values("ano")
            .annotate(
                total=Sum("valor"),
            )
            .order_by("ano")
        )
