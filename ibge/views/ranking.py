import logging
from rest_framework.response import Response
from rest_framework.decorators import api_view

from ibge.domain.repositories.populacao_query_repository import PopulacaoQueryRepository

logger = logging.getLogger(__name__)


@api_view(["GET"])
def ranking_estados_view(request):

    logger.info("[ranking_estados_view] Iniciando consulta")

    repo = PopulacaoQueryRepository()

    ano = request.GET.get("ano")

    if ano:
        ano = int(ano)
    else:
        ano = repo.ultimo_ano_disponivel()

    data = repo.ranking_estados(ano)

    return Response(list(data))