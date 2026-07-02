"""Resolver factory para indicadores do IBGE.

Mapeia códigos de indicadores às suas definições SIDRA e
aos serviços e transformadores adequados para cada tipo.
"""

import logging

logger = logging.getLogger(__name__)


class IndicatorResolver:
    """Factory que retorna o service correto para cada indicador.

    Mantém mapeamentos internos de indicadores para transformadores
    e definições SIDRA, inicializados sob demanda.
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
