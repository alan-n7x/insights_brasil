"""Serviço genérico para indicadores da API SIDRA do IBGE.

Implementa o fluxo padronizado de consulta à API SIDRA e
transformação dos dados para qualquer indicador definido.
"""

import logging
import time

from ibge.data_ingestion.definitions.sidra_indicadores import PIB

logger = logging.getLogger(__name__)


class SIDRAIndicatorService:
    """Serviço genérico para consulta de indicadores SIDRA.

    Pode ser utilizado para qualquer indicador definido no módulo
    sidra_indicadores.py, delegando a transformação ao respectivo
    transformador.
    """

    def __init__(self, client, transformer, indicador=None):
        """Inicializa o serviço com cliente, transformador e definição do indicador.

        Args:
            client: Instância de IBGESidraClient.
            transformer: Instância do transformador específico do indicador.
            indicador: Definição do indicador (padrão: PIB para compatibilidade).
        """
        self.client = client
        self.transformer = transformer
        self.indicador = indicador or PIB

    def fetch(self, ano_inicio, ano_fim=None):
        """Busca dados do indicador na API SIDRA e retorna registros transformados.

        Args:
            ano_inicio: Ano inicial do período.
            ano_fim: Ano final do período (opcional; se omitido, apenas ano_inicio).

        Returns:
            Lista de dicionários com registros transformados (ibge_id, ano, valor).
        """

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