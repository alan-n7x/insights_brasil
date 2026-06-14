import logging
from ibge.models import Estado

logger = logging.getLogger(__name__)


class EstadoRepository:

    def listar(self):

        logger.info("Buscando estados no banco")

        return Estado.objects.all().values(
            "codigo_externo",
            "nome",
            "sigla",
            "regiao",
        )

    def save(self, estado):

        return Estado.objects.update_or_create(
            codigo_externo=estado["id"],
            defaults={
                "nome": estado["nome"],
                "sigla": estado["sigla"],
                "regiao": estado["regiao"],  # <- aqui
            },
        )
