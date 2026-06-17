"""
LEGACY

Substituído por:

python manage.py sync_indicator --indicator PIB



import logging
import time

from django.core.management.base import BaseCommand

# from ibge.models.territorio import PIBMunicipio

from ingestion.ibge.clients.ibge_client import IBGEClient

from ingestion.ibge.clients.sidra_client import (
    IBGESidraClient,
)

from ingestion.ibge.services.pib_service import (
    PIBService,
)

from ingestion.ibge.repositories.legacy.pib_repository import (
    PIBRepository,
)

from ingestion.ibge.resolvers.municipio_resolver import (
    MunicipioResolver,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        inicio = time.perf_counter()

        logger.info("[sync_pib] Iniciando sync")

        service = PIBService(IBGESidraClient(IBGEClient()))

        repository = PIBRepository()

        resolver = MunicipioResolver()

        pibs = service.fetch_pib(
            2018,
            2021,
        )

        objetos = []

        ignorados = 0

        for pib in pibs:

            municipio = resolver.get(pib["municipio_ibge_id"])

            if not municipio:

                ignorados += 1

                continue

            objetos.append(
                PIBMunicipio(
                    municipio=municipio,
                    ano=pib["ano"],
                    valor=pib["valor"],
                )
            )

        inicio_save = time.perf_counter()

        repository.bulk_create(objetos)

        fim_save = time.perf_counter()

        fim = time.perf_counter()

        logger.info(
            "[sync_pib] Persistencia tempo=%.2fs",
            fim_save - inicio_save,
        )

        logger.info(
            "[sync_pib] FINALIZADO "
            "recebidos=%s "
            "salvos=%s "
            "ignorados=%s "
            "tempo=%.2fs",
            len(pibs),
            len(objetos),
            ignorados,
            fim - inicio,
        )
"""
