"""Serializers da API REST para formatação e validação dos dados de saída."""

from rest_framework import serializers


class SummarySerializer(serializers.Serializer):
    """Serializer para o sumário com ano, população, PIB e PIB per capita."""
    ano = serializers.IntegerField()
    populacao = serializers.IntegerField()
    pib = serializers.IntegerField()
    pib_per_capita = serializers.FloatField()


class MunicipalityItemSerializer(serializers.Serializer):
    """Serializer para item de município na listagem de indicadores."""
    codigo = serializers.IntegerField()
    nome = serializers.CharField()
    sigla = serializers.CharField()
    valor = serializers.FloatField()


class MunicipalityListSerializer(serializers.Serializer):
    """Serializer para lista de municípios com valores de indicador."""
    items = MunicipalityItemSerializer(many=True)


class RankingItemSerializer(serializers.Serializer):
    """Serializer para item de ranking por estado."""
    position = serializers.IntegerField()
    state = serializers.CharField()
    value = serializers.FloatField()

    class Meta:
        fields = ["position", "state", "value"]


class SeriesItemSerializer(serializers.Serializer):
    """Serializer para item de série temporal anual."""
    ano = serializers.IntegerField()
    value = serializers.FloatField()


class StateSerializer(serializers.Serializer):
    """Serializer para dados do estado (sigla, nome, região)."""
    sigla = serializers.CharField()
    nome = serializers.CharField()
    regiao = serializers.CharField(allow_null=True, required=False)


class MunicipalityDetailSerializer(serializers.Serializer):
    """Serializer para detalhamento de um município com dados regionais."""
    codigo = serializers.IntegerField()
    nome = serializers.CharField()
    estado = StateSerializer()
    microrregiao_id = serializers.IntegerField(allow_null=True, required=False)
    microrregiao_nome = serializers.CharField(allow_null=True, required=False)
    mesorregiao_id = serializers.IntegerField(allow_null=True, required=False)
    mesorregiao_nome = serializers.CharField(allow_null=True, required=False)
    regiao_imediata_id = serializers.IntegerField(allow_null=True, required=False)
    regiao_intermediaria_id = serializers.IntegerField(allow_null=True, required=False)


class RegiaoItemSerializer(serializers.Serializer):
    """Item de população agregada por região."""
    regiao = serializers.CharField()
    valor = serializers.FloatField()


class RankingEstadoSerializer(serializers.Serializer):
    """Item do ranking de estados por valor do indicador."""
    posicao = serializers.IntegerField()
    estado = serializers.CharField()
    valor = serializers.FloatField()


class DashboardResumoSerializer(serializers.Serializer):
    """Resumo completo para o dashboard com todos os dados agregados."""
    ano = serializers.IntegerField()
    populacao_total = serializers.IntegerField()
    pib_total = serializers.FloatField()
    pib_per_capita_medio = serializers.FloatField()
    populacao_por_regiao = RegiaoItemSerializer(many=True)
    ranking_estados = RankingEstadoSerializer(many=True)


class ParameterSerializer(serializers.Serializer):
    """Serializer para validação dos parâmetros de consulta da API."""
    ano = serializers.IntegerField(required=False)
    estado = serializers.CharField(required=False, max_length=2)
    municipio = serializers.IntegerField(required=False)
    nome = serializers.CharField(required=False, max_length=100)
    limit = serializers.IntegerField(required=False, min_value=1)
    order_by = serializers.ChoiceField(
        required=False, choices=["valor", "asc"], allow_blank=True,
    )
