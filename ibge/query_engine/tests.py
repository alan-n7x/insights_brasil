"""
Tests for the indicator query engine.

Run with: python manage.py test ibge.query_engine.tests
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.db import models
from decimal import Decimal
import json

from ibge.models import (
    Indicador,
    IndicadorMunicipio,
    Estado,
    Municipio,
)
from .query_engine import (
    IndicatorQueryEngine,
    QueryValidationError,
    QueryValidator,
    QueryBuilder,
)
from .semantic_model import (
    IndicatorRegistry,
    IndicatorSchema,
    GroupByField,
    FilterField,
    AggregationType,
)


class QueryEngineSetup(TestCase):
    """Base setup for query engine tests."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Clear and initialize registry
        IndicatorRegistry.clear()
        from .semantic_model import init_indicator_registry
        init_indicator_registry()
    
    def setUp(self):
        """Create test data."""
        
        # States
        self.estado_sp = Estado.objects.create(
            ibge_id=3550308,
            nome="São Paulo",
            sigla="SP",
            regiao="Sudeste",
        )
        self.estado_rj = Estado.objects.create(
            ibge_id=3304557,
            nome="Rio de Janeiro",
            sigla="RJ",
            regiao="Sudeste",
        )
        
        # Municipalities
        self.municipio_sp = Municipio.objects.create(
            ibge_id=3550308,
            nome="São Paulo",
            estado=self.estado_sp,
            regiao="Sudeste",
        )
        self.municipio_campinas = Municipio.objects.create(
            ibge_id=3509007,
            nome="Campinas",
            estado=self.estado_sp,
            regiao="Sudeste",
        )
        self.municipio_rj = Municipio.objects.create(
            ibge_id=3304557,
            nome="Rio de Janeiro",
            estado=self.estado_rj,
            regiao="Sudeste",
        )
        
        # Indicators
        self.pib = Indicador.objects.create(
            codigo="PIB",
            nome="Produto Interno Bruto",
        )
        self.populacao = Indicador.objects.create(
            codigo="POPULACAO",
            nome="População",
        )
        
        # Data
        IndicadorMunicipio.objects.create(
            municipio=self.municipio_sp,
            indicador=self.pib,
            ano=2023,
            valor=Decimal("2150000000.00"),
        )
        IndicadorMunicipio.objects.create(
            municipio=self.municipio_campinas,
            indicador=self.pib,
            ano=2023,
            valor=Decimal("180000000.00"),
        )
        IndicadorMunicipio.objects.create(
            municipio=self.municipio_rj,
            indicador=self.pib,
            ano=2023,
            valor=Decimal("980000000.00"),
        )
        
        # Populacao
        IndicadorMunicipio.objects.create(
            municipio=self.municipio_sp,
            indicador=self.populacao,
            ano=2023,
            valor=Decimal("11500000.00"),
        )
        IndicadorMunicipio.objects.create(
            municipio=self.municipio_rj,
            indicador=self.populacao,
            ano=2023,
            valor=Decimal("6500000.00"),
        )


class QueryValidatorTests(QueryEngineSetup):
    """Test the query validator."""
    
    def test_valid_aggregation(self):
        """Test validating aggregation functions."""
        schema = IndicatorRegistry.get("PIB")
        validator = QueryValidator(schema)
        
        # Valid aggregations
        result = validator.validate_aggregation("sum")
        self.assertEqual(result, AggregationType.SUM)
        
        result = validator.validate_aggregation("avg")
        self.assertEqual(result, AggregationType.AVG)
    
    def test_invalid_aggregation(self):
        """Test rejecting invalid aggregation."""
        schema = IndicatorRegistry.get("PIB")
        validator = QueryValidator(schema)
        
        with self.assertRaises(QueryValidationError):
            validator.validate_aggregation("invalid")
    
    def test_valid_group_by(self):
        """Test validating group_by fields."""
        schema = IndicatorRegistry.get("PIB")
        validator = QueryValidator(schema)
        
        result = validator.validate_group_by("estado")
        self.assertEqual(result, "estado")
        
        result = validator.validate_group_by("municipio")
        self.assertEqual(result, "municipio")
    
    def test_invalid_group_by(self):
        """Test rejecting invalid group_by."""
        schema = IndicatorRegistry.get("PIB")
        validator = QueryValidator(schema)
        
        with self.assertRaises(QueryValidationError):
            validator.validate_group_by("invalid_field")
    
    def test_limit_validation(self):
        """Test limit validation."""
        schema = IndicatorRegistry.get("PIB")
        validator = QueryValidator(schema)
        
        # Valid
        self.assertEqual(validator.validate_limit(100), 100)
        self.assertEqual(validator.validate_limit(None), 1000)
        
        # Invalid
        with self.assertRaises(QueryValidationError):
            validator.validate_limit(0)
        
        with self.assertRaises(QueryValidationError):
            validator.validate_limit(15000)


class QueryEngineTests(QueryEngineSetup):
    """Test the query engine."""
    
    def test_simple_group_by_estado(self):
        """Test grouping by estado."""
        engine = IndicatorQueryEngine()
        
        results, metadata = engine.query(
            indicator="PIB",
            group_by="estado",
            agg="sum",
            filters={"ano": 2023},
        )
        
        # Should have 2 estados
        self.assertEqual(len(results), 2)
        
        # SP should be first (sum = 2330000000)
        self.assertEqual(results[0]["estado"], "São Paulo")
        self.assertEqual(float(results[0]["total"]), 2330000000.00)
        
        # RJ should be second
        self.assertEqual(results[1]["estado"], "Rio de Janeiro")
        self.assertEqual(float(results[1]["total"]), 980000000.00)
    
    def test_group_by_municipio(self):
        """Test grouping by municipio."""
        engine = IndicatorQueryEngine()
        
        results, metadata = engine.query(
            indicator="PIB",
            group_by="municipio",
            agg="sum",
            filters={"ano": 2023},
        )
        
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["municipio"], "São Paulo")
    
    def test_filter_by_estado(self):
        """Test filtering by estado."""
        engine = IndicatorQueryEngine()
        
        results, metadata = engine.query(
            indicator="PIB",
            group_by="municipio",
            agg="sum",
            filters={"ano": 2023, "estado": "SP"},
        )
        
        # Only SP municipalities
        self.assertEqual(len(results), 2)
        self.assertIn(
            results[0]["municipio"],
            ["São Paulo", "Campinas"]
        )
    
    def test_multiple_filters(self):
        """Test multiple filters."""
        engine = IndicatorQueryEngine()
        
        results, metadata = engine.query(
            indicator="PIB",
            group_by="municipio",
            agg="sum",
            filters={"ano": 2023, "estado": ["SP", "RJ"]},
        )
        
        # All three municipalities
        self.assertEqual(len(results), 3)
    
    def test_limit_and_offset(self):
        """Test pagination."""
        engine = IndicatorQueryEngine()
        
        results, metadata = engine.query(
            indicator="PIB",
            group_by="municipio",
            agg="sum",
            filters={"ano": 2023},
            limit=2,
            offset=0,
        )
        
        self.assertEqual(len(results), 2)
    
    def test_ranking(self):
        """Test ranking."""
        engine = IndicatorQueryEngine()
        
        results, metadata = engine.query(
            indicator="PIB",
            group_by="estado",
            agg="sum",
            filters={"ano": 2023},
        )
        
        # Ranks should be sequential
        self.assertEqual(results[0]["rank"], 1)
        self.assertEqual(results[1]["rank"], 2)
    
    def test_invalid_indicator(self):
        """Test invalid indicator."""
        engine = IndicatorQueryEngine()
        
        with self.assertRaises(QueryValidationError):
            engine.query(
                indicator="INVALID",
                group_by="estado",
            )
    
    def test_schema_listing(self):
        """Test listing schemas."""
        engine = IndicatorQueryEngine()
        
        schemas = engine.list_indicators()
        self.assertGreater(len(schemas), 0)
        
        # Should have PIB and POPULACAO
        codes = [s["code"] for s in schemas]
        self.assertIn("PIB", codes)
        self.assertIn("POPULACAO", codes)
    
    def test_schema_detail(self):
        """Test getting schema details."""
        engine = IndicatorQueryEngine()
        
        schema = engine.get_indicator_schema("PIB")
        self.assertEqual(schema["code"], "PIB")
        self.assertEqual(schema["name"], "Produto Interno Bruto")
        self.assertIn("sum", schema["aggregations"])


class QueryAPITests(QueryEngineSetup):
    """Test the REST API views."""
    
    def setUp(self):
        super().setUp()
        self.client = Client()
    
    def test_query_endpoint(self):
        """Test query endpoint."""
        response = self.client.get(
            "/api/indicators/query",
            {
                "indicator": "PIB",
                "group_by": "estado",
                "filter_ano": "2023",
                "agg": "sum",
            },
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertIn("metadata", data)
        self.assertEqual(len(data["data"]), 2)
    
    def test_schema_list_endpoint(self):
        """Test schema list endpoint."""
        response = self.client.get("/api/indicators/schemas")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(len(data), 0)
    
    def test_schema_detail_endpoint(self):
        """Test schema detail endpoint."""
        response = self.client.get("/api/indicators/schemas/PIB")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["code"], "PIB")
    
    def test_validate_endpoint(self):
        """Test validation endpoint."""
        response = self.client.get(
            "/api/indicators/query/validate",
            {
                "indicator": "PIB",
                "group_by": "estado",
            },
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["valid"])
    
    def test_missing_parameters(self):
        """Test missing required parameters."""
        response = self.client.get(
            "/api/indicators/query",
            {"indicator": "PIB"},  # Missing group_by
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
