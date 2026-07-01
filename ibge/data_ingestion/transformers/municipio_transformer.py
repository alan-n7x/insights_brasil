"""Transformador de dados de municípios da API do IBGE.

Converte a estrutura complexa e hierárquica da API de localidades
do IBGE (com microrregiões, mesorregiões e regiões geográficas)
no modelo achatado utilizado pelo sistema.
"""

import logging

logger = logging.getLogger(__name__)


class MunicipioTransformer:
    """Transforma dados brutos de município da API IBGE para o formato interno."""

    def transform(self, m):
        """Converte um dicionário de município da API para o formato de persistência.

        Lida com as diferentes estruturas de dados da API (microrregião
        e regiao-imediata) e extrai as informações hierárquicas.

        Args:
            m: Dicionário com os dados brutos do município retornados pela API.

        Returns:
            Dicionário com os campos normalizados do município ou None se inválido.
        """

        logger.debug(
            "[MunicipioTransformer] Transformando municipio=%s",
            m.get("nome"),
        )

        # Estrutura antiga
        microrregiao = m.get("microrregiao") or {}
        mesorregiao = microrregiao.get("mesorregiao") or {}

        # Estrutura nova
        regiao_imediata = m.get("regiao-imediata") or {}
        regiao_intermediaria = (
            regiao_imediata.get("regiao-intermediaria") or {}
        )

        # UF pode vir por qualquer um dos caminhos
        uf = (
            mesorregiao.get("UF")
            or regiao_intermediaria.get("UF")
            or {}
        )

        regiao = uf.get("regiao") or {}

        estado_id = uf.get("id")

        # Investigação
        if estado_id is None:

            logger.warning(
                (
                    "[MunicipioTransformer] UF não encontrada "
                    "municipio=%s "
                    "ibge_id=%s "
                    "payload=%s"
                ),
                m.get("nome"),
                m.get("id"),
                m,
            )

        return {

            # obrigatórios
            "ibge_id": m.get("id"),
            "nome": m.get("nome"),
            "estado_id": estado_id,

            # opcionais
            "microrregiao_id": microrregiao.get("id"),
            "microrregiao_nome": microrregiao.get("nome"),

            "mesorregiao_id": mesorregiao.get("id"),
            "mesorregiao_nome": mesorregiao.get("nome"),

            "regiao_imediata_id": regiao_imediata.get("id"),
            "regiao_imediata_nome": regiao_imediata.get("nome"),

            "regiao_intermediaria_id": regiao_intermediaria.get("id"),
            "regiao_intermediaria_nome": regiao_intermediaria.get("nome"),

            "regiao": regiao.get("nome"),
        }