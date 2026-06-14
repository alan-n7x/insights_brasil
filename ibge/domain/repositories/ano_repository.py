from ibge.models import PopulacaoMunicipio


def listar_anos():

    return (
        PopulacaoMunicipio.objects.values_list("ano", flat=True)
        .distinct()
        .order_by("ano")
    )
