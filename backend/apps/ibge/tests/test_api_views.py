"""Testes de contrato dos endpoints da API."""

from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ibge.models import Estado, FatoIndicador, Indicador, Municipio, Tempo


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


class GenericIndicatorAPITest(APITestCase):
    def setUp(self):
        estado = Estado.objects.create(
            ibge_id=35, nome="São Paulo", sigla="SP", regiao="Sudeste"
        )
        self.municipio = Municipio.objects.create(
            ibge_id=3550308, nome="São Paulo", estado=estado, regiao="Sudeste"
        )
        indicador = Indicador.objects.create(
            codigo="IDH", nome="Índice de Desenvolvimento Humano", unidade="Índice"
        )
        tempo = Tempo.objects.create(ano=2022)
        FatoIndicador.objects.create(
            municipio=self.municipio,
            indicador=indicador,
            tempo=tempo,
            valor=Decimal("0.805"),
        )

    def test_lista_indicador_sem_view_ou_repositorio_especifico(self):
        response = self.client.get(
            reverse("indicador-list", kwargs={"codigo": "IDH"}),
            {"ano": 2022, "order_by": "valor"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["items"][0]["codigo"], self.municipio.ibge_id)
        self.assertEqual(response.data["items"][0]["valor"], 0.805)

    def test_retorna_serie_do_indicador_generico(self):
        response = self.client.get(
            reverse("indicador-serie", kwargs={"codigo": "IDH"}),
            {"municipio": self.municipio.ibge_id},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [{"ano": 2022, "value": 0.805}])

    def test_retorna_ranking_do_indicador_generico(self):
        response = self.client.get(
            reverse("indicador-ranking", kwargs={"codigo": "IDH"}),
            {"ano": 2022},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [{"position": 1, "state": "SP", "value": 0.805}],
        )
