import logging

logger = logging.getLogger(__name__)





class PopulationTransformer:

    def transform(self, data):
        
        series = data[0]["resultados"][0]["series"]

        result = []

        for item in series:

            codigo = item["localidade"]["id"]

            for ano, pop in item["serie"].items():

                if pop in ("...", "..", "-", None, ""):
                    continue

                try:

                    populacao = int(pop)

                except (ValueError, TypeError):

                    continue

                result.append(
                    {
                        "ibge_id": int(codigo),
                        "ano": int(ano),
                        "valor": populacao,
                    }
                )

        return result
