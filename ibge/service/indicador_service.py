from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class IndicadorService:

    PIB = "PIB"
    POPULACAO = "POPULACAO"
    PIB_PER_CAPITA = "PIB_PER_CAPITA"

    # -------------------------
    # CORE: PIB PER CAPITA (ESTADOS)
    # -------------------------
    def calcular_pib_per_capita_estados(self, pibs, populacoes):

        pop_map = {
            row["estado"]: row["populacao_total"]
            for row in populacoes
        }

        resultado = []

        for row in pibs:
            pop = pop_map.get(row["estado"])

            if not pop:
                continue

            resultado.append({
                "estado": row["estado"],
                "total": (row["pib_total"] / pop).quantize(Decimal("0.01")),
            })

        return self._ordenar(resultado, key="total", reverse=True)

    # -------------------------
    # CORE: PIB PER CAPITA (EVOLUÇÃO)
    # -------------------------
    def calcular_pib_per_capita_evolucao(self, pibs, populacoes):

        logger.info("[PIB_PER_CAPITA_EVOLUCAO]")

        pop_map = {
            row["ano"]: row["populacao_total"]
            for row in populacoes
        }

        resultado = []

        for row in pibs:
            pop = pop_map.get(row["ano"])

            if not pop:
                continue

            resultado.append({
                "ano": row["ano"],
                "total": (row["pib_total"] / pop).quantize(Decimal("0.01")),
            })

        return self._ordenar(resultado, key="ano")

    # -------------------------
    # UTIL: NORMALIZAR RANKING
    # -------------------------
    def formatar_ranking(self, rows, label_field="estado"):
        return [
            {
                label_field: row[label_field],
                "total": row["total"],
            }
            for row in rows
        ]

    # -------------------------
    # UTIL: NORMALIZAR EVOLUÇÃO
    # -------------------------
    def formatar_evolucao(self, rows):
        return [
            {
                "ano": row["ano"],
                "total": row["total"],
            }
            for row in rows
        ]

    # -------------------------
    # UTIL: ORDENAÇÃO GENÉRICA
    # -------------------------
    def _ordenar(self, data, key="total", reverse=False):
        return sorted(data, key=lambda x: x[key], reverse=reverse)