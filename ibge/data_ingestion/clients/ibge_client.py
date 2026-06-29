"""Cliente HTTP para consumo da API de dados do IBGE.

Fornece uma camada de comunicação com os serviços REST do IBGE,
gerenciando sessões, requisições e tratamento de erros.
"""

import logging
import requests

logger = logging.getLogger(__name__)


class IBGEClient:
    """Cliente base para requisições à API do IBGE.

    Encapsula uma sessão HTTP reutilizável e disponibiliza métodos
    padronizados para acesso aos endpoints da API.
    """

    BASE_URL = "https://servicodados.ibge.gov.br/api"

    def __init__(self):
        """Inicializa o cliente com uma sessão HTTP própria."""

        self.session = requests.Session()

    def get(self, endpoint, params=None):
        """Executa uma requisição GET ao endpoint informado.

        Args:
            endpoint: Caminho do recurso relativo à BASE_URL.
            params: Dicionário opcional de parâmetros de consulta.

        Returns:
            Dados JSON retornados pela API.

        Raises:
            requests.RequestException: Em caso de falha na requisição.
        """

        url = f"{self.BASE_URL}/{endpoint}"

        logger.info(f"[IBGEClient] GET {url}")

        try:

            response = self.session.get(url, params=params, timeout=10)

            logger.info(f"[IBGEClient] STATUS {response.status_code}")

            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:

            logger.exception(f"[IBGEClient] ERRO em {url}: {e}")
            raise
