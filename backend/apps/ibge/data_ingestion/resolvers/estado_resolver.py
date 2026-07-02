"""Resolver para estados com cache em memória.

Fornece acesso rápido a instâncias de Estado por código IBGE,
evitando consultas repetitivas ao banco de dados.
"""

from ibge.models.territorio import Estado


class EstadoResolver:
    """Resolver que mantém um cache em memória dos estados.

    Carrega todos os estados do banco na inicialização e permite
    consulta por código IBGE sem requisições adicionais.
    """

    def __init__(self):
        """Inicializa o cache com todos os estados do banco de dados."""
        self._cache = {
            e.ibge_id: e
            for e in Estado.objects.all()
        }

    def get(self, ibge_id):
        """Retorna um estado pelo seu código IBGE.

        Args:
            ibge_id: Código IBGE do estado.

        Returns:
            Instância de Estado ou None se não encontrado.
        """
        return self._cache.get(ibge_id)