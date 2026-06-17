from ibge.models import IndicadorMunicipio


class IndicadorMunicipioRepository:
    """
    Responsável apenas por persistência no banco.
    Não contém regra de negócio.
    """

    @staticmethod
    def save(municipio, indicador, ano: int, valor: float):
        obj, created = IndicadorMunicipio.objects.update_or_create(
            municipio=municipio,
            indicador=indicador,
            ano=ano,
            defaults={
                "valor": valor
            }
        )
        return obj, created