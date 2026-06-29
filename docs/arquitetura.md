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
│  pages/ → services/ → api/client.py → HTTP      │
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
| `GET /ibge/api/v1/painel/resumo/` | População, PIB, PIB per capita |
| `GET /ibge/api/v1/populacao/` | Lista de municípios com população |
| `GET /ibge/api/v1/populacao/ranking/` | Ranking por estado |
| `GET /ibge/api/v1/populacao/serie/` | Série temporal anual |
| `GET /ibge/api/v1/pib/` | (idem) |
| `GET /ibge/api/v1/pib_per_capita/` | (idem) |
| `GET /ibge/api/v1/estados/` | Lista de estados |
| `GET /ibge/api/v1/estados/{sigla}/` | Detalhe do estado |
| `GET /ibge/api/v1/municipios/{codigo}/` | Detalhe do município |
| `GET /swagger/` | Documentação interativa |
| `GET /redoc/` | Documentação ReDoc |

Todos os endpoints de indicador aceitam filtros: `ano`, `estado`, `municipio`, `limit`, `order_by=valor`.

## Dashboard (`apps/streamlit/`)

```
pages/        → Páginas do Streamlit (home.py, estados.py)
services/     → Transformação de dados entre API e UI
components/   → Gráficos (Plotly) e cards (st.metric)
utils/        → Formatação BRL, agregação geográfica
api/          → Cliente HTTP com logging e timeouts
```

- `home.py`: Resumo nacional, ranking de estados, população por região
- `estados.py`: Detalhes por estado com indicadores e séries

## Decisões Técnicas

- **drf-spectacular**: Geração automática de schema OpenAPI 3 — Swagger e ReDoc sem manutenção manual
- **ViewSets genéricos**: `IndicadorViewSet` com subclasses (`PopulacaoViewSet`, `PIBViewSet`) — novo indicador = nova subclasse
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
