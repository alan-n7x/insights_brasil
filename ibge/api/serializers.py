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

    indicador_id = serializers.IntegerField(source="indicador.id", read_only=True)
    indicador = serializers.CharField(source="indicador.nome", read_only=True)

    municipio_id = serializers.IntegerField(source="municipio.id", read_only=True)
    municipio = serializers.CharField(source="municipio.nome", read_only=True)

    ano = serializers.IntegerField(source="tempo.ano", read_only=True)

    class Meta:
        model = FatoIndicador
        fields = [
            "id",
            "valor",
            "indicador_id",
            "indicador",
            "municipio_id",
            "municipio",
            "ano",
        ]


class FatoIndicadorDetailSerializer(serializers.ModelSerializer):

    indicador = IndicadorSerializer(read_only=True)
    municipio = MunicipioSerializer(read_only=True)
    tempo = TempoSerializer(read_only=True)

    class Meta:
        model = FatoIndicador
        fields = [
            "id",
            "valor",
            "indicador",
            "municipio",
            "tempo",
        ]
