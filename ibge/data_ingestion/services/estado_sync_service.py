"""Serviço de sincronização de estados a partir da API do IBGE.

Orquestra o fluxo de busca, transformação e persistência dos
dados de estados brasileiros.
"""

import logging

from ibge.data_ingestion.clients.ibge_client import IBGEClient
from ibge.data_ingestion.transformers.estado_transformer import EstadoTransformer
from ibge.repositories.estado_repository import EstadoRepository

logger = logging.getLogger(__name__)


class EstadoSyncService:
    """Serviço que coordena a sincronização completa dos estados."""

    def __init__(self):
        """Configura o cliente, transformador e repositório de estados."""

        self.client = IBGEClient()

        self.transformer = EstadoTransformer()

        self.repository = EstadoRepository()

    def execute(self):
        """Executa o fluxo completo de sincronização dos estados.

        Busca os estados na API do IBGE, transforma os dados
        conforme o formato esperado e persiste no banco.

        Returns:
            Tupla (total_processado, total_criado) com a contagem de registros.
        """

        logger.info("[EstadoSyncService] Buscando estados no IBGE")

        estados = self.client.get("v1/localidades/estados")

        logger.info("[EstadoSyncService] %s estados recebidos", len(estados))

        estados_transformados = [
            self.transformer.transform(estado) for estado in estados
        ]

        logger.info("[EstadoSyncService] Estados transformados")

        total, criados = self.repository.save_many(estados_transformados)

        logger.info(
            "[EstadoSyncService] Total=%s Criados=%s",
            total,
            criados,
        )

        return total, criados
