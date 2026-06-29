SIGLA_PARA_REGIAO = {
    "AC": "Norte", "AP": "Norte", "AM": "Norte", "PA": "Norte", "RO": "Norte", "RR": "Norte", "TO": "Norte",
    "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste",
    "PB": "Nordeste", "PE": "Nordeste", "PI": "Nordeste", "RN": "Nordeste", "SE": "Nordeste",
    "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "RS": "Sul", "SC": "Sul",
    "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MS": "Centro-Oeste", "MT": "Centro-Oeste",
}

REGIACOES_ORDEM = ["Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]


def agregar_por_regiao(itens):
    """Agrupa uma lista de dicionários {sigla, valor} por região geográfica.

    Args:
        itens: Lista de dicionários com chaves sigla e valor.

    Returns:
        Dict com região como chave e total populacional como valor.
    """
    regioes = {r: 0 for r in REGIACOES_ORDEM}
    for m in itens:
        sigla = m.get("sigla", "")
        regiao = SIGLA_PARA_REGIAO.get(sigla.upper())
        if regiao:
            regioes[regiao] += m.get("valor", 0)
    return regioes
