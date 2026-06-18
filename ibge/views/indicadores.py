"""
Indicador Views - Refatorizado para usar Query Engine

Todas as views agora usam o novo motor de consultas flexível.
"""

from django.http import JsonResponse

from ibge.query_engine import IndicatorQueryEngine, QueryValidationError


engine = IndicatorQueryEngine()


def normalizar_codigo(codigo):
    return codigo.upper()


def indicador_nao_encontrado(codigo):
    return JsonResponse(
        {
            "erro": "Indicador não encontrado",
            "indicador": normalizar_codigo(codigo),
        },
        status=404,
    )


def listar_indicadores_view(request):
    """
    GET /indicadores/
    
    Lista todos os indicadores disponíveis.
    """
    try:
        schemas = engine.list_indicators()
        return JsonResponse(
            [
                {
                    "id": s["code"],
                    "codigo": s["code"],
                    "nome": s["name"],
                }
                for s in schemas
            ],
            safe=False,
        )
    except QueryValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)


def listar_anos_indicador_view(request, indicador):
    """
    GET /indicadores/{indicador}/anos/
    
    Lista todos os anos disponíveis para um indicador.
    """
    indicador = normalizar_codigo(indicador)

    try:
        engine.get_indicator_schema(indicador)
    except QueryValidationError:
        return indicador_nao_encontrado(indicador)

    try:
        # Query group by ano
        results, _ = engine.query(
            indicator=indicador,
            group_by="ano",
            limit=1000,
        )
        
        # Extract anos and sort
        anos = sorted(set(r["ano"] for r in results))
        
        return JsonResponse(anos, safe=False)
    
    except QueryValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)


def ranking_estados_indicador_view(request, indicador):
    """
    GET /indicadores/{indicador}/ranking-estados/?ano=2023
    
    Ranking de estados por indicador.
    """
    indicador = normalizar_codigo(indicador)

    try:
        engine.get_indicator_schema(indicador)
    except QueryValidationError:
        return indicador_nao_encontrado(indicador)

    try:
        ano = request.GET.get("ano")
        
        filters = {}
        if ano:
            filters["ano"] = int(ano)
        
        results, _ = engine.query(
            indicator=indicador,
            group_by="estado",
            filters=filters or None,
            agg="sum",
            limit=1000,
        )
        
        return JsonResponse(results, safe=False)
    
    except QueryValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)


def ranking_municipios_indicador_view(request, indicador):
    """
    GET /indicadores/{indicador}/ranking-municipios/?ano=2023&estado_id=35
    
    Ranking de municípios por indicador.
    """
    indicador = normalizar_codigo(indicador)

    try:
        engine.get_indicator_schema(indicador)
    except QueryValidationError:
        return indicador_nao_encontrado(indicador)

    try:
        ano = request.GET.get("ano")
        estado_id = request.GET.get("estado_id")
        limit = request.GET.get("limit", 1000)
        
        filters = {}
        if ano:
            filters["ano"] = int(ano)
        
        # If estado_id provided, convert to sigla for filtering
        if estado_id:
            from ibge.models import Estado
            try:
                estado = Estado.objects.get(ibge_id=int(estado_id))
                filters["estado"] = estado.sigla
            except Estado.DoesNotExist:
                pass
        
        results, _ = engine.query(
            indicator=indicador,
            group_by="municipio",
            filters=filters or None,
            agg="sum",
            limit=int(limit),
        )
        
        return JsonResponse(results, safe=False)
    
    except QueryValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)


def evolucao_estado_indicador_view(request, indicador):
    """
    GET /indicadores/{indicador}/evolucao/?estado_id=35
    
    Evolução temporal de um indicador para um estado (agrupado por ano).
    """
    indicador = normalizar_codigo(indicador)

    try:
        engine.get_indicator_schema(indicador)
    except QueryValidationError:
        return indicador_nao_encontrado(indicador)

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
            indicator=indicador,
            group_by="ano",
            filters=filters or None,
            agg="sum",
            limit=1000,
        )
        
        return JsonResponse(results, safe=False)
    
    except QueryValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)


def evolucao_municipio_indicador_view(request, indicador, municipio_ibge_id):
    """
    GET /indicadores/{indicador}/municipios/{municipio_ibge_id}/evolucao/
    
    Evolução temporal de um indicador para um município.
    """
    indicador = normalizar_codigo(indicador)

    try:
        engine.get_indicator_schema(indicador)
    except QueryValidationError:
        return indicador_nao_encontrado(indicador)

    try:
        from ibge.models import Municipio
        
        # Verify municipio exists
        municipio = Municipio.objects.get(ibge_id=municipio_ibge_id)
        
        ano_inicio = request.GET.get("ano_inicio")
        ano_fim = request.GET.get("ano_fim")
        
        filters = {"municipio": municipio.nome}
        
        # Note: The current query engine doesn't support range filters (ano_gte, ano_lte)
        # So we'll get all and filter in Python, or query will return all years
        if ano_inicio:
            filters["ano"] = int(ano_inicio)
        elif ano_fim:
            filters["ano"] = int(ano_fim)
        
        from ibge.models import IndicadorMunicipio
        from django.db.models import F
        
        # Direct query for better control on date range
        qs = IndicadorMunicipio.objects.filter(
            indicador__codigo=indicador,
            municipio__ibge_id=municipio_ibge_id,
        )
        
        if ano_inicio:
            qs = qs.filter(ano__gte=int(ano_inicio))
        if ano_fim:
            qs = qs.filter(ano__lte=int(ano_fim))
        
        data = list(
            qs.values("ano", "valor").order_by("ano")
        )
        
        return JsonResponse(data, safe=False)
    
    except QueryValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
