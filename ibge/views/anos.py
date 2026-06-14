import logging

from rest_framework.decorators import api_view
from rest_framework.response import Response

from ibge.services.ano_service import listar_anos

logger = logging.getLogger(__name__)


@api_view(["GET"])
def listar_anos_view(request):

    logger.info("[listar_anos_view] Consultando anos disponíveis")

    anos = listar_anos()

    return Response(list(anos))
