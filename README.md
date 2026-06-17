# Insights Brasil

Projeto Django para coletar dados públicos do IBGE, armazenar em banco local e
disponibilizar APIs que podem ser consumidas por dashboards, como o app em
Streamlit incluído neste repositório.

## Visão Geral

O fluxo principal do projeto é:

```text
APIs do IBGE/SIDRA
-> comandos de ingestão Django
-> banco de dados
-> consultas e views JSON
-> dashboard Streamlit
```

Hoje o projeto está focado em dados territoriais e indicadores municipais,
especialmente população e PIB, com uma modelagem preparada para receber novos
indicadores.

## Requisitos

- Python 3.12 ou superior
- SQLite, usado por padrão no ambiente local
- Ambiente virtual Python

## Configuração

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Copie o arquivo de exemplo de ambiente:

```bash
copy .env.example .env
```

Edite o `.env` se necessário. Em desenvolvimento, os valores padrão já são
suficientes.

Execute as migrações:

```bash
python manage.py migrate
```

## Rodando a API Django

```bash
python manage.py runserver
```

A API ficará disponível em:

```text
http://127.0.0.1:8000/api/ibge/
```

## Comandos de Ingestão

Sincronizar estados:

```bash
python manage.py sync_estados
```

Sincronizar um indicador SIDRA:

```bash
python manage.py sync_indicator --indicator POPULACAO --inicio 2022
```

Com intervalo de anos:

```bash
python manage.py sync_indicator --indicator POPULACAO --inicio 2010 --fim 2022
```

Indicadores disponíveis no fluxo atual:

```text
POPULACAO
PIB
PIB_PER_CAPITA
```

Os comandos antigos de população e PIB ficam em `ingestion/management/commands/legacy/`
e não fazem parte do fluxo recomendado. Use `sync_indicator` para novas coletas de
indicadores.

O indicador `PIB_PER_CAPITA` é derivado. Ele depende de `PIB` e `POPULACAO` já
sincronizados para o mesmo município e ano:

```bash
python manage.py sync_indicator --indicator PIB --inicio 2022
python manage.py sync_indicator --indicator POPULACAO --inicio 2022
python manage.py sync_indicator --indicator PIB_PER_CAPITA --inicio 2022
```

## Endpoints Principais

Listar estados:

```text
GET /api/ibge/estados/
```

Listar municípios:

```text
GET /api/ibge/municipios/
```

Listar anos disponíveis para população:

```text
GET /api/ibge/populacao/anos/
```

Ranking populacional por estado:

```text
GET /api/ibge/populacao/ranking-estados/?ano=2022
```

Evolução populacional:

```text
GET /api/ibge/populacao/evolucao/
GET /api/ibge/populacao/evolucao/?estado_id=1
```

Endpoints genéricos de indicadores:

```text
GET /api/ibge/indicadores/
GET /api/ibge/indicadores/POPULACAO/anos/
GET /api/ibge/indicadores/POPULACAO/ranking-estados/?ano=2022
GET /api/ibge/indicadores/POPULACAO/ranking-municipios/?ano=2022
GET /api/ibge/indicadores/POPULACAO/ranking-municipios/?ano=2022&estado_id=1&limit=20
GET /api/ibge/indicadores/POPULACAO/evolucao/
GET /api/ibge/indicadores/POPULACAO/evolucao/?estado_id=1
GET /api/ibge/indicadores/POPULACAO/municipios/3550308/evolucao/
GET /api/ibge/indicadores/POPULACAO/municipios/3550308/evolucao/?ano_inicio=2010&ano_fim=2022
```

## Rodando o Dashboard Streamlit

Com o servidor Django rodando, execute:

```bash
streamlit run apps/streamlit/streamlit_app.py
```

O dashboard consome a API Django local. A URL base pode ser alterada pela
variável de ambiente `INSIGHTS_API_BASE_URL`.

## Testes

```bash
python manage.py test
```

Os testes devem ser determinísticos e não depender da API externa do IBGE.
Clientes HTTP devem ser testados com mocks.

## Estrutura

```text
core/                  Configuração Django
ibge/                  Modelos, queries, views e URLs do domínio IBGE
ingestion/             Clientes, transformers, services e commands de coleta
apps/streamlit/        Dashboard interativo
docs/                  Documentação técnica
sql/                   Consultas auxiliares
```
