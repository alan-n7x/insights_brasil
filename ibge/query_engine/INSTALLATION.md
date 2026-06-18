# 🚀 Installation & Integration Guide

## Step 1: Add Query Engine URLs to Core URLs

Edit `core/urls.py` and add the query engine URLs:

```python
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Add this line:
    path("api/", include("ibge.query_engine.urls")),
    
    # ... other urls
]
```

---

## Step 2: Update Django Settings

Make sure you have Django REST Framework installed:

```bash
pip install djangorestframework
```

Add to `core/settings.py`:

```python
INSTALLED_APPS = [
    # ...
    "rest_framework",
    "ibge",
]

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",  # Change as needed
    ],
}

# Cache configuration (optional but recommended)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",  # Local memory
        # For production, use Redis:
        # "BACKEND": "django_redis.cache.RedisCache",
        # "LOCATION": "redis://127.0.0.1:6379/1",
    }
}
```

---

## Step 3: Run Migrations (if any)

No migrations are needed for the query engine itself, but make sure your models are set up:

```bash
python manage.py migrate
```

---

## Step 4: Test Installation

```bash
python manage.py test ibge.query_engine.tests
```

---

## Step 5: Populate Test Data

Load indicator data:

```python
from ibge.models import Indicador

# Create indicators if not exist
Indicador.objects.get_or_create(
    codigo="PIB",
    defaults={"nome": "Produto Interno Bruto"}
)

Indicador.objects.get_or_create(
    codigo="POPULACAO",
    defaults={"nome": "População"}
)
```

---

## API Endpoints

Once integrated, these endpoints become available:

### List All Indicators
```
GET /api/indicators/schemas
```

### Get Specific Indicator Schema
```
GET /api/indicators/schemas/PIB
```

### Execute Dynamic Query
```
GET /api/indicators/query?
  indicator=PIB
  &group_by=estado
  &filter_ano=2023
  &agg=sum
  &limit=10
```

### Validate Query (no execution)
```
GET /api/indicators/query/validate?
  indicator=PIB
  &group_by=estado
```

### Clear Cache
```
POST /api/indicators/cache/clear?indicator=PIB
```

---

## Usage Examples

### Python Client

```python
import requests

# List indicators
response = requests.get("http://localhost:8000/api/indicators/schemas")
print(response.json())

# Execute query
response = requests.get(
    "http://localhost:8000/api/indicators/query",
    params={
        "indicator": "PIB",
        "group_by": "estado",
        "filter_ano": 2023,
        "agg": "sum",
        "limit": 10,
    }
)

data = response.json()
for row in data["data"]:
    print(f"{row['estado']}: {row['total']:,.0f}")
```

### JavaScript/Fetch

```javascript
const response = await fetch(
  "/api/indicators/query?" + new URLSearchParams({
    indicator: "PIB",
    group_by: "estado",
    filter_ano: 2023,
    agg: "sum",
    limit: 10,
  })
);

const data = await response.json();
console.log(data);
```

### Streamlit Integration

```python
import streamlit as st
import requests

st.title("Indicadores Brasil")

# Get available indicators
indicators_response = requests.get("http://localhost:8000/api/indicators/schemas")
indicators = {i["code"]: i["name"] for i in indicators_response.json()}

selected = st.selectbox("Indicador", list(indicators.keys()))

# Query
response = requests.get(
    "http://localhost:8000/api/indicators/query",
    params={
        "indicator": selected,
        "group_by": st.selectbox("Agrupar por", ["estado", "municipio"]),
        "agg": st.selectbox("Agregação", ["sum", "avg", "count"]),
    }
)

data = response.json()
st.dataframe(data["data"])
```

---

## Performance Tuning

### 1. Database Indexes

The query engine assumes these indexes exist on `IndicadorMunicipio`:

```python
class Meta:
    indexes = [
        models.Index(fields=["indicador", "ano"]),
        models.Index(fields=["municipio", "indicador"]),
    ]
```

### 2. Redis Cache (Production)

```bash
pip install django-redis
```

Update settings:

```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
```

### 3. Query Optimization

Add select_related/prefetch_related in query builder if needed:

```python
qs = IndicadorMunicipio.objects\
    .select_related("municipio__estado")\
    .filter(...)
```

---

## Adding New Indicators

To add a new indicator to the registry:

1. Edit `ibge/query_engine/semantic_model.py`
2. Create a new `IndicatorSchema`:

```python
SAUDE_SCHEMA = IndicatorSchema(
    code="SAUDE",
    name="Índice de Saúde",
    model_name="IndicadorMunicipio",
    value_field="valor",
    aggregations=[AggregationType.SUM, AggregationType.AVG],
    group_by_fields=[
        GroupByField(...),
    ],
    filter_fields=[
        FilterField(...),
    ],
)
```

3. Register it:

```python
IndicatorRegistry.register(SAUDE_SCHEMA)
```

4. Update `init_indicator_registry()` to include it.

---

## Troubleshooting

### 404 on `/api/indicators/query`

Make sure:
- [ ] URLs are included in `core/urls.py`
- [ ] DRF is in `INSTALLED_APPS`
- [ ] Database has test data

### Invalid aggregation errors

Check that the aggregation is allowed for that indicator in the schema.

### Cache not working

Check Django cache backend:

```python
from django.core.cache import cache
cache.set("test", "value")
print(cache.get("test"))  # Should print "value"
```

---

## Next Steps

1. **Add more indicators** to the registry
2. **Implement advanced analytics**:
   - Time series forecasting
   - Anomaly detection
   - Percentile ranks

3. **BI Tools Integration**:
   - Metabase connector
   - Superset integration
   - Power BI direct query

4. **Export Formats**:
   - CSV/Excel export
   - BigQuery direct export
   - Parquet files
