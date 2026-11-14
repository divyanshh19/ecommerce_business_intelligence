"""
Test Suite: Data Validation & Quality Tests
"""

import pytest
import pandas as pd
from backend.etl.data_validation import DataValidator

def test_data_quality_scoring():
    validator = DataValidator()
    mock_datasets = {
        "customers": pd.DataFrame({"customer_id": ["c1", "c2"], "customer_unique_id": ["u1", "u2"]}),
        "orders": pd.DataFrame({"order_id": ["o1", "o2"], "customer_id": ["c1", "c2"], "order_status": ["delivered", "shipped"]}),
        "order_items": pd.DataFrame({"order_id": ["o1", "o2"], "product_id": ["p1", "p2"], "seller_id": ["s1", "s2"], "price": [10.0, 25.5]}),
        "products": pd.DataFrame({"product_id": ["p1", "p2"]}),
        "sellers": pd.DataFrame({"seller_id": ["s1", "s2"]}),
        "order_payments": pd.DataFrame({"order_id": ["o1", "o2"], "payment_value": [10.0, 25.5]}),
        "order_reviews": pd.DataFrame({"order_id": ["o1", "o2"], "review_score": [5, 4]})
    }
    report = validator.generate_data_quality_report(mock_datasets)
    assert "overall_quality_score" in report
    assert report["overall_quality_score"] >= 90.0
    assert report["referential_integrity"]["orders_to_customers"]["match_rate_pct"] == 100.0
    assert report["value_constraints"]["review_score_range"]["compliance_pct"] == 100.0
