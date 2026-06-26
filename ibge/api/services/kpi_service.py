from django.db.models import Sum, Avg, Max, Min, Count
from ibge.models import Indicador, FatoIndicador


class KPIService:
    """
    Camada de serviço para cálculo e retorno de KPIs a partir do modelo FatoIndicador.
    Encapsula as regras de agregação específicas por indicador, distinguindo
    entre indicadores **RAW** (dados já prontos, sem agregação) e
    **AGGREGATED** (requerem funções de agregação como Sum, Avg, etc.).
    """

    # ----------------------------------------------------------------------
    # REGISTRO DE REGRAS POR INDICADOR
    # ----------------------------------------------------------------------
    # Cada indicador pode ter:
    #   - type: "raw" ou "aggregated"
    #   - aggregation (opcional, apenas para type=="aggregated"):
    #         "sum", "avg", "max", "min", "count"
    # Se type == "aggregated" e aggregation não for especificado,
    # o padrão será "sum".
    # Se type == "raw", aggregation é ignorado.
    # ----------------------------------------------------------------------
    KPI_RULES = {
        # PIB_PER_CAPITA já vem pronto do IBGE; não deve ser somado.
        "PIB_PER_CAPITA": {
            "type": "raw"
        },
        # POPULACAO precisa ser somada entre municípios (pode ser agregada
        # por estado, região, etc. conforme a necessidade do consumidor).
        "POPULACAO": {
            "type": "aggregated",
            "aggregation": "sum"
        },
        # PIB agregado por Estado, ordenado do maior para o menor (ranking).
        "PIB": {
            "type": "aggregated",
            "aggregation": "sum",
            "group_by": "municipio__estado__nome",
            "order_by": "-total"
        },
        # Exemplo de indicador que poderia ser média (caso exista no futuro):
        # "IDH_MEDIO": {
        #     "type": "aggregated",
        #     "aggregation": "avg"
        # },
    }

    # Mapeamento de strings para funções de agregação do Django ORM.
    _AGGREGATION_FUNCS = {
        "sum": Sum,
        "avg": Avg,
        "max": Max,
        "min": Min,
        "count": Count,
    }

    @classmethod
    def _get_rule(cls, indicator_codigo: str) -> dict:
        """
        Retorna a regra de KPI para o código informado.
        Se o indicador não estiver cadastrado, assume type="aggregated"
        com aggregation="sum" (compatibilidade com comportamento antigo).
        """
        rule = cls.KPI_RULES.get(indicator_codigo)
        if rule is None:
            # Fallback para manter compatibilidade com código existente.
            return {"type": "aggregated", "aggregation": "sum"}
        return rule

    @classmethod
    def _apply_aggregation(cls, qs, agg_func):
        """
        Aplica a função de agregação ao queryset e retorna o valor escalar.
        """
        aggregated = qs.aggregate(total=agg_func('valor'))['total']
        return float(aggregated) if aggregated is not None else None

    @classmethod
    def _apply_grouped_aggregation(cls, qs, agg_func, group_by, order_by=None):
        """
        Aplica agregação agrupada ao queryset.
        Retorna uma lista de dicionários contendo o grupo e o total agregado.
        Se order_by for fornecido, aplica a ordenação.
        """
        # Agrupa pelo campo indicado e calcula a agregação
        queryset = qs.values(group_by).annotate(total=agg_func('valor'))
        if order_by:
            queryset = queryset.order_by(order_by)
        # Converte para lista de dict com valores float
        result = []
        for item in queryset:
            result.append({
                group_by.split('__')[-1]: item[group_by],
                'total': float(item['total']) if item['total'] is not None else None
            })
        return result

    @classmethod
    def get_indicators(cls, codigos: list[str], ano: int | None = None) -> dict:
        """
        Calcula e retorna os valores dos KPIs para os códigos de indicador e ano fornecidos.

        Parâmetros
        ----------
        codigos: lista de códigos de indicadores (ex: ['POPULACAO', 'PIB']).
        ano: ano opcional para filtrar os dados. Se None, considera todos os anos.

        Retorna
        -------
        dicionário que mapeia o código do indicador para um dicionário contendo pelo menos:
            - 'valor': valor calculado (float, dict, ou None se não houver dados)
            - 'nome': nome do indicador
            - 'codigo': código do indicador
        """
        resultado = {}

        for codigo in codigos:
            # Busca metadados do indicador (nome, etc.)
            try:
                indicador = Indicador.objects.get(codigo=codigo)
            except Indicador.DoesNotExist:
                # Se o indicador não for encontrado, retorna um placeholder vazio.
                resultado[codigo] = {
                    'valor': None,
                    'nome': '',
                    'codigo': codigo,
                }
                continue

            # Conjunto base filtrado pelo indicador e opcionalmente pelo ano
            qs = FatoIndicador.objects.filter(indicador__codigo=codigo)
            if ano is not None:
                qs = qs.filter(tempo__ano=ano)

            rule = cls._get_rule(codigo)
            kpi_type = rule.get("type")
            aggregation_name = rule.get("aggregation")

            if kpi_type == "aggregated":
                agg_func_cls = cls._AGGREGATION_FUNCS.get(aggregation_name or "sum", Sum)
                group_by = rule.get("group_by")
                order_by = rule.get("order_by")
                if group_by:
                    valor = cls._apply_grouped_aggregation(qs, agg_func_cls, group_by, order_by)
                else:
                    valor = cls._apply_aggregation(qs, agg_func_cls)
            elif kpi_type == "raw":
                # RAW: retorna os valores brutos, sem agregação.
                # Mantemos o mesmo comportamento anterior para PIB_PER_CAPITA:
                #   - Se ano informado: dict {municipio: valor}
                #   - Se ano não informado: dict aninhado {municipio: {ano: valor}}
                if ano is not None:
                    # Ano único: dicionário simples município -> valor
                    valor = {}
                    for linha in qs.order_by('municipio__nome'):
                        nome_mun = linha.municipio.nome  # type: ignore[attr-defined]
                        valor[nome_mun] = float(linha.valor)
                else:
                    # Sem filtro de ano: dicionário aninhado municipio -> {ano: valor}
                    valor = {}
                    for linha in qs.order_by('municipio__nome', 'tempo__ano'):
                        nome_mun = linha.municipio.nome  # type: ignore[attr-defined]
                        ano_registro = linha.tempo.ano  # type: ignore[attr-defined]
                        if nome_mun not in valor:
                            valor[nome_mun] = {}
                        valor[nome_mun][ano_registro] = float(linha.valor)
                # Se não houver dados, valor permanece como dicionário vazio
            else:
                # Tipo desconhecido: fallback para soma (não deve acontecer com regras válidas).
                valor = cls._apply_aggregation(qs, Sum)

            resultado[codigo] = {
                'valor': valor,
                'nome': indicador.nome,
                'codigo': codigo,
            }

        return resultado