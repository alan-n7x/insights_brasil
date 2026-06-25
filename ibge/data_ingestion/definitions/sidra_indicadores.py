from dataclasses import dataclass


@dataclass(frozen=True)
class IndicadorSIDRA:
    agregado: int
    variavel: int
    nome: str
    descricao: str = ""
    unidade: str = ""
    periodicidade: str = ""
    fonte: str = ""


POPULACAO = IndicadorSIDRA(
    agregado=6579,
    variavel=9324,
    nome="POPULACAO",
    descricao="População residente",
    unidade="Habitantes",
    periodicidade="Anual",
    fonte="IBGE"
)

PIB = IndicadorSIDRA(
    agregado=5938,
    variavel=37,
    nome="PIB",
    descricao="Produto Interno Bruto dos municípios",
    unidade="Mil Reais",
    periodicidade="Anual",
    fonte="IBGE SIDRA"
)

PIB_PER_CAPITA = IndicadorSIDRA(
    agregado=5938,
    variavel=543,
    nome="PIB_PER_CAPITA",
    descricao="Produto Interno Bruto per capita",
    unidade="Reais",
    periodicidade="Anual",
    fonte="IBGE SIDRA"
)

# Test indicator for development
TEST_INDICADOR = IndicadorSIDRA(
    agregado=1234,
    variavel=5678,
    nome="TEST_INDICADOR",
    descricao="Indicador de teste",
    unidade="Unidades",
    periodicidade="Mensal",
    fonte="Fonte de teste"
)
