"""
Mecanismo de Consulta (Query Engine) para análises analíticas.
Utiliza repositórios para buscar dados e aplica a lógica de negócios.
"""

from typing import List, Dict
from django.db.models import Count, DecimalField, Max, Min, OuterRef, Subquery, Sum, Value
from django.db.models.functions import Coalesce
from ibge.utils import get_scale_factor
from ibge.repositories.indicador_repository import IndicadorRepository
from ibge.repositories.municipio_repository import MunicipioRepository
from ibge.repositories.fato_indicador_repository import FatoIndicadorRepository
from ibge.models import FatoIndicador, Indicador, Municipio


class DashboardQuery:
    """Agrupa consultas analíticas do dashboard, provendo sumários, rankings e séries temporais."""

    @staticmethod
    def _get_latest_year() -> int:
        """Retorna o ano mais recente com dados disponíveis na tabela de fatos."""
        from ibge.models import Tempo

        latest = (
            Tempo.objects.filter(fato_indicadores__isnull=False)
            .order_by("-ano")
            .first()
        )
        return latest.ano if latest else 2023

    @staticmethod
    def _get_indicator(indicator_code: str):
        """Retorna um indicador pelo código, sem exigir métodos específicos no repositório."""
        return IndicadorRepository.get_by_codigo(indicator_code.upper())

    @staticmethod
    def _get_value_for_indicator(
        indicator_name: str, municipio=None, ano: int = None, estado: str = None
    ) -> float:
        """Retorna o valor do indicador para um município, estado ou total nacional.

        Args:
            indicator_name: Nome do indicador.
            municipio: Código IBGE ou instância de Municipio (opcional).
            ano: Ano de referência (opcional).
            estado: Sigla do estado (opcional).

        Returns:
            Valor numérico do indicador.
        """
        ano = ano or DashboardQuery._get_latest_year()
        ind = DashboardQuery._get_indicator(indicator_name)
        if not ind:
            return 0.0
        fator_escala = get_scale_factor(ind)
        if municipio:
            if not isinstance(municipio, Municipio):
                mun = MunicipioRepository.get_by_codigo(municipio)
                if not mun:
                    return 0.0
                municipio = mun
            return (FatoIndicadorRepository.get_value(municipio, ind, ano) or 0.0) * fator_escala
        else:
            return FatoIndicadorRepository.aggregate_sum(
                indicador=ind, ano=ano, estado_sigla=estado
            ) * fator_escala

    @staticmethod
    def _get_indicator_list(
        indicator_name: str, ano: int = None, estado: str = None,
        nome: str = None, limit: int = None, order_by: str = None,
    ) -> List[Dict]:
        """Retorna lista de municípios com os valores do indicador, com filtros e ordenação.

        Args:
            indicator_name: Nome do indicador.
            ano: Ano de referência.
            estado: Sigla do estado para filtrar.
            limit: Limite máximo de resultados.
            order_by: Campo para ordenação ("valor").

        Returns:
            Lista de dicionários com codigo, nome, sigla e valor.
        """
        ano = ano or DashboardQuery._get_latest_year()
        ind = DashboardQuery._get_indicator(indicator_name)
        if not ind:
            return []

        fator_escala = get_scale_factor(ind)

        valor_do_indicador = FatoIndicador.objects.filter(
            municipio_id=OuterRef("pk"),
            indicador=ind,
            tempo__ano=ano,
            tempo__mes__isnull=True,
            tempo__trimestre__isnull=True,
        ).values("valor")[:1]

        qs = MunicipioRepository.all().annotate(
            valor_indicador=Coalesce(
                Subquery(valor_do_indicador, output_field=DecimalField()),
                Value(0, output_field=DecimalField()),
            )
        )
        if estado:
            qs = qs.filter(estado__sigla=estado.upper())
        if nome:
            qs = qs.filter(nome__icontains=nome)
        qs = qs.select_related("estado")
        if order_by == "valor":
            qs = qs.order_by("-valor_indicador", "nome")
        elif order_by == "asc":
            qs = qs.order_by("valor_indicador", "nome")

        if limit is not None:
            qs = qs[:limit]

        return [
            {
                "codigo": mun.ibge_id,
                "nome": mun.nome,
                "sigla": mun.estado.sigla,
                "valor": float(mun.valor_indicador) * fator_escala,
            }
            for mun in qs
        ]

    @staticmethod
    def summary(ano: int = None, estado: str = None, municipio: int = None) -> dict:
        """Retorna um sumário com população, PIB e PIB per capita.

        Args:
            ano: Ano de referência.
            estado: Sigla do estado.
            municipio: Código IBGE do município.

        Returns:
            Dicionário com ano, populacao, pib e pib_per_capita.
        """
        ano = ano or DashboardQuery._get_latest_year()

        pop = DashboardQuery._get_value_for_indicator(
            "populacao", municipio=municipio, ano=ano, estado=estado
        )
        pib = DashboardQuery._get_value_for_indicator(
            "pib", municipio=municipio, ano=ano, estado=estado
        )

        pib_per_capita = (pib / pop) if pop > 0 else 0.0

        return {
            "ano": ano,
            "populacao": pop,
            "pib": pib,
            "pib_per_capita": pib_per_capita,
        }

    @staticmethod
    def get_ranking_by_estado(indicador, ano: int = None, limit: int = None) -> List[Dict]:
        """Retorna ranking dos estados por valor agregado do indicador.

        Args:
            indicador: Instância de Indicador.
            ano: Ano de referência.
            limit: Limite de resultados.

        Returns:
            Lista de dicionários com posicao, estado e valor.
        """
        if ano is None:
            ano = DashboardQuery._get_latest_year()
        fator_escala = get_scale_factor(indicador)

        qs = (
            FatoIndicador.objects.filter(
                indicador=indicador,
                tempo__ano=ano,
                tempo__mes__isnull=True,
                tempo__trimestre__isnull=True,
            )
            .values("municipio__estado__sigla")
            .annotate(total=Sum("valor"))
            .order_by("-total")
        )
        if limit is not None:
            qs = qs[:limit]

        ranking = []
        for i, item in enumerate(qs, start=1):
            valor_bruto = float(item["total"]) if item["total"] is not None else 0.0
            ranking.append(
                {
                    "posicao": i,
                    "estado": item["municipio__estado__sigla"].upper(),
                    "valor": valor_bruto * fator_escala,
                }
            )
        return ranking

    @staticmethod
    def get_time_series(
        indicator_name: str, estado: str = None, municipio: int = None
    ) -> List[Dict]:
        """Retorna série temporal anual do indicador.

        Args:
            indicator_name: Nome do indicador.
            estado: Sigla do estado para filtrar.
            municipio: Código IBGE do município para filtrar.

        Returns:
            Lista de dicionários com ano e valor.
        """
        ind = DashboardQuery._get_indicator(indicator_name)
        if not ind:
            return []

        fator_escala = get_scale_factor(ind)
        qs = FatoIndicador.objects.filter(
            indicador=ind, tempo__mes__isnull=True, tempo__trimestre__isnull=True
        )
        if municipio:
            qs = qs.filter(municipio__ibge_id=municipio)
        if estado:
            qs = qs.filter(municipio__estado__sigla=estado.upper())
        qs = qs.values("tempo__ano").annotate(total=Sum("valor")).order_by("tempo__ano")

        resultado = []
        for item in qs:
            valor_bruto = float(item["total"]) if item["total"] is not None else 0.0
            resultado.append(
                {
                    "ano": item["tempo__ano"],
                    "valor": valor_bruto * fator_escala,
                }
            )
        return resultado

    @staticmethod
    def get_populacao_por_regiao(ano: int = None) -> List[Dict]:
        """Retorna a população agregada por região geográfica.

        Args:
            ano: Ano de referência. Se omitido, usa o ano mais recente.

        Returns:
            Lista de dicionários com regiao e valor, ordenada por valor decrescente.
        """
        ano = ano or DashboardQuery._get_latest_year()
        ind = DashboardQuery._get_indicator("populacao")
        if not ind:
            return []

        from django.db.models import Sum

        qs = (
            FatoIndicador.objects.filter(
                indicador=ind,
                tempo__ano=ano,
                tempo__mes__isnull=True,
                tempo__trimestre__isnull=True,
            )
            .values("municipio__regiao")
            .annotate(total=Sum("valor"))
            .order_by("-total")
        )

        return [
            {"regiao": item["municipio__regiao"], "valor": float(item["total"])}
            for item in qs
            if item["municipio__regiao"]
        ]

    @staticmethod
    def dashboard_resumo(ano: int = None) -> dict:
        """Retorna todos os dados necessários para o dashboard em uma única chamada.

        Args:
            ano: Ano de referência. Se omitido, usa o ano mais recente.

        Returns:
            Dicionário com ano, populacao_total, pib_total, pib_per_capita_medio,
            populacao_por_regiao e ranking_estados.
        """
        anos_disponiveis = list(
            FatoIndicador.objects.filter(
                tempo__mes__isnull=True,
                tempo__trimestre__isnull=True,
            )
            .values_list("tempo__ano", flat=True)
            .distinct()
            .order_by("-tempo__ano")
        )
        ano = ano or (anos_disponiveis[0] if anos_disponiveis else DashboardQuery._get_latest_year())
        summary = DashboardQuery.summary(ano=ano)

        ind_pop = DashboardQuery._get_indicator("populacao")
        ranking = DashboardQuery.get_ranking_by_estado(ind_pop, ano)

        codigos_principais = ["POPULACAO", "PIB"]
        indicadores_principais = list(Indicador.objects.filter(codigo__in=codigos_principais))
        total_municipios = Municipio.objects.count()
        cobertos = (
            FatoIndicador.objects.filter(
                indicador__in=indicadores_principais,
                tempo__ano=ano,
                tempo__mes__isnull=True,
                tempo__trimestre__isnull=True,
            )
            .values("municipio_id")
            .annotate(indicadores=Count("indicador_id", distinct=True))
            .filter(indicadores=len(indicadores_principais))
            .count()
            if indicadores_principais
            else 0
        )
        periodo = FatoIndicador.objects.filter(
            tempo__mes__isnull=True,
            tempo__trimestre__isnull=True,
        ).aggregate(inicio=Min("tempo__ano"), fim=Max("tempo__ano"))
        ultima_atualizacao = FatoIndicador.objects.filter(
            tempo__ano=ano,
            tempo__mes__isnull=True,
            tempo__trimestre__isnull=True,
        ).aggregate(valor=Max("atualizado_em"))["valor"]

        fontes = sorted(
            {
                indicador.fonte
                for indicador in indicadores_principais
                if indicador.fonte
            }
        )
        ausentes = max(total_municipios - cobertos, 0)
        percentual = (cobertos / total_municipios * 100) if total_municipios else 0.0

        return {
            "ano": ano,
            "anos_disponiveis": anos_disponiveis,
            "populacao_total": int(summary["populacao"]),
            "pib_total": summary["pib"],
            "pib_per_capita_medio": summary["pib_per_capita"],
            "populacao_por_regiao": DashboardQuery.get_populacao_por_regiao(ano),
            "ranking_estados": [
                {
                    "posicao": r["posicao"],
                    "estado": r["estado"],
                    "valor": r["valor"],
                }
                for r in ranking
            ],
            "metadados": {
                "ultima_atualizacao": ultima_atualizacao,
                "periodo_inicio": periodo["inicio"],
                "periodo_fim": periodo["fim"],
                "municipios_total": total_municipios,
                "municipios_cobertos": cobertos,
                "registros_ausentes": ausentes,
                "cobertura_percentual": percentual,
                "fontes": fontes,
            },
        }
