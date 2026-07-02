"""Testes para o mecanismo de consulta DashboardQuery."""

from decimal import Decimal

from django.test import TestCase

from ibge.models import Estado, Indicador, FatoIndicador, Municipio, Tempo
from ibge.query_engine import DashboardQuery


class DashboardQueryTest(TestCase):
    """Testes para os métodos estáticos da classe DashboardQuery."""

    def setUp(self):
        """Configura os dados de teste: estados, municípios, indicadores e fatos."""
        estado = Estado.objects.create(
            ibge_id=35, nome="São Paulo", sigla="SP", regiao="Sudeste"
        )
        self.municipio = Municipio.objects.create(
            ibge_id=3550308, nome="São Paulo", estado=estado, regiao="Sudeste"
        )
        self.municipio2 = Municipio.objects.create(
            ibge_id=3550309, nome="Campinas", estado=estado, regiao="Sudeste"
        )
        self.ind_pop = Indicador.objects.create(
            codigo="POPULACAO", nome="POPULACAO", unidade="Habitantes"
        )
        self.ind_pib = Indicador.objects.create(
            codigo="PIB", nome="PIB", unidade="Mil Reais"
        )
        self.tempo = Tempo.objects.create(ano=2022, mes=None, trimestre=None)

        FatoIndicador.objects.create(
            municipio=self.municipio,
            indicador=self.ind_pop,
            tempo=self.tempo,
            valor=Decimal("10000"),
        )
        FatoIndicador.objects.create(
            municipio=self.municipio2,
            indicador=self.ind_pop,
            tempo=self.tempo,
            valor=Decimal("5000"),
        )
        FatoIndicador.objects.create(
            municipio=self.municipio,
            indicador=self.ind_pib,
            tempo=self.tempo,
            valor=Decimal("200"),
        )
        FatoIndicador.objects.create(
            municipio=self.municipio2,
            indicador=self.ind_pib,
            tempo=self.tempo,
            valor=Decimal("100"),
        )

    def test_summary_nacional(self):
        """Verifica se o sumário nacional calcula corretamente população, PIB e PIB per capita."""
        result = DashboardQuery.summary(ano=2022)
        self.assertEqual(result["populacao"], 15000.0)
        self.assertEqual(result["pib"], 300000.0)
        self.assertAlmostEqual(result["pib_per_capita"], 20.0)

    def test_summary_por_municipio(self):
        """Verifica se o sumário por município retorna os valores corretos."""
        result = DashboardQuery.summary(ano=2022, municipio=3550308)
        self.assertEqual(result["populacao"], 10000.0)
        self.assertEqual(result["pib"], 200000.0)
        self.assertAlmostEqual(result["pib_per_capita"], 20.0)

    def test_get_ranking_by_estado(self):
        """Verifica se o ranking por estado agrega corretamente os valores."""
        ranking = DashboardQuery.get_ranking_by_estado(self.ind_pib, 2022)
        self.assertEqual(len(ranking), 1)
        self.assertEqual(ranking[0]["estado"], "SP")
        self.assertEqual(ranking[0]["valor"], 300000.0)

    def test_get_time_series(self):
        """Verifica se a série temporal retorna os anos e valores corretos."""
        serie = DashboardQuery.get_time_series("populacao")
        self.assertEqual(len(serie), 1)
        self.assertEqual(serie[0]["ano"], 2022)
        self.assertEqual(serie[0]["valor"], 15000.0)

    def test_get_indicator_list_nacional(self):
        """Verifica se a lista nacional de indicadores retorna todos os municípios."""
        data = DashboardQuery._get_indicator_list("populacao", ano=2022)
        self.assertEqual(len(data), 2)
        valores = {d["codigo"]: d["valor"] for d in data}
        self.assertEqual(valores[3550308], 10000.0)
        self.assertEqual(valores[3550309], 5000.0)

    def test_get_indicator_list_com_limite(self):
        """Verifica se o limite de resultados é respeitado na listagem."""
        data = DashboardQuery._get_indicator_list("populacao", ano=2022, limit=1)
        self.assertEqual(len(data), 1)
