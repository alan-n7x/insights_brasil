# Arquitetura do Projeto Insights Brasil

## Objetivo

O Insights Brasil coleta dados públicos do IBGE, persiste esses dados em banco
local e disponibiliza estruturas para análise de indicadores territoriais.

## Fluxo Geral

```text
IBGE/SIDRA
-> commands de coleta (ibge/management/commands/)
-> banco de dados (SQLite)
-> queries e services (ibge/repository/, ibge/service/, ibge/query_engine/)
-> API endpoints (ibge/views/ ou ibge/query_engine/api_views.py)
```

## Camadas

### Domínio IBGE

O app `ibge` concentra todo o domínio territorial, incluindo ingestão de dados.

Responsabilidades:

- Modelar estados, municípios e indicadores (Star Schema).
- Consultar APIs externas do IBGE/SIDRA (clients/).
- Transformar payloads externos para o formato interno (transformers/).
- Persistir registros com operações idempotentes (repositories/).
- Orquestrar coleta de dados (services/).
- Resolver dependências via Factory pattern (resolvers/).

Exemplos de comandos:

```bash
python manage.py sync_estados
python manage.py sync_indicator --indicator POPULACAO --inicio 2022
```

Os comandos antigos de indicadores, como `sync_populacao` e `sync_pib`, foram
removidos. O fluxo recomendado para indicadores é o command genérico
`sync_indicator`.

### Banco de Dados

As principais entidades são:

- `Estado`: unidade federativa.
- `Municipio`: município vinculado a um estado.
- `Indicador`: catálogo de indicadores, como `POPULACAO` ou `PIB`.
- `Tempo`: dimensão temporal com granularidades (anual, mensal, trimestral).
- `FatoIndicador`: tabela fato com valor de um indicador por município e tempo.

A tabela `FatoIndicador` é a base analítica do projeto. Ela permite
adicionar novos indicadores sem criar uma tabela específica para cada métrica.
Indicadores derivados, como `PIB_PER_CAPITA`, também são gravados nessa mesma
tabela.

### Consulta de Dados

Os dados podem ser consultados via:

- **Django Admin**: Interface web para visualizar e editar dados
- **Python Shell**: Usando models e repositories do Django
- **Jupyter Notebooks**: Localizados em `ibge/notebooks/`

### Consulta Analítica (Query Engine)

Recentemente, adicionamos uma camada de consulta analítica com busca semântica
e caching, localizada em `ibge/query_engine/`. Essa camada permite:

- Consultas em linguagem natural sobre indicadores territoriais.
- Uso de embeddings semânticos para entender intenções do usuário.
- Cache de resultados para melhorar performance em consultas repetidas.
- Integração com o modelo star schema existente.

A arquitetura da engine de consulta inclui:

- **Modelo Semântico**: Mapeia conceitos de negócio (como "PIB per capita")
  para entidades do modelo (Indicador, Município, Tempo).
- **Cache de Consultas**: Armazena resultados de consultas frequentes.
- **API de Consulta**: Endpoints para consumir as consultas analíticas.

### Serviços de API

Além da engine de consulta, oferecemos endpoints genéricos para indicadores
via REST em `ibge/views/` e `ibge/query_engine/api_views.py`. Esses endpoints
permitem:

- Listar indicadores disponíveis.
- Obter dados de indicadores por município e período.
- Executar consultas pré-definidas de agregação.

### Estrutura de Pastas

```text
insights_brasil/
  core/                 Configuração Django
  ibge/                 Domínio IBGE completo (ingestão incorporada)
    models/             Tempo, Estado, Municipio, Indicador, FatoIndicador
    clients/            Clientes HTTP (IBGEClient, SidraClient)
    repositories/       Repositórios de dados (persistência)
    services/           Services de negócio e sync
    transformers/       Transformadores de dados externos
    resolvers/          Factory pattern para services
    definitions/        Catálogo de indicadores SIDRA
    query_engine/       Arquitetura de consulta com busca semântica e caching
    views/              Endpoints de API REST para indicadores
    management/commands/ Commands Django (sync_estados, sync_indicator, etc.)
    tests/              Testes do app ibge
    notebooks/          Jupyter notebooks para exploração
  docs/                 Documentação técnica
  sql/                  Consultas SQL auxiliares
```

## Próximos Passos Técnicos

- Ampliar testes unitários para transformers, services e repositories.
- Ampliar o catálogo de indicadores disponíveis em definitions/.
- Melhorar a interface da API REST com documentação interativa (Swagger/OpenAPI).
- Expandir capacidades da engine de consulta (mais tipos de consultas, melhorias no NLP).
- Adicionar cache para consultas frequentes na engine de consulta.
- Pré-calcular agregações muito usadas para melhorar performance de dashboards.
- Implementar dashboard de visualização (Streamlit ou similar).
- Preparar configuração de produção com variáveis de ambiente.
- Migrar de SQLite para PostgreSQL para produção.