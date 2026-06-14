import logging

logger = logging.getLogger(__name__)


# Rest Framework
from rest_framework.response import Response
from rest_framework.decorators import api_view


from ibge.services.ranking import ranking_estados


@api_view(["GET"])
def ranking_estados_view(request):
    logger.info("[ranking_estados_view] Iniciando consulta de ranking de estados")
    ano = int(request.GET.get("ano", 2025))

    print(f"Ranking de estados para o ano {ano}")

    data = ranking_estados(ano)

    return Response(list(data))
