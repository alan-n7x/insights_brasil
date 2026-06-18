from ibge.models import IndicadorMunicipio

import logging

logger = logging.getLogger(__name__)


class PIBPerCapitaService:
    """
    Retorna PIB per capita já calculado pelo IBGE (sem recomputar nada).
    """

    PIB_PER_CAPITA_CODIGO = "PIB_PER_CAPITA"

    def fetch(self, ano_inicio, ano_fim=None, estado_id=None):
        ano_fim = ano_fim or ano_inicio

        qs = IndicadorMunicipio.objects.filter(
            indicador__codigo=self.PIB_PER_CAPITA_CODIGO,
            ano__gte=ano_inicio,
            ano__lte=ano_fim,
        ).select_related("municipio")

        if estado_id:
            qs = qs.filter(municipio__estado_id=estado_id)
        
        return [
            {
                "ibge_id": item.municipio.ibge_id,
                "nome": item.municipio.nome,
                "ano": item.ano,
                "valor": float(item.valor),  # já pronto para gráfico
            }
            for item in qs.order_by("ano", "-valor")
        ]
