from django.http import JsonResponse

from ibge.models import Municipio


def listar_municipios_view(request):
    m = Municipio.objects.all()
    municipios = m.values(
        "id",
        "ibge_id",
        "nome",
        "estado_id",
    )

    return JsonResponse(list(municipios), safe=False)
