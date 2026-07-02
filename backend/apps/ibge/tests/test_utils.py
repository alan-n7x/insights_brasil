"""Testes para as funções utilitárias do módulo IBGE."""

from django.test import SimpleTestCase
from ibge.utils import get_scale_factor


class FakeIndicador:
    """Classe fictícia para simular um Indicador nos testes."""

    def __init__(self, unidade):
        self.unidade = unidade


class GetScaleFactorTest(SimpleTestCase):
    """Testes para a função get_scale_factor."""

    def test_mil_reais_retorna_1000(self):
        """Verifica se unidade 'Mil Reais' retorna fator 1000."""
        ind = FakeIndicador("Mil Reais")
        self.assertEqual(get_scale_factor(ind), 1000.0)

    def test_habitantes_retorna_1(self):
        """Verifica se unidade 'Habitantes' retorna fator 1."""
        ind = FakeIndicador("Habitantes")
        self.assertEqual(get_scale_factor(ind), 1.0)

    def test_reais_retorna_1(self):
        """Verifica se unidade 'Reais' retorna fator 1."""
        ind = FakeIndicador("Reais")
        self.assertEqual(get_scale_factor(ind), 1.0)

    def test_none_retorna_1(self):
        """Verifica se None retorna fator 1."""
        self.assertEqual(get_scale_factor(None), 1.0)
