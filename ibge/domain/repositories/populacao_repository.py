from django.db.models import Max
from ibge.models import PopulacaoMunicipio


class PopulacaoRepository:

    def save(self, municipio, ano, populacao):

        obj, created = PopulacaoMunicipio.objects.get_or_create(
            municipio=municipio,
            ano=ano,
            defaults={"populacao": populacao},
        )

        if not created and obj.populacao != populacao:
            obj.populacao = populacao
            obj.save(update_fields=["populacao"])
            return "updated"

        if created:
            return "created"

        return "ignored"
