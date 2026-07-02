"""Serviço de sincronização de municípios a partir da API do IBGE.

Obtém a lista completa de municípios brasileiros da API de
localidades e os transforma para o formato de persistência.
"""

import logging

from ibge.data_ingestion.transformers.municipio_transformer import (
    MunicipioTransformer,
)

logger = logging.getLogger(__name__)


class MunicipiosService:
    """Serviço que coordena a busca e transformação dos municípios."""

    def __init__(self, client):
        """Inicializa o serviço com um cliente HTTP e o transformador de municípios.

        Args:
            client: Instância de IBGEClient para requisições à API.
        """

        self.client = client

        self.transformer = MunicipioTransformer()

    def fetch_municipios(self):
        """Busca todos os municípios na API do IBGE e os transforma.

        Returns:
            Lista de dicionários com os dados dos municípios transformados.
        """

        logger.info("[MunicipiosService] Buscando municípios no IBGE")

        municipios = self.client.get("v1/localidades/municipios")

        logger.info(
            "[MunicipiosService] %s municípios recebidos",
            len(municipios),
        )

        municipios_transformados = []

        for municipio in municipios:
            municipio_transformado = self.transformer.transform(municipio)

            if municipio_transformado:

                municipios_transformados.append(municipio_transformado)

        logger.info(
            "[MunicipiosService] %s municípios transformados",
            len(municipios_transformados),
        )

        return municipios_transformados
