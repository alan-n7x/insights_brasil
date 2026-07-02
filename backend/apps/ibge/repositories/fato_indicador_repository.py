"""Repositório para o modelo FatoIndicador (leitura e escrita)."""

from django.db.models import Sum
from ibge.models import FatoIndicador, Tempo, Municipio, Indicador


class FatoIndicadorRepository:
    """Repositório para consulta e persistência dos fatos (valores) de indicadores por município e tempo."""

    @staticmethod
    def save(municipio, indicador, ano: int, valor: float):
        """Persiste um valor de indicador para um município em um ano específico.

        Cria o registro Tempo se necessário e realiza upsert em FatoIndicador.

        Args:
            municipio: Instância do modelo Municipio.
            indicador: Instância do modelo Indicador.
            ano: Ano de referência do dado.
            valor: Valor numérico do indicador.

        Returns:
            Tupla (objeto, criado) onde criado indica se foi uma inserção nova.
        """
        tempo, _ = Tempo.objects.get_or_create(
            ano=ano, mes=None, trimestre=None
        )
        obj, created = FatoIndicador.objects.update_or_create(
            municipio=municipio,
            indicador=indicador,
            tempo=tempo,
            defaults={"valor": valor}
        )
        return obj, created

    @staticmethod
    def get_value(municipio: Municipio, indicador: Indicador, ano: int):
        """Retorna o valor do indicador para um município e ano específicos.

        Args:
            municipio: Instância de Municipio.
            indicador: Instância de Indicador.
            ano: Ano de referência.

        Returns:
            Valor como float ou None se não encontrado.
        """
        try:
            f = FatoIndicador.objects.get(
                municipio=municipio,
                indicador=indicador,
                tempo__ano=ano,
                tempo__mes__isnull=True,
                tempo__trimestre__isnull=True
            )
            return float(f.valor) if f.valor is not None else None
        except FatoIndicador.DoesNotExist:
            return None

    @staticmethod
    def filter_queryset(indicador: Indicador = None, ano: int = None,
                        estado_sigla: str = None, municipio_codigo: int = None):
        """Retorna QuerySet base filtrado pelos parâmetros informados.

        Args:
            indicador: Instância de Indicador para filtrar.
            ano: Ano para filtrar.
            estado_sigla: Sigla do estado para filtrar.
            municipio_codigo: Código IBGE do município para filtrar.

        Returns:
            QuerySet de FatoIndicador.
        """
        qs = FatoIndicador.objects.select_related(
            'municipio__estado', 'indicador', 'tempo'
        ).filter(
            tempo__mes__isnull=True,
            tempo__trimestre__isnull=True
        )

        if indicador:
            qs = qs.filter(indicador=indicador)
        if ano is not None:
            qs = qs.filter(tempo__ano=ano)
        if estado_sigla:
            qs = qs.filter(municipio__estado__sigla=estado_sigla.upper())
        if municipio_codigo is not None:
            qs = qs.filter(municipio__ibge_id=municipio_codigo)
        return qs

    @staticmethod
    def aggregate_sum(indicador: Indicador = None, ano: int = None,
                      estado_sigla: str = None, municipio_codigo: int = None):
        """Retorna a soma dos valores do indicador aplicando os filtros informados.

        Args:
            indicador: Instância de Indicador.
            ano: Ano de referência.
            estado_sigla: Sigla do estado.
            municipio_codigo: Código IBGE do município.

        Returns:
            Soma dos valores como float.
        """
        qs = FatoIndicadorRepository.filter_queryset(
            indicador=indicador,
            ano=ano,
            estado_sigla=estado_sigla,
            municipio_codigo=municipio_codigo
        )
        result = qs.aggregate(total=Sum('valor'))
        return float(result['total']) if result['total'] is not None else 0.0

    @staticmethod
    def get_time_series(indicador: Indicador = None, estado_sigla: str = None,
                        municipio_codigo: int = None):
        """Retorna série temporal anual do indicador.

        Args:
            indicador: Instância de Indicador.
            estado_sigla: Sigla do estado para filtrar.
            municipio_codigo: Código IBGE do município para filtrar.

        Returns:
            Lista de dicionários com year e value.
        """
        qs = FatoIndicadorRepository.filter_queryset(
            indicador=indicador,
            estado_sigla=estado_sigla,
            municipio_codigo=municipio_codigo
        ).values('tempo__ano').annotate(
            total=Sum('valor')
        ).order_by('tempo__ano')

        return [
            {'year': item['tempo__ano'], 'value': float(item['total']) if item['total'] is not None else 0.0}
            for item in qs
        ]

    @staticmethod
    def get_ranking_by_estado(indicador: Indicador, ano: int):
        """Retorna ranking dos estados por valor total do indicador em um ano.

        Args:
            indicador: Instância de Indicador.
            ano: Ano de referência.

        Returns:
            Lista de dicionários com state e value, ordenada do maior para o menor valor.
        """
        qs = FatoIndicador.objects.filter(
            indicador=indicador,
            tempo__ano=ano,
            tempo__mes__isnull=True,
            tempo__trimestre__isnull=True
        ).values(
            'municipio__estado__sigla'
        ).annotate(
            total=Sum('valor')
        ).order_by('-total')

        return [
            {'state': item['municipio__estado__sigla'].upper(),
             'value': float(item['total']) if item['total'] is not None else 0.0}
            for item in qs
        ]
