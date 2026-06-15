from django.db.models import Sum, F, Max
from ibge.models import PopulacaoMunicipio


class PopulacaoQueryRepository:
    """Repository para consultas relacionadas à população dos municípios."""

    def ranking_estados(self, ano):
        """Retorna o ranking dos estados por população para um ano específico."""
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

    def evolucao_populacao(self):
        pass
