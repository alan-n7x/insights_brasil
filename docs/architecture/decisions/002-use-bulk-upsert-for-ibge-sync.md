# ADR-002: Usar bulk upsert para sincronização de dados do IBGE

## Status

Aceita.

## Contexto

O projeto sincroniza dados do IBGE, incluindo estados, municípios, indicadores, dimensões de tempo e fatos por município/ano/indicador.

Na primeira implementação, parte da sincronização usava métodos como `update_or_create()` dentro de loops. Essa abordagem é simples e legível, mas gera muitas consultas ao banco quando executada para milhares de registros.

Com o banco local, o impacto era menor. Com PostgreSQL remoto no Supabase, a latência de rede tornou o problema evidente: cada registro podia gerar ao menos um `SELECT` e um `INSERT` ou `UPDATE`, resultando em milhares de idas e voltas entre aplicação e banco.

Exemplo do problema:

```python
for municipio in municipios:
    Municipio.objects.update_or_create(
        ibge_id=municipio["ibge_id"],
        defaults={...},
    )
```

Para aproximadamente 5.570 municípios, isso pode gerar milhares de queries. Para indicadores e fatos, o volume cresce ainda mais.

## Decisão

Usar persistência em lote com `bulk_create`, `bulk_update` e, quando aplicável em PostgreSQL, `bulk_create(update_conflicts=True)` para executar UPSERT em lote.

A estratégia adotada é:

1. Buscar dados externos antes de abrir transação.
2. Transformar os dados em memória.
3. Carregar entidades relacionadas em lote.
4. Criar dicionários em memória para acesso O(1), como municípios por código IBGE.
5. Deduplicar registros antes de persistir.
6. Persistir em lotes, com `batch_size` controlado.
7. Usar `transaction.atomic()` apenas na etapa de gravação no banco.

Exemplo conceitual:

```python
Municipio.objects.bulk_create(
    municipios,
    batch_size=500,
    update_conflicts=True,
    unique_fields=["ibge_id"],
    update_fields=[
        "nome",
        "estado",
        "microrregiao_id",
        "microrregiao_nome",
        "mesorregiao_id",
        "mesorregiao_nome",
        "regiao_imediata_id",
        "regiao_imediata_nome",
        "regiao_intermediaria_id",
        "regiao_intermediaria_nome",
        "regiao",
        "atualizado_em",
    ],
)
```

## Consequências positivas

- Reduz drasticamente a quantidade de queries.
- Diminui a latência total da sincronização contra banco remoto.
- Mantém a sincronização idempotente quando há constraints únicas adequadas.
- Permite sincronizar milhares de registros sem depender de uma operação individual por item.
- Melhora a viabilidade de rodar cargas maiores de indicadores e fatos.
- Ajuda a separar claramente transformação de dados e persistência.

## Consequências negativas e trade-offs

- O código fica mais complexo que `update_or_create()`.
- Operações bulk não chamam `save()` individualmente.
- Signals como `pre_save` e `post_save` não são executados por registro em operações bulk.
- `auto_now=True` pode precisar ser tratado manualmente em campos como `atualizado_em`.
- `bulk_create(update_conflicts=True)` não informa diretamente quantos registros foram criados e quantos foram atualizados.
- É necessário garantir constraints únicas compatíveis com `unique_fields`.

## Alternativas consideradas

### Manter `update_or_create()`

Foi a solução mais simples no início, mas se tornou lenta com banco remoto e milhares de registros.

### Fazer `SELECT` e `save()` manualmente por item

Não resolve o problema principal, pois continua gerando consultas individuais.

### Usar SQL bruto com `INSERT ... ON CONFLICT`

Poderia ser mais explícito e performático em alguns cenários, mas aumentaria o acoplamento com PostgreSQL e reduziria a portabilidade do código Django.

### Usar fila ou worker assíncrono

Pode ser uma evolução futura para cargas recorrentes, mas não elimina a necessidade de persistência eficiente em lote.

## Resultado

A sincronização passou a usar uma estratégia mais adequada para dados em volume: cache em memória, deduplicação, transações controladas e persistência em lote.

Essa decisão tornou o processo mais próximo de um fluxo real de ingestão de dados em produção.
