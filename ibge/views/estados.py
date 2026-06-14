from django.http import JsonResponse

from ibge.services.estado_service import listar_estados


def listar_estados_view(request):

    estados = listar_estados()

    return JsonResponse(list(estados), safe=False)
