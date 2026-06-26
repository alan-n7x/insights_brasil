from django.db.models import Sum
from ibge.models import FatoIndicador


class KPIEngine:

    @staticmethod
    def get_indicator(indicador_codigo: str, ano: int):
        qs = (
            FatoIndicador.objects
            .filter(indicador__codigo=indicador_codigo, tempo__ano=ano)
            .select_related("indicador")
        )

        total = qs.aggregate(total=Sum("valor"))["total"] or 0

        first = qs.first()

        return {
            "codigo": indicador_codigo,
            "valor": total,
            "unidade": first.indicador.unidade if first else None
        }