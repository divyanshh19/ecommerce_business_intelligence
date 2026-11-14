"""
Test Suite: Data Cleaning Unit Tests
"""

import pytest
import pandas as pd
import numpy as np
from backend.etl.data_cleaning import DataCleaner

@pytest.fixture
def cleaner():
    return DataCleaner()

def test_clean_customers(cleaner):
    raw_cust = pd.DataFrame([
        {"customer_id": "c1  ", "customer_unique_id": "u1", "customer_zip_code_prefix": "12345", "customer_city": "sao paulo", "customer_state": "sp"},
        {"customer_id": "c1  ", "customer_unique_id": "u1", "customer_zip_code_prefix": "12345", "customer_city": "sao paulo", "customer_state": "sp"}, # duplicate
        {"customer_id": "c2", "customer_unique_id": "u2", "customer_zip_code_prefix": "invalid", "customer_city": "rio de janeiro", "customer_state": "rj"}
    ])
    cleaned = cleaner.clean_customers(raw_cust)
    assert len(cleaned) == 2
    assert cleaned.iloc[0]["customer_city"] == "Sao Paulo"
    assert cleaned.iloc[0]["customer_state"] == "SP"
    assert cleaned.iloc[1]["customer_zip_code_prefix"] == 0

def test_clean_orders_datetime_and_metrics(cleaner):
    raw_orders = pd.DataFrame([
        {
            "order_id": "o1",
            "customer_id": "c1",
            "order_status": "delivered",
            "order_purchase_timestamp": "2018-01-01 10:00:00",
            "order_approved_at": "2018-01-01 11:00:00",
            "order_delivered_carrier_date": "2018-01-02 12:00:00",
            "order_delivered_customer_date": "2018-01-05 10:00:00",
            "order_estimated_delivery_date": "2018-01-07 00:00:00"
        },
        {
            "order_id": "o2",
            "customer_id": "c2",
            "order_status": "delivered",
            "order_purchase_timestamp": "2018-01-01 10:00:00",
            "order_approved_at": "2018-01-01 11:00:00",
            "order_delivered_carrier_date": "2018-01-02 12:00:00",
            "order_delivered_customer_date": "2018-01-10 10:00:00", # Late
            "order_estimated_delivery_date": "2018-01-07 00:00:00"
        }
    ])
    cleaned = cleaner.clean_orders(raw_orders)
    assert len(cleaned) == 2
    assert cleaned.loc[cleaned["order_id"] == "o1", "is_on_time"].values[0] == 1
    assert cleaned.loc[cleaned["order_id"] == "o2", "is_delayed"].values[0] == 1
    assert cleaned.loc[cleaned["order_id"] == "o1", "actual_delivery_days"].values[0] == 4.0

def test_clean_products_translation(cleaner):
    trans = pd.DataFrame([{"product_category_name": "beleza_saude", "product_category_name_english": "health_beauty"}])
    clean_trans = cleaner.clean_category_translations(trans)
    
    raw_prods = pd.DataFrame([
        {"product_id": "p1", "product_category_name": "beleza_saude", "product_weight_g": 500.0},
        {"product_id": "p2", "product_category_name": None, "product_weight_g": None}
    ])
    cleaned = cleaner.clean_products(raw_prods, clean_trans)
    assert len(cleaned) == 2
    assert cleaned.loc[cleaned["product_id"] == "p1", "product_category_name_english"].values[0] == "Health Beauty"
    assert cleaned.loc[cleaned["product_id"] == "p2", "product_category_name_english"].values[0] == "Other"
    assert not pd.isnull(cleaned.loc[cleaned["product_id"] == "p2", "product_weight_g"].values[0])
