"""
Query validator and builder.

Converts API parameters into secure, validated queries.
"""

from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from django.db.models import QuerySet, Sum, Avg, Min, Max, Count, F
from django.core.exceptions import ValidationError

from .semantic_model import (
    IndicatorSchema,
    IndicatorRegistry,
    AggregationType,
    FilterOperator,
)


class QueryValidationError(ValidationError):
    """Raised when query parameters are invalid."""
    pass


class QueryValidator:
    """Validates query parameters against semantic model."""
    
    def __init__(self, schema: IndicatorSchema):
        self.schema = schema
    
    def validate_aggregation(self, agg: str) -> AggregationType:
        """Validate aggregation function."""
        try:
            agg_type = AggregationType(agg.lower())
        except ValueError:
            raise QueryValidationError(
                f"Invalid aggregation '{agg}'. Allowed: {[a.value for a in self.schema.aggregations]}"
            )
        
        if agg_type not in self.schema.aggregations:
            raise QueryValidationError(
                f"Aggregation '{agg}' not allowed for indicator '{self.schema.code}'. "
                f"Allowed: {[a.value for a in self.schema.aggregations]}"
            )
        
        return agg_type
    
    def validate_group_by(self, group_by: str) -> str:
        """Validate group_by field."""
        valid_fields = {field.name for field in self.schema.group_by_fields}
        
        if group_by not in valid_fields:
            raise QueryValidationError(
                f"Invalid group_by '{group_by}'. Allowed: {sorted(valid_fields)}"
            )
        
        return group_by
    
    def validate_filter(self, filter_name: str, filter_value: Any) -> Tuple[str, Any]:
        """Validate filter field and value."""
        valid_fields = {field.name: field for field in self.schema.filter_fields}
        
        if filter_name not in valid_fields:
            raise QueryValidationError(
                f"Invalid filter '{filter_name}'. Allowed: {sorted(valid_fields.keys())}"
            )
        
        # Type coercion
        field_def = valid_fields[filter_name]
        try:
            if field_def.field_type == "integer":
                if isinstance(filter_value, (list, tuple)):
                    filter_value = [int(v) for v in filter_value]
                else:
                    filter_value = int(filter_value)
            elif field_def.field_type == "float":
                if isinstance(filter_value, (list, tuple)):
                    filter_value = [float(v) for v in filter_value]
                else:
                    filter_value = float(filter_value)
        except (ValueError, TypeError) as e:
            raise QueryValidationError(
                f"Invalid value for filter '{filter_name}': {filter_value}. "
                f"Expected {field_def.field_type}"
            )
        
        return filter_name, filter_value
    
    def validate_limit(self, limit: Optional[int]) -> int:
        """Validate limit (max 10000)."""
        if limit is None:
            return 1000
        
        limit = int(limit)
        
        if limit < 1:
            raise QueryValidationError("Limit must be >= 1")
        
        if limit > 10000:
            raise QueryValidationError("Limit must be <= 10000")
        
        return limit
    
    def validate_offset(self, offset: Optional[int]) -> int:
        """Validate offset."""
        if offset is None:
            return 0
        
        offset = int(offset)
        
        if offset < 0:
            raise QueryValidationError("Offset must be >= 0")
        
        return offset


class QueryBuilder:
    """
    Builds Django ORM queries from validated parameters.
    
    This is where "semantic parameters" become actual SQL.
    """
    
    def __init__(self, schema: IndicatorSchema, validator: QueryValidator):
        self.schema = schema
        self.validator = validator
    
    def get_aggregation_func(self, agg_type: AggregationType):
        """Map aggregation type to Django ORM function."""
        mapping = {
            AggregationType.SUM: Sum,
            AggregationType.AVG: Avg,
            AggregationType.COUNT: Count,
            AggregationType.MIN: Min,
            AggregationType.MAX: Max,
        }
        return mapping[agg_type]
    
    def get_group_by_db_field(self, group_by: str) -> str:
        """Get Django ORM field path for group_by."""
        for field in self.schema.group_by_fields:
            if field.name == group_by:
                return field.db_field
        raise ValueError(f"Invalid group_by: {group_by}")
    
    def build_query(
        self,
        group_by: str,
        agg: str = "sum",
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 1000,
        offset: int = 0,
        order_by: Optional[str] = None,
    ) -> Tuple[QuerySet, Dict[str, Any]]:
        """
        Build a complete QuerySet with parameters.
        
        Returns:
            (queryset, metadata)
        """
        
        # Validate
        agg_type = self.validator.validate_aggregation(agg)
        group_by = self.validator.validate_group_by(group_by)
        limit = self.validator.validate_limit(limit)
        offset = self.validator.validate_offset(offset)
        
        # Import here to avoid circular imports
        from ibge.models import IndicadorMunicipio
        
        # Start with base queryset
        qs = IndicadorMunicipio.objects.filter(
            indicador__codigo=self.schema.code
        )
        
        # Apply filters
        if filters:
            qs = self._apply_filters(qs, filters)
        
        # Apply group by and aggregation
        group_by_field = self.get_group_by_db_field(group_by)
        agg_func = self.get_aggregation_func(agg_type)
        
        qs = qs.values(group_by_field).annotate(
            total=agg_func(self.schema.value_field)
        )
        
        # Apply ordering
        if order_by:
            order_by = self._validate_order_by(order_by)
            qs = qs.order_by(order_by)
        else:
            qs = qs.order_by("-total")
        
        # Pagination
        qs = qs[offset : offset + limit]
        
        metadata = {
            "group_by": group_by,
            "aggregation": agg_type.value,
            "filters": filters or {},
            "limit": limit,
            "offset": offset,
            "order_by": order_by or "-total",
        }
        
        return qs, metadata
    
    def _apply_filters(self, qs: QuerySet, filters: Dict[str, Any]) -> QuerySet:
        """Apply filters to queryset."""
        
        for filter_name, filter_value in filters.items():
            _, filter_value = self.validator.validate_filter(filter_name, filter_value)
            
            # Map semantic filter names to ORM fields
            orm_filter = self._get_orm_filter(filter_name)
            
            # Handle list filters (IN operator)
            if isinstance(filter_value, (list, tuple)):
                qs = qs.filter(**{f"{orm_filter}__in": filter_value})
            else:
                qs = qs.filter(**{orm_filter: filter_value})
        
        return qs
    
    def _get_orm_filter(self, filter_name: str) -> str:
        """Map semantic filter name to ORM field."""
        
        # Get field definition from schema
        field_def = None
        for f in self.schema.filter_fields:
            if f.name == filter_name:
                field_def = f
                break
        
        if not field_def:
            raise ValueError(f"Unknown filter: {filter_name}")
        
        # Map based on filter_name
        mapping = {
            "ano": "ano",
            "estado": "municipio__estado__sigla",
            "municipio": "municipio__nome",
            "regiao": "municipio__estado__regiao",
        }
        
        return mapping.get(filter_name, filter_name)
    
    def _validate_order_by(self, order_by: str) -> str:
        """Validate and normalize order_by parameter."""
        
        # Handle descending order
        if order_by.startswith("-"):
            field = order_by[1:]
            prefix = "-"
        else:
            field = order_by
            prefix = ""
        
        # Only allow ordering by aggregated column or valid group_by field
        allowed = ["total"]  # Always allow ordering by aggregation result
        
        # Also allow ordering by any group_by field
        for gf in self.schema.group_by_fields:
            allowed.append(gf.name)
        
        if field not in allowed:
            raise QueryValidationError(
                f"Invalid order_by '{order_by}'. Allowed: {allowed}"
            )
        
        # Map field name to ORM field if needed
        if field != "total" and field != "ano":
            # For non-aggregated fields, use the db_field
            for gf in self.schema.group_by_fields:
                if gf.name == field:
                    field = gf.db_field
                    break
        
        return f"{prefix}{field}"


class IndicatorQueryEngine:
    """
    Main query engine.
    
    Orchestrates validation, building, and execution.
    """
    
    def __init__(self):
        # Initialize registry on first use
        from .semantic_model import init_indicator_registry
        init_indicator_registry()
    
    def query(
        self,
        indicator: str,
        group_by: str,
        agg: str = "sum",
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 1000,
        offset: int = 0,
        order_by: Optional[str] = None,
    ) -> Tuple[List[Dict], Dict]:
        """
        Execute a query.
        
        Returns:
            (results, metadata)
        """
        
        # Get schema
        try:
            schema = IndicatorRegistry.get(indicator)
        except ValueError as e:
            raise QueryValidationError(str(e))
        
        # Create validator and builder
        validator = QueryValidator(schema)
        builder = QueryBuilder(schema, validator)
        
        # Build query
        qs, metadata = builder.build_query(
            group_by=group_by,
            agg=agg,
            filters=filters,
            limit=limit,
            offset=offset,
            order_by=order_by,
        )
        
        # Execute and format
        results = self._format_results(qs, group_by, agg)
        
        return results, metadata
    
    def _format_results(
        self,
        qs: QuerySet,
        group_by: str,
        agg: str,
    ) -> List[Dict]:
        """
        Format queryset results.
        
        Cleans up group_by field names and adds rank.
        """
        
        results = []
        for rank, row in enumerate(qs, start=1):
            
            # Get db field for group_by
            db_field = None
            for gf in IndicatorRegistry.get(list(IndicatorRegistry._registry.keys())[0]).group_by_fields:
                if gf.name == group_by:
                    db_field = gf.db_field
                    break
            
            # Extract the display name from the db_field key
            # "municipio__nome" -> "municipio"
            display_key = group_by
            
            # Format result
            formatted = {
                display_key: row.get(db_field) or row.get(display_key),
                "total": float(row["total"]) if row["total"] else 0,
                "rank": rank,
            }
            
            results.append(formatted)
        
        return results
    
    def get_indicator_schema(self, indicator: str) -> Dict:
        """Get schema details for indicator."""
        try:
            schema = IndicatorRegistry.get(indicator)
            return schema.to_dict()
        except ValueError as e:
            raise QueryValidationError(str(e))
    
    def list_indicators(self) -> List[Dict]:
        """List all available indicators."""
        return [schema.to_dict() for schema in IndicatorRegistry.list_all()]
