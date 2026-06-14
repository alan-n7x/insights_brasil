import logging

logger = logging.getLogger(__name__)


class MunicipiosService:

    def __init__(self, client):

        self.client = client

    def fetch_municipios(self):

        logger.info("[MunicipiosService] Buscando municípios no IBGE")

        municipios = self.client.get("localidades/municipios")

        return self._transform(municipios)

    def _transform(self, municipios):

        logger.info("[MunicipiosService] Transformando municípios")

        result = []

        for m in municipios:

            microrregiao = m.get("microrregiao")

            if not microrregiao:
                continue

            result.append(
                {
                    "codigo_externo": m["id"],
                    "nome": m["nome"],
                    "estado_id": m["microrregiao"]["mesorregiao"]["UF"]["id"],
                }
            )

        return result
