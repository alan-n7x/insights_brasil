"""Repositório para persistência de estados no banco de dados."""

import logging

from ibge.models.territorio import Estado

logger = logging.getLogger(__name__)


class EstadoRepository:
    """Camada de acesso a dados para a entidade Estado."""

    @staticmethod
    def save_many(estados):
        """Persiste uma lista de estados utilizando upsert (cria ou atualiza).

        Args:
            estados: Lista de dicionários com os dados dos estados.

        Returns:
            Tupla (total_processado, total_criado) com a contagem de registros.
        """
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
