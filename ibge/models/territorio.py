from django.db import models


# =========================
# DIMENSÃO: TEMPO
# =========================
class Tempo(models.Model):
    """
    Dimensão temporal para suportar diferentes granularidades.
    Permite dados anuais, mensais, trimestrais, semestrais.
    """

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


# Create your models here.
class Estado(models.Model):

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