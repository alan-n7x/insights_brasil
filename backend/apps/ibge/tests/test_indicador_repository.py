"""Testes para o repositório de indicadores (IndicadorRepository)."""

from django.test import TestCase

from ibge.models import Indicador
from ibge.repositories.indicador_repository import IndicadorRepository


class IndicadorRepositoryTest(TestCase):
    """Testes para os métodos de consulta de indicadores."""

    def setUp(self):
        """Cria um indicador de população para os testes."""
        self.ind = Indicador.objects.create(
            codigo="POPULACAO", nome="População", unidade="Habitantes"
        )

    def test_get_by_codigo_encontra(self):
        """Verifica se a busca por código retorna o indicador existente."""
        result = IndicadorRepository.get_by_codigo("POPULACAO")
        self.assertIsNotNone(result)
        self.assertEqual(result.codigo, "POPULACAO")

    def test_get_by_codigo_nao_encontra(self):
        """Verifica se a busca por código inexistente retorna None."""
        result = IndicadorRepository.get_by_codigo("INEXISTENTE")
        self.assertIsNone(result)

    def test_get_populacao(self):
        """Verifica se o método get_populacao retorna o indicador correto."""
        result = IndicadorRepository.get_populacao()
        self.assertIsNotNone(result)
        self.assertEqual(result.codigo, "POPULACAO")

    def test_get_pib_nao_encontrado(self):
        """Verifica se get_pib retorna None quando o indicador PIB não existe."""
        result = IndicadorRepository.get_pib()
        self.assertIsNone(result)
