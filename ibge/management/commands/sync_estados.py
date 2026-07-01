"""Comando de gerenciamento Django para sincronizar os estados brasileiros a partir da API do IBGE."""

import logging

from django.core.management.base import BaseCommand

from ibge.data_ingestion.services.estado_sync_service import EstadoSyncService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Comando que sincroniza os estados do IBGE no banco de dados local."""

    help = "Sincroniza os estados do IBGE"

    def handle(self, *args, **kwargs):
        """Executa a sincronização: obtém os dados da API e persiste os estados."""
        logger.info("[sync_estados] Sincronização iniciada")

        service = EstadoSyncService()

        total, criados = service.execute()

        logger.info(
            "[sync_estados] Recebidos=%s Criados=%s",
            total,
            criados,
        )
