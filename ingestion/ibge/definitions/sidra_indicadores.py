from dataclasses import dataclass


@dataclass(frozen=True)
class IndicadorSIDRA:
    agregado: int
    variavel: int
    nome: str


POPULACAO = IndicadorSIDRA(agregado=6579, variavel=9324, nome="População")

PIB = IndicadorSIDRA(agregado=5938, variavel=37, nome="PIB")
