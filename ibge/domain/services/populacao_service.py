import logging
from datetime import date

logger = logging.getLogger(__name__)


class PopulacaoService:

    def __init__(self, client):

        self.client = client

    def fetch_populacao(self):

        ano_fim = date.today().year
        ano_inicio = ano_fim - 10

        logger.info("[PopulacaoService] Buscando dados IBGE")

        data = self.client.get_populacao(ano_inicio, ano_fim)

        return self._transform(data)

    def _transform(self, data):

        series = data[0]["resultados"][0]["series"]

        result = []

        for item in series:

            codigo = item["localidade"]["id"]

            for ano, pop in item["serie"].items():

                # 🧠 proteção contra valores inválidos do IBGE
                if pop in ("...", "..", "-", None, ""):
                    continue

                try:
                    populacao = int(pop)
                except (ValueError, TypeError):
                    continue

                result.append(
                    {
                        "municipio_id": str(codigo),
                        "ano": int(ano),
                        "populacao": populacao,
                    }
                )

        return result
