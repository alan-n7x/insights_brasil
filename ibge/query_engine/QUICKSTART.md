# ⚡ Quick Start - Integração em 5 Minutos

Guia rápido para integrar o Query Engine ao seu projeto.

---

## Passo 1: Instalar DRF (1 minuto)

```bash
pip install djangorestframework
```

---

## Passo 2: Atualizar settings.py (1 minuto)

Abra `core/settings.py` e:

1. Adicione `rest_framework` a `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # ← ADICIONE ISSO
    'ibge',
    # ... outras apps
]
```

2. (Opcional) Adicione configuração de cache:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

---

## Passo 3: Atualizar urls.py (1 minuto)

Abra `core/urls.py` e adicione:

```python
from django.contrib import admin
from django.urls import path, include  # ← Importe include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ibge.query_engine.urls')),  # ← ADICIONE ISSO
    # ... outras urls
]
```

---

## Passo 4: Teste! (1 minuto)

```bash
# Iniciar servidor
python manage.py runserver

# Em outro terminal, testar endpoint
curl "http://localhost:8000/api/indicators/schemas"
```

Você deve ver os indicadores registrados (PIB, POPULACAO).

---

## Passo 5: Adicionar Dados (1 minuto)

No shell Django:

```bash
python manage.py shell
```

```python
from ibge.models import Indicador, IndicadorMunicipio, Estado, Municipio
from decimal import Decimal

# Criar estado
sp = Estado.objects.create(
    ibge_id=3550308,
    nome="São Paulo",
    sigla="SP",
    regiao="Sudeste",
)

# Criar município
sao_paulo = Municipio.objects.create(
    ibge_id=3550308,
    nome="São Paulo",
    estado=sp,
)

# Criar indicador
pib = Indicador.objects.create(
    codigo="PIB",
    nome="Produto Interno Bruto",
)

# Adicionar dados
IndicadorMunicipio.objects.create(
    municipio=sao_paulo,
    indicador=pib,
    ano=2023,
    valor=Decimal("2150000000.00"),
)

print("✓ Dados criados!")
```

---

## 🎉 Pronto!

Agora você tem um motor de consultas funcional!

### Testar:

```bash
# List indicators
curl "http://localhost:8000/api/indicators/schemas"

# Query PIB
curl "http://localhost:8000/api/indicators/query?indicator=PIB&group_by=estado&filter_ano=2023&agg=sum"

# Validate query (sem executar)
curl "http://localhost:8000/api/indicators/query/validate?indicator=PIB&group_by=estado"
```

---

## 📚 Próximos Passos

1. **Adicionar mais indicadores** → edit `ibge/query_engine/semantic_model.py`
2. **Usar em Streamlit** → veja `EXAMPLES.py`
3. **Usar em Python** → veja `EXAMPLES.py`
4. **Usar em JavaScript** → veja `EXAMPLES.py`
5. **Rodar testes** → `python manage.py test ibge.query_engine.tests`

---

## ❓ Troubleshooting

### 404 no endpoint

```
Erro: Page not found (404)
```

✓ Verifique se `rest_framework` está em `INSTALLED_APPS`
✓ Verifique se as URLs foram adicionadas a `core/urls.py`
✓ Reinicie o servidor Django

### Indicadores não aparecem

```
Erro: []  (lista vazia)
```

✓ Crie dados no banco (veja Passo 5 acima)
✓ Indicadores devem estar em `semantic_model.py`

### Erro "Invalid aggregation"

```
Error: Invalid aggregation 'invalid'. Allowed: ...
```

✓ Use apenas: `sum`, `avg`, `min`, `max`, `count`

---

## 🚀 Funciona!

Se conseguiu chegar aqui, o motor de consultas está funcionando.

Agora integre em suas apps:

- **Streamlit**: veja `EXAMPLES.py`
- **React/Vue**: use JavaScript client
- **Pandas**: use Python client
- **Power BI**: configure data source customizado

---

## 💡 Conceito

O que você criou:

```
Antes:
  /api/ranking_estados
  /api/ranking_municipios
  /api/comparacao_estados
  /api/evolucao_temporal
  ... + 20 endpoints

Agora:
  /api/indicators/query?indicator=X&group_by=Y&agg=Z
  ... 1 endpoint que faz tudo
```

Isso é um **data engine**.

---

**Quer mais? Veja:**
- `README.md` - Documentação completa
- `ARCHITECTURE.md` - Arquitetura técnica
- `INSTALLATION.md` - Integração detalhada
- `EXAMPLES.py` - Exemplos práticos
