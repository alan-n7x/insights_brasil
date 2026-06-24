import logging
import time

from ibge.data_ingestion.definitions.sidra_indicadores import PIB

logger = logging.getLogger(__name__)


class SIDRAIndicatorService:
    """
    Service genérico para indicadores SIDRA do IBGE.
    Pode ser usado para qualquer indicador definido em sidra_indicadores.py.
    """

    def __init__(self, client, transformer, indicador=None):
        self.client = client
        self.transformer = transformer
        self.indicador = indicador or PIB  # Default para PIB para compatibilidade

    def fetch(self, ano_inicio, ano_fim=None):

        inicio_execucao = time.perf_counter()

        logger.info(
            "[SIDRAIndicatorService] Buscando %s periodo=%s-%s",
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
                "[SIDRAIndicatorService] Nenhum dado retornado"
            )

            return []

        if "resultados" not in dados[0]:

            logger.warning(
                "[SIDRAIndicatorService] Resposta inesperada da API: %s",
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
            "[SIDRAIndicatorService] %s registros transformados tempo=%.2fs",
            len(registros),
            fim_execucao - inicio_execucao,
        )

        return registros


# Mantido para compatibilidade (alias)
PIBService = SIDRAIndicatorService