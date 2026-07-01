"""Resolver para municípios com cache em memória.

Fornece acesso rápido a instâncias de Municipio por código IBGE
com carregamento antecipado de todos os registros.
"""

from ibge.models.territorio import Municipio


class MunicipioResolver:
    """Resolver que mantém um cache em memória dos municípios.

    Carrega todos os municípios do banco na inicialização e permite
    consulta por código IBGE sem novas consultas ao banco.
    """

    def __init__(self):
        """Inicializa o cache com todos os municípios do banco de dados."""
        self._cache = {m.ibge_id: m for m in Municipio.objects.all()}

    def get(self, ibge_id):
        """Retorna um município pelo seu código IBGE.

        Args:
            ibge_id: Código IBGE do município.

        Returns:
            Instância de Municipio ou None se não encontrado.
        """
        return self._cache.get(ibge_id)
