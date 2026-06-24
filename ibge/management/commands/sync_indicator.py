import logging
import time

from django.core.management.base import BaseCommand

from ibge.data_ingestion.resolvers.indicator_resolver import IndicatorResolver

from ibge.data_ingestion.services.indicador_sync_service import (
    IndicadorSyncService,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument(
            "--indicator",
            required=True,
        )

        parser.add_argument(
            "--inicio",
            type=int,
            required=True,
        )

        parser.add_argument(
            "--fim",
            type=int,
            required=False,
        )

    def handle(self, *args, **kwargs):

        inicio_execucao = time.perf_counter()

        indicator = kwargs["indicator"].upper()

        ano_inicio = kwargs["inicio"]

        ano_fim = kwargs.get("fim") or ano_inicio

        logger.info(
            "[sync_indicator] Iniciando sync %s %s-%s",
            indicator,
            ano_inicio,
            ano_fim,
        )

        # Usa factory pattern para obter o service correto
        service = IndicatorResolver.get(indicator)

        registros = service.fetch(
            ano_inicio,
            ano_fim,
        )

        sync = IndicadorSyncService()

        sync.sync(
            codigo_indicador=indicator,
            registros=registros,
        )

        fim_execucao = time.perf_counter()

        logger.info(
            "[sync_indicator] FINALIZADO indicador=%s registros=%s tempo=%.2fs",
            indicator,
            len(registros),
            fim_execucao - inicio_execucao,
        )
