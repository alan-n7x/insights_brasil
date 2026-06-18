from decimal import Decimal
from ibge.models import IndicadorMunicipio


class PIBPerCapitaService:
    """
    Calcula PIB per capita a partir dos indicadores PIB e POPULACAO.
    """

    PIB_CODIGO = "PIB"
    POPULACAO_CODIGO = "POPULACAO"
    PIB_PER_CAPITA_CODIGO = "PIB_PER_CAPITA"

    def fetch(self, ano_inicio, ano_fim=None):
        ano_fim = ano_fim or ano_inicio

        populacoes = {
            (item.municipio_id, item.ano): item.valor
            for item in IndicadorMunicipio.objects.filter(
                indicador__codigo=self.POPULACAO_CODIGO,
                ano__gte=ano_inicio,
                ano__lte=ano_fim,
            )
        }

        pibs = (
            IndicadorMunicipio.objects.filter(
                indicador__codigo=self.PIB_CODIGO,
                ano__gte=ano_inicio,
                ano__lte=ano_fim,
            )
            .select_related("municipio")
        )

        registros = []

        for pib in pibs:
            populacao = populacoes.get((pib.municipio_id, pib.ano))

            # garante mesmo ano + município
            if populacao is None or populacao <= 0:
                continue

            # 🔥 ajuste importante: PIB do IBGE geralmente vem em mil reais
            pib_valor = pib.valor * Decimal("1000")

            pib_per_capita = (pib_valor / populacao).quantize(
                Decimal("0.01")
            )

            registros.append({
                "ibge_id": pib.municipio.ibge_id,
                "ano": pib.ano,
                "valor": pib_per_capita,
            })

        return registros