from django.db import models

# Create your models here.
class Estado(models.Model):

    id_ibge = models.IntegerField(unique=True)

    sigla = models.CharField(max_length=2)

    nome = models.CharField(max_length=100)

    def __str__(self):

        return self.nome