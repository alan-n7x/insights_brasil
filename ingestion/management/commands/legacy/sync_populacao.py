"""
LEGACY

Substituído por:


python manage.py sync_indicator --indicator POPULACAO


import logging
import time

from django.core.management.base import BaseCommand
from django.db import transaction

from ingestion.ibge.clients.ibge_client import IBGEClient
from ingestion.ibge.clients.sidra_client import IBGESidraClient
from ingestion.ibge.services.populacao_sync_service import PopulacaoService
from ingestion.ibge.repositories.populacao_repository import PopulacaoRepository
from ibge.models.territorio import Municipio

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        inicio = time.perf_counter()

        logger.info("[sync_populacao] Iniciando")

        base_client = IBGEClient()
        agregados_client = IBGESidraClient(base_client)

        service = PopulacaoService(agregados_client)
        repository = PopulacaoRepository()

        dados = service.fetch_populacao()

        municipios_map = {str(m.ibge_id): m for m in Municipio.objects.all()}

        created = updated = ignored = 0

        with transaction.atomic():

            for item in dados:

                municipio = municipios_map.get(item["municipio_id"])

                if not municipio:
                    ignored += 1
                    continue

                result = repository.save(municipio, item["ano"], item["populacao"])

                if result == "created":
                    created += 1
                elif result == "updated":
                    updated += 1
                else:
                    ignored += 1

        fim = time.perf_counter()

        logger.info(
            "[sync_populacao] finalizado created=%s updated=%s ignored=%s tempo=%.2fs",
            created,
            updated,
            ignored,
            fim - inicio,
        )
"""
