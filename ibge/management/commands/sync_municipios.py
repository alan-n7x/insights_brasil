"""Comando de gerenciamento Django para sincronizar municípios brasileiros a partir da API do IBGE."""

import logging
import time

from django.core.management.base import BaseCommand

from ibge.data_ingestion.clients.ibge_client import IBGEClient
from ibge.data_ingestion.services.municipio_sync_service import MunicipiosService
from ibge.data_ingestion.repositories.municipios_repository import MunicipioRepository
from ibge.data_ingestion.resolvers.estado_resolver import EstadoResolver

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Comando que sincroniza os municípios do IBGE no banco de dados local."""

    def handle(self, *args, **kwargs):
        """Executa a sincronização: busca municípios da API e persiste associando ao estado correspondente."""
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
