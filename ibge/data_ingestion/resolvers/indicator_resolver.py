from ibge.models import FatoIndicador, Tempo

import logging

logger = logging.getLogger(__name__)


class PIBPerCapitaService:
    """
    Retorna PIB per capita já calculado pelo IBGE (sem recomputar nada).
    """

    PIB_PER_CAPITA_CODIGO = "PIB_PER_CAPITA"

    def fetch(self, ano_inicio, ano_fim=None, estado_id=None):
        ano_fim = ano_fim or ano_inicio

        # Get Tempo objects for the year range
        tempos = Tempo.objects.filter(
            ano__gte=ano_inicio,
            ano__lte=ano_fim,
            mes=None,
            trimestre=None
        )

        qs = FatoIndicador.objects.filter(
            indicador__codigo=self.PIB_PER_CAPITA_CODIGO,
            tempo__in=tempos,
        ).select_related("municipio", "tempo")

        if estado_id:
            qs = qs.filter(municipio__estado_id=estado_id)

        return [
            {
                "ibge_id": item.municipio.ibge_id,
                "nome": item.municipio.nome,
                "ano": item.tempo.ano,
                "valor": float(item.valor),  # já pronto para gráfico
            }
            for item in qs.order_by("tempo__ano", "-valor")
        ]


class IndicatorResolver:
    """
    Factory pattern para obter o service correto para cada indicador.
    """

    @staticmethod
    def get(indicator_code: str):
        """
        Retorna o service correto para o indicador especificado.
        """
        from ibge.data_ingestion.services.pib_service import SIDRAIndicatorService
        from ibge.data_ingestion.services.populacao_sync_service import PopulacaoService
        from ibge.data_ingestion.clients.ibge_client import IBGEClient
        from ibge.data_ingestion.clients.sidra_client import IBGESidraClient
        from ibge.data_ingestion.transformers.pib_transformer import PIBTransformer
        from ibge.data_ingestion.transformers.population_transformer import PopulationTransformer
        from ibge.data_ingestion.definitions.sidra_indicadores import PIB, POPULACAO, PIB_PER_CAPITA

        # Mapeamento de indicadores para transformers
        transformers = {
            "PIB": PIBTransformer(),
            "POPULACAO": PopulationTransformer(),
            "PIB_PER_CAPITA": PIBTransformer(),  # Usa o mesmo transformer que PIB
        }

        # Mapeamento de indicadores para definições SIDRA
        indicadores = {
            "PIB": PIB,
            "POPULACAO": POPULACAO,
            "PIB_PER_CAPITA": PIB_PER_CAPITA,
        }

        if indicator_code not in indicadores:
            raise ValueError(
                f"Indicador {indicator_code} não suportado. "
                f"Indicadores disponíveis: {', '.join(indicadores.keys())}"
            )

        # Para população, usamos o service específico
        if indicator_code == "POPULACAO":
            # Cria client e service específico para população
            base_client = IBGEClient()
            client = IBGESidraClient(base_client)
            transformer = PopulationTransformer()
            service = PopulacaoService(client, transformer)
            return service
        else:
            # Para os outros, usamos o service genérico
            base_client = IBGEClient()
            client = IBGESidraClient(base_client)
            transformer = transformers[indicator_code]
            indicador = indicadores[indicator_code]
            return SIDRAIndicatorService(client, transformer, indicador)
