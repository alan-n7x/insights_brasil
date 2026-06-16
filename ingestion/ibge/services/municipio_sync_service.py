import logging

from ingestion.ibge.transformers.municipio_transformer import (
    MunicipioTransformer,
)

logger = logging.getLogger(__name__)


class MunicipiosService:

    def __init__(self, client):

        self.client = client

        self.transformer = MunicipioTransformer()

    def fetch_municipios(self):

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
