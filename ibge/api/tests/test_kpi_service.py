from django.test import TestCase
from ibge.models import Indicador, FatoIndicador, Municipio, Tempo, Estado
from ibge.api.services.kpi_service import KPIService

class KPIServiceTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Indicadores
        cls.pop   = Indicador.objects.create(codigo='POPULACAO',   nome='População')
        cls.pib   = Indicador.objects.create(codigo='PIB',        nome='PIB')
        cls.pibpc = Indicador.objects.create(codigo='PIB_PER_CAPITA', nome='PIB per Capita')
        # Estado
        cls.estado = Estado.objects.create(nome='Estado Teste', sigla='ET', regiao='Centro-Oeste', ibge_id=1)
        # Municípios
        cls.m1 = Municipio.objects.create(nome='São Paulo', ibge_id=1, estado=cls.estado)
        cls.m2 = Municipio.objects.create(nome='Rio de Janeiro', ibge_id=2, estado=cls.estado)
        # Additional state for ranking tests
        cls.estado2 = Estado.objects.create(nome='Estado Teste 2', sigla='ET2', regiao='Nordeste', ibge_id=2)
        cls.m3 = Municipio.objects.create(nome='Municipio A', ibge_id=3, estado=cls.estado2)
        cls.m4 = Municipio.objects.create(nome='Municipio B', ibge_id=4, estado=cls.estado2)
        # Anos
        cls.t2021 = Tempo.objects.create(ano=2021)
        cls.t2022 = Tempo.objects.create(ano=2022)
        # Dados POPULACAO
        FatoIndicador.objects.create(municipio=cls.m1, indicador=cls.pop,  tempo=cls.t2021, valor=100)
        FatoIndicador.objects.create(municipio=cls.m2, indicador=cls.pop,  tempo=cls.t2021, valor=200)
        # Dados PIB
        FatoIndicador.objects.create(municipio=cls.m1, indicador=cls.pib,  tempo=cls.t2021, valor=1000)
        FatoIndicador.objects.create(municipio=cls.m2, indicador=cls.pib,  tempo=cls.t2021, valor=2000)
        # Dados PIB adicional para segundo estado
        FatoIndicador.objects.create(municipio=cls.m3, indicador=cls.pib,  tempo=cls.t2021, valor=500)
        FatoIndicador.objects.create(municipio=cls.m4, indicador=cls.pib,  tempo=cls.t2021, valor=1500)
        # Dados PIB_PER_CAPITA (já pronto)
        FatoIndicador.objects.create(municipio=cls.m1, indicador=cls.pibpc, tempo=cls.t2021, valor=5000)
        FatoIndicador.objects.create(municipio=cls.m2, indicador=cls.pibpc, tempo=cls.t2021, valor=6000)
        # Opcional: PIB per capita para segundo estado
        FatoIndicador.objects.create(municipio=cls.m3, indicador=cls.pibpc, tempo=cls.t2021, valor=2000)
        FatoIndicador.objects.create(municipio=cls.m4, indicador=cls.pibpc, tempo=cls.t2021, valor=2500)

    def test_soma_padrao(self):
        res = KPIService.get_indicators(['POPULACAO'], ano=2021)
        self.assertEqual(res['POPULACAO']['valor'], 300.0)   # 100+200

    def test_pib_per_capita_raw_com_ano(self):
        res = KPIService.get_indicators(['PIB_PER_CAPITA'], ano=2021)
        self.assertIsInstance(res['PIB_PER_CAPITA']['valor'], dict)
        self.assertAlmostEqual(res['PIB_PER_CAPITA']['valor']['São Paulo'], 5000.0)
        self.assertAlmostEqual(res['PIB_PER_CAPITA']['valor']['Rio de Janeiro'], 6000.0)

    def test_pib_per_capita_raw_sem_ano(self):
        res = KPIService.get_indicators(['PIB_PER_CAPITA'], ano=None)
        self.assertIsInstance(res['PIB_PER_CAPITA']['valor'], dict)
        sp = res['PIB_PER_CAPITA']['valor']['São Paulo']
        self.assertIn(2021, sp)
        self.assertAlmostEqual(sp[2021], 5000.0)

    def test_indicador_desconhecido_placeholder(self):
        res = KPIService.get_indicators(['NAO_EXISTE'])
        self.assertIsNone(res['NAO_EXISTE']['valor'])
        self.assertEqual(res['NAO_EXISTE']['nome'], '')
        self.assertEqual(res['NAO_EXISTE']['codigo'], 'NAO_EXISTE')

    def test_pib_por_estado(self):
        res = KPIService.get_indicators(['PIB'], ano=2021)
        self.assertIsInstance(res['PIB']['valor'], list)
        vals = res['PIB']['valor']
        self.assertEqual(len(vals), 2)
        # Order descending by total
        self.assertEqual(vals[0]['nome'], 'Estado Teste')
        self.assertAlmostEqual(vals[0]['total'], 3000.0)
        self.assertEqual(vals[1]['nome'], 'Estado Teste 2')
        self.assertAlmostEqual(vals[1]['total'], 2000.0)
