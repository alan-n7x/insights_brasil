from ingestion.ibge.definitions.sidra_indicadores import PIB, POPULACAO

from ingestion.ibge.clients.ibge_client import IBGEClient
from ingestion.ibge.clients.sidra_client import IBGESidraClient

from ingestion.ibge.services.pib_service import PIBService
from ingestion.ibge.services.pib_per_capita_service import PIBPerCapitaService
from ingestion.ibge.services.populacao_sync_service import PopulacaoService

from ingestion.ibge.transformers.pib_transformer import PIBTransformer
from ingestion.ibge.transformers.population_transformer import PopulationTransformer


class IndicatorResolver:

    @staticmethod
    def get(codigo):

        codigo = codigo.upper()

        client = IBGESidraClient(IBGEClient())

        services = {
            PIB.nome: PIBService(
                client,
                PIBTransformer(),
            ),
            POPULACAO.nome: PopulacaoService(
                client,
                PopulationTransformer(),
            ),
            PIBPerCapitaService.PIB_PER_CAPITA_CODIGO: PIBPerCapitaService(),
        }

        return services[codigo]
