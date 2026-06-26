from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from ibge.models import Indicador, FatoIndicador, Municipio, Tempo, Estado

class KpiViewSetTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Indicadores
        cls.pop   = Indicador.objects.create(codigo='POPULACAO',   nome='População')
        cls.pibpc = Indicador.objects.create(codigo='PIB_PER_CAPITA', nome='PIB per Capita')
        # Estado
        cls.estado = Estado.objects.create(nome='Estado Teste', sigla='ET', regiao='Centro-Oeste', ibge_id=1)
        # Municípios
        cls.m1 = Municipio.objects.create(nome='São Paulo', ibge_id=1, estado=cls.estado)
        cls.m2 = Municipio.objects.create(nome='Rio de Janeiro', ibge_id=2, estado=cls.estado)
        # Ano
        cls.t2021 = Tempo.objects.create(ano=2021)
        # Dados
        FatoIndicador.objects.create(municipio=cls.m1, indicador=cls.pop,  tempo=cls.t2021, valor=100)
        FatoIndicador.objects.create(municipio=cls.m2, indicador=cls.pop,  tempo=cls.t2021, valor=200)
        FatoIndicador.objects.create(municipio=cls.m1, indicador=cls.pibpc, tempo=cls.t2021, valor=5000)
        FatoIndicador.objects.create(municipio=cls.m2, indicador=cls.pibpc, tempo=cls.t2021, valor=6000)

    def setUp(self):
        self.client = APIClient()

    def test_case_insensitive_indicators(self):
        resp = self.client.get(reverse('kpi-list'), {
            'indicadores': 'populacao,pib_per_capita',
            'ano': 2021
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('POPULACAO', data)
        self.assertIn('PIB_PER_CAPITA', data)
        self.assertIsInstance(data['POPULACAO']['valor'], (int, float))
        self.assertEqual(data['POPULACAO']['valor'], 300.0)  # 100+200
        self.assertIsInstance(data['PIB_PER_CAPITA']['valor'], dict)
        self.assertAlmostEqual(data['PIB_PER_CAPITA']['valor']['São Paulo'], 5000.0)
        self.assertAlmostEqual(data['PIB_PER_CAPITA']['valor']['Rio de Janeiro'], 6000.0)

    def test_default_indicators_when_empty(self):
        resp = self.client.get(reverse('kpi-list'), {'indicadores': ''})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('POPULACAO', data)  # fallback do serializer
        self.assertIsInstance(data['POPULACAO']['valor'], (int, float))

    def test_unknown_indicator_warning(self):
        # Após implementarmos o warning na view, esperamos campo _warnings
        resp = self.client.get(reverse('kpi-list'), {
            'indicadores': 'populacao,desconhecido',
            'ano': 2021
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('POPULACAO', data)
        self.assertIn('DESCONHECIDO', data)  # uppercased
        # Valor None para desconhecido
        self.assertIsNone(data['DESCONHECIDO']['valor'])
        # Esperamos warning
        self.assertIn('_warnings', data)
        self.assertIn('DESCONHECIDO', data['_warnings'])
