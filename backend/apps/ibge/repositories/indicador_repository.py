"""Repositório somente-leitura para o modelo Indicador."""

from ibge.models import Indicador


class IndicadorRepository:
    """Repositório para consulta de indicadores cadastrados no catálogo."""

    @staticmethod
    def get_by_codigo(codigo: str):
        """Retorna uma instância de Indicador pelo código ou None se não encontrado.

        Args:
            codigo: Código do indicador (ex: 'POPULACAO', 'PIB').

        Returns:
            Instância de Indicador ou None.
        """
        try:
            return Indicador.objects.get(codigo=codigo)
        except Indicador.DoesNotExist:
            return None

    @staticmethod
    def get_populacao():
        """Retorna o indicador de população."""
        return IndicadorRepository.get_by_codigo('POPULACAO')

    @staticmethod
    def get_pib():
        """Retorna o indicador de PIB."""
        return IndicadorRepository.get_by_codigo('PIB')

    @staticmethod
    def get_pib_per_capita():
        """Retorna o indicador de PIB per capita."""
        return IndicadorRepository.get_by_codigo('PIB_PER_CAPITA')
