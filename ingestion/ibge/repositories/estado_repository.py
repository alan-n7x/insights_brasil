import logging

from ibge.models.territorio import Estado

logger = logging.getLogger(__name__)


class EstadoRepository:

    def save_many(self, estados):

        criados = 0

        logger.info("[EstadoRepository] Salvando %s estados", len(estados))

        for estado in estados:

            _, created = Estado.objects.update_or_create(
                ibge_id=estado["ibge_id"], defaults=estado
            )

            if created:

                criados += 1

        logger.info("[EstadoRepository] Criados=%s", criados)

        return len(estados), criados
