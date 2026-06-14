from django.http import JsonResponse

from ibge.domain.repositories.estado_repository import EstadoRepository


def listar_estados_view(request):

    estados = EstadoRepository().listar()

    return JsonResponse(list(estados), safe=False)
