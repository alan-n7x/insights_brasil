# Consultas de Exemplo — ORM Django

Guia rápido para explorar os dados no shell do Django.

```bash
python manage.py shell
```

## Schema

```
Estado 1 ──── N Municipio
Municipio 1 ─ N FatoIndicador
Indicador 1 ── N FatoIndicador
Tempo 1 ────── N FatoIndicador
```

## Explorar

```python
from ibge.models import Municipio, Indicador, FatoIndicador, Tempo

# Quantos municípios?
Municipio.objects.count()

# Buscar município
Municipio.objects.get(nome="Mauá")

# Indicadores disponíveis
Indicador.objects.all().values("id", "codigo", "nome")
```

## Rankings

```python
from django.db.models import Sum

pop = Indicador.objects.get(codigo="POPULACAO")

# Top 10 municípios mais populosos
ranking = (
    FatoIndicador.objects
    .filter(indicador=pop)
    .select_related("municipio__estado", "tempo")
    .order_by("-valor")[:10]
)

# Top 10 por ano específico
ranking_2024 = (
    FatoIndicador.objects
    .filter(indicador__codigo="POPULACAO", tempo__ano=2024)
    .select_related("municipio")
    .order_by("-valor")[:10]
)

# População total por estado
por_estado = (
    FatoIndicador.objects
    .filter(indicador__codigo="POPULACAO")
    .values("municipio__estado__nome", "municipio__estado__sigla")
    .annotate(pop_total=Sum("valor"))
    .order_by("-pop_total")
)

# Ranking dentro de SP
ranking_sp = (
    FatoIndicador.objects
    .filter(indicador__codigo="POPULACAO", municipio__estado__sigla="SP")
    .select_related("municipio")
    .order_by("-valor")[:20]
)
```

## Equivalente SQL

```sql
SELECT m.nome, e.sigla, f.valor
FROM ibge_fatoindicador f
JOIN ibge_municipio m ON f.municipio_id = m.id
JOIN ibge_estado e ON m.estado_id = e.id
WHERE f.indicador_id = (SELECT id FROM ibge_indicador WHERE codigo = 'POPULACAO')
ORDER BY f.valor DESC
LIMIT 10;
```

## Sugestão de Serviço

```python
class RankingService:
    @staticmethod
    def municipios_por_indicador(codigo, ano=None, limite=10):
        qs = (
            FatoIndicador.objects
            .filter(indicador__codigo=codigo)
            .select_related("municipio", "municipio__estado")
        )
        if ano:
            qs = qs.filter(tempo__ano=ano)
        return qs.order_by("-valor")[:limite]
```
