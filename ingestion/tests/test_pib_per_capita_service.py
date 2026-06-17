from decimal import Decimal

from django.test import TestCase

from ibge.models import Estado, Indicador, IndicadorMunicipio, Municipio
from ingestion.ibge.services.pib_per_capita_service import PIBPerCapitaService


class PIBPerCapitaServiceTest(TestCase):

    def setUp(self):
        estado = Estado.objects.create(
            ibge_id=35,
            nome="São Paulo",
            sigla="SP",
            regiao="Sudeste",
        )
        self.municipio = Municipio.objects.create(
            ibge_id=3550308,
            nome="São Paulo",
            estado=estado,
            regiao="Sudeste",
        )
        self.pib = Indicador.objects.create(
            codigo="PIB",
            nome="PIB",
        )
        self.populacao = Indicador.objects.create(
            codigo="POPULACAO",
            nome="População",
        )

    def test_calcula_pib_per_capita(self):
        IndicadorMunicipio.objects.create(
            municipio=self.municipio,
            indicador=self.pib,
            ano=2022,
            valor=Decimal("200000"),
        )
        IndicadorMunicipio.objects.create(
            municipio=self.municipio,
            indicador=self.populacao,
            ano=2022,
            valor=Decimal("1000"),
        )

        registros = PIBPerCapitaService().fetch(2022)

        self.assertEqual(
            registros,
            [
                {
                    "ibge_id": 3550308,
                    "ano": 2022,
                    "valor": Decimal("200000.00"),
                }
            ],
        )

    def test_ignora_municipio_sem_populacao_no_mesmo_ano(self):
        IndicadorMunicipio.objects.create(
            municipio=self.municipio,
            indicador=self.pib,
            ano=2022,
            valor=Decimal("200000"),
        )

        registros = PIBPerCapitaService().fetch(2022)

        self.assertEqual(registros, [])
