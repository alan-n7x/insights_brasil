"""Comando de gerenciamento Django para sincronizar municípios brasileiros a partir da API do IBGE."""

import logging
import time

from django.core.management.base import BaseCommand

from ibge.data_ingestion.clients.ibge_client import IBGEClient
from ibge.data_ingestion.resolvers.estado_resolver import EstadoResolver
from ibge.data_ingestion.services.municipio_sync_service import MunicipiosService
from ibge.models import Municipio
from ibge.repositories.municipio_repository import MunicipioRepository

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Comando que sincroniza os municípios do IBGE no banco de dados local."""

    def handle(self, *args, **kwargs):
        """Busca, prepara e persiste os municípios em lote."""
        inicio = time.perf_counter()

        logger.info("[sync_municipios] Iniciando sync")

        service = MunicipiosService(IBGEClient())
        repository = MunicipioRepository()
        resolver = EstadoResolver()

        municipios = service.fetch_municipios()

        municipios_para_upsert = []
        ignorados = 0

        for dados in municipios:
            estado = resolver.get(dados["estado_id"])

            if not estado:
                ignorados += 1
                logger.warning(
                    "[sync_municipios] estado não encontrado municipio=%s",
                    dados["nome"],
                )
                continue

            municipios_para_upsert.append(
                Municipio(
                    ibge_id=dados["ibge_id"],
                    nome=dados["nome"],
                    estado=estado,
                    microrregiao_id=dados["microrregiao_id"],
                    microrregiao_nome=dados["microrregiao_nome"],
                    mesorregiao_id=dados["mesorregiao_id"],
                    mesorregiao_nome=dados["mesorregiao_nome"],
                    regiao_imediata_id=dados["regiao_imediata_id"],
                    regiao_imediata_nome=dados["regiao_imediata_nome"],
                    regiao_intermediaria_id=dados["regiao_intermediaria_id"],
                    regiao_intermediaria_nome=dados[
                        "regiao_intermediaria_nome"
                    ],
                    regiao=dados["regiao"],
                )
            )

        processados = repository.bulk_upsert(municipios_para_upsert)

        fim = time.perf_counter()

        logger.info(
            "[sync_municipios] FINALIZADO recebidos=%s "
            "processados=%s ignorados=%s tempo=%.2fs",
            len(municipios),
            processados,
            ignorados,
            fim - inicio,
        )
