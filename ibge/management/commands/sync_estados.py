import logging
import requests

from django.core.management.base import BaseCommand

from ibge.domain.repositories.estado_repository import EstadoRepository
from ibge.infra.ibge_client import IBGEClient
from ibge.domain.services.estados_service import EstadosService

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "Sincroniza os estados do IBGE"

    def handle(self, *args, **kwargs):

        logger.info("[sync_estados] Sincronização iniciada")

        service = EstadosService(IBGEClient())

        repository = EstadoRepository()

        estados = service.fetch_estados()

        criados = 0

        for estado in estados:

            _, created = repository.save(estado)

            if created:
                criados += 1

        logger.info(
            "[sync_estados] Recebidos=%s Criados=%s",
            len(estados),
            criados,
        )
