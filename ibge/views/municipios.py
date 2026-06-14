from django.http import JsonResponse

from ibge.domain.repositories.municipios_repository import MunicipioRepository


def listar_municipios_view(request):
    m = MunicipioRepository()
    municipios = m.listar()

    return JsonResponse(list(municipios), safe=False)
