#!/usr/bin/env python
"""
Quick Reference: Essential Commands & Code Snippets

Copy & paste commands for the query engine.
"""

# ============================================================================
# INSTALLATION COMMANDS
# ============================================================================

"""
1. Install DRF
   pip install djangorestframework

2. Update core/settings.py
   - Add 'rest_framework' to INSTALLED_APPS
   - Add CACHES config (optional)

3. Update core/urls.py
   path('api/', include('ibge.query_engine.urls')),

4. Restart server
   python manage.py runserver

5. Test
   curl http://localhost:8000/api/indicators/schemas
"""


# ============================================================================
# PYTHON: USING THE ENGINE DIRECTLY
# ============================================================================

from ibge.query_engine import IndicatorQueryEngine

engine = IndicatorQueryEngine()

# Query 1: Ranking by Estado
results, metadata = engine.query(
    indicator="PIB",
    group_by="estado",
    filters={"ano": 2023},
    agg="sum",
    limit=10,
)

# Query 2: Ranking by Municipio in SP
results, metadata = engine.query(
    indicator="POPULACAO",
    group_by="municipio",
    filters={"estado": "SP", "ano": 2023},
    agg="avg",
)

# Query 3: Time Series
results, metadata = engine.query(
    indicator="PIB",
    group_by="ano",
    filters={"estado": "RJ"},
    agg="sum",
)


# ============================================================================
# REST API: CURL EXAMPLES
# ============================================================================

"""
1. List all indicators
   curl http://localhost:8000/api/indicators/schemas

2. Get specific indicator schema
   curl http://localhost:8000/api/indicators/schemas/PIB

3. Query: Ranking Estados by PIB
   curl "http://localhost:8000/api/indicators/query?
     indicator=PIB
     &group_by=estado
     &filter_ano=2023
     &agg=sum
     &limit=10"

4. Query: Ranking Municipios in SP
   curl "http://localhost:8000/api/indicators/query?
     indicator=POPULACAO
     &group_by=municipio
     &filter_estado=SP
     &filter_ano=2023
     &agg=avg
     &limit=20"

5. Query: Time Series (Evolution)
   curl "http://localhost:8000/api/indicators/query?
     indicator=SAUDE
     &group_by=ano
     &filter_estado=MG
     &agg=avg"

6. Validate query (no execution)
   curl "http://localhost:8000/api/indicators/query/validate?
     indicator=PIB
     &group_by=estado"

7. Clear cache
   curl -X POST http://localhost:8000/api/indicators/cache/clear?indicator=PIB
"""


# ============================================================================
# STREAMLIT: QUICK INTEGRATION
# ============================================================================

STREAMLIT_TEMPLATE = """
import streamlit as st
import requests
import pandas as pd

st.title("Indicadores Brasil")

# Get indicators
resp = requests.get("http://localhost:8000/api/indicators/schemas")
indicators = {i["code"]: i["name"] for i in resp.json()}

# UI
col1, col2, col3 = st.columns(3)
indicator = col1.selectbox("Indicador", list(indicators.keys()))
group_by = col2.selectbox("Agrupar por", ["estado", "municipio"])
agg = col3.selectbox("Agregação", ["sum", "avg", "count"])

# Query
resp = requests.get(
    "http://localhost:8000/api/indicators/query",
    params={
        "indicator": indicator,
        "group_by": group_by,
        "agg": agg,
    }
)

# Display
df = pd.DataFrame(resp.json()["data"])
st.dataframe(df)
st.bar_chart(df.set_index(group_by)["total"])
"""


# ============================================================================
# PYTHON CLIENT: REUSABLE CLASS
# ============================================================================

PYTHON_CLIENT = """
import requests
import pandas as pd

class IndicatorClient:
    def __init__(self, url="http://localhost:8000"):
        self.url = url
    
    def query(self, indicator, group_by, **filters):
        params = {
            "indicator": indicator,
            "group_by": group_by,
            **filters,
        }
        resp = requests.get(f"{self.url}/api/indicators/query", params=params)
        return pd.DataFrame(resp.json()["data"])

# Usage:
client = IndicatorClient()
df = client.query(
    "PIB",
    "estado",
    filter_ano=2023,
    agg="sum",
    limit=10,
)
print(df)
"""


# ============================================================================
# ADDING NEW INDICATOR
# ============================================================================

ADD_INDICATOR = """
# In ibge/query_engine/semantic_model.py

from .semantic_model import (
    IndicatorSchema, GroupByField, FilterField, AggregationType
)

# Define schema
SAUDE_SCHEMA = IndicatorSchema(
    code="SAUDE",
    name="Índice de Saúde",
    model_name="IndicadorMunicipio",
    value_field="valor",
    aggregations=[AggregationType.SUM, AggregationType.AVG],
    group_by_fields=[
        GroupByField("municipio", "Município", "municipio__nome"),
        GroupByField("estado", "Estado", "municipio__estado__sigla"),
        GroupByField("ano", "Ano", "ano"),
    ],
    filter_fields=[
        FilterField("ano", "Ano", "integer"),
        FilterField("estado", "Estado", "string"),
    ],
)

# Register
IndicatorRegistry.register(SAUDE_SCHEMA)

# Update init_indicator_registry()
def init_indicator_registry():
    IndicatorRegistry.register(PIB_SCHEMA)
    IndicatorRegistry.register(POPULACAO_SCHEMA)
    IndicatorRegistry.register(SAUDE_SCHEMA)  # ADD THIS
"""


# ============================================================================
# RUNNING TESTS
# ============================================================================

"""
# All tests
python manage.py test ibge.query_engine.tests

# Specific test
python manage.py test ibge.query_engine.tests.QueryEngineTests

# With coverage
coverage run --source='ibge.query_engine' manage.py test
coverage report

# Verbose
python manage.py test ibge.query_engine.tests -v 2
"""


# ============================================================================
# DEBUGGING
# ============================================================================

DEBUG_QUERIES = """
# Enable SQL query logging in settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

# Or in Django shell
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as ctx:
    engine.query(...)
    for q in ctx.captured_queries:
        print(q['sql'])
"""


# ============================================================================
# COMMON PATTERNS
# ============================================================================

PATTERNS = {
    "Top 10": {
        "code": """
results, _ = engine.query(
    indicator="PIB",
    group_by="estado",
    agg="sum",
    limit=10,
)
""",
    },
    
    "Filter by State": {
        "code": """
results, _ = engine.query(
    indicator="PIB",
    group_by="municipio",
    filters={"estado": "SP"},
    limit=50,
)
""",
    },
    
    "Time Series": {
        "code": """
results, _ = engine.query(
    indicator="POPULACAO",
    group_by="ano",
    filters={"estado": "RJ"},
    agg="sum",
)
""",
    },
    
    "Average by State": {
        "code": """
results, _ = engine.query(
    indicator="PIB",
    group_by="estado",
    agg="avg",
)
""",
    },
    
    "Multiple Filters": {
        "code": """
results, _ = engine.query(
    indicator="SAUDE",
    group_by="municipio",
    filters={
        "estado": ["SP", "RJ"],
        "ano": [2022, 2023],
    },
)
""",
    },
}


# ============================================================================
# PERFORMANCE TUNING
# ============================================================================

PERFORMANCE_TIPS = """
1. Enable Query Caching (in settings.py)
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.redis.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
       }
   }

2. Check Database Indexes
   python manage.py sqlsequencereset ibge | python manage.py dbshell

3. Monitor Slow Queries
   - Enable SQL logging
   - Use Django Debug Toolbar
   - Check query time in metadata

4. Limit Results
   - Always use limit parameter
   - Default is 1000, max is 10000

5. Batch Processing
   - Use offset for pagination
   - Don't load everything at once
"""


# ============================================================================
# SECURITY CHECKLIST
# ============================================================================

SECURITY = """
✅ Parametrized queries (no SQL injection)
✅ Whitelist validation (schema enforcement)
✅ Type checking (int/str/float)
✅ Result limits (max 10K rows)
✅ No raw SQL execution
✅ Framework-level protection (Django ORM)

If in production:
- Require authentication (add IsAuthenticated permission)
- Rate limit API (django-ratelimit)
- Monitor logs for abuse
- Use HTTPS only
- Run on separate app server
"""


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

TROUBLESHOOTING = """
Problem: 404 Not Found
Solution: Check URLs in core/urls.py includes query_engine.urls

Problem: ImportError: No module named 'rest_framework'
Solution: pip install djangorestframework

Problem: Query returns empty list
Solution: 
  1. Check data exists in database
  2. Verify indicator code in semantic_model.py
  3. Check filter values match data

Problem: "Invalid aggregation" error
Solution: Check aggregations allowed in schema for that indicator

Problem: Slow query (>10 seconds)
Solution:
  1. Check database indexes exist
  2. Check limit parameter
  3. Check cache is working
  4. Analyze SQL query

Problem: Cache not working
Solution:
  1. Check CACHES setting in settings.py
  2. Verify Redis is running (if using Redis)
  3. Check cache backend logs
"""


if __name__ == "__main__":
    print("📚 Query Engine Quick Reference")
    print("\nSee this file for:")
    print("  - Installation commands")
    print("  - Python usage examples")
    print("  - REST API curl commands")
    print("  - Streamlit integration")
    print("  - Adding new indicators")
    print("  - Testing & debugging")
    print("  - Performance tuning")
    print("  - Security checklist")
    print("  - Troubleshooting guide")
