import logging

from ibge.data_ingestion.clients.ibge_client import IBGEClient
from ibge.data_ingestion.transformers.estado_transformer import EstadoTransformer
from ibge.data_ingestion.repositories.estado_repository import EstadoRepository

logger = logging.getLogger(__name__)


class EstadoSyncService:

    def __init__(self):

        self.client = IBGEClient()

        self.transformer = EstadoTransformer()

        self.repository = EstadoRepository()

    def execute(self):

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
