"""Cliente HTTP para consumir a API REST do Insight Brasil.

Fornece funções tipadas para acessar endpoints de estados,
municípios, indicadores, rankings e séries temporais.
"""
import logging
import requests

logger = logging.getLogger(__name__)

BASE_URL = "http://127.0.0.1:8000/ibge/api/v1"


def api_get(endpoint, params=None):
    """Executa uma requisição GET genérica à API.

    Args:
        endpoint: Caminho do endpoint ou URL completa.
        params: Parâmetros de consulta opcionais.

    Returns:
        Dados da resposta em JSON.

    Raises:
        ConnectionError: Se a API estiver indisponível.
        Timeout: Se a requisição exceder o tempo limite.
        HTTPError: Se a API retornar erro HTTP.
    """
    url = f"{BASE_URL}/{endpoint}/" if not endpoint.startswith("http") else endpoint
    logger.debug("GET %s params=%s", url, params)
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        logger.debug("Response %s: %s ...", url, str(data)[:200])
        return data
    except requests.exceptions.ConnectionError:
        logger.error("API indisponível em %s", url)
        raise
    except requests.exceptions.Timeout:
        logger.error("Timeout ao acessar %s", url)
        raise
    except requests.exceptions.HTTPError as e:
        logger.error("HTTP %s em %s: %s", e.response.status_code, url, e.response.text[:200])
        raise
    except Exception as e:
        logger.exception("Erro inesperado ao acessar %s: %s", url, e)
        raise


def get_estados():
    """Retorna a lista de todos os estados brasileiros."""
    return api_get("estados")


def get_estado(sigla):
    """Retorna os dados de um estado específico pela sigla.

    Args:
        sigla: Sigla do estado (ex.: "SP", "RJ").
    """
    return api_get(f"estados/{sigla}")


def get_municipio(codigo):
    """Retorna os dados de um município pelo código IBGE.

    Args:
        codigo: Código IBGE do município.
    """
    return api_get(f"municipios/{codigo}")


def get_resumo(ano=None, estado=None, municipio=None):
    """Obtém o resumo de indicadores (população, PIB, PIB per capita).

    Args:
        ano: Ano de referência (opcional).
        estado: Sigla do estado (opcional).
        municipio: Código do município (opcional).
    """
    params = {}
    if ano is not None:
        params["ano"] = ano
    if estado:
        params["estado"] = estado
    if municipio:
        params["municipio"] = municipio
    return api_get("painel/resumo", params=params)


def listar_indicador(indicador, ano=None, estado=None, municipio=None, limit=None):
    """Lista valores de um indicador com filtros opcionais.

    Args:
        indicador: Nome do indicador (ex.: "populacao").
        ano: Ano de referência (opcional).
        estado: Sigla do estado (opcional).
        municipio: Código do município (opcional).
        limit: Limite de registros (opcional).
    """
    params = {}
    if ano is not None:
        params["ano"] = ano
    if estado:
        params["estado"] = estado
    if municipio:
        params["municipio"] = municipio
    if limit is not None:
        params["limit"] = limit
    return api_get(indicador, params=params)


def get_ranking(indicador, ano=None, limit=10):
    """Obtém o ranking de um indicador entre os estados.

    Args:
        indicador: Nome do indicador (ex.: "populacao").
        ano: Ano de referência (opcional).
        limit: Número de posições no ranking (padrão 10).
    """
    params = {"limit": limit}
    if ano is not None:
        params["ano"] = ano
    return api_get(f"{indicador}/ranking", params=params)


def get_dashboard_resumo(ano=None):
    """Obtém todos os dados prontos para o dashboard em uma única chamada.

    Args:
        ano: Ano de referência (opcional).

    Returns:
        Dicionário com ano, populacao_total, pib_total, pib_per_capita_medio,
        populacao_por_regiao e ranking_estados.
    """
    params = {}
    if ano is not None:
        params["ano"] = ano
    return api_get("dashboard/resumo", params=params)


def get_serie(indicador, estado=None, municipio=None):
    """Obtém a série temporal de um indicador.

    Args:
        indicador: Nome do indicador (ex.: "populacao").
        estado: Sigla do estado (opcional).
        municipio: Código do município (opcional).
    """
    params = {}
    if estado:
        params["estado"] = estado
    if municipio:
        params["municipio"] = municipio
    return api_get(f"{indicador}/serie", params=params)