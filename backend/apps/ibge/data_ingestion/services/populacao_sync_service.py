"""Serviço de sincronização de dados populacionais do IBGE.

Especializado na consulta e transformação do indicador de
população residente, que possui estrutura de resposta distinta
dos demais indicadores SIDRA.
"""

import logging

from ibge.data_ingestion.definitions.sidra_indicadores import POPULACAO

logger = logging.getLogger(__name__)


class PopulacaoService:
    """Serviço específico para o indicador de população."""

    indicador = POPULACAO

    def __init__(self, client, transformer):
        """Inicializa o serviço com cliente SIDRA e transformador de população.

        Args:
            client: Instância de IBGESidraClient.
            transformer: Instância de PopulationTransformer.
        """

        self.client = client

        self.transformer = transformer

    def fetch(self, ano_inicio, ano_fim=None):
        """Busca dados de população na API SIDRA e retorna registros transformados.

        Args:
            ano_inicio: Ano inicial do período.
            ano_fim: Ano final do período (opcional).

        Returns:
            Lista de dicionários com registros de população (ibge_id, ano, valor).
        """

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
