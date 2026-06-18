# 🏗️ Query Engine Architecture

## Overview

```
┌─────────────────────────────────────┐
│  Frontend (Streamlit / BI Tools)    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Query API View (DRF Generic)       │
│  GET /api/indicators/query          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Query Validator                    │
│  - Params validation                │
│  - Security rules                   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Query Engine                       │
│  - Semantic model lookup            │
│  - Build ORM query                  │
│  - Execute & format                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Cache Layer (Redis)                │
│  - Query result cache               │
│  - Metadata cache                   │
│  - Invalidation rules               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Django ORM                         │
│  - IndicadorMunicipio               │
│  - Municipio / Estado               │
└─────────────────────────────────────┘
```

---

## Core Components

### 1️⃣ Semantic Model (`IndicatorSchema`)
**Responsabilidade:** Define quais campos agregam, quais filtram, quais agrupam.

```python
{
  "PIB": {
    "name": "Produto Interno Bruto",
    "model": "IndicadorMunicipio",
    "value_field": "valor",
    "aggregations": ["sum", "avg", "min", "max"],
    "group_by_fields": [
      "municipio",
      "estado",
      "regiao",
      "mesorregiao"
    ],
    "filter_fields": [
      "estado",
      "municipio",
      "ano",
      "regiao"
    ],
    "time_field": "ano"
  }
}
```

### 2️⃣ Query Engine (`IndicatorQueryEngine`)
**Responsabilidade:** 
- Validar parâmetros
- Construir query ORM dinamicamente
- Aplicar filtros, agregações, ordenação
- Retornar dados formatados

### 3️⃣ Query Builder (`IndicatorQueryBuilder`)
**Responsabilidade:**
- Converter parâmetros de API em ORM QuerySet
- Aplicar filtros dinâmicos
- Construir agregações
- Aplicar ordenação e limites

### 4️⃣ Cache Layer (`QueryCache`)
**Responsabilidade:**
- Cache de resultados de queries
- Cache de metadados
- Invalidação inteligente por tags
- TTL configurável

### 5️⃣ API View (`IndicatorsQueryView`)
**Responsabilidade:**
- Receber requisição com parâmetros
- Chamar query engine
- Retornar resultado formatado

---

## Query Examples

### Example 1: Ranking Estados por PIB (2023)
```
GET /api/indicators/query?
  indicator=PIB
  &group_by=estado
  &year=2023
  &agg=sum
  &limit=10
  &order_by=-total

Response:
[
  {
    "estado": "São Paulo",
    "total": 2150000000.00,
    "rank": 1
  },
  {
    "estado": "Rio de Janeiro",
    "total": 980000000.00,
    "rank": 2
  },
  ...
]
```

### Example 2: Evolução Temporal (Série)
```
GET /api/indicators/query?
  indicator=POPULACAO
  &group_by=ano
  &filter_estado=SP
  &agg=sum

Response:
[
  {
    "ano": 2020,
    "total": 46000000.00
  },
  {
    "ano": 2021,
    "total": 46500000.00
  },
  ...
]
```

### Example 3: Comparação Múltiplos Indicadores
```
GET /api/indicators/query?
  indicator=PIB,POPULACAO
  &group_by=municipio
  &filter_estado=MG
  &year=2023

Response:
[
  {
    "municipio": "Belo Horizonte",
    "pib": 150000000.00,
    "populacao": 2500000
  },
  ...
]
```

### Example 4: Municípios com filtro + ranking
```
GET /api/indicators/query?
  indicator=SAUDE
  &group_by=municipio
  &filter_estado=RJ
  &filter_year_gte=2020
  &agg=avg
  &limit=20
  &order_by=-total

Response:
[
  {
    "municipio": "Rio de Janeiro",
    "total": 850.50,
    "rank": 1
  },
  ...
]
```

---

## Security & Validation

### ✅ Allowed Operations
- Filtros: `estado`, `municipio`, `ano`, `regiao`, `mesorregiao`
- Group by: `estado`, `municipio`, `ano`, `regiao`, `mesorregiao`, `indicador`
- Agregações: `sum`, `avg`, `count`, `min`, `max`
- Ordenação: `asc`, `desc` por qualquer campo retornado

### ❌ Forbidden
- SQL injection (parametrized queries)
- Unlimited results (sempre com limit)
- Aggregações não permitidas para o indicador
- Group by em campos não cadastrados

---

## Caching Strategy

```
Query Cache Key: 
  {indicator}:{group_by}:{filters}:{agg}:{order_by}

TTL:
  - Metadata: 24 horas
  - Results: 1 hora
  - Rankings: 4 horas

Invalidation Tags:
  - indicator:PIB
  - ano:2023
  - estado:SP
  - municipio:*
```

---

## Data Flow Example

**Request:**
```
GET /api/indicators/query?
  indicator=PIB
  &group_by=estado
  &year=2023
  &agg=sum
  &limit=5
```

**Steps:**

1. **Validator** ✓
   - Indicador PIB existe?
   - group_by=estado é válido para PIB?
   - agg=sum é permitido?

2. **Query Engine**
   - Busca schema de PIB
   - Monta ORM query
   - Aplica filtros (year=2023)
   - Agrupa por estado
   - Sum de valor
   - Limita a 5

3. **Cache Check**
   - Cache hit? Retorna
   - Cache miss? Continua

4. **Query Builder**
   ```python
   qs = IndicadorMunicipio.objects
     .filter(indicador__codigo='PIB', ano=2023)
     .values('municipio__estado__nome')
     .annotate(total=Sum('valor'))
     .order_by('-total')[:5]
   ```

5. **Response**
   ```json
   [
     {"estado": "SP", "total": 2150000000.00},
     {"estado": "RJ", "total": 980000000.00},
     ...
   ]
   ```

---

## API Endpoints Gerados Automaticamente

| Endpoint | Purpose |
|----------|---------|
| `GET /api/indicators/schemas` | Lista todos os schemas disponíveis |
| `GET /api/indicators/schemas/<code>` | Detalhes de um indicador |
| `GET /api/indicators/query` | Query dinâmica (o motor) |
| `GET /api/indicators/query/validate` | Valida parâmetros sem executar |
| `GET /api/indicators/cache/clear` | Limpa cache (admin only) |

---

## Performance Considerations

1. **Indexes:**
   - `(indicador, ano)` ✓
   - `(municipio, indicador)` ✓
   - `(estado, ano)` (adicionar se necessário)

2. **Materialized Views (futuro):**
   - Agregações pré-computadas
   - Refresh diário

3. **Query Optimization:**
   - Prefetch related
   - Select related
   - Only relevant fields

---

## Extensões Futuras

1. **Multiple Indicators Query**
   - Jointure entre indicadores
   - Correlações

2. **Time Series Forecasting**
   - Predictar próximos anos
   - Tendências

3. **Export Formats**
   - CSV, Excel, Parquet
   - BigQuery direct export

4. **BI Tools Integration**
   - Metabase connector
   - Superset integration
   - Power BI direct query

5. **Advanced Analytics**
   - Percentile ranks
   - Growth rates
   - Anomaly detection
