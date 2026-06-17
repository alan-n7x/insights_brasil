from django.db import models
from .territorio import Municipio


# =========================
# DIMENSÃO: INDICADOR
# =========================
class Indicador(models.Model):
    """
    Catálogo de indicadores (PIB, POPULACAO, SAUDE, EDUCACAO...)
    """

    codigo = models.CharField(max_length=50, unique=True, db_index=True)
    nome = models.CharField(max_length=150)

    def __str__(self):
        return self.nome


# =========================
# FATO: INDICADORES POR MUNICÍPIO
# =========================
class IndicadorMunicipio(models.Model):
    """
    Tabela central do BI.
    Tudo vira aqui.
    """

    municipio = models.ForeignKey(
        Municipio,
        on_delete=models.CASCADE,
        related_name="indicadores",
    )

    indicador = models.ForeignKey(
        Indicador,
        on_delete=models.CASCADE,
        related_name="valores",
    )

    ano = models.IntegerField(db_index=True)

    valor = models.DecimalField(
        max_digits=20,
        decimal_places=2,
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["municipio", "indicador", "ano"],
                name="uniq_indicador_municipio_ano",
            )
        ]

        indexes = [
            models.Index(fields=["indicador", "ano"]),
            models.Index(fields=["municipio", "indicador"]),
        ]

        ordering = ["municipio", "indicador", "-ano"]

    def __str__(self):
        return f"{self.municipio} - {self.indicador} - {self.ano}"
