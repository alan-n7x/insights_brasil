"""Modelos de domínio para o esquema estrela (Star Schema) de indicadores: Indicador, Tempo e FatoIndicador."""

from django.db import models
from .territorio import Municipio


class Indicador(models.Model):
    """Catálogo de indicadores socioeconômicos (PIB, POPULACAO, SAUDE, EDUCACAO, etc.).

    Armazena metadados como código, nome, descrição, unidade, periodicidade e fonte.
    """

    codigo = models.CharField(max_length=50, unique=True, db_index=True)
    nome = models.CharField(max_length=150)

    descricao = models.TextField(
        blank=True,
        help_text="Descrição detalhada do indicador"
    )

    unidade = models.CharField(
        max_length=50,
        blank=True,
        help_text="Unidade de medida (ex: habitantes, R$ milhões, índice)"
    )

    periodicidade = models.CharField(
        max_length=30,
        blank=True,
        help_text="Periodicidade dos dados (ex: Anual, Mensal, Trimestral)"
    )

    fonte = models.CharField(
        max_length=100,
        blank=True,
        help_text="Fonte dos dados (ex: IBGE/SIDRA)"
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Indicador"
        verbose_name_plural = "Indicadores"

    def __str__(self):
        return self.nome


class Tempo(models.Model):
    """Dimensão temporal para suportar diferentes granularidades (anual, mensal, trimestral)."""

    ano = models.IntegerField(db_index=True)

    mes = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        help_text="1-12 para dados mensais"
    )

    trimestre = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        help_text="1-4 para dados trimestrais"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["ano", "mes", "trimestre"],
                name="uniq_tempo"
            )
        ]
        ordering = ["-ano", "-mes", "-trimestre"]
        verbose_name = "Tempo"
        verbose_name_plural = "Tempos"

    def __str__(self):
        if self.mes:
            return f"{self.ano}-{self.mes:02d}"
        elif self.trimestre:
            return f"{self.ano}-T{self.trimestre}"
        return str(self.ano)


class FatoIndicador(models.Model):
    """Tabela fato central do esquema estrela, relacionando município, indicador e tempo com um valor."""

    municipio = models.ForeignKey(
        Municipio,
        on_delete=models.CASCADE,
        related_name="fato_indicadores",
        db_index=True,
    )

    indicador = models.ForeignKey(
        Indicador,
        on_delete=models.CASCADE,
        related_name="fato_valores",
        db_index=True,
    )

    tempo = models.ForeignKey(
        Tempo,
        on_delete=models.CASCADE,
        related_name="fato_indicadores",
        db_index=True,
    )

    valor = models.DecimalField(
        max_digits=20,
        decimal_places=4,
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["municipio", "indicador", "tempo"],
                name="uniq_fato_indicador",
            )
        ]

        indexes = [
            models.Index(fields=["indicador", "tempo"]),
            models.Index(fields=["municipio", "indicador"]),
            models.Index(fields=["municipio", "tempo"]),
        ]

        ordering = ["municipio", "indicador", "-tempo"]

        verbose_name = "Fato Indicador"
        verbose_name_plural = "Fatos Indicadores"

    def __str__(self):
        return f"{self.municipio} - {self.indicador} - {self.tempo}"
