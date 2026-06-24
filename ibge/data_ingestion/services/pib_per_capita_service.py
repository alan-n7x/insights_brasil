from decimal import Decimal
from ibge.models import FatoIndicador, Tempo


class PIBPerCapitaService:
    """
    Calcula PIB per capita a partir dos indicadores PIB e POPULACAO.
    """

    PIB_CODIGO = "PIB"
    POPULACAO_CODIGO = "POPULACAO"
    PIB_PER_CAPITA_CODIGO = "PIB_PER_CAPITA"

    def fetch(self, ano_inicio, ano_fim=None):
        ano_fim = ano_fim or ano_inicio

        # Get Tempo objects for the year range
        tempos = Tempo.objects.filter(
            ano__gte=ano_inicio,
            ano__lte=ano_fim,
            mes=None,
            trimestre=None
        )

        populacoes = {
            (item.municipio_id, item.tempo.ano): item.valor
            for item in FatoIndicador.objects.filter(
                indicador__codigo=self.POPULACAO_CODIGO,
                tempo__in=tempos,
            )
        }

        pibs = (
            FatoIndicador.objects.filter(
                indicador__codigo=self.PIB_CODIGO,
                tempo__in=tempos,
            )
            .select_related("municipio", "tempo")
        )

        registros = []

        for pib in pibs:
            populacao = populacoes.get((pib.municipio_id, pib.tempo.ano))

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
                "ano": pib.tempo.ano,
                "valor": pib_per_capita,
            })

        return registros