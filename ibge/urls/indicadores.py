from django.urls import path

from ibge.views.indicadores import (
    evolucao_estado_indicador_view,
    evolucao_municipio_indicador_view,
    listar_anos_indicador_view,
    listar_indicadores_view,
    ranking_estados_indicador_view,
    ranking_municipios_indicador_view,
)


urlpatterns = [
    path("", listar_indicadores_view, name="listar-indicadores"),
    path("<str:indicador>/anos/", listar_anos_indicador_view),
    path("<str:indicador>/ranking-estados/", ranking_estados_indicador_view),
    path("<str:indicador>/ranking-municipios/", ranking_municipios_indicador_view),
    path("<str:indicador>/evolucao/", evolucao_estado_indicador_view),
    path(
        "<str:indicador>/municipios/<int:municipio_ibge_id>/evolucao/",
        evolucao_municipio_indicador_view,
    ),
]
