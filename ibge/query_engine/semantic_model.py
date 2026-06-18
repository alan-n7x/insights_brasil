"""
Semantic model for indicators.

Define which fields are aggregable, filterable, groupable for each indicator.
This is the "business rules" layer.
"""

from typing import Dict, List, Literal
from dataclasses import dataclass, field
from enum import Enum


class AggregationType(str, Enum):
    """Allowed aggregation functions."""
    SUM = "sum"
    AVG = "avg"
    COUNT = "count"
    MIN = "min"
    MAX = "max"


class FilterOperator(str, Enum):
    """Allowed filter operators."""
    EQ = "eq"
    IN = "in"
    GTE = "gte"
    LTE = "lte"
    GT = "gt"
    LT = "lt"
    RANGE = "range"


@dataclass
class FilterField:
    """Definition of a filterable field."""
    name: str
    label: str
    field_type: Literal["string", "integer", "float", "date"]
    operators: List[FilterOperator] = field(default_factory=lambda: [FilterOperator.EQ, FilterOperator.IN])
    example: str = None


@dataclass
class GroupByField:
    """Definition of a groupable field."""
    name: str
    label: str
    db_field: str  # ORM field path (e.g., "municipio__estado__sigla")
    field_type: Literal["string", "integer", "float"]


@dataclass
class IndicatorSchema:
    """
    Complete definition of an indicator.
    
    This is what drives the query engine.
    """
    
    # Basic info (required)
    code: str
    name: str
    model_name: str  # "IndicadorMunicipio"
    value_field: str  # Field that contains the value (e.g., "valor")
    
    # Basic info (optional)
    description: str = ""
    
    # Aggregations
    aggregations: List[AggregationType] = field(default_factory=lambda: [
        AggregationType.SUM,
        AggregationType.AVG,
        AggregationType.MIN,
        AggregationType.MAX,
    ])
    
    # Dimensions
    group_by_fields: List[GroupByField] = field(default_factory=list)
    filter_fields: List[FilterField] = field(default_factory=list)
    
    # Time
    time_field: str = "ano"  # Default time field
    
    # Cache config
    cache_ttl_seconds: int = 3600  # 1 hour
    
    def __post_init__(self):
        """Validate schema on creation."""
        if not self.code or not self.name:
            raise ValueError("code and name are required")
        if not self.group_by_fields:
            raise ValueError(f"Schema {self.code} must have at least one group_by field")
    
    def to_dict(self) -> Dict:
        """Serialize to dict for API response."""
        return {
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "aggregations": [agg.value for agg in self.aggregations],
            "group_by_fields": [
                {
                    "name": field.name,
                    "label": field.label,
                    "type": field.field_type,
                }
                for field in self.group_by_fields
            ],
            "filter_fields": [
                {
                    "name": field.name,
                    "label": field.label,
                    "type": field.field_type,
                    "operators": [op.value for op in field.operators],
                    "example": field.example,
                }
                for field in self.filter_fields
            ],
        }


class IndicatorRegistry:
    """
    Central registry of all indicator schemas.
    
    This is the "semantic layer" - defines what queries are possible.
    """
    
    _registry: Dict[str, IndicatorSchema] = {}
    
    @classmethod
    def register(cls, schema: IndicatorSchema):
        """Register a new indicator schema."""
        cls._registry[schema.code.upper()] = schema
    
    @classmethod
    def get(cls, code: str) -> IndicatorSchema:
        """Get schema by indicator code."""
        code = code.upper()
        if code not in cls._registry:
            raise ValueError(f"Indicator '{code}' not found in registry")
        return cls._registry[code]
    
    @classmethod
    def exists(cls, code: str) -> bool:
        """Check if indicator exists."""
        return code.upper() in cls._registry
    
    @classmethod
    def list_all(cls) -> List[IndicatorSchema]:
        """List all registered indicators."""
        return list(cls._registry.values())
    
    @classmethod
    def clear(cls):
        """Clear registry (for testing)."""
        cls._registry.clear()


# =============================================================================
# INDICATOR DEFINITIONS (Catálogo de Indicadores)
# =============================================================================

# PIB
PIB_SCHEMA = IndicatorSchema(
    code="PIB",
    name="Produto Interno Bruto",
    description="PIB dos municípios em valores nominais",
    model_name="IndicadorMunicipio",
    value_field="valor",
    aggregations=[
        AggregationType.SUM,
        AggregationType.AVG,
        AggregationType.MIN,
        AggregationType.MAX,
    ],
    group_by_fields=[
        GroupByField(
            name="municipio",
            label="Município",
            db_field="municipio__nome",
            field_type="string",
        ),
        GroupByField(
            name="estado",
            label="Estado",
            db_field="municipio__estado__nome",
            field_type="string",
        ),
        GroupByField(
            name="estado_sigla",
            label="UF",
            db_field="municipio__estado__sigla",
            field_type="string",
        ),
        GroupByField(
            name="regiao",
            label="Região",
            db_field="municipio__estado__regiao",
            field_type="string",
        ),
        GroupByField(
            name="ano",
            label="Ano",
            db_field="ano",
            field_type="integer",
        ),
    ],
    filter_fields=[
        FilterField(
            name="ano",
            label="Ano",
            field_type="integer",
            operators=[FilterOperator.EQ, FilterOperator.IN, FilterOperator.GTE, FilterOperator.LTE],
            example="2023",
        ),
        FilterField(
            name="estado",
            label="Estado (sigla)",
            field_type="string",
            operators=[FilterOperator.EQ, FilterOperator.IN],
            example="SP,RJ",
        ),
        FilterField(
            name="municipio",
            label="Município",
            field_type="string",
            operators=[FilterOperator.EQ, FilterOperator.IN],
            example="São Paulo",
        ),
        FilterField(
            name="regiao",
            label="Região",
            field_type="string",
            operators=[FilterOperator.IN],
            example="Sudeste",
        ),
    ],
)


# POPULAÇÃO
POPULACAO_SCHEMA = IndicatorSchema(
    code="POPULACAO",
    name="População",
    description="População dos municípios",
    model_name="IndicadorMunicipio",
    value_field="valor",
    aggregations=[
        AggregationType.SUM,
        AggregationType.AVG,
    ],
    group_by_fields=[
        GroupByField(
            name="municipio",
            label="Município",
            db_field="municipio__nome",
            field_type="string",
        ),
        GroupByField(
            name="estado",
            label="Estado",
            db_field="municipio__estado__sigla",
            field_type="string",
        ),
        GroupByField(
            name="ano",
            label="Ano",
            db_field="ano",
            field_type="integer",
        ),
    ],
    filter_fields=[
        FilterField(
            name="ano",
            label="Ano",
            field_type="integer",
            operators=[FilterOperator.EQ, FilterOperator.IN, FilterOperator.GTE, FilterOperator.LTE],
        ),
        FilterField(
            name="estado",
            label="Estado",
            field_type="string",
            operators=[FilterOperator.EQ, FilterOperator.IN],
        ),
    ],
)


# =============================================================================
# AUTO-REGISTER ALL SCHEMAS
# =============================================================================

def init_indicator_registry():
    """Initialize the indicator registry with all schemas."""
    IndicatorRegistry.register(PIB_SCHEMA)
    IndicatorRegistry.register(POPULACAO_SCHEMA)
