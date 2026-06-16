import requests

from django.test import TestCase


class TestIBGEAPI(TestCase):

    def test_conexao_ibge_estados(self):

        url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"

        response = requests.get(url, timeout=10)

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertTrue(isinstance(data, list))

        self.assertGreater(len(data), 0)