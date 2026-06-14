from django.db.models import Sum
from ibge.models import PopulacaoMunicipio


def ranking_estados(ano: int):
    return (
        PopulacaoMunicipio.objects.filter(ano=ano)
        .values("municipio__estado__nome")
        .annotate(total=Sum("populacao"))
        .order_by("-total")
    )
