"""
Module: analytics_schema.py
Purpose: Pydantic schemas for API response validation and serialization.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ExecutiveKPIs(BaseModel):
    total_revenue: float
    total_orders: int
    total_customers: int
    average_order_value: float
    average_review_score: float
    on_time_delivery_rate: float
    average_delivery_days: float
    delayed_orders_count: int

class TrendPoint(BaseModel):
    date: str
    revenue: float
    orders: int
    aov: float
    moving_avg_revenue: Optional[float] = None

class CategoryMetric(BaseModel):
    category: str
    orders: int
    items_sold: int
    revenue: float
    avg_price: float
    avg_rating: float
    revenue_share_pct: float

class ProductMetric(BaseModel):
    product_id: str
    category: str
    units_sold: int
    total_revenue: float
    avg_price: float
    avg_rating: float

class RegionalMetric(BaseModel):
    state: str
    orders: int
    revenue: float
    avg_delivery_days: float
    on_time_rate: float
    delayed_orders: int
    avg_rating: float

class DashboardOverviewResponse(BaseModel):
    kpis: ExecutiveKPIs
    monthly_trends: List[TrendPoint]
    category_distribution: List[CategoryMetric]
    top_products: List[ProductMetric]
    regional_performance: List[RegionalMetric]

class CustomerSegmentMetric(BaseModel):
    customer_segment: str
    customer_count: int
    avg_recency_days: float
    avg_order_frequency: float
    avg_customer_spend: float
    total_segment_revenue: float
    percentage_of_customers: float

class RFMAnalyticsResponse(BaseModel):
    total_unique_customers: int
    repeat_customers_count: int
    repeat_purchase_rate_pct: float
    average_customer_spend: float
    average_purchase_frequency: float
    clv_proxy: float
    reference_anchor_date: str
    segments: List[CustomerSegmentMetric]
    recency_distribution: List[Dict[str, Any]]
    frequency_distribution: List[Dict[str, Any]]
    monetary_distribution: List[Dict[str, Any]]

class DeliveryOperationsResponse(BaseModel):
    avg_delivery_days: float
    avg_estimated_days: float
    on_time_delivery_rate: float
    total_delivered_orders: int
    delayed_orders_count: int
    regional_delivery: List[RegionalMetric]
    delay_impact_on_reviews: List[Dict[str, Any]]
    fulfillment_funnel: List[Dict[str, Any]]

class PaymentMethodMetric(BaseModel):
    payment_type: str
    transaction_count: int
    total_payment_value: float
    transaction_share_pct: float
    gmv_share_pct: float
    avg_installments: float
    avg_ticket_value: float

class PaymentAnalyticsResponse(BaseModel):
    methods: List[PaymentMethodMetric]
    installments_distribution: List[Dict[str, Any]]
    monthly_payment_trends: List[Dict[str, Any]]

class ReviewAnalyticsResponse(BaseModel):
    average_score: float
    total_reviews: int
    positive_review_pct: float
    negative_review_pct: float
    score_distribution: List[Dict[str, Any]]
    category_reviews: List[Dict[str, Any]]
    delivery_delay_correlation: List[Dict[str, Any]]

class DataQualityTableAudit(BaseModel):
    records: int
    columns: int
    null_values: int
    completeness_pct: float
    duplicate_rows: int
    uniqueness_pct: float
    quality_score: float

class DataQualityResponse(BaseModel):
    overall_quality_score: float
    status: str
    total_records_processed: int
    total_null_values: int
    average_completeness_pct: float
    average_referential_integrity_pct: float
    average_validity_pct: float
    last_refresh_timestamp: str
    tables: Dict[str, DataQualityTableAudit]
    referential_integrity: Dict[str, Any]
    value_constraints: Dict[str, Any]
