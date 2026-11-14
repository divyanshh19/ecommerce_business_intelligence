"""
Test Suite: SQL Analytical Queries Validation
Verifies that the analytical SQL queries produce valid business results against the database.
"""

import pytest
from sqlalchemy import text
from backend.app.database import engine

def test_top_products_query():
    sql = """
    SELECT 
        p.product_id,
        COALESCE(p.product_category_name_english, 'Other') AS category,
        COUNT(oi.order_item_id) AS units_sold,
        ROUND(SUM(oi.price), 2) AS total_revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY p.product_id, p.product_category_name_english
    ORDER BY total_revenue DESC
    LIMIT 10;
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()
        assert len(rows) == 10
        assert rows[0][3] > 10000.0  # Top product revenue > R$ 10,000

def test_category_rankings_query():
    sql = """
    SELECT 
        COALESCE(p.product_category_name_english, 'Other') AS category,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        ROUND(SUM(oi.price), 2) AS total_revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY COALESCE(p.product_category_name_english, 'Other')
    ORDER BY total_revenue DESC
    LIMIT 5;
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()
        assert len(rows) == 5
        assert rows[0][2] > 500000.0  # Top category revenue > R$ 500,000

def test_rfm_distribution_query():
    sql = """
    SELECT 
        customer_segment,
        COUNT(*) AS customer_count,
        ROUND(SUM(monetary_value), 2) AS total_revenue
    FROM customer_rfm_segments
    GROUP BY customer_segment
    ORDER BY customer_count DESC;
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()
        assert len(rows) >= 5
        total_cust = sum(r[1] for r in rows)
        assert total_cust > 90000

def test_delay_vs_review_score_query():
    sql = """
    SELECT 
        o.is_delayed,
        COUNT(r.review_id) AS review_count,
        ROUND(AVG(r.review_score), 2) AS avg_score
    FROM orders o
    JOIN order_reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY o.is_delayed;
    """
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()
        assert len(rows) == 2
        # Verify that on-time orders have significantly higher review score than delayed orders
        scores = {r[0]: r[2] for r in rows}
        assert scores[0] > scores[1]  # On-time score (0) > Delayed score (1)
