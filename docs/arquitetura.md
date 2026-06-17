# Arquitetura do Projeto Insights Brasil

## Objetivo

O Insights Brasil coleta dados públicos do IBGE, persiste esses dados em banco
local e os disponibiliza por meio de APIs e dashboards interativos.

## Fluxo Geral

```text
IBGE/SIDRA
-> commands de coleta
-> banco de dados
-> queries e services
-> views JSON
-> Streamlit
```

## Camadas

### Domínio IBGE

O app `ibge` concentra os modelos, consultas, views e URLs relacionados aos
dados territoriais e indicadores.

Responsabilidades:

- Modelar estados, municípios e indicadores.
- Expor endpoints JSON.
- Agregar dados para rankings e séries históricas.
- Manter as views sem dependência direta das APIs externas.

### Ingestão

O app `ingestion` concentra a coleta e normalização dos dados.

Responsabilidades:

- Consultar APIs externas do IBGE/SIDRA.
- Transformar payloads externos para o formato interno.
- Resolver dependências, como estado ou município existente.
- Persistir registros com operações idempotentes.
- Registrar logs de execução.

Exemplos de comandos:

```bash
python manage.py sync_estados
python manage.py sync_indicator --indicator POPULACAO --inicio 2022
```

Os comandos antigos de indicadores, como `sync_populacao` e `sync_pib`, ficam na
pasta `ingestion/management/commands/legacy/`. O fluxo recomendado para
indicadores é o command genérico `sync_indicator`.

### Banco de Dados

As principais entidades são:

- `Estado`: unidade federativa.
- `Municipio`: município vinculado a um estado.
- `Indicador`: catálogo de indicadores, como `POPULACAO` ou `PIB`.
- `IndicadorMunicipio`: tabela fato com valor de um indicador por município e ano.

A tabela `IndicadorMunicipio` é a base analítica do projeto. Ela permite
adicionar novos indicadores sem criar uma tabela específica para cada métrica.
Indicadores derivados, como `PIB_PER_CAPITA`, também são gravados nessa mesma
tabela para que os endpoints genéricos consigam consumi-los da mesma forma que
os indicadores vindos diretamente do SIDRA.

### API

As views expõem dados em JSON.

Endpoints principais:

```text
/api/ibge/estados/
/api/ibge/municipios/
/api/ibge/populacao/anos/
/api/ibge/populacao/ranking-estados/
/api/ibge/populacao/evolucao/
/api/ibge/indicadores/
/api/ibge/indicadores/<indicador>/anos/
/api/ibge/indicadores/<indicador>/ranking-estados/
/api/ibge/indicadores/<indicador>/ranking-municipios/
/api/ibge/indicadores/<indicador>/evolucao/
/api/ibge/indicadores/<indicador>/municipios/<municipio_ibge_id>/evolucao/
```

As views devem consultar dados já persistidos. Elas não devem chamar diretamente
as APIs externas do IBGE.

Os endpoints de `populacao` continuam existindo por compatibilidade, mas o fluxo
mais escalável para o dashboard é consumir os endpoints genéricos de
`indicadores`.

### Streamlit

O Streamlit é responsável pela visualização.

```text
Usuário
-> Streamlit
-> API Django
-> JSON
-> DataFrame
-> gráfico
```

O dashboard não deve acessar diretamente:

- Banco de dados.
- APIs externas do IBGE.
- Models do Django.

## Estrutura de Pastas

```text
insights_brasil/
  core/                 Configuração Django
  ibge/                 Domínio, models, queries, views e urls
  ingestion/            Coleta, transformação e persistência
  apps/streamlit/       Dashboard
  docs/                 Documentação técnica
  sql/                  Consultas auxiliares
```

## Próximos Passos Técnicos

- Ampliar testes unitários para transformers, services e queries.
- Criar endpoints genéricos para indicadores além de população.
- Adicionar cache para consultas frequentes.
- Pré-calcular agregações muito usadas.
- Melhorar filtros do dashboard Streamlit.
- Preparar configuração de produção com variáveis de ambiente.
