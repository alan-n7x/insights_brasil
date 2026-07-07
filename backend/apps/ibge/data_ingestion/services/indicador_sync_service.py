"""Servico de sincronizacao de indicadores municipais."""

import logging

from ibge.models import Indicador
from ibge.repositories.fato_indicador_repository import FatoIndicadorRepository
from ibge.data_ingestion.resolvers.municipio_resolver import MunicipioResolver

logger = logging.getLogger(__name__)


class IndicadorSyncService:
    """Coordena a sincronizacao em lote de indicadores por municipio."""

    def __init__(self):
        self.repo = FatoIndicadorRepository()
        self.resolver = MunicipioResolver()

    def get_indicador(self, codigo: str, indicador_def=None):
        """Obtem ou cria o indicador e sincroniza seus metadados."""
        indicador, _ = Indicador.objects.get_or_create(
            codigo=codigo,
            defaults={"nome": codigo},
        )
        if indicador_def is not None:
            indicador.nome = indicador_def.nome
            indicador.descricao = indicador_def.descricao
            indicador.unidade = indicador_def.unidade
            indicador.periodicidade = indicador_def.periodicidade
            indicador.fonte = indicador_def.fonte
            indicador.save()

        return indicador

    def get_municipio(self, ibge_id):
        """Resolve um municipio pelo codigo IBGE usando o cache."""
        return self.resolver.get(ibge_id)

    def sync(
        self,
        codigo_indicador: str,
        indicador_def=None,
        registros: list[dict] | None = None,
    ) -> tuple[int, int]:
        """Sincroniza os registros com um unico upsert por lote."""
        registros = registros or []
        logger.info(
            "[IndicadorSync] Iniciando sync %s registros=%s",
            codigo_indicador,
            len(registros),
        )

        indicador = self.get_indicador(codigo_indicador, indicador_def)
        municipios = self.resolver.get_many(
            registro.get("ibge_id") for registro in registros
        )
        total, erros = self.repo.bulk_upsert(
            registros=registros,
            indicador=indicador,
            municipios=municipios,
        )

        logger.info(
            "[IndicadorSync] indicador=%s total=%s erros=%s",
            codigo_indicador,
            total,
            erros,
        )
        return total, erros
