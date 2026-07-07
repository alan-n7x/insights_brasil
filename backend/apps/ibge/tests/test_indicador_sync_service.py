"""Testes da persistencia em lote de indicadores."""

from decimal import Decimal

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from ibge.data_ingestion.services.indicador_sync_service import IndicadorSyncService
from ibge.models import Estado, FatoIndicador, Municipio, Tempo


class IndicadorSyncServiceTest(TestCase):
    def setUp(self):
        estado = Estado.objects.create(
            ibge_id=35, nome="Sao Paulo", sigla="SP", regiao="Sudeste"
        )
        self.municipio = Municipio.objects.create(
            ibge_id=3550308,
            nome="Sao Paulo",
            estado=estado,
            regiao="Sudeste",
        )

    def test_cria_e_atualiza_fatos_em_lote(self):
        service = IndicadorSyncService()
        resultado = service.sync(
            codigo_indicador="PIB",
            registros=[
                {"ibge_id": 3550308, "ano": 2021, "valor": "100.00"},
                {"ibge_id": 3550308, "ano": 2022, "valor": "200.00"},
            ],
        )

        self.assertEqual(resultado, (2, 0))
        self.assertEqual(Tempo.objects.count(), 2)
        self.assertEqual(FatoIndicador.objects.count(), 2)

        resultado = service.sync(
            codigo_indicador="PIB",
            registros=[
                {"ibge_id": 3550308, "ano": 2022, "valor": "250.00"},
            ],
        )

        self.assertEqual(resultado, (1, 0))
        self.assertEqual(
            FatoIndicador.objects.get(tempo__ano=2022).valor,
            Decimal("250.0000"),
        )

    def test_ultimo_duplicado_prevalece_e_invalidos_sao_ignorados(self):
        resultado = IndicadorSyncService().sync(
            codigo_indicador="POPULACAO",
            registros=[
                {"ibge_id": 3550308, "ano": 2022, "valor": 100},
                {"ibge_id": 3550308, "ano": 2022, "valor": 110},
                {"ibge_id": 9999999, "ano": 2022, "valor": 50},
                {"ibge_id": 3550308, "ano": 2023, "valor": None},
            ],
        )

        self.assertEqual(resultado, (1, 2))
        self.assertEqual(FatoIndicador.objects.get().valor, Decimal("110.0000"))

    def test_quantidade_de_queries_nao_cresce_por_registro(self):
        municipios = [
            Municipio(
                ibge_id=3500000 + indice,
                nome=f"Municipio {indice}",
                estado=self.municipio.estado,
            )
            for indice in range(20)
        ]
        Municipio.objects.bulk_create(municipios)
        registros = [
            {"ibge_id": municipio.ibge_id, "ano": 2024, "valor": indice}
            for indice, municipio in enumerate(municipios)
        ]

        with CaptureQueriesContext(connection) as queries:
            resultado = IndicadorSyncService().sync(
                codigo_indicador="TESTE_BULK",
                registros=registros,
            )

        self.assertEqual(resultado, (20, 0))
        self.assertLess(len(queries), 12)
