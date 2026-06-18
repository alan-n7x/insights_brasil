# 📚 Query Engine - Complete Documentation Index

## 🎯 Getting Started

**New to the query engine? Start here:**

1. **[QUICKSTART.md](QUICKSTART.md)** ⚡ (5 minutes)
   - Install DRF
   - Update settings
   - Add URLs
   - Test immediately
   - **→ Get it running in 5 minutes**

2. **[README.md](README.md)** 📖 (15 minutes)
   - What it does
   - How it works
   - Core concepts
   - Usage examples
   - Security features
   - **→ Understand the full picture**

---

## 🔧 Technical Deep Dives

3. **[ARCHITECTURE.md](ARCHITECTURE.md)** 🏗️ (30 minutes)
   - Complete architecture diagram
   - Component design
   - Query examples
   - Data flow walkthrough
   - Performance considerations
   - **→ Understand how it's built**

4. **[DIAGRAMS.md](DIAGRAMS.md)** 📊 (Visual)
   - Data flow diagrams (Mermaid)
   - Component architecture
   - Security layers
   - Caching strategy
   - **→ See it visually**

---

## 📖 Integration & Setup

5. **[INSTALLATION.md](INSTALLATION.md)** 🚀 (Detailed)
   - Step-by-step integration
   - Django settings
   - DRF configuration
   - Cache setup
   - Troubleshooting
   - Adding new indicators
   - **→ Integrate properly**

6. **[EXAMPLES.py](EXAMPLES.py)** 💡 (Real Code)
   - Django views
   - Streamlit app
   - Python client
   - JavaScript client
   - Management commands
   - WebSocket consumer
   - **→ Copy & paste patterns**

---

## 🐍 Python Modules

### Core Engine
- **[semantic_model.py](semantic_model.py)** 🧠
  - `IndicatorSchema` - Defines what's possible
  - `IndicatorRegistry` - Central catalog
  - Schema definitions (PIB, POPULACAO)
  - Filter/Aggregation/GroupBy definitions

- **[query_engine.py](query_engine.py)** ⚙️
  - `QueryValidator` - Validates parameters
  - `QueryBuilder` - Builds ORM queries
  - `IndicatorQueryEngine` - Main orchestrator
  - Error handling

- **[query_cache.py](query_cache.py)** ⚡
  - `QueryCache` - Result caching
  - `MetadataCache` - Schema caching
  - TTL management
  - Invalidation strategy

- **[api_views.py](api_views.py)** 🌐
  - `IndicatorSchemaView` - List/detail schemas
  - `IndicatorQueryView` - Execute queries
  - `QueryValidateView` - Validate without executing
  - `CacheClearView` - Cache control

### Integration
- **[urls.py](urls.py)** 🔗
  - URL routing for all endpoints
  - API paths
  - View registration

- **[__init__.py](__init__.py)** 📦
  - Package initialization
  - Exports
  - Setup function

### Testing
- **[tests.py](tests.py)** ✅
  - QueryValidatorTests
  - QueryEngineTests
  - QueryAPITests
  - 30+ test cases
  - Data setup utilities

---

## 📍 API Endpoints

### Available Endpoints

```
GET /api/indicators/schemas
├─ List all indicator schemas

GET /api/indicators/schemas/<code>
├─ Get specific indicator schema

GET /api/indicators/query
├─ Execute dynamic query (main endpoint)
├─ Params: indicator, group_by, agg, filter_*, limit, offset, order_by

GET /api/indicators/query/validate
├─ Validate query parameters (no execution)

POST /api/indicators/cache/clear
├─ Clear cache (admin only)
```

---

## 🗂️ File Organization

```
ibge/query_engine/
├── 📘 QUICKSTART.md          ← START HERE (5 min)
├── 📙 README.md              ← Main guide (15 min)
├── 📕 ARCHITECTURE.md        ← Deep dive (30 min)
├── 📊 DIAGRAMS.md           ← Visual architecture
├── 📗 INSTALLATION.md        ← Integration steps
├── 📓 EXAMPLES.py            ← Real code examples
├── 📋 INDEX.md               ← This file
│
├── 🐍 Core Code
│   ├── semantic_model.py     ← What's possible
│   ├── query_engine.py       ← Main engine
│   ├── query_cache.py        ← Caching
│   ├── api_views.py          ← REST endpoints
│   ├── urls.py               ← URL routing
│   ├── __init__.py           ← Package init
│   └── tests.py              ← Test suite
│
├── 📄 Models (Django)
│   └── In ibge/models/
│       ├── territorio.py     ← Estado, Municipio
│       └── sidra_indicadores.py ← Indicador, IndicadorMunicipio
```

---

## 🚀 Typical Workflows

### 1. Add New Indicator
```
1. Edit semantic_model.py
2. Create IndicatorSchema
3. Register in init_indicator_registry()
4. Restart Django
5. Automatically works in API
```
→ See: [INSTALLATION.md - Adding New Indicators](INSTALLATION.md#adding-new-indicators)

### 2. Query Data (Python)
```python
from ibge.query_engine import IndicatorQueryEngine

engine = IndicatorQueryEngine()
results, metadata = engine.query(
    indicator="PIB",
    group_by="estado",
    filters={"ano": 2023},
)
```
→ See: [EXAMPLES.py - Python Client](EXAMPLES.py)

### 3. Query Data (REST)
```bash
curl "http://localhost:8000/api/indicators/query?
  indicator=PIB&group_by=estado&filter_ano=2023&agg=sum"
```
→ See: [ARCHITECTURE.md - Query Examples](ARCHITECTURE.md)

### 4. Use in Streamlit
```python
import requests
resp = requests.get(
    "http://localhost:8000/api/indicators/query",
    params={...}
)
data = resp.json()["data"]
st.dataframe(data)
```
→ See: [EXAMPLES.py - Streamlit](EXAMPLES.py)

---

## 🔍 Key Concepts

### Semantic Model
"Rules about what's possible"
- Which fields can group by
- Which fields can filter
- Which aggregations are allowed
- **See:** `semantic_model.py`

### Query Engine
"Orchestrator that makes queries happen"
- Validates parameters
- Builds ORM queries
- Executes & formats results
- **See:** `query_engine.py`

### Query Builder
"Converts parameters to Django ORM"
- Maps semantic names to DB fields
- Applies filters
- Creates aggregations
- **See:** `query_engine.py` (QueryBuilder class)

### Cache Layer
"Smart result caching"
- Caches by query signature
- TTL per indicator type
- Automatic invalidation
- **See:** `query_cache.py`

### Validator
"Ensures safety"
- Type checking
- Whitelist enforcement
- Limit enforcement
- **See:** `query_engine.py` (QueryValidator class)

---

## ⚙️ Configuration

### Django Settings
```python
# In core/settings.py

INSTALLED_APPS = [
    # ...
    'rest_framework',  # Required
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        # For production, use Redis
    }
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}
```

### URL Configuration
```python
# In core/urls.py

path('api/', include('ibge.query_engine.urls')),
```

---

## 🧪 Testing

### Run All Tests
```bash
python manage.py test ibge.query_engine.tests
```

### Run Specific Test
```bash
python manage.py test ibge.query_engine.tests.QueryEngineTests.test_simple_group_by_estado
```

### Coverage
```bash
coverage run --source='ibge.query_engine' manage.py test
coverage report
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| 404 on endpoints | Add URLs to core/urls.py |
| DRF import error | `pip install djangorestframework` |
| No indicators listed | Create data or check registry |
| Cache not working | Check CACHES settings |
| Slow queries | Check database indexes |
| 400 validation error | Check parameter names & types |

→ See: [INSTALLATION.md - Troubleshooting](INSTALLATION.md#troubleshooting)

---

## 📊 Performance Tips

1. **Database Indexes** - Already defined in models
2. **Query Caching** - Automatic with Redis
3. **Limit Results** - Max 10,000 rows
4. **Batch Queries** - Use limit/offset for pagination
5. **Monitor Slow Queries** - Use Django Debug Toolbar

→ See: [ARCHITECTURE.md - Performance](ARCHITECTURE.md#performance-considerations)

---

## 🔐 Security Checklist

- ✅ Parameterized queries (no SQL injection)
- ✅ Field whitelisting (only schema fields)
- ✅ Type validation (int/str/float coercion)
- ✅ Aggregation whitelist (only allowed functions)
- ✅ Result limits (max 10,000 rows)
- ✅ No direct SQL execution

→ See: [ARCHITECTURE.md - Security](ARCHITECTURE.md#security--validation)

---

## 🎯 Next Steps

### After Installation
1. ✅ Run QUICKSTART.md (5 min)
2. ✅ Read README.md (15 min)
3. ✅ Run tests: `python manage.py test ibge.query_engine.tests`
4. ✅ Test endpoints with curl/Postman

### For Development
1. Read ARCHITECTURE.md for deep understanding
2. Check EXAMPLES.py for integration patterns
3. Add your own indicators to semantic_model.py
4. Build your frontend (Streamlit/React/etc)

### For Production
1. Set up Redis caching
2. Configure authentication
3. Set up monitoring/logging
4. Load all indicators into registry
5. Document your custom indicators

---

## 🤝 Contributing

To add features:
1. Read ARCHITECTURE.md
2. Update semantic_model.py for new indicators
3. Add tests in tests.py
4. Update documentation

---

## 📞 Support

- **Quick question?** → Check QUICKSTART.md
- **How does it work?** → Check README.md
- **Technical details?** → Check ARCHITECTURE.md
- **Real code?** → Check EXAMPLES.py
- **Error?** → Check INSTALLATION.md Troubleshooting

---

## 📄 Document Versions

| File | Purpose | Time | Status |
|------|---------|------|--------|
| QUICKSTART.md | Get running fast | 5 min | ✅ |
| README.md | Understand system | 15 min | ✅ |
| ARCHITECTURE.md | Technical deep dive | 30 min | ✅ |
| DIAGRAMS.md | Visual guide | 10 min | ✅ |
| INSTALLATION.md | Integration guide | 20 min | ✅ |
| EXAMPLES.py | Code samples | - | ✅ |
| tests.py | Test suite | - | ✅ |
| Code | Python modules | - | ✅ |

---

**Last Updated:** 2026-06-18

**Status:** 🟢 Complete & Production-Ready

**Questions?** Start with QUICKSTART.md!
