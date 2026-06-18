"""
URL configuration for the query engine API.
"""

from django.urls import path

from .api_views import (
    IndicatorSchemaView,
    IndicatorQueryView,
    QueryValidateView,
    CacheClearView,
)

urlpatterns = [
    # Schemas
    path(
        "indicators/schemas",
        IndicatorSchemaView.as_view(),
        name="indicator_schemas_list",
    ),
    path(
        "indicators/schemas/<str:indicator_code>",
        IndicatorSchemaView.as_view(),
        name="indicator_schema_detail",
    ),
    
    # Query
    path(
        "indicators/query",
        IndicatorQueryView.as_view(),
        name="indicator_query",
    ),
    
    # Validate
    path(
        "indicators/query/validate",
        QueryValidateView.as_view(),
        name="indicator_query_validate",
    ),
    
    # Cache
    path(
        "indicators/cache/clear",
        CacheClearView.as_view(),
        name="indicator_cache_clear",
    ),
]
