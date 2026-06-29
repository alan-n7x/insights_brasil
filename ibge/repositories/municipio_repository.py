"""Repositório somente-leitura para o modelo Municipio."""

from ibge.models import Municipio


class MunicipioRepository:
    """Repositório para consulta de municípios."""

    @staticmethod
    def get_by_codigo(codigo: int):
        """Retorna uma instância de Municipio pelo código IBGE ou None.

        Args:
            codigo: Código IBGE do município.

        Returns:
            Instância de Municipio ou None.
        """
        try:
            return Municipio.objects.get(ibge_id=codigo)
        except Municipio.DoesNotExist:
            return None

    @staticmethod
    def filter_by_estado(sigla: str):
        """Retorna QuerySet de municípios filtrados pela sigla do estado.

        Args:
            sigla: Sigla do estado (ex: SP, RJ).

        Returns:
            QuerySet de Municipio.
        """
        return Municipio.objects.filter(estado__sigla=sigla.upper())

    @staticmethod
    def all():
        """Retorna QuerySet com todos os municípios."""
        return Municipio.objects.all()

    @staticmethod
    def values_list_id_nome():
        """Retorna lista de tuplas (id, nome) de todos os municípios."""
        return Municipio.objects.values_list('id', 'nome')

    @staticmethod
    def values_id_nome_sigla():
        """Retorna lista de dicionários com id, nome e sigla do estado."""
        return Municipio.objects.values(
            'id',
            'nome',
            'estado__sigla'
        )
