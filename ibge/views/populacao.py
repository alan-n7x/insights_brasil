"""
Populacao Views - Population-specific endpoints

Usa o novo Query Engine motor para queries dinâmicas.
"""

from django.http import JsonResponse
from ibge.query_engine import IndicatorQueryEngine, QueryValidationError


engine = IndicatorQueryEngine()
INDICADOR = "POPULACAO"


def ranking_estados_view(request):
    """
    GET /api/ibge/populacao/ranking-estados/?ano=2023
    
    Ranking de estados por população.
    """
    try:
        ano = request.GET.get("ano")
        
        filters = {}
        if ano:
            filters["ano"] = int(ano)
        
        results, _ = engine.query(
            indicator=INDICADOR,
            group_by="estado",
            filters=filters or None,
            agg="sum",
            limit=1000,
        )
        
        return JsonResponse(results, safe=False)
    
    except QueryValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)


def evolucao_populacao_view(request):
    """
    GET /api/ibge/populacao/evolucao/?estado_id=35
    
    Evolução temporal de população por estado.
    """
    try:
        estado_id = request.GET.get("estado_id")
        
        filters = {}
        if estado_id:
            from ibge.models import Estado
            try:
                estado = Estado.objects.get(ibge_id=int(estado_id))
                filters["estado"] = estado.sigla
            except Estado.DoesNotExist:
                pass
        
        results, _ = engine.query(
            indicator=INDICADOR,
            group_by="ano",
            filters=filters or None,
            agg="sum",
            limit=1000,
        )
        
        return JsonResponse(results, safe=False)
    
    except QueryValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)


def listar_anos_populacao_view(request):
    """
    GET /api/ibge/populacao/anos/
    
    Lista todos os anos disponíveis para população.
    """
    try:
        results, _ = engine.query(
            indicator=INDICADOR,
            group_by="ano",
            limit=1000,
        )
        
        # Extract anos and sort
        anos = sorted(set(r["ano"] for r in results))
        
        return JsonResponse(anos, safe=False)
    
    except QueryValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
