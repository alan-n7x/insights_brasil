import logging

logger = logging.getLogger(__name__)


class IBGESidraClient:

    def __init__(self, base_client):
        self.client = base_client

    def get_populacao(self, ano_inicio: int, ano_fim: int):

        logger.info(
            "[IBGESidraClient] Buscando população periodo=%s-%s",
            ano_inicio,
            ano_fim,
        )

        path = (
            f"v3/agregados/6579/" f"periodos/{ano_inicio}-{ano_fim}/" f"variaveis/9324"
        )

        params = {
            "localidades": "N6[all]",
        }

        return self.client.get(path, params=params)
