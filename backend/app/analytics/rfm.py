"""
Module: rfm.py
Purpose: Enterprise RFM (Recency, Frequency, Monetary) Customer Segmentation & Analytics Engine.
"""

import logging
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def calculate_rfm(
    df_orders: pd.DataFrame,
    df_customers: pd.DataFrame,
    df_order_items: pd.DataFrame
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Computes empirical RFM metrics, segment classifications, and summary statistics.
    
    Analytical Assumptions:
    - Anchors reference date at 1 day post the maximum recorded order timestamp in Olist.
    - Uses customer_unique_id (identifying distinct individuals) rather than order-specific customer_id.
    - Excludes canceled/unavailable orders to ensure monetary metrics reflect realized revenue.
    """
    logger.info("Starting RFM Customer Segmentation...")

    # Filter delivered/valid orders
    valid_orders = df_orders[df_orders["order_status"].isin(["delivered", "shipped", "invoiced"])].copy()
    
    # Merge orders with customers to link to customer_unique_id
    order_cust = valid_orders.merge(
        df_customers[["customer_id", "customer_unique_id"]],
        on="customer_id",
        how="inner"
    )

    # Calculate order-level monetary values from order_items
    order_spend = df_order_items.groupby("order_id").agg(
        order_value=("price", "sum"),
        order_freight=("freight_value", "sum")
    ).reset_index()
    order_spend["order_gross"] = order_spend["order_value"] + order_spend["order_freight"]

    order_cust_spend = order_cust.merge(order_spend, on="order_id", how="left")
    order_cust_spend["order_gross"] = order_cust_spend["order_gross"].fillna(0.0)

    # Reference date for Recency
    max_timestamp = order_cust_spend["order_purchase_timestamp"].max()
    reference_date = max_timestamp + pd.Timedelta(days=1)
    logger.info(f"RFM Reference Anchor Date: {reference_date} (Max purchase: {max_timestamp})")

    # Aggregate by customer_unique_id
    rfm = order_cust_spend.groupby("customer_unique_id").agg(
        last_purchase_date=("order_purchase_timestamp", "max"),
        first_purchase_date=("order_purchase_timestamp", "min"),
        frequency=("order_id", "nunique"),
        monetary_value=("order_gross", "sum")
    ).reset_index()

    # Recency in days
    rfm["recency_days"] = (reference_date - rfm["last_purchase_date"]).dt.days
    rfm["avg_order_value"] = np.round(rfm["monetary_value"] / rfm["frequency"], 2)

    # R_score: 5 (most recent) to 1 (least recent) via quintiles
    try:
        rfm["r_score"] = pd.qcut(rfm["recency_days"], q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    except ValueError:
        rfm["r_score"] = pd.cut(rfm["recency_days"], bins=5, labels=[5, 4, 3, 2, 1]).astype(int)

    # M_score: 1 (lowest) to 5 (highest) via quintiles
    try:
        rfm["m_score"] = pd.qcut(rfm["monetary_value"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    except ValueError:
        rfm["m_score"] = pd.cut(rfm["monetary_value"], bins=5, labels=[1, 2, 3, 4, 5]).astype(int)

    # F_score: tailored threshold scoring because ~97% of Olist customers are single-purchase
    def assign_f_score(f: int) -> int:
        if f >= 4:
            return 5
        elif f == 3:
            return 4
        elif f == 2:
            return 3
        else:
            return 1

    rfm["f_score"] = rfm["frequency"].apply(assign_f_score)
    rfm["rfm_score"] = rfm["r_score"].astype(str) + rfm["f_score"].astype(str) + rfm["m_score"].astype(str)

    # Assign actionable Business Segments
    def classify_segment(row) -> str:
        r = row["r_score"]
        f = row["f_score"]
        m = row["m_score"]

        if (r >= 4 and f >= 3 and m >= 4) or (r == 5 and f >= 3):
            return "Champions"
        elif (r >= 3 and f >= 3) or (r >= 4 and f == 2):
            return "Loyal Customers"
        elif r >= 4 and f == 1 and m >= 3:
            return "Potential Loyalists"
        elif r >= 4 and f == 1 and m <= 2:
            return "New Customers"
        elif r == 3 and f == 1:
            return "Promising"
        elif r <= 2 and f >= 3:
            return "At Risk"
        elif r == 1 and f == 1 and m <= 2:
            return "Lost Customers"
        elif r <= 2 and m >= 4:
            return "High-Value At Risk"
        else:
            return "Need Attention"

    rfm["customer_segment"] = rfm.apply(classify_segment, axis=1)

    # Calculate Business Intelligence Metrics
    total_customers = int(len(rfm))
    repeat_customers = int((rfm["frequency"] > 1).sum())
    repeat_rate_pct = round((repeat_customers / total_customers) * 100.0, 2)
    avg_customer_spend = round(float(rfm["monetary_value"].mean()), 2)
    avg_purchase_frequency = round(float(rfm["frequency"].mean()), 2)
    clv_proxy = round(avg_customer_spend * avg_purchase_frequency, 2)

    # Segment breakdown
    segment_summary = rfm.groupby("customer_segment").agg(
        count=("customer_unique_id", "count"),
        avg_recency=("recency_days", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary_value", "mean"),
        total_revenue=("monetary_value", "sum")
    ).reset_index()

    segment_summary["percentage"] = np.round((segment_summary["count"] / total_customers) * 100.0, 2)
    segment_summary["avg_recency"] = np.round(segment_summary["avg_recency"], 1)
    segment_summary["avg_frequency"] = np.round(segment_summary["avg_frequency"], 2)
    segment_summary["avg_monetary"] = np.round(segment_summary["avg_monetary"], 2)
    segment_summary["total_revenue"] = np.round(segment_summary["total_revenue"], 2)

    metrics = {
        "total_unique_customers": total_customers,
        "repeat_customers_count": repeat_customers,
        "repeat_purchase_rate_pct": repeat_rate_pct,
        "average_customer_spend": avg_customer_spend,
        "average_purchase_frequency": avg_purchase_frequency,
        "customer_lifetime_value_proxy": clv_proxy,
        "reference_anchor_date": str(reference_date.date()),
        "segments": segment_summary.to_dict(orient="records")
    }

    logger.info(f"RFM Segmentation completed. {total_customers:,} unique customers analyzed. Repeat rate: {repeat_rate_pct}%")
    return rfm, metrics

if __name__ == "__main__":
    from backend.etl.data_loader import DataLoader
    from backend.etl.data_cleaning import DataCleaner
    
    loader = DataLoader()
    raw = loader.load_all_datasets()
    cleaner = DataCleaner()
    clean = cleaner.clean_all(raw, save_processed=False)
    rfm_df, rfm_metrics = calculate_rfm(clean["orders"], clean["customers"], clean["order_items"])
    print("RFM Summary Metrics:", rfm_metrics)
