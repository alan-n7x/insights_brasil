from django.db.models import Sum, F, Max
from ibge.models import PopulacaoMunicipio


class PopulacaoQuery:
    """Classe para consultas relacionadas à população dos municípios."""

    def ranking_estados(self, ano=None):
        """
        Retorna ranking dos estados por população.
        Se ano não for informado, usa o último disponível.
        """

        if ano is None:
            ano = self.ultimo_ano_disponivel()

        if ano is None:
            return []  # banco vazio ainda

        return (
            PopulacaoMunicipio.objects.filter(ano=ano)
            .values(estado=F("municipio__estado__nome"))
            .annotate(total=Sum("populacao"))
            .order_by("-total")
        )

    def ultimo_ano_disponivel(self):
        """Retorna o último ano para o qual temos dados de população disponíveis."""
        return PopulacaoMunicipio.objects.aggregate(ultimo_ano=Max("ano"))["ultimo_ano"]

    def listar_anos(self):
        """Retorna uma lista de anos para os quais temos dados de população disponíveis."""

        return (
            PopulacaoMunicipio.objects.values_list("ano", flat=True)
            .distinct()
            .order_by("ano")
        )

    def evolucao_populacao(self, estado_id=None):
        """Evolução da população, soma da população de TODOS os municípios por ano"""
        qs = PopulacaoMunicipio.objects.all()

        if estado_id:
            qs = qs.filter(municipio__estado_id=estado_id)

        return qs.values("ano").annotate(total=Sum("populacao")).order_by("ano")
