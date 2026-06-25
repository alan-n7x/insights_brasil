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

    # Mapeamento de indicadores para transformers
    _transformers = {}

    # Mapeamento de indicadores para definições SIDRA
    _indicadores = {}

    @classmethod
    def _initialize_mappings(cls):
        # Avoid circular imports by importing inside the method
        from ibge.data_ingestion.transformers.pib_transformer import PIBTransformer
        from ibge.data_ingestion.transformers.population_transformer import PopulationTransformer
        from ibge.data_ingestion.definitions.sidra_indicadores import IndicadorSIDRA

        # Clear existing mappings (in case of re-initialization)
        cls._transformers.clear()
        cls._indicadores.clear()

        # Import the module containing indicator definitions
        import ibge.data_ingestion.definitions.sidra_indicadores as sidra_module

        # Iterate over all attributes of the module
        for attr_name in dir(sidra_module):
            attr = getattr(sidra_module, attr_name)
            # Check if the attribute is an instance of IndicadorSIDRA
            if isinstance(attr, IndicadorSIDRA):
                # Use the attribute name as the indicator code (e.g., "POPULACAO")
                indicator_code = attr_name
                cls._indicadores[indicator_code] = attr

                # Determine transformer: POPULACAO uses PopulationTransformer, others use PIBTransformer
                if indicator_code == "POPULACAO":
                    cls._transformers[indicator_code] = PopulationTransformer()
                else:
                    cls._transformers[indicator_code] = PIBTransformer()

        logger.debug(
            "[IndicatorResolver] Initialized %d indicators: %s",
            len(cls._indicadores),
            list(cls._indicadores.keys()),
        )

    @staticmethod
    def get(indicator_code: str):
        """
        Retorna o service correto para o indicador especificado.
        """
        # Initialize mappings on first call
        if not IndicatorResolver._indicadores:
            IndicatorResolver._initialize_mappings()

        from ibge.data_ingestion.services.pib_service import SIDRAIndicatorService
        from ibge.data_ingestion.services.populacao_sync_service import PopulacaoService
        from ibge.data_ingestion.clients.ibge_client import IBGEClient
        from ibge.data_ingestion.clients.sidra_client import IBGESidraClient

        if indicator_code not in IndicatorResolver._indicadores:
            raise ValueError(
                f"Indicador {indicator_code} não suportado. "
                f"Indicadores disponíveis: {', '.join(IndicatorResolver._indicadores.keys())}"
            )

        # Para população, usamos o service específico
        if indicator_code == "POPULACAO":
            # Cria client e service específico para população
            base_client = IBGEClient()
            client = IBGESidraClient(base_client)
            transformer = IndicatorResolver._transformers[indicator_code]
            service = PopulacaoService(client, transformer)
            return service
        else:
            # Para os outros, usamos o service genérico
            base_client = IBGEClient()
            client = IBGESidraClient(base_client)
            transformer = IndicatorResolver._transformers[indicator_code]
            indicador = IndicatorResolver._indicadores[indicator_code]
            return SIDRAIndicatorService(client, transformer, indicador)

    @staticmethod
    def get_indicator_definition(indicator_code: str):
        """
        Retorna a definição do indicador (Instancia de IndicadorSIDRA) para o código especificado.
        """
        if not IndicatorResolver._indicadores:
            IndicatorResolver._initialize_mappings()
        if indicator_code not in IndicatorResolver._indicadores:
            raise ValueError(
                f"Indicador {indicator_code} não suportado. "
                f"Indicadores disponíveis: {', '.join(IndicatorResolver._indicadores.keys())}"
            )
        return IndicatorResolver._indicadores[indicator_code]
