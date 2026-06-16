import logging
import time

from ingestion.ibge.transformers.pib_transformer import (
    PIBTransformer,
)

logger = logging.getLogger(__name__)


class PIBService:

    def __init__(self, client):

        self.client = client

        self.transformer = PIBTransformer()

    def fetch_pib(
        self,
        ano_inicio: int,
        ano_fim: int | None = None,
    ):

        inicio = time.perf_counter()

        logger.info(
            "[PIBService] Buscando PIB periodo=%s-%s",
            ano_inicio,
            ano_fim or ano_inicio,
        )

        dados = self.client.get_pib(
            ano_inicio,
            ano_fim,
        )

        resultados = dados[0]["resultados"]

        logger.info(
            "[PIBService] %s resultados recebidos",
            len(resultados),
        )

        registros = []

        for resultado in resultados:

            for serie in resultado["series"]:

                registros.extend(self.transformer.transform(serie))

        fim = time.perf_counter()

        logger.info(
            "[PIBService] %s registros transformados tempo=%.2fs",
            len(registros),
            fim - inicio,
        )

        return registros
