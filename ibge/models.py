from django.db import models


# Create your models here.
class Estado(models.Model):

    nome = models.CharField(max_length=100)

    sigla = models.CharField(max_length=2, unique=True)

    regiao = models.CharField(max_length=50)

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return self.nome
