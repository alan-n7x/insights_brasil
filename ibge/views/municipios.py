from django.http import JsonResponse

from ibge.services.municipios_service import listar_municipios


def listar_municipios_view(request):

    municipios = listar_municipios()

    return JsonResponse(
        list(municipios),
        safe=False
    )