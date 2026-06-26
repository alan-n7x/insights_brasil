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
    - ``indicadores``: lista de códigos de indicadores (case-insensitive).
      Pode ser uma string separada por vírgula ou uma lista de strings.
    - ``ano``: ano inteiro opcional.
    O método ``validate_indicadores`` normaliza cada código para maiúsculas
    e remove espaços em branco, garantindo compatibilidade com o banco de
    dados que armazena códigos de indicadores em maiúsculas.
    """
    indicadores = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        default=["POPULACAO"]
    )
    ano = serializers.IntegerField(required=False)

    def validate_indicadores(self, value):
        """
        Normaliza cada item para maiúsculas e remove espaços em branco.
        Aceita strings separadas por vírgula dentro da lista.
        Itens vazios são ignorados; se a lista resultante estiver vazia,
        retorna o padrão ["POPULACAO"].
        """
        result = []
        for item in value:
            # Divide por vírgulas para suportar entrada CSV como "populacao,pib_per_capita"
            parts = item.split(',')
            for part in parts:
                part = part.strip()
                if part:
                    result.append(part.upper())
        if not result:
            return ["POPULACAO"]
        return result
