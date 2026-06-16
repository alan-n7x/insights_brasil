import logging

logger = logging.getLogger(__name__)


class IBGESidraClient:

    def __init__(self, base_client):
        self.client = base_client

    def _get_indicador(
        self,
        agregado: int,
        variavel: int,
        ano_inicio: int,
        ano_fim: int | None = None,
        localidades: str = "N6[all]",
    ):

        if ano_fim is None:
            ano_fim = ano_inicio

        path = (
            f"v3/agregados/{agregado}/"
            f"periodos/{ano_inicio}-{ano_fim}/"
            f"variaveis/{variavel}"
        )

        params = {
            "localidades": localidades,
        }

        return self.client.get(path, params=params)

    def get_populacao(
        self,
        ano_inicio: int,
        ano_fim: int | None = None,
    ):

        logger.info(
            "[IBGESidraClient] Buscando população periodo=%s-%s",
            ano_inicio,
            ano_fim or ano_inicio,
        )

        return self._get_indicador(
            agregado=6579,
            variavel=9324,
            ano_inicio=ano_inicio,
            ano_fim=ano_fim,
        )

    def get_pib(
        self,
        ano_inicio: int,
        ano_fim: int | None = None,
    ):

        logger.info(
            "[IBGESidraClient] Buscando PIB periodo=%s-%s",
            ano_inicio,
            ano_fim or ano_inicio,
        )

        return self._get_indicador(
            agregado=5938,
            variavel=37,
            ano_inicio=ano_inicio,
            ano_fim=ano_fim,
        )