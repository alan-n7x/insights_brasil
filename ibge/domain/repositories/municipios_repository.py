import logging
from ibge.models import Municipio

logger = logging.getLogger(__name__)


class MunicipioRepository:

    def save(self, municipio, estado):

        return Municipio.objects.update_or_create(
            codigo_externo=municipio["codigo_externo"],
            defaults={
                "nome": municipio["nome"],
                "estado": estado,
            },
        )

    def listar(self):

        logger.info("Buscando municípios no banco")

        return Municipio.objects.all().values(
            "id",
            "nome",
        )
