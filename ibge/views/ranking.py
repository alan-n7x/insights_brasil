import logging
from rest_framework.response import Response
from rest_framework.decorators import api_view

logger = logging.getLogger(__name__)


from ibge.services.ranking import (
    ranking_estados,
    ultimo_ano_disponivel,
)


@api_view(["GET"])
def ranking_estados_view(request):

    logger.info("[ranking_estados_view] Iniciando consulta")

    ano = request.GET.get("ano")

    if ano:

        ano = int(ano)

    else:

        ano = ultimo_ano_disponivel()

    data = ranking_estados(ano)

    return Response(list(data))
