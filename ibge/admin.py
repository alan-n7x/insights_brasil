from django.contrib import admin

# Register your models here.
from .models import Estado, Municipio, PopulacaoMunicipio


@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "sigla")
    search_fields = ("nome", "sigla")


@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "ibge_id", "estado")
    search_fields = ("nome",)


@admin.register(PopulacaoMunicipio)
class PopulacaoMunicipioAdmin(admin.ModelAdmin):
    list_display = ("municipio", "ano", "populacao")
    list_filter = ("ano", "municipio__estado")
