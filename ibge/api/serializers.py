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


class KpiQuerySerializer(serializers.Serializer):
    """
    Serializer for validating query-string parameters of the KPI endpoint.
    - ``indicators``: list of indicator codes (case-insensitive).
    - ``ano``: optional integer year.
    The ``validate_indicators`` method normalizes each code to upper‑case
    and strips surrounding whitespace, ensuring compatibility with the
    database which stores indicator codes in uppercase.
    """
    indicators = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=["POPULACAO"]
    )
    ano = serializers.IntegerField(required=False)

    def validate_indicators(self, value):
        """
        Normalize each item to upper‑case and strip whitespace.
        Empty items are ignored; if the resulting list is empty,
        fall back to the default ["POPULACAO"].
        """
        # Normalize to uppercase and strip whitespace, strip
        cleaned = [item.strip().upper() for item in value if item.strip()]
        if not cleaned:
            return ["POPULACAO"]
        return cleaned
