from ibge.models.territorio import PIBMunicipio


class PIBRepository:

    model = PIBMunicipio

    def save(
        self,
        municipio,
        dados,
    ):

        return self.model.objects.update_or_create(
            municipio=municipio,
            ano=dados["ano"],
            defaults={
                "valor": dados["valor"],
            },
        )

    def bulk_create(
        self,
        objetos,
        batch_size=1000,
    ):

        return self.model.objects.bulk_create(
            objetos,
            batch_size=batch_size,
            ignore_conflicts=True,
        )
