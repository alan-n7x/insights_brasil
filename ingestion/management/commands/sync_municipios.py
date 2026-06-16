import logging
import time

from django.core.management.base import BaseCommand

from ingestion.ibge.clients.ibge_client import IBGEClient
from ingestion.ibge.services.municipio_sync_service import MunicipiosService
from ingestion.ibge.repositories.municipios_repository import MunicipioRepository
from ingestion.ibge.resolvers.estado_resolver import EstadoResolver

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        inicio = time.perf_counter()

        logger.info("[sync_municipios] Iniciando sync")

        service = MunicipiosService(IBGEClient())
        repository = MunicipioRepository()
        resolver = EstadoResolver()

        municipios = service.fetch_municipios()

        criados = 0
        ignorados = 0

        for m in municipios:

            estado = resolver.get(m["estado_id"])

            if not estado:
                ignorados += 1
                logger.warning(
                    "[sync_municipios] estado não encontrado municipio=%s",
                    m["nome"],
                )
                continue

            _, created = repository.save(m, estado)

            if created:
                criados += 1
            else:
                ignorados += 1

        fim = time.perf_counter()

        logger.info(
            "[sync_municipios] FINALIZADO recebidos=%s criados=%s ignorados=%s tempo=%.2fs",
            len(municipios),
            criados,
            ignorados,
            fim - inicio,
        )
