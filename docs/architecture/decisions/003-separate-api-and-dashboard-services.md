# ADR-003: Separar API Django e dashboard Streamlit em serviços distintos

## Status

Aceita.

## Contexto

O projeto Insights Brasil possui duas responsabilidades principais:

1. API backend em Django/Django REST Framework.
2. Dashboard em Streamlit para visualização dos dados.

Inicialmente, durante o desenvolvimento local, é comum executar tudo no mesmo ambiente e acessar diretamente serviços locais. Porém, em produção, misturar responsabilidades aumenta o acoplamento, dificulta deploys independentes e pode expor credenciais desnecessárias.

O backend é responsável por regras de negócio, acesso ao PostgreSQL, migrations, admin, documentação da API e endpoints REST.

O dashboard deve consumir a API via HTTP/JSON, sem conhecer credenciais do banco.

## Decisão

Implantar a API Django e o dashboard Streamlit como **serviços separados**.

Arquitetura adotada:

```text
Usuário
   │
   ▼
Dashboard Streamlit
   │
   │ HTTP / JSON
   ▼
Django REST API
   │
   ▼
Supabase PostgreSQL
```

A API expõe endpoints como:

```text
https://insights-brasil-api.onrender.com/ibge/api/v1/
```

O dashboard lê a URL da API por variável de ambiente, por exemplo:

```env
INSIGHTS_API_BASE_URL=https://insights-brasil-api.onrender.com/ibge/api/v1
```

ou outra variável equivalente definida no código do dashboard.

## Consequências positivas

- O dashboard não precisa de credenciais do PostgreSQL.
- O backend centraliza o acesso ao banco e as regras de negócio.
- API e dashboard podem ter deploys independentes.
- A interface pode evoluir sem alterar diretamente a camada de dados.
- A API pode ser consumida por outros clientes no futuro.
- O modelo fica mais próximo de uma arquitetura full-stack real.

## Consequências negativas e trade-offs

- Há mais de um serviço para configurar e monitorar.
- O dashboard depende da disponibilidade da API.
- Chamadas HTTP adicionam latência em relação ao acesso direto ao banco.
- É necessário configurar variáveis de ambiente separadas para API e dashboard.
- Pode ser necessário tratar timeouts, erros de rede e respostas vazias no Streamlit.

## Alternativas consideradas

### Streamlit acessando diretamente o banco

Seria simples no começo, mas exporia credenciais do banco ao serviço de frontend e duplicaria lógica de acesso a dados.

### Django servindo também o dashboard

Reduziria o número de serviços, mas limitaria a flexibilidade do Streamlit e misturaria responsabilidades.

### Monolito único com API e Streamlit no mesmo processo

Facilitaria o deploy inicial, mas criaria acoplamento operacional e dificultaria manutenção futura.

## Resultado

A separação entre API e dashboard estabelece um fluxo mais limpo:

```text
Django REST API
    └── dados, regras, banco, admin, schema

Streamlit Dashboard
    └── visualização, filtros, gráficos, UX
```

Essa decisão ajuda o projeto a evoluir com fronteiras mais claras entre backend e frontend.
