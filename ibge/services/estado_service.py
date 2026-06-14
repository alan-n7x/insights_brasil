from ibge.models import Estado


def listar_estados():

    return Estado.objects.all().values(
        "codigo_externo",
        "nome",
        "sigla",
        "regiao",
    )
