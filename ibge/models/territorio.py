"""Modelos de domínio representando divisões territoriais brasileiras: Estados e Municípios."""

from django.db import models


class Estado(models.Model):
    """Representa um estado brasileiro com código IBGE, nome, sigla e região."""

    ibge_id = models.IntegerField(unique=True, db_index=True)

    nome = models.CharField(max_length=100, db_index=True)

    sigla = models.CharField(max_length=2, unique=True)

    regiao = models.CharField(max_length=50, db_index=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:

        ordering = ["nome"]

        verbose_name = "Estado"

        verbose_name_plural = "Estados"

    def __str__(self):

        return f"{self.nome} ({self.sigla})"


class Municipio(models.Model):
    """Representa um município brasileiro com código IBGE, nome e vínculo ao estado."""

    ibge_id = models.IntegerField(unique=True, db_index=True)
    nome = models.CharField(max_length=150, db_index=True)

    estado = models.ForeignKey(
        "Estado",
        on_delete=models.PROTECT,
        related_name="municipios",
        db_index=True,
    )

    # ===== MICRORREGIÃO =====
    microrregiao_id = models.IntegerField(null=True, blank=True, db_index=True)
    microrregiao_nome = models.CharField(max_length=150, null=True, blank=True)

    # ===== MESORREGIÃO =====
    mesorregiao_id = models.IntegerField(null=True, blank=True, db_index=True)
    mesorregiao_nome = models.CharField(max_length=150, null=True, blank=True)

    # ===== REGIÃO IMEDIATA =====
    regiao_imediata_id = models.IntegerField(null=True, blank=True, db_index=True)
    regiao_imediata_nome = models.CharField(max_length=150, null=True, blank=True)

    # ===== REGIÃO INTERMEDIÁRIA =====
    regiao_intermediaria_id = models.IntegerField(null=True, blank=True, db_index=True)
    regiao_intermediaria_nome = models.CharField(max_length=150, null=True, blank=True)

    # ===== REGIÃO (macro) =====
    regiao = models.CharField(max_length=50, null=True, blank=True, db_index=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Município"
        verbose_name_plural = "Municípios"

    def __str__(self):
        return f"{self.nome} - {self.estado.sigla}"
