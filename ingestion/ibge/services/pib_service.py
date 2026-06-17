import logging
import time

from ingestion.ibge.definitions.sidra_indicadores import PIB

logger = logging.getLogger(__name__)


class PIBService:

    indicador = PIB

    def __init__(self, client, transformer):

        self.client = client
        self.transformer = transformer

    def fetch(self, ano_inicio, ano_fim=None):

        inicio_execucao = time.perf_counter()

        logger.info(
            "[PIBService] Buscando %s periodo=%s-%s",
            self.indicador.nome,
            ano_inicio,
            ano_fim or ano_inicio,
        )

        dados = self.client.get_indicator(
            indicador=self.indicador,
            ano_inicio=ano_inicio,
            ano_fim=ano_fim,
        )

        if not dados:
            logger.warning(
                "[PIBService] Nenhum dado retornado"
            )

            return []

        if "resultados" not in dados[0]:

            logger.warning(
                "[PIBService] Resposta inesperada da API: %s",
                dados,
            )

            return []

        registros = []

        for resultado in dados[0]["resultados"]:

            for serie in resultado.get("series", []):

                registros.extend(
                    self.transformer.transform(
                        serie
                    )
                )

        fim_execucao = time.perf_counter()

        logger.info(
            "[PIBService] %s registros transformados tempo=%.2fs",
            len(registros),
            fim_execucao - inicio_execucao,
        )

        return registros