import requests

from config import API_BASE_URL, REQUEST_TIMEOUT


class InsightsAPIClient:

    def __init__(self, base_url=API_BASE_URL, timeout=REQUEST_TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout

    def get(self, path, params=None):
        url = f"{self.base_url}{path}"
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def listar_estados(self):
        return self.get("/api/ibge/estados/")

    def listar_municipios(self):
        return self.get("/api/ibge/municipios/")

    def listar_indicadores(self):
        return self.get("/api/ibge/indicadores/")

    def listar_anos(self, indicador):
        return self.get(f"/api/ibge/indicadores/{indicador}/anos/")

    def ranking_estados(self, indicador, ano=None):
        return self.get(
            f"/api/ibge/indicadores/{indicador}/ranking-estados/",
            params={"ano": ano} if ano else None,
        )

    def ranking_municipios(self, indicador, ano=None, estado_id=None, limit=20):
        params = {
            "ano": ano,
            "estado_id": estado_id,
            "limit": limit,
        }
        return self.get(
            f"/api/ibge/indicadores/{indicador}/ranking-municipios/",
            params={key: value for key, value in params.items() if value},
        )

    def evolucao_estado(self, indicador, estado_id=None):
        return self.get(
            f"/api/ibge/indicadores/{indicador}/evolucao/",
            params={"estado_id": estado_id} if estado_id else None,
        )

    def evolucao_municipio(self, indicador, municipio_ibge_id, ano_inicio=None, ano_fim=None):
        params = {
            "ano_inicio": ano_inicio,
            "ano_fim": ano_fim,
        }
        return self.get(
            f"/api/ibge/indicadores/{indicador}/municipios/{municipio_ibge_id}/evolucao/",
            params={key: value for key, value in params.items() if value},
        )
