"""Serviço de sincronização de indicadores municipais.

Gerencia a obtenção ou criação de indicadores e a persistência
de registros de fato (valor por município/ano) no banco.
"""

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
    """Serviço que coordena a sincronização de indicadores para municípios."""

    def __init__(self):
        """Inicializa o repositório de fatos e o resolver de municípios."""

        self.repo = FatoIndicadorRepository()

        self.resolver = MunicipioResolver()

    def get_indicador(self, codigo: str, indicador_def=None):
        """Obtém ou cria um registro de indicador pelo código.

        Se uma definição SIDRA for fornecida, mantém os metadados
        sincronizados com a definição.

        Args:
            codigo: Código identificador do indicador.
            indicador_def: Instância opcional de IndicadorSIDRA para atualização.

        Returns:
            Instância do modelo Indicador.
        """

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
        """Resolve um município pelo código IBGE usando o cache.

        Args:
            ibge_id: Código IBGE do município.

        Returns:
            Instância de Municipio ou None.
        """
        return self.resolver.get(ibge_id)

    def sync(
        self,
        codigo_indicador: str,
        indicador_def=None,
        registros: list[dict] = None,
    ):
        """Sincroniza registros de um indicador para múltiplos municípios.

        Percorre a lista de registros, resolve cada município e persiste
        o fato (valor do indicador por município/ano).

        Args:
            codigo_indicador: Código do indicador a ser sincronizado.
            indicador_def: Definição SIDRA opcional para atualizar metadados.
            registros: Lista de dicionários com ibge_id, ano e valor.
        """

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
