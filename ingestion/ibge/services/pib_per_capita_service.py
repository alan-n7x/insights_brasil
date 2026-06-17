from decimal import Decimal

from ibge.models import IndicadorMunicipio


class PIBPerCapitaService:
    """
    Calcula PIB per capita a partir dos indicadores PIB e POPULACAO.

    O PIB municipal do SIDRA é tratado como valor em mil reais, por isso o
    cálculo multiplica o PIB por 1000 antes de dividir pela população.
    """

    PIB_CODIGO = "PIB"
    POPULACAO_CODIGO = "POPULACAO"
    PIB_PER_CAPITA_CODIGO = "PIB_PER_CAPITA"
    PIB_MULTIPLICADOR = Decimal("1000")

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

        registros = []

        pibs = IndicadorMunicipio.objects.filter(
            indicador__codigo=self.PIB_CODIGO,
            ano__gte=ano_inicio,
            ano__lte=ano_fim,
        ).select_related("municipio")

        for pib in pibs:
            populacao = populacoes.get((pib.municipio_id, pib.ano))

            if not populacao or populacao <= 0:
                continue

            valor = (pib.valor * self.PIB_MULTIPLICADOR / populacao).quantize(
                Decimal("0.01")
            )

            registros.append(
                {
                    "ibge_id": pib.municipio.ibge_id,
                    "ano": pib.ano,
                    "valor": valor,
                }
            )

        return registros
