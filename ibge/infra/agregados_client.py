import logging

logger = logging.getLogger(__name__)


class IBGEAgregadosClient:

    def __init__(self, base_client):

        self.client = base_client

    def get_populacao(self, ano_inicio, ano_fim):

        logger.info("[IBGEAgregadosClient] Buscando população")

        path = f"v3/agregados/6579/" f"periodos/{ano_inicio}-{ano_fim}/variaveis/9324"

        params = {"localidades": "N6[all]"}

        return self.client.get(path, params=params)
