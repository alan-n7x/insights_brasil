from django.http import JsonResponse
from ibge.queries.populacao_queries import PopulacaoQuery

repo = PopulacaoQuery()


def ranking_estados_view(request):
    ano = request.GET.get("ano")

    data = repo.ranking_estados(ano)

    return JsonResponse(list(data), safe=False)


def evolucao_populacao_view(request):
    estado_id = request.GET.get("estado_id")

    data = repo.evolucao_populacao(estado_id=estado_id)

    return JsonResponse(list(data), safe=False)


def listar_anos_populacao_view(request):
    anos = repo.listar_anos()
    return JsonResponse(list(anos), safe=False)
