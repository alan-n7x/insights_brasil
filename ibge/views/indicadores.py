from django.http import JsonResponse

from ibge.models import Indicador
from ibge.queries.indicador_query import IndicadorQuery


repo = IndicadorQuery()


def normalizar_codigo(codigo):
    return codigo.upper()


def indicador_existe(codigo):
    return Indicador.objects.filter(codigo=normalizar_codigo(codigo)).exists()


def indicador_nao_encontrado(codigo):
    return JsonResponse(
        {
            "erro": "Indicador não encontrado",
            "indicador": normalizar_codigo(codigo),
        },
        status=404,
    )


def listar_indicadores_view(request):
    return JsonResponse(
        list(repo.listar_indicadores()),
        safe=False,
    )


def listar_anos_indicador_view(request, indicador):
    indicador = normalizar_codigo(indicador)

    if not indicador_existe(indicador):
        return indicador_nao_encontrado(indicador)

    return JsonResponse(
        list(repo.listar_anos(indicador=indicador)),
        safe=False,
    )


def ranking_estados_indicador_view(request, indicador):
    indicador = normalizar_codigo(indicador)

    if not indicador_existe(indicador):
        return indicador_nao_encontrado(indicador)

    ano = request.GET.get("ano")

    return JsonResponse(
        list(
            repo.ranking_estados(
                indicador=indicador,
                ano=ano,
            )
        ),
        safe=False,
    )


def ranking_municipios_indicador_view(request, indicador):
    indicador = normalizar_codigo(indicador)

    if not indicador_existe(indicador):
        return indicador_nao_encontrado(indicador)

    ano = request.GET.get("ano")
    estado_id = request.GET.get("estado_id")
    limit = request.GET.get("limit")

    data = list(
        repo.ranking_municipios(
            indicador=indicador,
            ano=ano,
            estado_id=estado_id,
            limit=limit,
        )
    )

    for row in data:
        row["municipio"] = row.pop("municipio_nome")

    return JsonResponse(data, safe=False)


def evolucao_estado_indicador_view(request, indicador):
    indicador = normalizar_codigo(indicador)

    if not indicador_existe(indicador):
        return indicador_nao_encontrado(indicador)

    estado_id = request.GET.get("estado_id")

    return JsonResponse(
        list(
            repo.evolucao_estado(
                indicador=indicador,
                estado_id=estado_id,
            )
        ),
        safe=False,
    )


def evolucao_municipio_indicador_view(request, indicador, municipio_ibge_id):
    indicador = normalizar_codigo(indicador)

    if not indicador_existe(indicador):
        return indicador_nao_encontrado(indicador)

    ano_inicio = request.GET.get("ano_inicio")
    ano_fim = request.GET.get("ano_fim")

    return JsonResponse(
        list(
            repo.evolucao_municipio(
                indicador=indicador,
                municipio_ibge_id=municipio_ibge_id,
                ano_inicio=ano_inicio,
                ano_fim=ano_fim,
            )
        ),
        safe=False,
    )
