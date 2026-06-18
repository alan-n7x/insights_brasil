"""
Municipios Views - List all municipalities
"""

from django.http import JsonResponse
from ibge.models import Municipio


def listar_municipios_view(request):
    """
    GET /api/ibge/municipios/
    
    Lista todos os municípios.
    """
    estado_id = request.GET.get("estado_id")
    
    qs = Municipio.objects.all()
    
    if estado_id:
        qs = qs.filter(estado_id=int(estado_id))
    
    data = list(
        qs.values(
            "id",
            "ibge_id",
            "nome",
            "estado_id",
            "estado__nome",
            "estado__sigla",
            "regiao",
        )
        .order_by("nome")
    )
    
    return JsonResponse(data, safe=False)
