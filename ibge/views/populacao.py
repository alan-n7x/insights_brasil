from django.http import JsonResponse
from ibge.queries.indicador_query import IndicadorQuery

repo = IndicadorQuery()

INDICADOR = "POPULACAO"


def ranking_estados_view(request):

    ano = request.GET.get("ano")

    return JsonResponse(
        list(
            repo.ranking_estados(
                indicador=INDICADOR,
                ano=ano,
            )
        ),
        safe=False,
    )


def evolucao_populacao_view(request):

    estado_id = request.GET.get("estado_id")

    data = repo.evolucao_estado(
        indicador=INDICADOR,
        estado_id=estado_id,
    )

    return JsonResponse(
        list(data),
        safe=False,
    )


def listar_anos_populacao_view(request):

    anos = repo.listar_anos(
        indicador=INDICADOR,
    )

    return JsonResponse(
        list(anos),
        safe=False,
    )
