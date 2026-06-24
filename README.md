# Insights Brasil

Projeto Django para coletar dados públicos do IBGE, armazenar em banco local e
analisar indicadores territoriais brasileiros.

## Visão Geral

O fluxo principal do projeto é:

```text
APIs do IBGE/SIDRA
-> comandos de ingestão Django (ibge/management/commands/)
-> banco de dados (SQLite)
-> consultas e services (ibge/repository/, ibge/service/, ibge/query_engine/)
-> API endpoints para consumo (ibge/views/ ou ibge/query_engine/api_views.py)
-> painéis analíticos (Streamlit ou similar)
```

Hoje o projeto está focado em dados territoriais e indicadores municipais,
especialmente população e PIB, com uma modelagem preparada para receber novos
indicadores. Recentemente, adicionamos uma camada de consulta com busca semântica
e caching para consultas analíticas flexíveis.

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

## Rodando o Projeto

```bash
python manage.py runserver
```

O painel de admin estará disponível em:

```text
http://127.0.0.1:8000/admin/
```

Endpoints de API genéricos para indicadores estão disponíveis em:

```text
http://127.0.0.1:8000/api/indicadores/
```

Documentação interativa (Swagger) disponível em DEBUG=True:
http://127.0.0.1:8000/swagger/

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

O indicador `PIB_PER_CAPITA` é derivado. Ele depende de `PIB` e `POPULACAO` já
sincronizados para o mesmo município e ano:

```bash
python manage.py sync_indicator --indicator PIB --inicio 2022
python manage.py sync_indicator --indicator POPULACAO --inicio 2022
python manage.py sync_indicator --indicator PIB_PER_CAPITA --inicio 2022
```

**Nota:** Os comandos antigos de população e PIB foram removidos e não fazem
parte do fluxo recomendado. Use `sync_indicator` para novas coletas de
indicadores.

## Consulta de Dados

Os dados podem ser consultados via:

- **Django Admin**: Interface web para visualizar e editar dados
- **Python Shell**: Usando models e repositories do Django
- **Jupyter Notebooks**: Localizados em `ibge/notebooks/`
- **API REST**: Endpoints genéricos para indicadores (ver acima)

Exemplo de consulta via Python shell:

```python
from ibge.models import Estado, Municipio, Indicador, FatoIndicador

# Listar estados
Estado.objects.all()

# Consultar população de um município
from ibge.models import Tempo
from ibge.repositories.indicador_municipio_repository import FatoIndicadorRepository

# Dados podem ser consultados via ORM Django ou repositories
```

## Consulta Analítica (Query Engine)

Para consultas analíticas avançadas com busca semântica e caching, use o
módulo de consulta:

```python
from ibge.query_engine.query_engine import IndicatorQueryEngine

engine = IndicatorQueryEngine()
results = engine.execute("Qual o PIB per capita de São Paulo em 2022?")
```

Veja mais em `ibge/query_engine/README.md`.

## Estrutura do Projeto

```text
core/                  Configuração Django
ibge/                  Domínio IBGE completo (ingestão incorporada)
  - models/            Tempo, Estado, Municipio, Indicador, FatoIndicador
  - clients/           Clientes HTTP (IBGEClient, SidraClient)
  - repositories/      Repositórios de dados (persistência)
  - services/          Services de negócio e sync
  - transformers/      Transformadores de dados externos
  - resolvers/         Factory pattern para services
  - definitions/       Catálogo de indicadores SIDRA
  - query_engine/      Arquitetura de consulta com busca semântica e caching
  - views/             Endpoints de API REST para indicadores
  - management/commands/  Commands Django (sync_estados, sync_indicator, etc.)
  - tests/             Testes do app ibge
  - notebooks/         Jupyter notebooks para exploração
docs/                  Documentação técnica
sql/                   Consultas SQL auxiliares
```

## Testes

```bash
python manage.py test
```

Os testes devem ser determinísticos e não depender da API externa do IBGE.
Clientes HTTP devem ser testados com mocks.

## Modelagem de Dados

O projeto usa um **Star Schema** para análise de indicadores territoriais:

- **Dimensões**: `Estado`, `Municipio`, `Indicador`, `Tempo`
- **Tabela Fato**: `FatoIndicador` (valores por município, indicador e tempo)

A dimensão `Tempo` permite granularidades diferentes (anual, mensal, trimestral).