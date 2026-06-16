import logging

from ingestion.ibge.definitions.sidra_indicadores import (
    IndicadorSIDRA,
    PIB,
    POPULACAO,
)

logger = logging.getLogger(__name__)


class IBGESidraClient:

    def __init__(self, base_client):

        self.client = base_client

    def _get_indicador(
        self,
        indicador: IndicadorSIDRA,
        ano_inicio: int,
        ano_fim: int | None = None,
        localidades: str = "N6[all]",
    ):

        if ano_fim is None:
            ano_fim = ano_inicio

        logger.info(
            "[IBGESidraClient] Buscando %s periodo=%s-%s",
            indicador.nome,
            ano_inicio,
            ano_fim,
        )

        path = (
            f"v3/agregados/{indicador.agregado}/"
            f"periodos/{ano_inicio}-{ano_fim}/"
            f"variaveis/{indicador.variavel}"
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

        return self._get_indicador(
            indicador=POPULACAO,
            ano_inicio=ano_inicio,
            ano_fim=ano_fim,
        )

    def get_pib(
        self,
        ano_inicio: int,
        ano_fim: int | None = None,
    ):

        return self._get_indicador(
            indicador=PIB,
            ano_inicio=ano_inicio,
            ano_fim=ano_fim,
        )