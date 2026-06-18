# Visual Architecture Diagrams

All diagrams in Mermaid format.

---

## Complete Data Flow

```mermaid
sequenceDiagram
    participant Client as Client<br/>(Streamlit/JS/Python)
    participant API as Query API<br/>(DRF View)
    participant Cache as Cache<br/>(Redis/Memory)
    participant Engine as Query Engine
    participant Validator as Validator
    participant Builder as Query Builder
    participant ORM as Django ORM
    participant DB as Database

    Client->>API: GET /api/indicators/query?...
    API->>Cache: Check cache
    Cache-->>API: Not found
    
    API->>Engine: engine.query(...)
    Engine->>Validator: validate_aggregation()
    Validator-->>Engine: ✓ OK
    Engine->>Validator: validate_group_by()
    Validator-->>Engine: ✓ OK
    
    Engine->>Builder: build_query(...)
    Builder->>ORM: .filter().values().annotate()
    ORM->>DB: SELECT...GROUP BY...
    DB-->>ORM: Results
    ORM-->>Builder: QuerySet
    
    Builder-->>Engine: (results, metadata)
    
    Engine->>Cache: set(results, ttl=3600)
    Cache-->>Engine: ✓ Cached
    
    Engine-->>API: (results, metadata)
    API-->>Client: JSON Response
    Client->>Client: Render/Plot
```

---

## Component Architecture

```mermaid
graph TB
    subgraph Client["Frontend Layer"]
        ST["Streamlit App"]
        JS["JavaScript/React"]
        BI["BI Tools (Power BI)"]
        PY["Python Script"]
    end
    
    subgraph API["REST API Layer"]
        V1["IndicatorSchemaView"]
        V2["IndicatorQueryView"]
        V3["QueryValidateView"]
        V4["CacheClearView"]
    end
    
    subgraph Engine["Query Engine Layer"]
        QE["IndicatorQueryEngine"]
        QV["QueryValidator"]
        QB["QueryBuilder"]
    end
    
    subgraph Semantic["Semantic Layer"]
        SM["IndicatorSchema"]
        REG["IndicatorRegistry"]
        PIB["PIB Schema"]
        POP["POPULACAO Schema"]
    end
    
    subgraph Cache["Cache Layer"]
        QC["QueryCache"]
        MC["MetadataCache"]
    end
    
    subgraph Data["Data Access Layer"]
        ORM["Django ORM"]
        MOD["IndicadorMunicipio"]
        EST["Estado"]
        MUN["Municipio"]
        IND["Indicador"]
    end
    
    subgraph DB["Database"]
        SQL["SQLite/PostgreSQL"]
    end
    
    ST --> V2
    JS --> V1
    BI --> V2
    PY --> V1
    
    V1 --> QE
    V2 --> QE
    V3 --> QE
    V4 --> QC
    
    QE --> QV
    QE --> QB
    
    QV --> SM
    QB --> SM
    
    SM --> REG
    REG --> PIB
    REG --> POP
    
    QE --> QC
    QE --> MC
    QE --> ORM
    
    ORM --> MOD
    ORM --> EST
    ORM --> MUN
    ORM --> IND
    
    MOD --> SQL
    EST --> SQL
    MUN --> SQL
    IND --> SQL
    
    QC -.->|Quick Check| Cache
    MC -.->|Metadata| Cache
```

---

## Query Processing Pipeline

```mermaid
graph LR
    A["Raw Parameters<br/>indicator=PIB<br/>group_by=estado<br/>filter_ano=2023"] -->|Parse| B["Parse Request"]
    
    B --> C["Extract Filters"]
    C --> D["Check Cache"]
    
    D -->|Hit| E["Return Cached"]
    D -->|Miss| F["Validate"]
    
    F -->|Invalid| G["Return Error"]
    F -->|Valid| H["Get Schema"]
    
    H --> I["Build ORM Query"]
    I --> J["Execute Query"]
    
    J --> K["Format Results"]
    K --> L["Add Ranking"]
    
    L --> M["Cache Result"]
    M --> N["Return JSON"]
    
    E --> N
    
    style A fill:#e1f5ff
    style E fill:#c8e6c9
    style G fill:#ffcdd2
    style N fill:#f1f8e9
```

---

## Caching Strategy

```mermaid
graph TB
    subgraph Request["Incoming Request"]
        R["GET /api/indicators/query?<br/>indicator=PIB<br/>group_by=estado<br/>filter_ano=2023"]
    end
    
    subgraph KeyGen["Cache Key Generation"]
        K["MD5 Hash of:<br/>indicator:PIB<br/>group_by:estado<br/>agg:sum<br/>filter_ano:2023"]
    end
    
    subgraph CacheCheck["Check Cache"]
        CH{{"Cache<br/>Hit?"}}
    end
    
    subgraph Exec["Execute Query"]
        EX["QuerySet → Results<br/>(1-2 seconds)"]
    end
    
    subgraph Store["Store Cache"]
        ST["QueryCache.set(<br/>key,<br/>results,<br/>ttl=3600)"]
    end
    
    subgraph Return["Return Response"]
        RT["metadata.cached = true/false"]
    end
    
    R --> K
    K --> CacheCheck
    CacheCheck -->|Yes| RT
    CacheCheck -->|No| EX
    EX --> ST
    ST --> RT
    
    style RT fill:#f1f8e9
```

---

## Semantic Model: How It Works

```mermaid
graph TB
    subgraph Schema["Indicator Schema Definition"]
        CODE["code: 'PIB'"]
        NAME["name: 'Produto Interno Bruto'"]
        AGG["aggregations: [sum, avg, min, max]"]
        GB["group_by_fields: [estado, municipio, regiao, ano]"]
        FF["filter_fields: [ano, estado, municipio, regiao]"]
    end
    
    subgraph Validation["Validation"]
        V1["user_group_by == 'estado'?"]
        V2["Check in group_by_fields"]
        V3{"Valid?"}
    end
    
    subgraph Build["Build ORM"]
        B1["Get db_field = 'municipio__estado__nome'"]
        B2["Create .values(db_field)"]
        B3["Create .annotate(total=Sum(valor))"]
    end
    
    subgraph Execute["Execute"]
        E["Django ORM → SQL Query"]
        E2["Database Returns Rows"]
    end
    
    Schema --> Validation
    Validation --> V1
    V1 --> V2
    V2 --> V3
    V3 -->|Yes| Build
    V3 -->|No| Error["Return Error"]
    
    Build --> B1
    B1 --> B2
    B2 --> B3
    B3 --> Execute
    Execute --> E
    E --> E2
```

---

## Security: Multi-Layer Protection

```mermaid
graph TB
    subgraph L1["Layer 1: URL Routing"]
        R["Limited to defined<br/>endpoints"]
    end
    
    subgraph L2["Layer 2: Parameter Parsing"]
        P["Only read from<br/>query_params"]
    end
    
    subgraph L3["Layer 3: Semantic Validation"]
        S["Check against schema<br/>whitelists"]
    end
    
    subgraph L4["Layer 4: Type Validation"]
        T["Convert & validate<br/>types (int, str, float)"]
    end
    
    subgraph L5["Layer 5: ORM Safety"]
        O["Django ORM handles<br/>parameterization"]
    end
    
    subgraph L6["Layer 6: Result Limits"]
        L["Max 10,000 rows<br/>returned"]
    end
    
    Input["Malicious Input<br/>?indicator=PIB'; DROP TABLE--"] -->|blocked| L1
    L1 -->|blocked| L2
    L2 -->|blocked| L3
    L3 -->|blocked| L4
    L4 -->|blocked| L5
    L5 -->|blocked| L6
    L6 -->|safe| Output["Safe Result"]
    
    style Output fill:#c8e6c9
    style Input fill:#ffcdd2
```

---

## Query Builder: ORM Construction

```mermaid
graph LR
    A["Parameters:<br/>indicator=PIB<br/>group_by=estado<br/>agg=sum<br/>filter_ano=2023"] -->|1. Get Base| B["IndicadorMunicipio.objects"]
    
    B -->|2. Filter Indicator| C["filter(indicador__codigo=PIB)"]
    
    C -->|3. Filter Time| D["filter(ano=2023)"]
    
    D -->|4. Group & Aggregate| E["values('municipio__estado__nome')<br/>.annotate(total=Sum('valor'))"]
    
    E -->|5. Order| F["order_by('-total')"]
    
    F -->|6. Paginate| G["[0:1000]"]
    
    G -->|7. Execute| H["QuerySet → SQL"]
    
    H -->|8. Format| I["List of Dicts<br/>[{estado: SP, total: 2.1B}, ...]"]
    
    style I fill:#f1f8e9
```

---

## Adding a New Indicator: Step by Step

```mermaid
graph TD
    A["Need new indicator?"] -->|EDUCACAO| B["Create Schema"]
    
    B --> C["Define:<br/>- code<br/>- name<br/>- aggregations<br/>- group_by_fields<br/>- filter_fields"]
    
    C --> D["Register"]
    D --> E["IndicatorRegistry.register(EDUCACAO_SCHEMA)"]
    
    E --> F["Update init_indicator_registry()"]
    
    F --> G["Restart Django"]
    
    G --> H["API Automatically Supports:"]
    H --> H1["GET /api/indicators/schemas/EDUCACAO"]
    H1 --> H2["GET /api/indicators/query?indicator=EDUCACAO&..."]
    H2 --> H3["GET /api/indicators/query/validate?indicator=EDUCACAO&..."]
    
    style H1 fill:#e1f5ff
    style H2 fill:#e1f5ff
    style H3 fill:#e1f5ff
```

---

## Performance: From Slow to Fast

```mermaid
graph LR
    subgraph Before["❌ Without Query Engine"]
        B1["Create endpoint"]
        B2["Write SQL"]
        B3["Serialize response"]
        B1 --> B2 --> B3
    end
    
    subgraph After["✅ With Query Engine"]
        A1["Call engine.query()"]
        A2["Cache Hit?<br/>Return in 1ms"]
        A3["Cache Miss?<br/>Execute<br/>1-2 seconds"]
        A1 --> A2
        A1 --> A3
    end
    
    subgraph Typical["Typical API Call<br/>Cache Hit"]
        T["Request → Check Cache → Hit → JSON → 5ms"]
    end
    
    Before -.->|Repeat for each query| Before
    
    After -->|1st call| A3
    After -->|2nd+ calls| A2
    
    A2 --> Typical
    
    style T fill:#c8e6c9
    style A2 fill:#c8e6c9
```

---

## Integration Points

```mermaid
graph TB
    subgraph External["External Systems"]
        ST["Streamlit"]
        JS["JavaScript/Vue"]
        BI["Power BI"]
        PYTHON["Python Scripts"]
        DASH["Dash/Plotly"]
    end
    
    subgraph Project["Your Project"]
        API["REST API<br/>/api/indicators/*"]
        ENGINE["Query Engine"]
        DB["Database"]
    end
    
    ST -->|HTTPS| API
    JS -->|HTTPS| API
    BI -->|Direct Query| API
    PYTHON -->|Requests| API
    DASH -->|Requests| API
    
    API --> ENGINE
    ENGINE --> DB
    
    style API fill:#bbdefb
    style ENGINE fill:#c5cae9
```

---

**Want to understand the code deeper? Start with ARCHITECTURE.md**
