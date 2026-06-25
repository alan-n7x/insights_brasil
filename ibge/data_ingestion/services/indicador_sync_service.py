import logging

from ibge.models import Indicador, Municipio

from ibge.data_ingestion.repositories.indicador_municipio_repository import (
    FatoIndicadorRepository,
)

from ibge.data_ingestion.resolvers.municipio_resolver import (
    MunicipioResolver,
)

logger = logging.getLogger(__name__)


class IndicadorSyncService:

    def __init__(self):

        self.repo = FatoIndicadorRepository()

        self.resolver = MunicipioResolver()

    def get_indicador(self, codigo: str, indicador_def=None):

        indicador, created = Indicador.objects.get_or_create(
            codigo=codigo,
            defaults={
                "nome": codigo,
            },
        )
        if indicador_def is not None:
            # Update fields from definition to keep in sync with sidra_indicadores.py
            indicador.nome = indicador_def.nome
            indicador.descricao = indicador_def.descricao
            indicador.unidade = indicador_def.unidade
            indicador.periodicidade = indicador_def.periodicidade
            indicador.fonte = indicador_def.fonte
            indicador.save()

        return indicador

    def get_municipio(self, ibge_id):

        return self.resolver.get(ibge_id)

    def sync(
        self,
        codigo_indicador: str,
        indicador_def=None,
        registros: list[dict] = None,
    ):

        logger.info(
            "[IndicadorSync] Iniciando sync %s registros=%s",
            codigo_indicador,
            len(registros) if registros else 0,
        )

        indicador = self.get_indicador(codigo_indicador, indicador_def)

        total = 0

        erros = 0

        for row in registros:

            try:

                ibge_id = row.get("ibge_id")

                if not ibge_id:

                    erros += 1

                    logger.warning(
                        "[IndicadorSync] Registro inválido: %s",
                        row,
                    )

                    continue

                municipio = self.get_municipio(ibge_id)

                self.repo.save(
                    municipio=municipio,
                    indicador=indicador,
                    ano=row["ano"],
                    valor=row["valor"],
                )

                total += 1

            except Municipio.DoesNotExist:

                erros += 1

                logger.warning(
                    "[IndicadorSync] Município não encontrado: %s",
                    row.get("ibge_id"),
                )

            except Exception as e:

                erros += 1

                logger.exception(
                    "[IndicadorSync] erro inesperado: %s",
                    str(e),
                )

        logger.info(
            "[IndicadorSync] indicador=%s total=%s erros=%s",
            codigo_indicador,
            total,
            erros,
        )
