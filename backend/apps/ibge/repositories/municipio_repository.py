"""Repositório para o modelo Municipio (leitura e escrita)."""

import logging

from django.db import transaction
from django.utils import timezone
from ibge.models import Municipio

logger = logging.getLogger(__name__)


class MunicipioRepository:
    """Repositório para consulta e persistência de municípios."""

    @staticmethod
    def save(municipio, estado):
        """Persiste um município associado a um estado (upsert).

        Args:
            municipio: Dicionário com os dados do município transformados.
            estado: Instância do modelo Estado ao qual o município pertence.

        Returns:
            Tupla (objeto, criado) do update_or_create.
        """
        return Municipio.objects.update_or_create(
            ibge_id=municipio["ibge_id"],
            defaults={
                "nome": municipio["nome"],
                "estado": estado,
                "microrregiao_id": municipio["microrregiao_id"],
                "microrregiao_nome": municipio["microrregiao_nome"],
                "mesorregiao_id": municipio["mesorregiao_id"],
                "mesorregiao_nome": municipio["mesorregiao_nome"],
                "regiao_imediata_id": municipio["regiao_imediata_id"],
                "regiao_imediata_nome": municipio["regiao_imediata_nome"],
                "regiao_intermediaria_id": municipio["regiao_intermediaria_id"],
                "regiao_intermediaria_nome": municipio["regiao_intermediaria_nome"],
                "regiao": municipio["regiao"],
            },
        )

    @staticmethod
    def bulk_upsert(municipios: list[Municipio], batch_size: int = 500) -> int:
        """Cria ou atualiza municípios em lote.

        Args:
            municipios: Instâncias que serão criadas ou atualizadas.
            batch_size: Quantidade máxima de registros processados por lote.

        Returns:
            Quantidade de municípios enviados para persistência.
        """

        if not municipios:
            logger.info("Nenhum município para sincronizar.")

            return 0
        agora = timezone.now()

        update_fields = [
            "nome",
            "estado",
            "microrregiao_id",
            "microrregiao_nome",
            "mesorregiao_id",
            "mesorregiao_nome",
            "regiao_imediata_id",
            "regiao_imediata_nome",
            "regiao_intermediaria_id",
            "regiao_intermediaria_nome",
            "regiao",
            "atualizado_em",
        ]

        logger.info(
            "Enviando %s municípios para UPSERT em lote. batch_size=%s",
            len(municipios),
            batch_size,
        )

        for municipio in municipios:
            municipio.atualizado_em = agora

        with transaction.atomic():
            Municipio.objects.bulk_create(
                municipios,
                batch_size=batch_size,
                update_conflicts=True,
                unique_fields=["ibge_id"],
                update_fields=update_fields,
            )

        return len(municipios)

    @staticmethod
    def listar():
        """Retorna os identificadores e nomes de todos os municípios.

        Returns:
            QuerySet contendo os campos `id` e `nome`.
        """
        logger.info("Buscando municípios no banco")
        return Municipio.objects.all().values("id", "nome")

    @staticmethod
    def get_by_codigo(codigo: int):
        """Retorna uma instância de Municipio pelo código IBGE ou None.

        Args:
            codigo: Código IBGE do município.

        Returns:
            Instância de Municipio ou None.
        """
        try:
            return Municipio.objects.get(ibge_id=codigo)
        except Municipio.DoesNotExist:
            return None

    @staticmethod
    def filter_by_estado(sigla: str):
        """Retorna QuerySet de municípios filtrados pela sigla do estado.

        Args:
            sigla: Sigla do estado (ex: SP, RJ).

        Returns:
            QuerySet de Municipio.
        """
        return Municipio.objects.filter(estado__sigla=sigla.upper())

    @staticmethod
    def all():
        """Retorna todos os municípios.

        Returns:
            QuerySet contendo todas as instâncias de Município.
        """
        return Municipio.objects.all()

    @staticmethod
    def values_list_id_nome():
        """Retorna os identificadores e nomes de todos os municípios.

        Returns:
            QuerySet de tuplas no formato `(id, nome)`.
        """
        return Municipio.objects.values_list("id", "nome")

    @staticmethod
    def values_id_nome_sigla():
        """Retorna municípios com a sigla dos respectivos estados.

        Returns:
            QuerySet de dicionários com id, nome e sigla do estado.
        """
        return Municipio.objects.values("id", "nome", "estado__sigla")
