"""
REST API views for the indicator query engine.

Provides generic endpoints for dynamic indicator queries.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import json

from .query_engine import IndicatorQueryEngine, QueryValidationError
from .query_cache import QueryCache, MetadataCache


class IndicatorSchemaView(APIView):
    """
    List all available indicators or get details of one.
    
    GET /api/indicators/schemas
    GET /api/indicators/schemas/PIB
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request, indicator_code=None):
        """Get indicator schema(s)."""
        
        engine = IndicatorQueryEngine()
        
        try:
            if indicator_code:
                # Get specific schema
                cached = MetadataCache.get_schema(indicator_code)
                if cached:
                    schema = cached
                else:
                    schema = engine.get_indicator_schema(indicator_code)
                    MetadataCache.set_schema(indicator_code, schema)
                
                return Response(schema)
            else:
                # List all schemas
                cached = MetadataCache.get_all_schemas()
                if cached:
                    schemas = cached
                else:
                    schemas = engine.list_indicators()
                    MetadataCache.set_all_schemas(schemas)
                
                return Response(schemas)
        
        except QueryValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class IndicatorQueryView(APIView):
    """
    Generic indicator query endpoint.
    
    GET /api/indicators/query?
      indicator=PIB
      &group_by=estado
      &year=2023
      &agg=sum
      &limit=10
      &order_by=-total
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Execute indicator query."""
        
        try:
            # Extract parameters
            indicator = request.query_params.get("indicator")
            group_by = request.query_params.get("group_by")
            
            if not indicator or not group_by:
                return Response(
                    {
                        "error": "Missing required parameters",
                        "required": ["indicator", "group_by"],
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            # Optional parameters
            agg = request.query_params.get("agg", "sum")
            limit = int(request.query_params.get("limit", 1000))
            offset = int(request.query_params.get("offset", 0))
            order_by = request.query_params.get("order_by", "-total")
            
            # Extract filters from query params
            # Filters are prefixed with "filter_" (e.g., filter_ano=2023, filter_estado=SP)
            filters = {}
            for key, value in request.query_params.items():
                if key.startswith("filter_"):
                    filter_name = key[7:]  # Remove "filter_" prefix
                    
                    # Handle multiple values (comma-separated)
                    if "," in value:
                        value = [v.strip() for v in value.split(",")]
                    
                    filters[filter_name] = value
            
            # Check cache
            cached_result = QueryCache.get(
                indicator=indicator,
                group_by=group_by,
                filters=filters or None,
                agg=agg,
                order_by=order_by,
            )
            
            if cached_result is not None:
                return Response({
                    "data": cached_result,
                    "metadata": {
                        "indicator": indicator,
                        "group_by": group_by,
                        "aggregation": agg,
                        "filters": filters,
                        "limit": limit,
                        "offset": offset,
                        "cached": True,
                    }
                })
            
            # Execute query
            engine = IndicatorQueryEngine()
            results, metadata = engine.query(
                indicator=indicator,
                group_by=group_by,
                agg=agg,
                filters=filters or None,
                limit=limit,
                offset=offset,
                order_by=order_by,
            )
            
            # Cache result
            QueryCache.set(
                indicator=indicator,
                group_by=group_by,
                results=results,
                filters=filters or None,
                agg=agg,
                order_by=order_by,
                ttl=3600,  # 1 hour
            )
            
            metadata["cached"] = False
            
            return Response({
                "data": results,
                "metadata": metadata,
            })
        
        except QueryValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        except Exception as e:
            return Response(
                {"error": f"Query execution error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class QueryValidateView(APIView):
    """
    Validate query parameters without executing.
    
    GET /api/indicators/query/validate?
      indicator=PIB
      &group_by=estado
      &agg=sum
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Validate query parameters."""
        
        try:
            indicator = request.query_params.get("indicator")
            group_by = request.query_params.get("group_by")
            agg = request.query_params.get("agg", "sum")
            order_by = request.query_params.get("order_by", "-total")
            
            if not indicator or not group_by:
                return Response(
                    {
                        "valid": False,
                        "error": "Missing required parameters: indicator, group_by",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            engine = IndicatorQueryEngine()
            schema = engine.get_indicator_schema(indicator)
            
            # Validate parameters
            from .query_engine import QueryValidator, QueryBuilder
            validator = QueryValidator(schema)
            
            # These will raise exceptions if invalid
            validator.validate_aggregation(agg)
            validator.validate_group_by(group_by)
            validator.validate_order_by(order_by)
            
            return Response({
                "valid": True,
                "indicator": indicator,
                "schema_code": schema["code"],
                "schema_name": schema["name"],
            })
        
        except QueryValidationError as e:
            return Response(
                {
                    "valid": False,
                    "error": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class CacheClearView(APIView):
    """
    Clear cache for an indicator.
    
    POST /api/indicators/cache/clear?indicator=PIB
    
    Admin only.
    """
    
    permission_classes = [AllowAny]  # In production, use IsAdminUser
    
    def post(self, request):
        """Clear cache."""
        
        indicator = request.query_params.get("indicator")
        
        if indicator:
            QueryCache.clear_by_indicator(indicator)
            MetadataCache.clear_all()
            return Response({
                "status": "cleared",
                "indicator": indicator,
            })
        else:
            # Clear all
            MetadataCache.clear_all()
            return Response({
                "status": "cleared",
                "indicator": "all",
            })
