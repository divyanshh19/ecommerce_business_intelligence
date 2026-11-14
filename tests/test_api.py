"""
Test Suite: FastAPI Endpoints & Analytical Route Functions Unit Tests
"""

import pytest
from backend.app.main import root, health_check
from backend.app.routes.api import (
    get_dashboard_overview,
    get_sales_trends,
    get_sales_categories,
    get_customer_segments,
    get_customer_rfm,
    get_top_products,
    get_product_performance,
    get_operations_delivery,
    get_payment_analysis,
    get_reviews_analysis,
    get_data_quality
)

def test_root():
    data = root()
    assert data["status"] == "ONLINE"
    assert "platform" in data

def test_health():
    data = health_check()
    assert data["status"] == "HEALTHY"
    assert data["database_connected"] is True
    assert data["orders_loaded"] > 90000

def test_dashboard_overview():
    data = get_dashboard_overview()
    assert "kpis" in data
    assert "monthly_trends" in data
    assert "category_distribution" in data
    assert "top_products" in data
    assert "regional_performance" in data
    assert data["kpis"]["total_orders"] > 90000
    assert data["kpis"]["total_revenue"] > 1000000

def test_sales_trends():
    data = get_sales_trends()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "revenue" in data[0]

def test_sales_categories():
    data = get_sales_categories(limit=10)
    assert isinstance(data, list)
    assert len(data) == 10
    assert "revenue" in data[0]

def test_customer_segments():
    data = get_customer_segments()
    assert isinstance(data, list)
    assert len(data) > 0

def test_customer_rfm():
    data = get_customer_rfm()
    assert data["total_unique_customers"] > 90000
    assert "repeat_purchase_rate_pct" in data
    assert "segments" in data

def test_product_performance():
    data = get_product_performance(limit=5)
    assert "top_products" in data
    assert "lowest_selling_products" in data
    assert len(data["top_products"]) == 5

def test_operations_delivery():
    data = get_operations_delivery()
    assert "avg_delivery_days" in data
    assert "on_time_delivery_rate" in data
    assert "regional_delivery" in data

def test_payment_analysis():
    data = get_payment_analysis()
    assert "methods" in data
    assert len(data["methods"]) > 0

def test_reviews_analysis():
    data = get_reviews_analysis()
    assert data["average_score"] > 3.5
    assert len(data["score_distribution"]) > 0

def test_data_quality():
    data = get_data_quality()
    assert data["overall_quality_score"] > 90.0
