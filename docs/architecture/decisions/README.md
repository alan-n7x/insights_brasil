# Architecture Decision Records

Este diretório registra decisões técnicas relevantes do projeto **Insights Brasil**.

As decisões aqui documentadas seguem o formato ADR: contexto, decisão, consequências e alternativas consideradas. O objetivo é preservar o raciocínio técnico por trás da arquitetura, do deploy e das otimizações feitas no projeto.

## Decisões registradas

| ADR | Título | Status |
| --- | --- | --- |
| [ADR-001](./001-use-supabase-session-pooler.md) | Usar Supabase Session Pooler para conexão PostgreSQL em produção | Aceita |
| [ADR-002](./002-use-bulk-upsert-for-ibge-sync.md) | Usar bulk upsert para sincronização de dados do IBGE | Aceita |
| [ADR-003](./003-separate-api-and-dashboard-services.md) | Separar API Django e dashboard Streamlit em serviços distintos | Aceita |

## Como adicionar uma nova decisão

1. Crie um arquivo numerado no formato `NNN-titulo-curto.md`.
2. Registre o contexto do problema.
3. Descreva a decisão tomada.
4. Liste consequências positivas, negativas e trade-offs.
5. Atualize esta tabela.

## Template sugerido

```markdown
# ADR-XXX: Título da decisão

## Status

Proposta | Aceita | Substituída | Rejeitada

## Contexto

Qual problema levou à decisão?

## Decisão

O que foi decidido?

## Consequências

O que melhorou, o que piorou e quais trade-offs foram aceitos?

## Alternativas consideradas

Quais opções foram avaliadas e por que não foram escolhidas?
```
