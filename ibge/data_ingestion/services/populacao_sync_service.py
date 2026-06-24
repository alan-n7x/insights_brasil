import logging

from ibge.data_ingestion.definitions.sidra_indicadores import POPULACAO

logger = logging.getLogger(__name__)


class PopulacaoService:

    indicador = POPULACAO

    def __init__(self, client, transformer):

        self.client = client

        self.transformer = transformer

    def fetch(self, ano_inicio, ano_fim=None):

        logger.info(
            "[PopulacaoService] Buscando %s periodo=%s-%s",
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

            logger.warning("[PopulacaoService] Nenhum dado retornado")

            return []

        if "resultados" not in dados[0]:

            logger.warning(
                "[PopulacaoService] Resposta inesperada: %s",
                dados,
            )

            return []

        return self.transformer.transform(dados)
