from django.db.models import Sum, F, Max

from ibge.models import IndicadorMunicipio


class PopulacaoQuery:
    """Consultas relacionadas à população dos municípios."""

    INDICADOR = "POPULACAO"

    def ranking_estados(self, ano=None):

        if ano is None:
            ano = self.ultimo_ano_disponivel()

        if ano is None:
            return []

        return (
            IndicadorMunicipio.objects.filter(
                indicador__codigo=self.INDICADOR,
                ano=ano,
            )
            .values(estado=F("municipio__estado__nome"))
            .annotate(total=Sum("valor"))
            .order_by("-total")
        )

    def ultimo_ano_disponivel(self):

        return (
            IndicadorMunicipio.objects.filter(
                indicador__codigo=self.INDICADOR
            ).aggregate(ultimo_ano=Max("ano"))
        )["ultimo_ano"]

    def listar_anos(self):

        return (
            IndicadorMunicipio.objects.filter(indicador__codigo=self.INDICADOR)
            .values_list(
                "ano",
                flat=True,
            )
            .distinct()
            .order_by("ano")
        )

    def evolucao_populacao(self, estado_id=None):

        qs = IndicadorMunicipio.objects.filter(indicador__codigo=self.INDICADOR)

        if estado_id:

            qs = qs.filter(municipio__estado_id=estado_id)

        return qs.values("ano").annotate(total=Sum("valor")).order_by("ano")
