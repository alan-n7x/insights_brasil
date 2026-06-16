import logging

logger = logging.getLogger(__name__)


class MunicipioTransformer:

    def transform(self, m):

        logger.debug("[MunicipioTransformer] %s", m.get("nome"))

        microrregiao = m.get("microrregiao") or {}
        mesorregiao = microrregiao.get("mesorregiao") or {}
        uf = mesorregiao.get("UF") or {}

        regiao_imediata = m.get("regiao-imediata") or {}
        regiao_intermediaria = regiao_imediata.get("regiao-intermediaria") or {}
        regiao = uf.get("regiao") or {}

        return {
            # obrigatórios
            "ibge_id": m.get("id"),
            "nome": m.get("nome"),
            "estado_id": uf.get("id"),

            # opcionais (NUNCA quebram o pipeline)
            "microrregiao_id": microrregiao.get("id"),
            "microrregiao_nome": microrregiao.get("nome"),

            "mesorregiao_id": mesorregiao.get("id"),
            "mesorregiao_nome": mesorregiao.get("nome"),

            "regiao_imediata_id": regiao_imediata.get("id"),
            "regiao_imediata_nome": regiao_imediata.get("nome"),

            "regiao_intermediaria_id": regiao_intermediaria.get("id"),
            "regiao_intermediaria_nome": regiao_intermediaria.get("nome"),

            "regiao": regiao.get("nome"),
        }