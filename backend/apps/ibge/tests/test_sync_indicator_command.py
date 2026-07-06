"""Testes do comando de sincronização genérica de indicadores."""

from unittest.mock import Mock, patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase


class SyncIndicatorCommandTest(SimpleTestCase):
    @patch("ibge.management.commands.sync_indicator.IndicadorSyncService")
    @patch("ibge.management.commands.sync_indicator.IndicatorResolver")
    def test_preserva_fim_ausente_para_consulta_de_ano_unico(
        self, resolver, sync_service_class
    ):
        service = Mock()
        service.fetch.return_value = []
        resolver.get.return_value = service
        resolver.get_indicator_definition.return_value = Mock()

        call_command("sync_indicator", indicator="PIB", inicio=2020)

        service.fetch.assert_called_once_with(2020, None)
        sync_service_class.return_value.sync.assert_called_once()

    @patch("ibge.management.commands.sync_indicator.IndicadorSyncService")
    @patch("ibge.management.commands.sync_indicator.IndicatorResolver")
    def test_repassa_intervalo_quando_fim_e_informado(
        self, resolver, sync_service_class
    ):
        service = Mock()
        service.fetch.return_value = []
        resolver.get.return_value = service
        resolver.get_indicator_definition.return_value = Mock()

        call_command("sync_indicator", indicator="PIB", inicio=2020, fim=2022)

        service.fetch.assert_called_once_with(2020, 2022)
        sync_service_class.return_value.sync.assert_called_once()

    def test_rejeita_intervalo_invertido(self):
        with self.assertRaisesMessage(CommandError, "--fim não pode ser menor que --inicio"):
            call_command("sync_indicator", indicator="PIB", inicio=2022, fim=2020)
