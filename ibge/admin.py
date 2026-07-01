from django.contrib import admin

# Register your models here.
from .models.territorio import Estado, Municipio


@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "sigla")
    search_fields = ("nome", "sigla")


@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "ibge_id", "estado")
    search_fields = ("nome",)
