"""Transformador de dados populacionais da API SIDRA do IBGE.

Converte a resposta estruturada da API SIDRA para o indicador
de população em registros individuais por município e ano.
"""

import logging

logger = logging.getLogger(__name__)


class PopulationTransformer:
    """Transforma dados de população da API SIDRA para o formato interno."""

    def transform(self, data):
        """Converte a resposta da API SIDRA em registros de população.

        Extrai as séries de população, filtra valores inválidos e
        retorna registros padronizados.

        Args:
            data: Lista de resultados retornada pela API SIDRA.

        Returns:
            Lista de dicionários com ibge_id, ano e valor (int).
        """
        
        series = data[0]["resultados"][0]["series"]

        result = []

        for item in series:

            codigo = item["localidade"]["id"]

            for ano, pop in item["serie"].items():

                if pop in ("...", "..", "-", None, ""):
                    continue

                try:

                    populacao = int(pop)

                except (ValueError, TypeError):

                    continue

                result.append(
                    {
                        "ibge_id": int(codigo),
                        "ano": int(ano),
                        "valor": populacao,
                    }
                )

        return result
