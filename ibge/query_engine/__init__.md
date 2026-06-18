"""
Initialize the query engine module.

This module provides a flexible, semantic-driven system for building
dynamic queries on indicator data.

Quick start:
    
    from ibge.query_engine import IndicatorQueryEngine
    
    engine = IndicatorQueryEngine()
    results, metadata = engine.query(
        indicator="PIB",
        group_by="estado",
        filters={"ano": 2023},
    )

For more info, see:
    - QUICKSTART.md - 5-minute integration guide
    - README.md - Comprehensive documentation
    - ARCHITECTURE.md - Technical deep dive
    - INSTALLATION.md - Detailed setup guide
    - EXAMPLES.py - Real-world usage examples
"""

from .query_engine import IndicatorQueryEngine, QueryValidationError
from .semantic_model import IndicatorRegistry, IndicatorSchema

__all__ = [
    "IndicatorQueryEngine",
    "QueryValidationError",
    "IndicatorRegistry",
    "IndicatorSchema",
]


def setup():
    """Initialize the query engine (called on app startup)."""
    from .semantic_model import init_indicator_registry
    init_indicator_registry()
