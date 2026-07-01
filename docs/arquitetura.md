# Arquitetura do Projeto — Insight Brasil

## Objetivo

Coletar, armazenar e disponibilizar indicadores socioeconômicos do IBGE para análise territorial brasileira, com API REST e dashboard interativo.

## Fluxo Geral

```
IBGE/SIDRA (APIs públicas)
  ↓ clients/ (HTTP)
Transformers (normalização)
  ↓
Repositories (persistência idempotente)
  ↓
Banco SQLite (Star Schema)
  ↓
DashboardQuery (consultas agregadas)
  ↓
API REST (serializers + views)
  ↓
Dashboard Streamlit (gráficos)
```

## Diagrama de Camadas

```
┌──────────────────────────────────────────────────┐
│  Dashboard Streamlit (apps/streamlit/)           │
│  pages/ → api/client.py → HTTP                  │
├──────────────────────────────────────────────────┤
│  API REST (ibge/api/)                            │
│  views.py → query_engine.py → repositories/     │
├──────────────────────────────────────────────────┤
│  Query Engine (ibge/query_engine.py)             │
│  DashboardQuery: summary, ranking, time series   │
├──────────────────────────────────────────────────┤
│  Repositórios (ibge/repositories/)               │
│  IndicadorRepository, MunicipioRepository,       │
│  FatoIndicadorRepository                         │
├──────────────────────────────────────────────────┤
│  Star Schema (ibge/models/)                      │
│  Estado, Municipio, Indicador, Tempo,           │
│  FatoIndicador                                   │
├──────────────────────────────────────────────────┤
│  ETL Pipeline (ibge/data_ingestion/)             │
│  clients/ → transformers/ → services/ → repos   │
└──────────────────────────────────────────────────┘
```

## Star Schema

```
Estado 1 ──── N Municipio
Municipio 1 ─ N FatoIndicador
Indicador 1 ── N FatoIndicador
Tempo 1 ────── N FatoIndicador
```

`FatoIndicador` é a tabela fato central: valor de um indicador para um município em um período. Suporta granularidades anual, mensal e trimestral via dimensão `Tempo`.

## ETL Pipeline (`ibge/data_ingestion/`)

| Camada | Responsabilidade | Exemplo |
|--------|------------------|---------|
| clients/ | HTTP requests para APIs externas | IBGEClient, SidraClient |
| definitions/ | Catálogo de indicadores SIDRA | IndicadorSIDRA |
| transformers/ | Normalização de payloads externos | PopulationTransformer |
| repositories/ | Persistência upsert | IndicadorMunicipioRepository |
| services/ | Orquestração da coleta | IndicadorSyncService |
| resolvers/ | Factory (service → repositório) | IndicatorResolver |

## API REST (`ibge/api/`)

| Endpoint | Descrição |
|----------|-----------|
| `GET /ibge/api/v1/dashboard/resumo/` | BFF: todos os dados prontos (pop, PIB, região, ranking) |
| `GET /ibge/api/v1/painel/resumo/` | População, PIB, PIB per capita |
| `GET /ibge/api/v1/indicador/{codigo}/` | Lista municipios p/ qualquer indicador |
| `GET /ibge/api/v1/indicador/{codigo}/ranking/` | Ranking por estado |
| `GET /ibge/api/v1/indicador/{codigo}/serie/` | Série temporal anual |
| `GET /ibge/api/v1/populacao/` | (compatibilidade) |
| `GET /ibge/api/v1/pib/` | (compatibilidade) |
| `GET /ibge/api/v1/pib-per-capita/` | (compatibilidade) |
| `GET /ibge/api/v1/estados/` | Lista de estados |
| `GET /ibge/api/v1/estados/{sigla}/` | Detalhe do estado |
| `GET /ibge/api/v1/municipios/{codigo}/` | Detalhe do município |
| `GET /swagger/` | Documentação interativa |
| `GET /redoc/` | Documentação ReDoc |

Filtros em indicadores: `ano`, `estado`, `municipio`, `limit`, `order_by=valor`.

## Dashboard (`apps/streamlit/`)

```
pages/        → Páginas do Streamlit (home.py, estados.py)
components/   → Gráficos (Plotly) e cards (st.metric)
api/          → Cliente HTTP com logging e timeouts
```

O dashboard consome o endpoint BFF (`/dashboard/resumo/`) — zero lógica de negócio no frontend.

- `home.py`: Resumo nacional, ranking de estados, população por região
- `estados.py`: Detalhes por estado com indicadores e séries

## Decisões Técnicas

- **drf-spectacular**: Geração automática de schema OpenAPI 3 — Swagger e ReDoc sem manutenção manual
- **ViewSet único parametrizado**: `IndicadorViewSet` recebe o código do indicador via URL (`/indicador/{codigo}/`) — novo indicador = só cadastrar no banco
- **BFF endpoint**: `GET /dashboard/resumo/` entrega dados prontos para o dashboard — frontend vira só camada de apresentação
- **Batch loading**: `_get_indicator_list` carrega todos os `FatoIndicador` em 1 query (dict) em vez de N+1
- **Dados derivados**: `PIB_PER_CAPITA` é calculado e armazenado como `FatoIndicador`, não computado em tempo real
- **Idempotência**: Repositórios usam `update_or_create` — re-executar sync não duplica dados

## Pendências / Próximos Passos

- Migrar SQLite → PostgreSQL
- Ampliar cobertura de testes unitários
- Adicionar cache Redis para consultas frequentes
- Expandir catálogo de indicadores (educação, saúde)
- Autenticação e autorização na API
- Deploy em produção (Docker, CI/CD)
