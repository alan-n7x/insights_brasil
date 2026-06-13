from django.db import models


# Create your models here.
class Estado(models.Model):
    codigo_externo = models.IntegerField(unique=True)

    nome = models.CharField(max_length=100)

    sigla = models.CharField(max_length=2, unique=True)

    regiao = models.CharField(max_length=50)

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return self.nome


class Municipio(models.Model):

    codigo_externo = models.IntegerField(unique=True)

    nome = models.CharField(max_length=150)

    estado = models.ForeignKey(
        Estado, on_delete=models.CASCADE, related_name="municipios"
    )

    criado_em = models.DateTimeField(auto_now_add=True)
