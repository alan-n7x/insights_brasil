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
            ano=2021,
            valor=12000000,
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

    def test_ranking_populacao_por_estado_legacy(self):
        response = self.client.get(
            "/api/ibge/populacao/ranking-estados/",
            {"ano": 2022},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [{"estado": "São Paulo", "total": "12345678"}],
        )

    def test_lista_anos_populacao_legacy(self):
        response = self.client.get("/api/ibge/populacao/anos/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [2021, 2022])

    def test_lista_indicadores(self):
        response = self.client.get("/api/ibge/indicadores/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    "id": self.indicador.id,
                    "codigo": "POPULACAO",
                    "nome": "População",
                }
            ],
        )

    def test_lista_anos_indicador(self):
        response = self.client.get("/api/ibge/indicadores/populacao/anos/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [2021, 2022])

    def test_ranking_estados_indicador(self):
        response = self.client.get(
            "/api/ibge/indicadores/POPULACAO/ranking-estados/",
            {"ano": 2022},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [{"estado": "São Paulo", "total": "12345678"}],
        )

    def test_ranking_municipios_indicador(self):
        response = self.client.get(
            "/api/ibge/indicadores/POPULACAO/ranking-municipios/",
            {"ano": 2022},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    "municipio": "São Paulo",
                    "municipio_ibge_id": 3550308,
                    "estado": "São Paulo",
                    "sigla": "SP",
                    "total": "12345678",
                }
            ],
        )

    def test_evolucao_estado_indicador(self):
        response = self.client.get("/api/ibge/indicadores/POPULACAO/evolucao/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {"ano": 2021, "total": "12000000"},
                {"ano": 2022, "total": "12345678"},
            ],
        )

    def test_evolucao_municipio_indicador(self):
        response = self.client.get(
            "/api/ibge/indicadores/POPULACAO/municipios/3550308/evolucao/",
            {"ano_inicio": 2022},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{"ano": 2022, "valor": "12345678.00"}])

    def test_indicador_inexistente_retorna_404(self):
        response = self.client.get("/api/ibge/indicadores/INVALIDO/anos/")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {
                "erro": "Indicador não encontrado",
                "indicador": "INVALIDO",
            },
        )
