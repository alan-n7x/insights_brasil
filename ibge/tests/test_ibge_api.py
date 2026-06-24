from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from ibge.data_ingestion.clients.ibge_client import IBGEClient


class IBGEClientTest(SimpleTestCase):

    @patch("ibge.data_ingestion.clients.ibge_client.requests.Session")
    def test_get_retorna_json_da_api(self, session_class):
        response = Mock()
        response.status_code = 200
        response.json.return_value = [{"id": 35, "nome": "São Paulo"}]
        response.raise_for_status.return_value = None

        session = Mock()
        session.get.return_value = response
        session_class.return_value = session

        client = IBGEClient()
        data = client.get("v1/localidades/estados")

        session.get.assert_called_once_with(
            "https://servicodados.ibge.gov.br/api/v1/localidades/estados",
            params=None,
            timeout=10,
        )
        response.raise_for_status.assert_called_once()
        self.assertEqual(data, [{"id": 35, "nome": "São Paulo"}])

    @patch("ibge.data_ingestion.clients.ibge_client.requests.Session")
    def test_get_repassa_parametros(self, session_class):
        response = Mock()
        response.status_code = 200
        response.json.return_value = []
        response.raise_for_status.return_value = None

        session = Mock()
        session.get.return_value = response
        session_class.return_value = session

        client = IBGEClient()
        client.get("v3/agregados", params={"localidades": "N6[all]"})

        session.get.assert_called_once_with(
            "https://servicodados.ibge.gov.br/api/v3/agregados",
            params={"localidades": "N6[all]"},
            timeout=10,
        )