import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ibge.domain.repositories.populacao_query_repository import PopulacaoQueryRepository

logger = logging.getLogger(__name__)


@api_view(["GET"])
def anos_view(request):

    logger.info("[anos_view] request received")

    repo = PopulacaoQueryRepository()

    anos = repo.listar_anos()

    return Response(list(anos))
