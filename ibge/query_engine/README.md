# 🧠 Indicator Query Engine

**A flexible, semantic-driven system for building dynamic queries on indicator data.**

This is the "motor de consultas" that transforms your project from a static dashboard into a **data analytics platform**.

---

## 🎯 What It Does

Instead of creating endpoints for each query type...

```
❌ /ranking_estados
❌ /ranking_municipios
❌ /evolucao_temporal
❌ /comparacao_...
```

You get **ONE powerful endpoint** that handles all queries:

```
✅ GET /api/indicators/query?
     indicator=PIB
     &group_by=estado
     &filter_ano=2023
     &agg=sum
     &limit=10
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│  Streamlit / BI Tools / Frontend    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Query API (Generic DRF View)       │ ← You call this
│  GET /api/indicators/query          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Semantic Model (defines rules)     │ ← What's allowed
│  - Which fields can aggregate       │
│  - Which fields can filter          │
│  - Which fields can group by        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Query Engine (orchestrator)        │ ← Does the work
│  - Validates parameters             │
│  - Builds Django ORM query          │
│  - Executes & formats               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Django ORM + Database              │ ← Actual data
└─────────────────────────────────────┘
```

---

## 📚 Core Components

### 1. **Semantic Model** (`semantic_model.py`)
Defines what's possible for each indicator.

```python
PIB_SCHEMA = IndicatorSchema(
    code="PIB",
    name="Produto Interno Bruto",
    
    # What fields can be aggregated?
    aggregations=["sum", "avg", "min", "max"],
    
    # What can we group by?
    group_by_fields=["municipio", "estado", "regiao", "ano"],
    
    # What can we filter by?
    filter_fields=["ano", "estado", "municipio"],
)
```

### 2. **Query Validator** (`query_engine.py`)
Validates all parameters before execution.

```python
validator = QueryValidator(schema)
validator.validate_aggregation("sum")  # ✓ OK
validator.validate_group_by("estado")  # ✓ OK
validator.validate_group_by("invalid")  # ✗ Raises error
```

### 3. **Query Builder** (`query_engine.py`)
Converts parameters into Django ORM queries.

```python
builder = QueryBuilder(schema, validator)
qs, metadata = builder.build_query(
    group_by="estado",
    agg="sum",
    filters={"ano": 2023},
)
```

### 4. **Query Engine** (`query_engine.py`)
Orchestrates everything.

```python
engine = IndicatorQueryEngine()
results, metadata = engine.query(
    indicator="PIB",
    group_by="estado",
    filters={"ano": 2023},
    agg="sum",
)
```

### 5. **Cache Layer** (`query_cache.py`)
Smart caching with TTL per indicator.

```python
# Check cache
cached = QueryCache.get("PIB", "estado", {"ano": 2023})

if cached:
    return cached

# Execute & cache
results, _ = engine.query(...)
QueryCache.set("PIB", "estado", results, ttl=3600)
```

### 6. **API Views** (`api_views.py`)
REST endpoints powered by DRF.

```python
# Automatic endpoints:
GET /api/indicators/schemas           # List all
GET /api/indicators/schemas/PIB       # Details
GET /api/indicators/query             # The motor
GET /api/indicators/query/validate    # Validate (no execution)
POST /api/indicators/cache/clear      # Cache control
```

---

## 🚀 Usage Examples

### Example 1: Ranking Estados por PIB

```bash
curl "http://localhost:8000/api/indicators/query?
  indicator=PIB
  &group_by=estado
  &filter_ano=2023
  &agg=sum
  &limit=5"
```

**Response:**
```json
{
  "data": [
    {"estado": "São Paulo", "total": 2150000000.00, "rank": 1},
    {"estado": "Rio de Janeiro", "total": 980000000.00, "rank": 2},
    ...
  ],
  "metadata": {
    "indicator": "PIB",
    "group_by": "estado",
    "aggregation": "sum",
    "filters": {"ano": 2023},
    "cached": false
  }
}
```

### Example 2: Série Temporal (Evolução)

```bash
curl "http://localhost:8000/api/indicators/query?
  indicator=POPULACAO
  &group_by=ano
  &filter_estado=SP
  &agg=sum"
```

### Example 3: Múltiplos Filtros

```bash
curl "http://localhost:8000/api/indicators/query?
  indicator=PIB
  &group_by=municipio
  &filter_estado=SP
  &filter_ano=2023
  &agg=avg
  &limit=20"
```

---

## 🔒 Security Features

✅ **Parametrized Queries** - No SQL injection risk

✅ **Field Whitelisting** - Only allowed fields can be queried

✅ **Type Validation** - Integer/string/float type checking

✅ **Aggregation Whitelist** - Only allowed aggregations per indicator

✅ **Result Limits** - Max 10,000 rows to prevent memory issues

---

## ⚡ Performance

### Smart Caching
- Query results cached for 1 hour
- Metadata cached for 24 hours
- Automatic invalidation on data changes

### Database Optimization
- Indexes on `(indicador, ano)` and `(municipio, indicador)`
- Uses Django ORM aggregations (computed in DB, not Python)
- Select related / prefetch related for foreign keys

### Query Example
```python
# This becomes one SQL query:
qs = IndicadorMunicipio.objects\
    .filter(indicador__codigo='PIB', ano=2023)\
    .values('municipio__estado__nome')\
    .annotate(total=Sum('valor'))\
    .order_by('-total')[:10]
```

---

## 📦 Adding New Indicators

Super simple. Just add to `semantic_model.py`:

```python
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

IndicatorRegistry.register(SAUDE_SCHEMA)
```

That's it. The API automatically supports it.

---

## 🧪 Testing

```bash
# Run all tests
python manage.py test ibge.query_engine.tests

# Run specific test
python manage.py test ibge.query_engine.tests.QueryEngineTests.test_simple_group_by_estado
```

---

## 🔄 Integration with Streamlit

```python
import requests
import streamlit as st
import pandas as pd

# Get available indicators
resp = requests.get("http://localhost:8000/api/indicators/schemas")
indicators = {i["code"]: i["name"] for i in resp.json()}

# UI
st.title("Análise de Indicadores")
indicator = st.selectbox("Indicador", list(indicators.keys()))
group_by = st.selectbox("Agrupar por", ["estado", "municipio"])
agg = st.selectbox("Agregação", ["sum", "avg", "min", "max"])

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
data = resp.json()["data"]
df = pd.DataFrame(data)
st.dataframe(df)
st.bar_chart(df.set_index(group_by)["total"])
```

---

## 🎓 Key Concepts

### Query Signature
A unique key that identifies each query:
```
indicator:PIB | group_by:estado | agg:sum | filter_ano:2023
```
Used for caching and invalidation.

### Semantic Layer
Rules that define what's allowed:
- What fields aggregate?
- What fields filter?
- What fields group?
- What aggregations are permitted?

### Whitelist Security
Only fields in the schema can be queried. Prevents:
- Accidental exposure of sensitive fields
- SQL injection
- Unlimited result sets

---

## 🚢 Production Checklist

- [ ] DRF installed and configured
- [ ] Redis for caching (not local memory)
- [ ] Database indexes created
- [ ] All indicators registered in schema
- [ ] Tests passing
- [ ] Rate limiting enabled (optional)
- [ ] Authentication/authorization configured
- [ ] Logging configured
- [ ] Documentation updated

---

## 🧩 Future Extensions

1. **Multiple Indicators Query**
   - JOIN between indicators
   - Calculate ratios
   
2. **Time Series Forecasting**
   - Predict next years
   - Trend analysis

3. **Export Formats**
   - CSV, Excel, Parquet
   - Direct BigQuery export

4. **BI Tools Integration**
   - Metabase
   - Superset
   - Power BI

5. **Advanced Analytics**
   - Percentile ranks
   - Growth rates
   - Anomaly detection

---

## 📖 Files

```
ibge/query_engine/
├── ARCHITECTURE.md          # Detailed architecture
├── INSTALLATION.md          # Setup guide
├── README.md               # This file
├── __init__.py
├── semantic_model.py       # Indicator definitions
├── query_engine.py         # Core engine + validator + builder
├── query_cache.py          # Caching layer
├── api_views.py           # DRF views
├── urls.py                # URL routing
└── tests.py               # Complete test suite
```

---

## 💡 The Big Picture

This query engine is the **foundation** for:
- Data API for external tools
- Metabase/Superset integration
- Custom analytics dashboards
- ML feature engineering
- Data exports for analysis
- BI tool connections

It's the **analytics layer** that makes your data accessible at scale.

---

**Questions? See INSTALLATION.md or ARCHITECTURE.md**
