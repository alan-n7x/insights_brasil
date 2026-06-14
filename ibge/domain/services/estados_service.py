# ibge/services/estados_service.py

import logging

logger = logging.getLogger(__name__)


class EstadosService:

    def __init__(self, client):

        self.client = client

    def fetch_estados(self):

        logger.info("[EstadosService] Buscando estados no IBGE")

        estados = self.client.get("localidades/estados")

        return self._transform(estados)

    def _transform(self, estados):

        logger.info("[EstadosService] Transformando dados dos estados")

        return [
            {
                "id": e["id"],
                "nome": e["nome"],
                "sigla": e["sigla"],
                "regiao": e["regiao"]["nome"],
            }
            for e in estados
        ]
