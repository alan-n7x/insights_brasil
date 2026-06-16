import logging
import requests

logger = logging.getLogger(__name__)


class IBGEClient:

    BASE_URL = "https://servicodados.ibge.gov.br/api/"

    def __init__(self):

        self.session = requests.Session()

    def get(self, endpoint, params=None):

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
