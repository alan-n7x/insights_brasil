"""
Indicator Query Engine

A flexible, semantic-driven system for building dynamic queries on indicator data.

Usage:
    from ibge.query_engine import IndicatorQueryEngine
    
    engine = IndicatorQueryEngine()
    results, metadata = engine.query(
        indicator="PIB",
        group_by="estado",
        filters={"ano": 2023},
        agg="sum",
        limit=10,
    )
"""

from .query_engine import IndicatorQueryEngine, QueryValidationError
from .semantic_model import IndicatorRegistry, IndicatorSchema

__all__ = [
    "IndicatorQueryEngine",
    "QueryValidationError",
    "IndicatorRegistry",
    "IndicatorSchema",
]
