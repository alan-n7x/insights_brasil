from django.test import TestCase
from django.urls import reverse

from ibge.models import Estado, Indicador, IndicadorMunicipio, Municipio


class IBGEAPITest(TestCase):

    def setUp(self):
        self.estado = Estado.objects.create(
            ibge_id=35,
            nome="São Paulo",
            sigla="SP",
            regiao="Sudeste",
        )
        self.municipio = Municipio.objects.create(
            ibge_id=3550308,
            nome="São Paulo",
            estado=self.estado,
            regiao="Sudeste",
        )
        self.indicador = Indicador.objects.create(
            codigo="POPULACAO",
            nome="População",
        )
        IndicadorMunicipio.objects.create(
            municipio=self.municipio,
            indicador=self.indicador,
            ano=2022,
            valor=12345678,
        )

    def test_lista_estados(self):
        response = self.client.get(reverse("listar-estados"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()[0],
            {
                "id": self.estado.id,
                "ibge_id": 35,
                "nome": "São Paulo",
                "sigla": "SP",
                "regiao": "Sudeste",
            },
        )

    def test_lista_municipios(self):
        response = self.client.get(reverse("listar-municipios"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()[0],
            {
                "id": self.municipio.id,
                "ibge_id": 3550308,
                "nome": "São Paulo",
                "estado_id": self.estado.id,
            },
        )

    def test_ranking_populacao_por_estado(self):
        response = self.client.get(
            "/api/ibge/populacao/ranking-estados/",
            {"ano": 2022},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [{"estado": "São Paulo", "total": "12345678"}],
        )

    def test_lista_anos_populacao(self):
        response = self.client.get("/api/ibge/populacao/anos/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [2022])
