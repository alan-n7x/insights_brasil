"""Transformador de dados de PIB da API SIDRA do IBGE.

Converte a série temporal de PIB por município retornada pela
API SIDRA em uma lista de registros padronizados.
"""

from decimal import Decimal


class PIBTransformer:
    """Transforma séries de PIB da API SIDRA para o formato interno."""

    def transform(self, serie):
        """Converte uma série SIDRA de PIB em registros individuais por ano.

        Ignora valores nulos ou indicadores de dados indisponíveis.

        Args:
            serie: Dicionário com localidade id e dict ano -> valor.

        Returns:
            Lista de dicionários com ibge_id, ano e valor (Decimal).
        """

        municipio_ibge_id = int(serie["localidade"]["id"])

        registros = []

        for ano, valor in serie["serie"].items():

            if valor in (None, "-", "..."):
                continue

            registros.append(
                {
                    "ibge_id": municipio_ibge_id,  # <- CORRIGIDO
                    "ano": int(ano),
                    "valor": Decimal(valor),
                }
            )

        return registros
