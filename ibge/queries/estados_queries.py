from ibge.models import Estado
import logging


logger = logging.getLogger(__name__)

def listar_estados():
    logger.info("[listar_estados] Listando estados")
    return Estado.objects.all().values(
        "id",
        "ibge_id",
        "nome",
        "sigla",
        "regiao",
    )
