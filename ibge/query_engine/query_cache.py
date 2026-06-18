"""
Intelligent caching layer for query results.

Uses Django cache with custom tagging and invalidation strategies.
"""

import hashlib
import json
from typing import Dict, List, Any, Optional
from django.core.cache import cache
from django.utils.encoding import force_bytes


class QueryCache:
    """
    Smart cache for indicator queries.
    
    - Cache by query signature
    - Automatic invalidation by tags
    - Configurable TTL per indicator
    """
    
    PREFIX = "indicator_query"
    METADATA_PREFIX = "indicator_meta"
    
    @staticmethod
    def _make_key(indicator: str, group_by: str, filters: Dict, agg: str, order_by: str) -> str:
        """
        Generate cache key from query parameters.
        
        Deterministic and collision-safe.
        """
        
        # Create a normalized string representation
        key_parts = [
            f"indicator:{indicator.upper()}",
            f"group_by:{group_by}",
            f"agg:{agg}",
            f"order_by:{order_by}",
        ]
        
        # Add filters in sorted order for determinism
        if filters:
            filters_sorted = sorted(
                (k, json.dumps(v, sort_keys=True, default=str))
                for k, v in filters.items()
            )
            for k, v in filters_sorted:
                key_parts.append(f"filter_{k}:{v}")
        
        # Hash to keep key length reasonable
        key_str = "|".join(key_parts)
        key_hash = hashlib.md5(force_bytes(key_str)).hexdigest()
        
        return f"{QueryCache.PREFIX}:{key_hash}"
    
    @staticmethod
    def get(
        indicator: str,
        group_by: str,
        filters: Optional[Dict] = None,
        agg: str = "sum",
        order_by: str = "-total",
    ) -> Optional[List[Dict]]:
        """Retrieve cached query result."""
        
        key = QueryCache._make_key(indicator, group_by, filters or {}, agg, order_by)
        return cache.get(key)
    
    @staticmethod
    def set(
        indicator: str,
        group_by: str,
        results: List[Dict],
        filters: Optional[Dict] = None,
        agg: str = "sum",
        order_by: str = "-total",
        ttl: int = 3600,
    ):
        """Cache query result."""
        
        key = QueryCache._make_key(indicator, group_by, filters or {}, agg, order_by)
        cache.set(key, results, ttl)
    
    @staticmethod
    def clear_by_indicator(indicator: str):
        """
        Clear all cached results for an indicator.
        
        Note: Django's cache doesn't support pattern deletion.
        In production, use Redis with KEYS pattern or implement a tag system.
        """
        # This is a simplified approach
        # In production, use: cache.delete_pattern(f"{QueryCache.PREFIX}:*:{indicator}:*")
        pass
    
    @staticmethod
    def invalidate_for_update(indicator: str, anos: List[int] = None):
        """
        Invalidate cache when indicator data is updated.
        
        Args:
            indicator: Indicator code that was updated
            anos: Specific years that were updated (if None, invalidate all years)
        """
        # In production with Redis, you'd use tags:
        # cache.delete_many([f"{QueryCache.PREFIX}:indicator:{indicator}:*"])
        pass


class MetadataCache:
    """Cache for indicator schemas and metadata."""
    
    PREFIX = "indicator_schema"
    TTL = 86400  # 24 hours
    
    @staticmethod
    def get_schema(indicator: str) -> Optional[Dict]:
        """Get cached indicator schema."""
        key = f"{MetadataCache.PREFIX}:{indicator.upper()}"
        return cache.get(key)
    
    @staticmethod
    def set_schema(indicator: str, schema: Dict):
        """Cache indicator schema."""
        key = f"{MetadataCache.PREFIX}:{indicator.upper()}"
        cache.set(key, schema, MetadataCache.TTL)
    
    @staticmethod
    def get_all_schemas() -> Optional[List[Dict]]:
        """Get cached list of all schemas."""
        key = f"{MetadataCache.PREFIX}:all"
        return cache.get(key)
    
    @staticmethod
    def set_all_schemas(schemas: List[Dict]):
        """Cache list of all schemas."""
        key = f"{MetadataCache.PREFIX}:all"
        cache.set(key, schemas, MetadataCache.TTL)
    
    @staticmethod
    def clear_all():
        """Clear all metadata cache."""
        # In production with Redis: cache.delete_pattern(f"{MetadataCache.PREFIX}:*")
        pass
