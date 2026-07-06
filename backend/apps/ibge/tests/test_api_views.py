"""Testes de contrato dos endpoints territoriais da API."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ibge.models import Estado, Municipio


class MunicipalityDetailAPITest(APITestCase):
    def setUp(self):
        estado = Estado.objects.create(
            ibge_id=35, nome="São Paulo", sigla="SP", regiao="Sudeste"
        )
        self.municipio = Municipio.objects.create(
            ibge_id=3550308,
            nome="São Paulo",
            estado=estado,
            regiao="Sudeste",
            microrregiao_id=35061,
            microrregiao_nome="São Paulo",
        )

    def test_retorna_contrato_com_estado_aninhado(self):
        response = self.client.get(
            reverse("municipio-detalhe", kwargs={"codigo": self.municipio.ibge_id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["codigo"], 3550308)
        self.assertEqual(response.data["nome"], "São Paulo")
        self.assertEqual(
            response.data["estado"],
            {"sigla": "SP", "nome": "São Paulo", "regiao": "Sudeste"},
        )
        self.assertEqual(response.data["microrregiao_id"], 35061)

    def test_retorna_404_quando_municipio_nao_existe(self):
        response = self.client.get(
            reverse("municipio-detalhe", kwargs={"codigo": 9999999})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
