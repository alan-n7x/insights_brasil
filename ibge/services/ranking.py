from django.db.models import Sum, Max, F

from ibge.models import PopulacaoMunicipio


def ultimo_ano_disponivel():

    return PopulacaoMunicipio.objects.aggregate(ultimo_ano=Max("ano"))["ultimo_ano"]


def ranking_estados(ano: int):

    return (
        PopulacaoMunicipio.objects.filter(ano=ano)
        .values(estado=F("municipio__estado__nome"))
        .annotate(total=Sum("populacao"))
        .order_by("-total")
    )
