# Insight Brasil

Plataforma de BI para indicadores socioeconômicos brasileiros. Coleta dados do IBGE/SIDRA, disponibiliza via API REST e exibe em dashboard interativo Streamlit.

## Stack

| Camada | Tecnologia |
|--------|------------|
| Backend | Django 6.0 + DRF 3.15 |
| Banco | PostgreSQL 17 |
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

## Subir a stack com Docker

- Docker com Compose

```bash
cp .env.example .env
docker compose up --build
```

Na primeira inicialização, o backend aguarda o PostgreSQL, executa as migrations e
coleta os arquivos estáticos automaticamente. Os dados ficam persistidos no volume
`postgres_data`.

Serviços:

- API/Swagger: `http://localhost:8000/swagger/`
- Healthcheck (inclui banco): `http://localhost:8000/health/`
- Dashboard: `http://localhost:8501`
- PostgreSQL: `localhost:5432`

Comandos úteis:

```bash
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py sync_estados
docker compose logs -f backend
docker compose down
# Remove também os dados locais (operação destrutiva):
docker compose down -v
```

As credenciais locais vêm do `.env`. Troque `POSTGRES_PASSWORD` e
`DJANGO_SECRET_KEY` fora do ambiente de desenvolvimento.

## Desenvolvimento sem Docker para a aplicação

Mantenha apenas o banco no Docker e rode Django/Streamlit no host:

```bash
cp .env.example .env
docker compose up -d database
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements/production.txt -r backend/requirements/development.txt
python backend/manage.py migrate
python backend/manage.py runserver
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
├── backend/config/        Configuração e composição Django
├── backend/apps/ibge/     Domínio IBGE
│   ├── models/            Star Schema: Estado, Municipio, Indicador, Tempo, FatoIndicador
│   ├── api/               REST endpoints (views, serializers, urls)
│   ├── data_ingestion/    ETL pipeline (clients, transformers, services, resolvers)
│   ├── repositories/      Abstração de persistência
│   ├── management/commands/  sync_estados, sync_indicator, sync_municipios
│   ├── query_engine.py    Consultas agregadas (DashboardQuery)
│   └── tests/             17 testes
├── frontend/              Dashboard interativo
│   ├── api/client.py      Transporte HTTP
│   ├── components/        Gráficos e cards
│   └── pages/             home.py, estados.py
├── docker-compose.yml     PostgreSQL, API e dashboard
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
