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

    def get_indicador(self, codigo: str):

        indicador, _ = Indicador.objects.get_or_create(
            codigo=codigo,
            defaults={
                "nome": codigo,
            },
        )

        return indicador

    def get_municipio(self, ibge_id):

        return self.resolver.get(ibge_id)

    def sync(
        self,
        codigo_indicador: str,
        registros: list[dict],
    ):

        logger.info(
            "[IndicadorSync] Iniciando sync %s registros=%s",
            codigo_indicador,
            len(registros),
        )

        indicador = self.get_indicador(codigo_indicador)

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
