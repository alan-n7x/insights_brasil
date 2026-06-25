from rest_framework import serializers
from ibge.models import Indicador, Estado, Municipio, Tempo, FatoIndicador


class IndicadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicador
        fields = ["id", "nome", "codigo", "descricao", "unidade", "fonte"]


class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = ["id", "nome", "sigla", "ibge_id"]


class MunicipioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipio
        fields = ["id", "nome", "ibge_id"]


class TempoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tempo
        fields = [
            "id",
            "ano",
            "mes",
            "trimestre",
        ]


class FatoIndicadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = FatoIndicador
        fields = ["id", "valor", "indicador", "municipio", "tempo"]
