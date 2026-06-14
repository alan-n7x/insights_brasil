# services/indicadores.py

from ...infra.ibge_client import IBGEClient


class IBGEIndicadores:
    """Classe para acessar os indicadores do IBGE."""

    def __init__(self):
        """Inicializa o cliente do IBGE, que é responsável por fazer as requisições HTTP para a API do IBGE."""
        self.client = IBGEClient()

    def listar_estados(self):

        return self.client.get("localidades/estados")
