import logging
from ibge.models.territorio import Municipio

logger = logging.getLogger(__name__)


def listar_municipios():
    logger.info("[listar_municipios] Listando municípios")

    return Municipio.objects.all().values(
        "id",
        "ibge_id",
        "nome",
        "estado_id",
    )
