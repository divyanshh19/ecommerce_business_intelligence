"""
Module: etl_pipeline.py
Purpose: Main orchestrator for Extract, Transform, Validate, and Load operations.
Safe to rerun idempotently without duplicating records.
"""

import sys
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd
from sqlalchemy import text

# Ensure root directory is on PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.etl.data_loader import DataLoader
from backend.etl.data_cleaning import DataCleaner
from backend.etl.data_validation import DataValidator
from backend.app.analytics.rfm import calculate_rfm
from backend.app.database import engine, init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class ETLPipeline:
    def __init__(self, raw_dir: str = "data/raw", processed_dir: str = "data/processed"):
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        self.loader = DataLoader(raw_dir)
        self.cleaner = DataCleaner(processed_dir)
        self.validator = DataValidator()
        self.execution_summary = {}

    def create_database_views(self):
        """Create analytical reporting views compatible with the current SQL dialect."""
        is_sqlite = "sqlite" in str(engine.url)
        logger.info(f"Creating analytical views for dialect: {'SQLite' if is_sqlite else 'MySQL 8+'}...")

        date_fmt = "strftime('%Y-%m', o.order_purchase_timestamp)" if is_sqlite else "DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m')"

        views = [
            # 1. Executive Monthly KPIs View
            f"""
            CREATE VIEW IF NOT EXISTS view_executive_monthly_kpis AS
            SELECT 
                {date_fmt} AS order_year_month,
                COUNT(DISTINCT o.order_id) AS total_orders,
                COUNT(DISTINCT c.customer_unique_id) AS active_customers,
                ROUND(SUM(oi.price), 2) AS gross_merchandise_value,
                ROUND(SUM(oi.freight_value), 2) AS total_freight,
                ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue,
                ROUND(AVG(oi.price), 2) AS avg_item_price,
                ROUND(SUM(oi.price + oi.freight_value) / NULLIF(COUNT(DISTINCT o.order_id), 0), 2) AS average_order_value
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.order_status <> 'canceled'
            GROUP BY {date_fmt};
            """,

            # 2. Category Performance View
            """
            CREATE VIEW IF NOT EXISTS view_category_performance AS
            SELECT 
                COALESCE(p.product_category_name_english, 'Other') AS category_name,
                COUNT(DISTINCT oi.order_id) AS order_volume,
                COUNT(oi.product_id) AS items_sold,
                ROUND(SUM(oi.price), 2) AS total_sales,
                ROUND(AVG(oi.price), 2) AS avg_unit_price,
                ROUND(AVG(r.review_score), 2) AS avg_review_score
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            JOIN orders o ON oi.order_id = o.order_id
            LEFT JOIN order_reviews r ON o.order_id = r.order_id
            WHERE o.order_status = 'delivered'
            GROUP BY COALESCE(p.product_category_name_english, 'Other');
            """,

            # 3. Regional Delivery Performance View
            """
            CREATE VIEW IF NOT EXISTS view_regional_delivery_performance AS
            SELECT 
                c.customer_state AS state_code,
                COUNT(o.order_id) AS total_delivered_orders,
                ROUND(AVG(o.actual_delivery_days), 1) AS avg_actual_delivery_days,
                ROUND(AVG(o.estimated_delivery_days), 1) AS avg_estimated_delivery_days,
                SUM(o.is_delayed) AS delayed_orders_count,
                ROUND((SUM(o.is_on_time) * 100.0) / NULLIF(COUNT(o.order_id), 0), 2) AS on_time_delivery_rate,
                ROUND(AVG(r.review_score), 2) AS avg_satisfaction_score
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            LEFT JOIN order_reviews r ON o.order_id = r.order_id
            WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
            GROUP BY c.customer_state;
            """,

            # 4. Payment Method Breakdown View
            """
            CREATE VIEW IF NOT EXISTS view_payment_method_breakdown AS
            SELECT 
                op.payment_type,
                COUNT(DISTINCT op.order_id) AS transaction_count,
                ROUND(SUM(op.payment_value), 2) AS total_payment_value,
                ROUND(AVG(op.payment_installments), 1) AS avg_installments,
                ROUND(AVG(op.payment_value), 2) AS avg_transaction_value
            FROM order_payments op
            JOIN orders o ON op.order_id = o.order_id
            WHERE o.order_status <> 'canceled'
            GROUP BY op.payment_type;
            """,

            # 5. Customer RFM Summary View
            """
            CREATE VIEW IF NOT EXISTS view_customer_rfm_summary AS
            SELECT 
                customer_segment,
                COUNT(*) AS customer_count,
                ROUND(AVG(recency_days), 1) AS avg_recency_days,
                ROUND(AVG(frequency), 2) AS avg_order_frequency,
                ROUND(AVG(monetary_value), 2) AS avg_customer_spend,
                ROUND(SUM(monetary_value), 2) AS total_segment_revenue
            FROM customer_rfm_segments
            GROUP BY customer_segment;
            """
        ]

        with engine.connect() as conn:
            for v_sql in views:
                try:
                    conn.execute(text(v_sql.strip()))
                except Exception as e:
                    logger.warning(f"View creation note: {e}")
            conn.commit()

    def run(self, nrows: Optional[int] = None) -> Dict[str, Any]:
        """Execute full ETL Pipeline."""
        start_time = time.time()
        timestamp = datetime.utcnow().isoformat()
        logger.info(f"========== STARTING ETL PIPELINE EXECUTION [{timestamp}] ==========")

        # 1. EXTRACT
        raw_datasets = self.loader.load_all_datasets(nrows=nrows)

        # 2. TRANSFORM & CLEAN
        cleaned_datasets = self.cleaner.clean_all(raw_datasets, save_processed=True)

        # 3. VALIDATE & DATA QUALITY
        quality_report = self.validator.generate_data_quality_report(cleaned_datasets)

        # 4. CUSTOMER ANALYTICS & RFM SEGMENTATION
        rfm_df, rfm_metrics = calculate_rfm(
            cleaned_datasets["orders"],
            cleaned_datasets["customers"],
            cleaned_datasets["order_items"]
        )

        # 5. INITIALIZE DB TABLES & LOAD DATA
        logger.info("Loading cleaned records into relational database...")
        table_mappings = [
            ("customers", cleaned_datasets["customers"]),
            ("sellers", cleaned_datasets["sellers"]),
            ("product_category_translation", cleaned_datasets["category_translation"]),
            ("products", cleaned_datasets["products"]),
            ("geolocation", cleaned_datasets["geolocation"]),
            ("orders", cleaned_datasets["orders"]),
            ("order_items", cleaned_datasets["order_items"]),
            ("order_payments", cleaned_datasets["order_payments"]),
            ("order_reviews", cleaned_datasets["order_reviews"]),
            ("customer_rfm_segments", rfm_df)
        ]

        loaded_counts = {}
        with engine.begin() as conn:
            for table_name, df_table in table_mappings:
                logger.info(f"Writing {len(df_table):,} records to table: {table_name}...")
                df_table.to_sql(
                    name=table_name,
                    con=conn,
                    if_exists="replace",
                    index=False,
                    chunksize=5000
                )
                loaded_counts[table_name] = len(df_table)

            # Record Data Quality Logs in DB
            dq_rows = []
            for t_name, t_rep in quality_report["tables"].items():
                dq_rows.append({
                    "table_name": t_name,
                    "total_records": t_rep["records"],
                    "valid_records": t_rep["records"] - t_rep["duplicate_rows"],
                    "missing_values": t_rep["null_values"],
                    "duplicate_records": t_rep["duplicate_rows"],
                    "quality_score": t_rep["quality_score"],
                    "executed_at": datetime.utcnow()
                })
            df_dq = pd.DataFrame(dq_rows)
            df_dq.to_sql("data_quality_logs", con=conn, if_exists="replace", index=False)

        # 6. CREATE ANALYTICAL VIEWS
        self.create_database_views()

        duration = round(time.time() - start_time, 2)
        logger.info(f"========== ETL COMPLETED SUCCESSFULLY in {duration}s ==========")

        summary = {
            "execution_status": "SUCCESS",
            "timestamp": timestamp,
            "duration_seconds": duration,
            "overall_quality_score": quality_report["overall_quality_score"],
            "total_records_processed": quality_report["total_records_processed"],
            "table_record_counts": loaded_counts,
            "rfm_summary": rfm_metrics,
            "quality_report": quality_report
        }

        # Cache summary to JSON for instant API lookup
        summary_path = Path("data/processed/latest_etl_summary.json")
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, default=str)

        self.execution_summary = summary
        return summary

if __name__ == "__main__":
    pipeline = ETLPipeline()
    pipeline.run()
