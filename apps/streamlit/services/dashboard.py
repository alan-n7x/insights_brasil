import logging
from api.client import get_resumo, get_ranking, listar_indicador
from utils.geo import agregar_por_regiao

logger = logging.getLogger(__name__)


def carregar_resumo():
    """Retorna um dicionário com ano, população, PIB e PIB per capita do ano mais recente.

    Returns:
        Dict com as chaves ano, populacao, pib, pib_per_capita.
    """
    data = get_resumo()
    return {
        "ano": data.get("ano", "---"),
        "populacao": int(data.get("populacao", 0)),
        "pib": data.get("pib", 0),
        "pib_per_capita": data.get("pib_per_capita", 0),
    }


def carregar_ranking_estados(limit=10):
    """Carrega o ranking populacional dos estados para exibição em gráfico.

    Args:
        limit: Número de estados no ranking (padrão 10).

    Returns:
        Dict com as listas Estado e Populacao.
    """
    ranking = get_ranking("populacao", limit=limit)
    itens = ranking if isinstance(ranking, list) else []
    if not itens:
        return {"Estado": [], "Populacao": []}
    return {
        "Estado": [r["state"] for r in itens],
        "Populacao": [r["value"] for r in itens],
    }


def carregar_dados_por_regiao():
    """Carrega dados populacionais agregados por região.

    Returns:
        Dict com as listas Regiao e Populacao.
    """
    lista = listar_indicador("populacao")
    itens = lista.get("items", []) if isinstance(lista, dict) else (lista if isinstance(lista, list) else [])
    regioes = agregar_por_regiao(itens)
    total = sum(regioes.values())
    if total < 100_000_000:
        logger.warning("Total populacional suspeito (%.0f): possivelmente o servidor Django está com código antigo (limit default 10)", total)
    return {
        "Regiao": list(regioes.keys()),
        "Populacao": [int(v) for v in regioes.values()],
    }
