"""Cliente especializado para a API SIDRA do IBGE.

Monta URLs específicas do SIDRA a partir de definições de indicadores
e delega a requisição HTTP ao cliente base.
"""

import logging

from ibge.data_ingestion.definitions.sidra_indicadores import IndicadorSIDRA

logger = logging.getLogger(__name__)


class IBGESidraClient:
    """Cliente para consulta de agregados SIDRA do IBGE.

    Converte definições de indicadores em chamadas à API de agregados
    do SIDRA, gerenciando períodos e localidades.
    """

    def __init__(self, base_client):
        """Inicializa o cliente SIDRA.

        Args:
            base_client: Instância de IBGECliente para executar as requisições.
        """

        self.client = base_client

    def get_indicator(
        self,
        indicador: IndicadorSIDRA,
        ano_inicio: int,
        ano_fim: int | None = None,
        localidades: str = "N6[all]",
    ):
        """Obtém dados de um indicador SIDRA para o período e localidades informados.

        Args:
            indicador: Definição do indicador (agregado, variável, nome).
            ano_inicio: Ano inicial do período de consulta.
            ano_fim: Ano final do período (opcional; se omitido, consulta apenas ano_inicio).
            localidades: Código das localidades no formato SIDRA (padrão: N6[all]).

        Returns:
            Lista de dicionários com os dados retornados pela API SIDRA.
        """

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
