from django.http import JsonResponse
from ibge.queries.estados_queries import listar_estados


def listar_estados_view(request):
    data = list(listar_estados())
    return JsonResponse(data, safe=False)
