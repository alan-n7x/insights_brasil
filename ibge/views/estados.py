"""
Estados Views - List all states/regions
"""

from django.http import JsonResponse
from ibge.models import Estado


def listar_estados_view(request):
    """
    GET /api/ibge/estados/
    
    Lista todos os estados.
    """
    data = list(
        Estado.objects.all()
        .values("id", "ibge_id", "nome", "sigla", "regiao")
        .order_by("nome")
    )
    return JsonResponse(data, safe=False)
