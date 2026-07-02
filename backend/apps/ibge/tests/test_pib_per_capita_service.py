"""Testes para o serviço de cálculo de PIB per capita."""

from decimal import Decimal

from django.test import TestCase

from ibge.models import Estado, Indicador, FatoIndicador, Municipio, Tempo
from ibge.data_ingestion.services.pib_per_capita_service import PIBPerCapitaService


class PIBPerCapitaServiceTest(TestCase):
    """Testes para o cálculo de PIB per capita a partir dos dados de PIB e população."""

    def setUp(self):
        """Configura os dados de teste: estado, município, indicadores de PIB e população."""
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
        self.tempo_2022 = Tempo.objects.create(
            ano=2022,
            mes=None,
            trimestre=None
        )

    def test_calcula_pib_per_capita(self):
        """Verifica se o PIB per capita é calculado corretamente dividindo PIB pela população."""
        FatoIndicador.objects.create(
            municipio=self.municipio,
            indicador=self.pib,
            tempo=self.tempo_2022,
            valor=Decimal("200"),
        )
        FatoIndicador.objects.create(
            municipio=self.municipio,
            indicador=self.populacao,
            tempo=self.tempo_2022,
            valor=Decimal("1000"),
        )

        registros = PIBPerCapitaService().fetch(2022)

        self.assertEqual(
            registros,
            [
                {
                    "ibge_id": 3550308,
                    "ano": 2022,
                    "valor": Decimal("200.00"),
                }
            ],
        )
