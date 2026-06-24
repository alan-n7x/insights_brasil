Seu schema está muito bom para começar a explorar dados com o ORM. O modelo principal parece ser um esquema estrela simples:

* `Municipio`
* `Estado`
* `Indicador` (POPULACAO, PIB, PIB_PER_CAPITA)
* `Tempo`
* `FatoIndicador` (a tabela fato)

Relacionamento:

```text
Estado 1 ---- N Municipio
Municipio 1 -- N FatoIndicador
Indicador 1 -- N FatoIndicador
Tempo 1 ----- N FatoIndicador
```

## Entrando no shell

```bash
python manage.py shell
```

ou melhor:

```bash
python manage.py shell_plus
```

(se usar django-extensions)

---

## Explorar os dados

### Quantidade de municípios

```python
from ibge.models import Municipio

Municipio.objects.count()
```

### Listar municípios

```python
Municipio.objects.all()[:10]
```

### Buscar Mauá

```python
Municipio.objects.get(nome="Mauá")
```

---

## Ver os indicadores existentes

```python
from ibge.models import Indicador

Indicador.objects.all().values("id", "codigo", "nome")
```

Pelo schema encontrei:

```text
POPULACAO
PIB
PIB_PER_CAPITA
```

---

## Ranking de população

### Descobrir o indicador população

```python
from ibge.models import Indicador

pop = Indicador.objects.get(codigo="POPULACAO")
```

### Top 10 municípios mais populosos

```python
from ibge.models import FatoIndicador

ranking = (
    FatoIndicador.objects
    .filter(indicador=pop)
    .select_related(
        "municipio",
        "municipio__estado",
        "tempo"
    )
    .order_by("-valor")[:10]
)

for item in ranking:
    print(
        item.municipio.nome,
        item.municipio.estado.sigla,
        item.valor
    )
```

---

## Ranking de população de um ano específico

```python
ranking = (
    FatoIndicador.objects
    .filter(
        indicador__codigo="POPULACAO",
        tempo__ano=2024
    )
    .select_related("municipio")
    .order_by("-valor")[:10]
)
```

---

## Top 10 PIB

```python
ranking = (
    FatoIndicador.objects
    .filter(indicador__codigo="PIB")
    .select_related("municipio")
    .order_by("-valor")[:10]
)
```

---

## Top 10 PIB per capita

```python
ranking = (
    FatoIndicador.objects
    .filter(indicador__codigo="PIB_PER_CAPITA")
    .select_related("municipio")
    .order_by("-valor")[:10]
)
```

---

## Ranking dentro de um estado

Exemplo São Paulo:

```python
ranking = (
    FatoIndicador.objects
    .filter(
        indicador__codigo="POPULACAO",
        municipio__estado__sigla="SP"
    )
    .select_related(
        "municipio",
        "municipio__estado"
    )
    .order_by("-valor")[:20]
)
```

---

## Agregação por estado

População total por estado:

```python
from django.db.models import Sum

ranking_estados = (
    FatoIndicador.objects
    .filter(indicador__codigo="POPULACAO")
    .values(
        "municipio__estado__nome",
        "municipio__estado__sigla"
    )
    .annotate(pop_total=Sum("valor"))
    .order_by("-pop_total")
)
```

---

## Consulta estilo SQL usando ORM

SQL:

```sql
SELECT m.nome, e.sigla, f.valor
FROM ibge_fatoindicador f
JOIN ibge_municipio m ON f.municipio_id = m.id
JOIN ibge_estado e ON m.estado_id = e.id
JOIN ibge_indicador i ON f.indicador_id = i.id
WHERE i.codigo = 'POPULACAO'
ORDER BY f.valor DESC
LIMIT 10;
```

ORM:

```python
FatoIndicador.objects.filter(
    indicador__codigo="POPULACAO"
).select_related(
    "municipio",
    "municipio__estado"
).order_by("-valor")[:10]
```

---

Uma próxima evolução interessante seria criar um serviço:

```python
class RankingService:
    @staticmethod
    def municipios_por_indicador(codigo, ano=None, limite=10):
        qs = (
            FatoIndicador.objects
            .filter(indicador__codigo=codigo)
            .select_related(
                "municipio",
                "municipio__estado"
            )
        )

        if ano:
            qs = qs.filter(tempo__ano=ano)

        return qs.order_by("-valor")[:limite]
```

Assim você já começa a separar a lógica de consulta do resto da aplicação. Isso fica bem profissional para um projeto de dados do IBGE.
