from decimal import Decimal


class PIBTransformer:

    def transform(self, serie):

        municipio_ibge_id = int(serie["localidade"]["id"])

        registros = []

        for ano, valor in serie["serie"].items():

            if valor in (None, "-", "..."):
                continue

            registros.append(
                {
                    "ibge_id": municipio_ibge_id,  # <- CORRIGIDO
                    "ano": int(ano),
                    "valor": Decimal(valor),
                }
            )

        return registros
