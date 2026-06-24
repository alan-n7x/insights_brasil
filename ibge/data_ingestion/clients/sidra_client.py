import logging

from ibge.data_ingestion.definitions.sidra_indicadores import IndicadorSIDRA

logger = logging.getLogger(__name__)


class IBGESidraClient:

    def __init__(self, base_client):

        self.client = base_client

    def get_indicator(
        self,
        indicador: IndicadorSIDRA,
        ano_inicio: int,
        ano_fim: int | None = None,
        localidades: str = "N6[all]",
    ):

        periodo = str(ano_inicio) if ano_fim is None else f"{ano_inicio}-{ano_fim}"

        logger.info(
            "[IBGESidraClient] Buscando %s periodo=%s",
            indicador.nome,
            periodo,
        )

        path = (
            f"v3/agregados/{indicador.agregado}/"
            f"periodos/{periodo}/"
            f"variaveis/{indicador.variavel}"
        )

        return self.client.get(
            path,
            params={
                "localidades": localidades,
            },
        )
