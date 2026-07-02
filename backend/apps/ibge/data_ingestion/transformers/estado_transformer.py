"""Transformador de dados de estados da API do IBGE.

Converte a estrutura retornada pela API de localidades do IBGE
no formato interno utilizado pelo sistema.
"""


class EstadoTransformer:
    """Transforma dados brutos de estado da API IBGE para o formato interno."""

    def transform(self, estado):
        """Converte um dicionário de estado da API para o formato de persistência.

        Args:
            estado: Dicionário com os dados brutos do estado retornados pela API.

        Returns:
            Dicionário com campos ibge_id, nome, sigla e regiao.
        """

        return {
            "ibge_id": estado["id"],
            "nome": estado["nome"],
            "sigla": estado["sigla"],
            "regiao": estado["regiao"]["nome"],
        }
