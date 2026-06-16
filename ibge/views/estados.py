from django.http import JsonResponse
from ibge.models import Estado


def listar_estados_view(request):

    estados = Estado.objects.all().values(
        "id",
        "ibge_id",
        "nome",
        "sigla",
        "regiao",
    )

    return JsonResponse(list(estados), safe=False)