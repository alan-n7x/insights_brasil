"""
Mecanismo de Consulta (Query Engine) para análises analíticas.
Utiliza repositórios para buscar dados e aplica a lógica de negócios.
"""

from typing import List, Dict
from django.db.models import Sum
from ibge.utils import get_scale_factor
from ibge.repositories.indicador_repository import IndicadorRepository
from ibge.repositories.municipio_repository import MunicipioRepository
from ibge.repositories.fato_indicador_repository import FatoIndicadorRepository
from ibge.models import FatoIndicador, Municipio


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
    def _get_indicator(indicator_name: str):
        """Retorna a instância de Indicador a partir do nome usando o repositório."""
        return getattr(IndicadorRepository, f"get_{indicator_name}")()

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
        if municipio:
            if not isinstance(municipio, Municipio):
                mun = MunicipioRepository.get_by_codigo(municipio)
                if not mun:
                    return 0.0
                municipio = mun
            return FatoIndicadorRepository.get_value(municipio, ind, ano) or 0.0
        else:
            return FatoIndicadorRepository.aggregate_sum(
                indicador=ind, ano=ano, estado_sigla=estado
            )

    @staticmethod
    def _get_indicator_list(
        indicator_name: str, ano: int = None, estado: str = None,
        limit: int = None, order_by: str = None,
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

        valores = {
            f.municipio_id: float(f.valor) * fator_escala
            for f in FatoIndicador.objects.filter(
                indicador=ind,
                tempo__ano=ano,
                tempo__mes__isnull=True,
                tempo__trimestre__isnull=True,
            )
        }

        qs = MunicipioRepository.all()
        if estado:
            qs = MunicipioRepository.filter_by_estado(estado)
        qs = qs.select_related("estado")

        result = []
        for mun in qs:
            val = valores.get(mun.id, 0.0)
            result.append(
                {
                    "codigo": mun.ibge_id,
                    "nome": mun.nome,
                    "sigla": mun.estado.sigla,
                    "valor": val,
                }
            )

        if order_by == "valor":
            result.sort(key=lambda x: x["valor"], reverse=True)

        if limit is not None:
            result = result[:limit]

        return result

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

        ind_pib = DashboardQuery._get_indicator("pib")
        fator_pib = get_scale_factor(ind_pib)
        pib_real = pib * fator_pib
        pib_per_capita = (pib_real / pop) if pop > 0 else 0.0

        return {
            "ano": ano,
            "populacao": pop,
            "pib": pib_real,
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
