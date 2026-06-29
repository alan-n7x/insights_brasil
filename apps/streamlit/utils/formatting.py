"""Funções de formatação de valores monetários e numéricos no padrão brasileiro."""


def _brl_replace(value_str):
    """Troca separadores decimais e de milhar para o padrão brasileiro.

    Args:
        value_str: String no formato 1,000.00.

    Returns:
        String no formato 1.000,00.
    """
    return value_str.replace(",", "X").replace(".", ",").replace("X", ".")


def format_brl(value):
    """Formata um valor numérico como moeda brasileira (R$).

    Valores altos são abreviados com tri (trilhão), bi (bilhão) ou mi (milhão).

    Args:
        value: Número a ser formatado.

    Returns:
        String formatada (ex.: "R$ 1,23 bi") ou "---" se vazio.
    """
    if not value:
        return "---"
    if value >= 1_000_000_000_000:
        return _brl_replace(f"R$ {value / 1_000_000_000_000:,.2f}") + " tri"
    if value >= 1_000_000_000:
        return _brl_replace(f"R$ {value / 1_000_000_000:,.2f}") + " bi"
    if value >= 1_000_000:
        return _brl_replace(f"R$ {value / 1_000_000:,.2f}") + " mi"
    return _brl_replace(f"R$ {value:,.2f}")


def format_int(value):
    """Formata um valor inteiro com abreviação brasileira.

    Args:
        value: Número inteiro a ser formatado.

    Returns:
        String formatada (ex.: "1,23 mi") ou "---" se vazio.
    """
    if not value:
        return "---"
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f} bi".replace(".", ",")
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f} mi".replace(".", ",")
    return f"{int(value):,}".replace(",", ".")
