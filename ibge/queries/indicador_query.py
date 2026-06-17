from django.db.models import F, Max, Sum

from ibge.models import Indicador, IndicadorMunicipio


class IndicadorQuery:

    def listar_indicadores(self):

        return Indicador.objects.all().values(
            "id",
            "codigo",
            "nome",
        ).order_by("codigo")

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

    def ranking_municipios(
        self,
        indicador,
        ano=None,
        estado_id=None,
        limit=None,
    ):

        if ano is None:

            ano = self.ultimo_ano_disponivel(indicador)

        qs = IndicadorMunicipio.objects.filter(
            indicador__codigo=indicador,
            ano=ano,
        )

        if estado_id:

            qs = qs.filter(
                municipio__estado_id=estado_id,
            )

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

        if limit:

            qs = qs[: int(limit)]

        return qs

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
