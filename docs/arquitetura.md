# Arquitetura do Projeto Insights Brasil

## Objetivo

O projeto Insights Brasil tem como objetivo coletar dados públicos do IBGE, armazená-los em banco de dados e disponibilizá-los através de APIs e dashboards interativos.

---

## Fluxo Geral

```text
IBGE

↓

Commands de Coleta

↓

Banco de Dados

↓

Services

↓

Views REST

↓

Streamlit
```

---

## Commands

Os commands são responsáveis pela coleta e persistência dos dados.

Exemplos:

* sync_estados
* sync_municipios
* sync_populacao

Responsabilidades:

* Consultar a API do IBGE;
* Validar os dados;
* Persistir no banco;
* Atualizar registros existentes;
* Registrar logs de execução.

Exemplo:

```bash
python manage.py sync_estados

python manage.py sync_municipios

python manage.py sync_populacao
```

---

## Banco de Dados

O banco armazena os dados históricos.

Principais tabelas:

### Estado

* codigo_externo
* nome
* sigla
* regiao

### Municipio

* codigo_externo
* nome
* estado

### PopulacaoMunicipio

* municipio
* ano
* populacao

Essa estrutura permite análises históricas e comparações entre períodos.

---

## Services

Os services contêm as regras de negócio.

Exemplos:

* estado_service
* municipio_service
* ranking_service
* ano_service

Responsabilidades:

* Consultar dados do banco;
* Realizar agregações;
* Criar rankings;
* Definir regras de negócio;
* Preparar dados para as views.

---

## Views

As views expõem os dados em formato JSON.

Exemplos:

* /api/ibge/estados/
* /api/ibge/municipios/
* /api/ibge/anos/
* /api/ibge/ranking/estados/

As views não acessam diretamente o IBGE.

Toda informação deve vir do banco através dos services.

---

## Streamlit

O Streamlit é responsável apenas pela visualização.

Fluxo:

```text
Usuário

↓

Streamlit

↓

API Django

↓

JSON

↓

DataFrame

↓

Gráfico
```

O Streamlit não acessa diretamente:

* Banco de dados;
* API do IBGE;
* Models do Django.

Ele apenas consome a API REST.

---

## Estrutura de Pastas

```text
insights_brasil

ibge

├── management
│   └── commands
│
├── models
│
├── services
│
├── views
│
├── urls
│
└── tests

apps

└── streamlit
    ├── streamlit_app.py
    └── charts
```

---

## Próximos Passos

* Indicadores de crescimento populacional;
* Ranking de crescimento por estado;
* Evolução ano a ano por município;
* Cache para consultas frequentes;
* Pré-cálculo de indicadores;
* Projeções populacionais futuras;
* Dashboard interativo com múltiplos gráficos.
