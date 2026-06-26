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

Indicadores disponíveis:

Todos os indicadores definidos em `ibge/data_ingestion/definitions/sidra_indicadores.py` são suportados pelo comando `sync_indicator`. Basta indicar o código do indicador (ex: `POPULACAO`, `PIB`, `PIB_PER_CAPITA` ou qualquer outro que você adicionar ao arquivo).

O indicador `PIB_PER_CAPITA` é derivado. Ele depende de `PIB` e `POPULACAO` já sincronizados para o mesmo município e ano:

```bash
python manage.py sync_indicator --indicator PIB --inicio 2022
python manage.py sync_indicator --indicator POPULACAO --inicio 2022
python manage.py sync_indicator --indicator PIB_PER_CAPITA --inicio 2022
```

Nota: Os comandos antigos de população e PIB foram removidos e não fazem parte do fluxo recomendado. Use `sync_indicator` para novas coletas de indicadores.

## Consulta de Dados

Os dados podem ser consultados via:

- **Django Admin**: Interface web para visualizar e editar dados
- **Python Shell**: Usando models e repositories do Django
- **Jupyter Notebooks**: Localizados em `ibge/notebooks/`
- **API REST**: Endpoints genéricos para indicadores (ver acima)
- **API de KPIs**: Endpoint específico para cálculo e retorno de indicadores chave (KPIs)

### API de KPIs

Endpoint: `GET /ibge/api/v1/kpi/` (ou o caminho configurado no `urls.py`).

#### Parâmetros de query

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `indicadores` | `string` ou `list` | Código(s) do indicador. Aceita vírgula para múltiplos valores (ex: `indicadores=populacao,pib_per_capita`). Não diferencia maiúsculas/minúsculas. Se vazio ou não informado, padrão = `POPULACAO`. |
| `ano` | `integer` (opcional) | Ano para filtrar os fatos. Se omitido, considera **todos os anos** disponíveis. |

**Observações de formatação**

- `indicadores` pode ser passado como uma string separada por vírgulas **ou** como lista repetida (`?indicadores=populacao&indicadores=pib_per_capita`).
- Espaços em torno das vírgulas são ignorados.
- Os códigos são convertidos automaticamente para **MAIÚSCULOS** antes da consulta ao banco.

#### Formato da resposta

```json
{
  "<CÓDIGO_DO_INDICADOR>": {
    "valor": <número ou dicionário ou lista>,
    "nome": "<Nome do indicador>",
    "codigo": "<CÓDIGO DO INDICADOR>"
  },
  "_warnings": "Indicadores não encontrados: XXX, YYY"   // presente apenas se houver avisos
}
```

- **Indicadores do tipo AGGREGATED** (ex.: `POPULACAO`, `PIB`): 
  - Se o indicador **não** tiver agrupamento definido (`group_by`), `valor` → número (soma dos valores de todos os municípios para o ano solicitado, ou de todos os anos se `ano` não for informado).
  - Se o indicador **tiver** agrupamento (como o PIB, que agrupa por estado), `valor` → lista de objetos, cada objeto contendo o nome do grupo e o total agregado. Para o PIB, cada objeto tem `"nome"` (nome do estado) e `"total"` (PIB daquele estado). A lista já vem ordenada do maior para o menor PIB (conforme `order_by="-total"`).
- **Indicadores do tipo RAW** (ex.: `PIB_PER_CAPITA`): `valor` → dicionário onde a chave é o nome do município e o valor é o número correspondente. Se `ano` for informado, retorna `{municipio: valor}` para aquele ano; caso contrário, retorna `{municipio: {ano: valor, ...}}`.

#### Exemplos de uso

| Objetivo | Exemplo de URL | Comentário |
|----------|----------------|------------|
| População total (todos os anos) | `http://localhost:8000/ibge/api/v1/kpi/` | Usa o indicador padrão `POPULACAO` |
| População de 2021 | `http://localhost:8000/ibge/api/v1/kpi/?indicadores=populacao&ano=2021` | Soma da população de todos os municípios em 2021 |
| PIB per capita de 2021 | `http://localhost:8000/ibge/api/v1/kpi/?indicadores=pib_per_capita&ano=2021` | Retorna `{ "São Paulo": 5000.0, "Rio de Janeiro": 6000.0 }` |
| Múltiplos indicadores, ano específico | `http://localhost:8000/ibge/api/v1/kpi/?indicadores=populacao,pib_per_capita&ano=2021` | `POPULACAO` → soma de 2021; `PIB_PER_CAPITA` → dicionário por município (2021) |
| PIB por estado (ranking) | `http://localhost:8000/ibge/api/v1/kpi/?indicadores=pib&ano=2021` | Retorna lista ordenada de estados com seus PIBs totais (ex: `[{"nome":"São Paulo","total":...}, ...]`) |
| Indicador inexistente + indicador válido | `http://localhost:8000/ibge/api/v1/kpi/?indicadores=populacao,desconhecido&ano=2021` | Resposta contém `POPULACAO` (valor calculado) e `DESCONHECIDO` (valor `null`), além de `_warnings: "Indicadores não encontrados: DESCONHECIDO"` |
| String vazia nos indicadores (usa o padrão) | `http://localhost:8000/ibge/api/v1/kpi/?indicadores=` | Mesmo que `/ibge/api/v1/kpi/` – retorna `POPULACAO` (soma de todos) |
| Lista via repetição | `http://localhost:8000/ibge/api/v1/kpi/?indicadores=populacao&indicadores=pib` | Equivalente a `?indicadores=populacao,pib` |

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