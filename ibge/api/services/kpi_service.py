from django.db.models import Sum
from ibge.models import Indicador, FatoIndicador


class KPIService:
    """
    Camada de serviço para cálculo e retorno de KPIs a partir do modelo FatoIndicador.
    Encapsula as regras de agregação específicas por indicador.
    """

    # Registro de regras de agregação específicas por código de indicador.
    # Se não estiver presente, a regra padrão é 'soma' (soma do valor entre os municípios para o ano dado).
    _AGGREGATION_RULES = {
        # PIB_PER_CAPITA vem pré‑calculado; devemos retornar o valor armazenado
        # sem nenhuma agregação adicional (sem soma, sem recálculo).
        'PIB_PER_CAPITA': 'direto',
    }

    @classmethod
    def _get_aggregation_rule(cls, indicator_codigo: str) -> str:
        """Retorna a regra de agregação para o código do indicador fornecido."""
        return cls._AGGREGATION_RULES.get(indicator_codigo, 'soma')

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

            regra = cls._get_aggregation_rule(codigo)

            if regra == 'soma':
                # Padrão: soma entre municípios (e quaisquer outras dimensões) para o ano
                agregado = qs.aggregate(total=Sum('valor'))['total']
                valor = float(agregado) if agregado is not None else None
            elif regra == 'direto':
                # Para indicadores como PIB_PER_CAPITA: retorna o valor armazenado tal como está.
                # Retorna um mapeamento do nome do município para seu valor.
                # Se um ano específico for solicitado, mapeia município -> valor.
                # Se nenhum filtro de ano, aninhe por ano: município -> {ano: valor}.
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
                # Fallback para soma caso uma regra desconhecida seja encontrada.
                agregado = qs.aggregate(total=Sum('valor'))['total']
                valor = float(agregado) if agregado is not None else None

            resultado[codigo] = {
                'valor': valor,
                'nome': indicador.nome,
                'codigo': codigo,
            }

        return resultado