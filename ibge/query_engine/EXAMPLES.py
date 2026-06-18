"""
Example: Using the Query Engine in Real Applications

This file shows practical examples of using the query engine in:
1. Django Views
2. Streamlit Apps
3. Management Commands
4. External Clients
"""

# ============================================================================
# 1. DJANGO VIEWS (Using the engine directly)
# ============================================================================

from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .query_engine import IndicatorQueryEngine, QueryValidationError


class IndicatorAnalysisView(View):
    """
    Example: Custom view that uses the query engine.
    """
    
    def get(self, request):
        """
        GET /analysis/?indicator=PIB&estado=SP
        """
        
        try:
            indicator = request.GET.get("indicator", "PIB")
            estado = request.GET.get("estado")
            
            engine = IndicatorQueryEngine()
            
            filters = {}
            if estado:
                filters["estado"] = estado
            
            results, metadata = engine.query(
                indicator=indicator,
                group_by="municipio",
                filters=filters,
                limit=50,
            )
            
            return JsonResponse({
                "indicator": indicator,
                "municipalities": results,
                "total_count": len(results),
            })
        
        except QueryValidationError as e:
            return JsonResponse({"error": str(e)}, status=400)


# ============================================================================
# 2. STREAMLIT APP (Using the API)
# ============================================================================

EXAMPLE_STREAMLIT_CODE = """
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Indicadores Brasil", layout="wide")

# ─────────────────────────────────────────────────────────────
# Sidebar: Controles
# ─────────────────────────────────────────────────────────────

st.sidebar.title("⚙️ Filtros")

# Get available indicators from API
@st.cache_data
def get_indicators():
    resp = requests.get("http://localhost:8000/api/indicators/schemas")
    return {i["code"]: i["name"] for i in resp.json()}

indicators = get_indicators()
selected_indicator = st.sidebar.selectbox(
    "📊 Indicador",
    list(indicators.keys()),
    format_func=lambda x: indicators[x],
)

# Aggregation
agg_type = st.sidebar.selectbox(
    "🔢 Agregação",
    ["sum", "avg", "min", "max"],
)

# Group by
group_by = st.sidebar.selectbox(
    "📍 Agrupar por",
    ["estado", "municipio", "regiao"],
)

# Filters
filter_ano = st.sidebar.slider("📅 Ano", 2020, 2023, 2023)
filter_estado = st.sidebar.selectbox(
    "🗺️ Estado (opcional)",
    ["Todos", "SP", "RJ", "MG", "BA"],
)

# ─────────────────────────────────────────────────────────────
# Main: Query & Display
# ─────────────────────────────────────────────────────────────

st.title(f"📈 {indicators[selected_indicator]}")

# Build query params
params = {
    "indicator": selected_indicator,
    "group_by": group_by,
    "agg": agg_type,
    "filter_ano": filter_ano,
    "limit": 100,
}

if filter_estado != "Todos":
    params["filter_estado"] = filter_estado

# Execute query
with st.spinner("Executando query..."):
    resp = requests.get(
        "http://localhost:8000/api/indicators/query",
        params=params,
    )
    
    if resp.status_code != 200:
        st.error(f"Erro: {resp.json()['error']}")
    else:
        data = resp.json()
        results = data["data"]
        metadata = data["metadata"]
        
        # ─────────────────────────────────────────────────────────────
        # Display Results
        # ─────────────────────────────────────────────────────────────
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Registros", len(results))
        col2.metric("Do Cache?", "Sim" if metadata["cached"] else "Não")
        
        # Aggregate value
        total = sum(r["total"] for r in results)
        col3.metric("Total", f"{total:,.0f}")
        
        # DataFrame
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)
        
        # Visualization
        if len(results) > 0:
            # Rename column for plotting
            key = list(results[0].keys())[0]  # First key is the group_by field
            
            fig = px.bar(
                df,
                x=key,
                y="total",
                title=f"{indicators[selected_indicator]} por {group_by}",
                labels={"total": "Valor"},
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Export options
            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"{selected_indicator}_{filter_ano}.csv",
                )
            
            with col2:
                excel = df.to_excel(index=False)
                st.download_button(
                    label="📥 Download Excel",
                    data=excel,
                    file_name=f"{selected_indicator}_{filter_ano}.xlsx",
                )
"""


# ============================================================================
# 3. MANAGEMENT COMMAND (Batch operations)
# ============================================================================

EXAMPLE_MANAGEMENT_COMMAND = """
# File: ibge/management/commands/export_indicators.py

from django.core.management.base import BaseCommand
import csv
from ibge.query_engine import IndicatorQueryEngine
from ibge.query_engine.semantic_model import IndicatorRegistry


class Command(BaseCommand):
    help = "Export all indicators to CSV files"
    
    def add_arguments(self, parser):
        parser.add_argument(
            "--indicator",
            type=str,
            help="Export specific indicator",
        )
        parser.add_argument(
            "--year",
            type=int,
            help="Filter by year",
        )
    
    def handle(self, *args, **options):
        engine = IndicatorQueryEngine()
        
        # Get indicators to export
        if options["indicator"]:
            indicators = [options["indicator"]]
        else:
            indicators = [s.code for s in IndicatorRegistry.list_all()]
        
        for indicator in indicators:
            self.export_indicator(
                engine,
                indicator,
                options.get("year"),
            )
    
    def export_indicator(self, engine, indicator, year=None):
        \"\"\"Export single indicator.\"\"\"
        
        filters = {}
        if year:
            filters["ano"] = year
        
        # Query all group_by options
        for group_by in ["estado", "municipio"]:
            try:
                results, _ = engine.query(
                    indicator=indicator,
                    group_by=group_by,
                    filters=filters,
                    limit=10000,
                )
                
                filename = f"export_{indicator}_{group_by}.csv"
                
                with open(filename, "w", newline="") as f:
                    if results:
                        fieldnames = results[0].keys()
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(results)
                
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Exported {filename}")
                )
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Failed {indicator}/{group_by}: {e}")
                )


# Usage:
# python manage.py export_indicators
# python manage.py export_indicators --indicator PIB --year 2023
"""


# ============================================================================
# 4. EXTERNAL CLIENT (Python)
# ============================================================================

EXAMPLE_PYTHON_CLIENT = """
import requests
import pandas as pd


class IndicatorClient:
    \"\"\"Client for Indicator Query Engine API.\"\"\"
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def get_indicators(self):
        \"\"\"List all available indicators.\"\"\"
        resp = requests.get(f"{self.base_url}/api/indicators/schemas")
        resp.raise_for_status()
        return resp.json()
    
    def query(
        self,
        indicator,
        group_by,
        agg="sum",
        filters=None,
        limit=1000,
    ):
        \"\"\"Execute a query.\"\"\"
        
        params = {
            "indicator": indicator,
            "group_by": group_by,
            "agg": agg,
            "limit": limit,
        }
        
        # Add filters
        if filters:
            for key, value in filters.items():
                if isinstance(value, (list, tuple)):
                    params[f"filter_{key}"] = ",".join(map(str, value))
                else:
                    params[f"filter_{key}"] = value
        
        resp = requests.get(
            f"{self.base_url}/api/indicators/query",
            params=params,
        )
        resp.raise_for_status()
        return resp.json()
    
    def to_dataframe(self, result):
        \"\"\"Convert query result to pandas DataFrame.\"\"\"
        return pd.DataFrame(result["data"])


# Usage:
client = IndicatorClient()

# List indicators
indicators = client.get_indicators()
print(f"Available: {[i['code'] for i in indicators]}")

# Query PIB by estado
result = client.query(
    indicator="PIB",
    group_by="estado",
    filters={"ano": 2023},
    agg="sum",
)

df = client.to_dataframe(result)
print(df)
print(f"\\nTotal: {df['total'].sum():,.0f}")

# Top 5 states
print("\\nTop 5 Estados:")
print(df.head(5)[["estado", "total"]])

# Export to CSV
df.to_csv("pib_estados_2023.csv", index=False)
"""


# ============================================================================
# 5. EXTERNAL CLIENT (JavaScript/Node.js)
# ============================================================================

EXAMPLE_JS_CLIENT = """
// indicatorClient.js

class IndicatorClient {
  constructor(baseUrl = "http://localhost:8000") {
    this.baseUrl = baseUrl;
  }

  async getIndicators() {
    const resp = await fetch(`${this.baseUrl}/api/indicators/schemas`);
    return resp.json();
  }

  async query(indicator, groupBy, options = {}) {
    const params = new URLSearchParams({
      indicator,
      group_by: groupBy,
      agg: options.agg || "sum",
      limit: options.limit || 1000,
    });

    // Add filters
    if (options.filters) {
      for (const [key, value] of Object.entries(options.filters)) {
        params.append(`filter_${key}`, value);
      }
    }

    const resp = await fetch(
      `${this.baseUrl}/api/indicators/query?${params}`
    );
    
    if (!resp.ok) {
      throw new Error(`Query failed: ${resp.status}`);
    }
    
    return resp.json();
  }
}

// Usage:
const client = new IndicatorClient();

// List indicators
const indicators = await client.getIndicators();
console.log("Available:", indicators.map(i => i.code));

// Query
const result = await client.query("PIB", "estado", {
  filters: { ano: 2023 },
});

console.log("Results:", result.data);

// Display
const table = document.createElement("table");
result.data.forEach(row => {
  const tr = table.insertRow();
  tr.insertCell(0).textContent = row.estado;
  tr.insertCell(1).textContent = row.total.toLocaleString("pt-BR");
});
document.body.appendChild(table);
"""


# ============================================================================
# 6. REAL-TIME DASHBOARD (WebSocket)
# ============================================================================

EXAMPLE_WEBSOCKET = """
# File: ibge/consumers.py (Django Channels)

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .query_engine import IndicatorQueryEngine


class IndicatorConsumer(AsyncWebsocketConsumer):
    \"\"\"WebSocket consumer for real-time indicator updates.\"\"\"
    
    async def connect(self):
        await self.accept()
    
    async def receive(self, text_data):
        \"\"\"Receive query from client.\"\"\"
        
        try:
            message = json.loads(text_data)
            
            engine = IndicatorQueryEngine()
            results, metadata = engine.query(
                indicator=message["indicator"],
                group_by=message["group_by"],
                filters=message.get("filters"),
                agg=message.get("agg", "sum"),
            )
            
            await self.send(json.dumps({
                "status": "success",
                "data": results,
                "metadata": metadata,
            }))
        
        except Exception as e:
            await self.send(json.dumps({
                "status": "error",
                "error": str(e),
            }))
"""


if __name__ == "__main__":
    print("📚 QUERY ENGINE USAGE EXAMPLES")
    print("\nSee this file for practical examples of using the query engine in:")
    print("  1. Django Views")
    print("  2. Streamlit Apps")
    print("  3. Management Commands")
    print("  4. Python Clients")
    print("  5. JavaScript Clients")
    print("  6. WebSocket (Real-time)")
