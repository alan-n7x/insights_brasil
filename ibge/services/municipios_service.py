from ibge.models import Municipio


def listar_municipios():

    return Municipio.objects.all().values(
        "id",
        "nome",
    )
