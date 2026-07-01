# Insight Brasil

Plataforma de BI para indicadores socioeconômicos brasileiros. Coleta dados do IBGE/SIDRA, disponibiliza via API REST e exibe em dashboard interativo Streamlit.

## Stack

| Camada | Tecnologia |
|--------|------------|
| Backend | Django 6.0 + DRF 3.15 |
| Banco | SQLite (dev) / PostgreSQL (prod) |
| API | REST com drf-spectacular (Swagger UI) |
| Dashboard | Streamlit + Plotly |
| ETL | Clients HTTP → Transformers → Services → Repositórios |

## Fluxo

```
IBGE/SIDRA (APIs públicas)
  ↓ comandos de ingestão (sync_estados, sync_indicator)
Banco de Dados (Star Schema)
  ↓ DashboardQuery / Repositórios
API REST (/ibge/api/v1/)
  ↓ requests HTTP
Dashboard Streamlit (/apps/streamlit/)
```

## Requisitos

- Python 3.12+
- Ambiente virtual Python

## Configuração Rápida

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
```

## Servidores

```bash
# Terminal 1 - API
python manage.py runserver

# Terminal 2 - Dashboard
streamlit run apps/streamlit/app.py
```

Endpoints:

- Admin: `http://127.0.0.1:8000/admin/`
- API: `http://127.0.0.1:8000/ibge/api/v1/`
- Swagger: `http://127.0.0.1:8000/swagger/`
- ReDoc: `http://127.0.0.1:8000/redoc/`
- Dashboard: `http://127.0.0.1:8501`

## API REST

### Painel de Resumo

`GET /ibge/api/v1/painel/resumo/`

Parâmetros: `ano`, `estado` (sigla), `municipio` (código IBGE)

Retorna `{ano, populacao, pib, pib_per_capita}`.

### Dashboard (BFF)

`GET /ibge/api/v1/dashboard/resumo/` — tudo pronto em 1 chamada:

```json
{
  "ano": 2021,
  "populacao_total": 213317639,
  "pib_total": 9000000000000,
  "pib_per_capita_medio": 42200,
  "populacao_por_regiao": [
    {"regiao": "Sudeste", "valor": 89632912}
  ],
  "ranking_estados": [
    {"posicao": 1, "estado": "SP", "valor": 46649132}
  ]
}
```

### Indicador Genérico

`GET /ibge/api/v1/indicador/{codigo}/` (lista municipios)

`GET /ibge/api/v1/indicador/{codigo}/ranking/` (ranking por estado)

`GET /ibge/api/v1/indicador/{codigo}/serie/` (série temporal)

Ex: `/indicador/POPULACAO/`, `/indicador/PIB/ranking/`, `/indicador/PIB_PER_CAPITA/serie/`

Parâmetros: `ano`, `estado`, `municipio`, `limit`, `order_by=valor`

Compatibilidade: URLs `/populacao/`, `/pib/`, `/pib-per-capita/` continuam funcionando.

## Ingestão de Dados

```bash
# Sincronizar estados
python manage.py sync_estados

# Sincronizar indicador
python manage.py sync_indicator --indicator POPULACAO --inicio 2010 --fim 2022

# PIB per capita (derivado) — requer PIB e POPULACAO primeiro
python manage.py sync_indicator --indicator PIB --inicio 2022
python manage.py sync_indicator --indicator POPULACAO --inicio 2022
python manage.py sync_indicator --indicator PIB_PER_CAPITA --inicio 2022
```

Indicadores disponíveis: todos em `ibge/data_ingestion/definitions/sidra_indicadores.py`.

## Estrutura do Projeto

```
insights_brasil/
├── core/                  Configuração Django
├── ibge/                  Domínio IBGE
│   ├── models/            Star Schema: Estado, Municipio, Indicador, Tempo, FatoIndicador
│   ├── api/               REST endpoints (views, serializers, urls)
│   ├── data_ingestion/    ETL pipeline (clients, transformers, services, resolvers)
│   ├── repositories/      Abstração de persistência
│   ├── management/commands/  sync_estados, sync_indicator, sync_municipios
│   ├── query_engine.py    Consultas agregadas (DashboardQuery)
│   └── tests/             17 testes
├── apps/streamlit/        Dashboard interativo
│   ├── api/client.py      Transporte HTTP
│   ├── components/        Gráficos e cards
│   └── pages/             home.py, estados.py
└── docs/                  Documentação técnica
```

## Modelagem (Star Schema)

- **Dimensões**: `Estado`, `Municipio`, `Indicador`, `Tempo`
- **Tabela Fato**: `FatoIndicador` (valor por município × indicador × tempo)

## Testes

```bash
python manage.py test ibge.tests
```

Determinísticos, sem dependência de API externa. Clientes HTTP testados com mocks.
