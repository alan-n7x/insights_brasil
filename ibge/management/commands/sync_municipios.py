import logging
import time

from django.core.management.base import BaseCommand

from ibge.infra.ibge_client import IBGEClient
from ibge.domain.services.municipios_service import MunicipiosService
from ibge.domain.repositories.municipios_repository import MunicipioRepository
from ibge.models import Estado

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        inicio = time.perf_counter()

        logger.info("[sync_municipios] Iniciando sync")

        service = MunicipiosService(IBGEClient())
        repository = MunicipioRepository()

        municipios = service.fetch_municipios()

        criados = 0
        ignorados = 0

        for m in municipios:

            try:

                estado = Estado.objects.get(codigo_externo=m["estado_id"])

                _, created = repository.save(m, estado)

                if created:
                    criados += 1
                else:
                    ignorados += 1

            except Estado.DoesNotExist:

                ignorados += 1

                logger.warning(
                    "[sync_municipios] estado não encontrado municipio=%s",
                    m["nome"],
                )

        fim = time.perf_counter()

        logger.info(
            "[sync_municipios] FINALIZADO recebidos=%s criados=%s ignorados=%s tempo=%.2fs",
            len(municipios),
            criados,
            ignorados,
            fim - inicio,
        )
