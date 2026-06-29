"""Repositório para persistência de municípios no banco de dados.

Gerencia o ciclo de vida dos registros de municípios, incluindo
criação, atualização e consulta.
"""

import logging

from ibge.models.territorio import Municipio

logger = logging.getLogger(__name__)


class MunicipioRepository:
    """Camada de acesso a dados para a entidade Municipio."""

    def save(self, municipio, estado):
        """Persiste um município associado a um estado (upsert).

        Args:
            municipio: Dicionário com os dados do município transformados.
            estado: Instância do modelo Estado ao qual o município pertence.

        Returns:
            Tupla (objeto, criado) do update_or_create.
        """

        return Municipio.objects.update_or_create(
            ibge_id=municipio["ibge_id"],
            defaults={
                "nome": municipio["nome"],
                "estado": estado,
                "microrregiao_id": municipio["microrregiao_id"],
                "microrregiao_nome": municipio["microrregiao_nome"],
                "mesorregiao_id": municipio["mesorregiao_id"],
                "mesorregiao_nome": municipio["mesorregiao_nome"],
                "regiao_imediata_id": municipio["regiao_imediata_id"],
                "regiao_imediata_nome": municipio["regiao_imediata_nome"],
                "regiao_intermediaria_id": municipio["regiao_intermediaria_id"],
                "regiao_intermediaria_nome": municipio["regiao_intermediaria_nome"],
                "regiao": municipio["regiao"],
            },
        )

    def listar(self):

        logger.info("Buscando municípios no banco")

        return Municipio.objects.all().values(
            "id",
            "nome",
        )
