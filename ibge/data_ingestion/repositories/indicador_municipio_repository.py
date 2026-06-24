from ibge.models import FatoIndicador, Tempo


class FatoIndicadorRepository:
    """
    Responsável apenas por persistência no banco.
    Não contém regra de negócio.
    """

    @staticmethod
    def save(municipio, indicador, ano: int, valor: float):
        # Get or create Tempo record for the year
        tempo, _ = Tempo.objects.get_or_create(
            ano=ano,
            mes=None,
            trimestre=None
        )
        
        obj, created = FatoIndicador.objects.update_or_create(
            municipio=municipio,
            indicador=indicador,
            tempo=tempo,
            defaults={
                "valor": valor
            }
        )
        return obj, created