import logging

from django.core.management.base import BaseCommand

from ingestion.ibge.services.estado_sync_service import EstadoSyncService

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "Sincroniza os estados do IBGE"

    def handle(self, *args, **kwargs):

        logger.info("[sync_estados] Sincronização iniciada")

        service = EstadoSyncService()

        total, criados = service.execute()

        logger.info(
            "[sync_estados] Recebidos=%s Criados=%s",
            total,
            criados,
        )
