from django.http import JsonResponse
from ibge.queries.municipios_queries import listar_municipios


def listar_municipios_view(request):
    data = list(listar_municipios())
    return JsonResponse(data, safe=False)
