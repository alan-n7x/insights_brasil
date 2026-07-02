"""Utilitários diversos para transformação de dados e fatores de escala dos indicadores."""


def get_scale_factor(indicador) -> float:
    """Retorna o fator de escala com base na unidade do indicador.

    Args:
        indicador: Instância de Indicador ou None.

    Returns:
        1000.0 se a unidade for "Mil Reais", 1.0 caso contrário.
    """
    return 1000.0 if (indicador and indicador.unidade == "Mil Reais") else 1.0
