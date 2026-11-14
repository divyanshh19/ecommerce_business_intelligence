"""
Module: data_cleaning.py
Purpose: Clean, format, impute, and standardize all Olist datasets.
"""

import logging
from pathlib import Path
from typing import Dict, Tuple
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class DataCleaner:
    def __init__(self, processed_dir: str = "data/processed"):
        self.processed_dir = Path(processed_dir).resolve()
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.cleaning_stats = {}

    def clean_category_translations(self, df_trans: pd.DataFrame) -> pd.DataFrame:
        """Standardize category translation table."""
        df = df_trans.copy()
        df["product_category_name"] = df["product_category_name"].str.strip().str.lower()
        df["product_category_name_english"] = df["product_category_name_english"].str.strip().str.lower()
        df = df.drop_duplicates(subset=["product_category_name"])
        
        # Add common missing categories if not in translation file
        extra_categories = pd.DataFrame([
            {"product_category_name": "portateis_cozinha_e_preparadores_de_alimentos", "product_category_name_english": "portable_kitchen_food_preparers"},
            {"product_category_name": "pc_gamer", "product_category_name_english": "pc_gamer"},
            {"product_category_name": "outro", "product_category_name_english": "other"},
            {"product_category_name": "unknown", "product_category_name_english": "other"}
        ])
        df = pd.concat([df, extra_categories], ignore_index=True).drop_duplicates(subset=["product_category_name"])
        return df

    def clean_customers(self, df_customers: pd.DataFrame) -> pd.DataFrame:
        """Clean customers dataset."""
        df = df_customers.copy()
        init_rows = len(df)
        df["customer_id"] = df["customer_id"].astype(str).str.strip()
        df["customer_unique_id"] = df["customer_unique_id"].astype(str).str.strip()
        df["customer_city"] = df["customer_city"].astype(str).str.strip().str.title()
        df["customer_state"] = df["customer_state"].astype(str).str.strip().str.upper()
        df["customer_zip_code_prefix"] = pd.to_numeric(df["customer_zip_code_prefix"], errors="coerce").fillna(0).astype(int)
        
        # Drop duplicates on primary key
        df = df.drop_duplicates(subset=["customer_id"])
        self.cleaning_stats["customers"] = {
            "initial_rows": init_rows,
            "final_rows": len(df),
            "removed_duplicates": init_rows - len(df)
        }
        return df

    def clean_sellers(self, df_sellers: pd.DataFrame) -> pd.DataFrame:
        """Clean sellers dataset."""
        df = df_sellers.copy()
        init_rows = len(df)
        df["seller_id"] = df["seller_id"].astype(str).str.strip()
        df["seller_city"] = df["seller_city"].astype(str).str.strip().str.title()
        df["seller_state"] = df["seller_state"].astype(str).str.strip().str.upper()
        df["seller_zip_code_prefix"] = pd.to_numeric(df["seller_zip_code_prefix"], errors="coerce").fillna(0).astype(int)
        
        df = df.drop_duplicates(subset=["seller_id"])
        self.cleaning_stats["sellers"] = {
            "initial_rows": init_rows,
            "final_rows": len(df),
            "removed_duplicates": init_rows - len(df)
        }
        return df

    def clean_products(self, df_products: pd.DataFrame, df_trans: pd.DataFrame) -> pd.DataFrame:
        """Clean products and enrich with English category names."""
        df = df_products.copy()
        init_rows = len(df)
        df["product_id"] = df["product_id"].astype(str).str.strip()

        # Fix column spelling if needed
        col_renames = {
            "product_name_lenght": "product_name_length",
            "product_description_lenght": "product_description_length"
        }
        df = df.rename(columns=col_renames)

        # Handle missing category names gracefully (don't blindly drop products)
        df["product_category_name"] = df["product_category_name"].fillna("outro").astype(str).str.strip().str.lower()

        # Merge with translation
        df = df.merge(df_trans, on="product_category_name", how="left")
        df["product_category_name_english"] = df["product_category_name_english"].fillna(df["product_category_name"]).str.replace("_", " ").str.title()

        # Impute numerical specifications with median
        num_cols = ["product_name_length", "product_description_length", "product_photos_qty", 
                    "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"]
        for col in num_cols:
            if col in df.columns:
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)

        df = df.drop_duplicates(subset=["product_id"])
        self.cleaning_stats["products"] = {
            "initial_rows": init_rows,
            "final_rows": len(df),
            "categories_count": df["product_category_name_english"].nunique()
        }
        return df

    def clean_orders(self, df_orders: pd.DataFrame) -> pd.DataFrame:
        """Clean orders, parse datetimes, and compute delivery metrics."""
        df = df_orders.copy()
        init_rows = len(df)
        df["order_id"] = df["order_id"].astype(str).str.strip()
        df["customer_id"] = df["customer_id"].astype(str).str.strip()
        df["order_status"] = df["order_status"].astype(str).str.strip().str.lower()

        # Convert datetime columns
        date_cols = [
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date"
        ]
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], errors="coerce")

        # Operational metrics (in days)
        df["actual_delivery_days"] = (df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.total_seconds() / 86400.0
        df["estimated_delivery_days"] = (df["order_estimated_delivery_date"] - df["order_purchase_timestamp"]).dt.total_seconds() / 86400.0
        df["delivery_delay_days"] = (df["order_delivered_customer_date"] - df["order_estimated_delivery_date"]).dt.total_seconds() / 86400.0

        # Boolean flags (1 or 0 for easy SQL / aggregation)
        df["is_delivered"] = (df["order_status"] == "delivered").astype(int)
        df["is_delayed"] = np.where(df["delivery_delay_days"] > 0, 1, 0)
        df["is_on_time"] = np.where(df["delivery_delay_days"] <= 0, 1, 0)

        df = df.drop_duplicates(subset=["order_id"])
        self.cleaning_stats["orders"] = {
            "initial_rows": init_rows,
            "final_rows": len(df),
            "delivered_orders": int(df["is_delivered"].sum()),
            "delayed_orders": int(df["is_delayed"].sum())
        }
        return df

    def clean_order_items(self, df_items: pd.DataFrame) -> pd.DataFrame:
        """Clean order items, parse prices, and ensure positive values."""
        df = df_items.copy()
        init_rows = len(df)
        df["order_id"] = df["order_id"].astype(str).str.strip()
        df["order_item_id"] = pd.to_numeric(df["order_item_id"], errors="coerce").fillna(1).astype(int)
        df["product_id"] = df["product_id"].astype(str).str.strip()
        df["seller_id"] = df["seller_id"].astype(str).str.strip()
        df["shipping_limit_date"] = pd.to_datetime(df["shipping_limit_date"], errors="coerce")

        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0.0).clip(lower=0.0)
        df["freight_value"] = pd.to_numeric(df["freight_value"], errors="coerce").fillna(0.0).clip(lower=0.0)
        df["total_value"] = df["price"] + df["freight_value"]

        df = df.drop_duplicates(subset=["order_id", "order_item_id"])
        self.cleaning_stats["order_items"] = {
            "initial_rows": init_rows,
            "final_rows": len(df),
            "total_gmv": float(round(df["price"].sum(), 2))
        }
        return df

    def clean_order_payments(self, df_payments: pd.DataFrame) -> pd.DataFrame:
        """Clean payment records and handle invalid types."""
        df = df_payments.copy()
        init_rows = len(df)
        df["order_id"] = df["order_id"].astype(str).str.strip()
        df["payment_sequential"] = pd.to_numeric(df["payment_sequential"], errors="coerce").fillna(1).astype(int)
        df["payment_type"] = df["payment_type"].astype(str).str.strip().str.lower().replace({"not_defined": "other"})
        df["payment_installments"] = pd.to_numeric(df["payment_installments"], errors="coerce").fillna(1).astype(int).clip(lower=1)
        df["payment_value"] = pd.to_numeric(df["payment_value"], errors="coerce").fillna(0.0).clip(lower=0.0)

        df = df.drop_duplicates(subset=["order_id", "payment_sequential"])
        self.cleaning_stats["order_payments"] = {
            "initial_rows": init_rows,
            "final_rows": len(df),
            "total_payment_value": float(round(df["payment_value"].sum(), 2))
        }
        return df

    def clean_order_reviews(self, df_reviews: pd.DataFrame) -> pd.DataFrame:
        """Clean reviews, convert scores, handle missing comment texts."""
        df = df_reviews.copy()
        init_rows = len(df)
        df["review_id"] = df["review_id"].astype(str).str.strip()
        df["order_id"] = df["order_id"].astype(str).str.strip()
        df["review_score"] = pd.to_numeric(df["review_score"], errors="coerce").fillna(5).astype(int).clip(lower=1, upper=5)
        df["review_comment_title"] = df["review_comment_title"].fillna("").astype(str).str.strip()
        df["review_comment_message"] = df["review_comment_message"].fillna("").astype(str).str.strip()

        df["review_creation_date"] = pd.to_datetime(df["review_creation_date"], errors="coerce")
        df["review_answer_timestamp"] = pd.to_datetime(df["review_answer_timestamp"], errors="coerce")

        # Deduplicate on review_id and order_id
        df = df.sort_values("review_answer_timestamp", ascending=False).drop_duplicates(subset=["review_id", "order_id"])
        self.cleaning_stats["order_reviews"] = {
            "initial_rows": init_rows,
            "final_rows": len(df),
            "average_review_score": float(round(df["review_score"].mean(), 2))
        }
        return df

    def clean_geolocation(self, df_geo: pd.DataFrame) -> pd.DataFrame:
        """
        Deduplicate the 1M+ geolocation coordinates down to unique zip_code_prefix centroids.
        This provides massive performance gains and prevents cartesian join explosion.
        """
        df = df_geo.copy()
        init_rows = len(df)
        df["geolocation_zip_code_prefix"] = pd.to_numeric(df["geolocation_zip_code_prefix"], errors="coerce").fillna(0).astype(int)
        df["geolocation_lat"] = pd.to_numeric(df["geolocation_lat"], errors="coerce")
        df["geolocation_lng"] = pd.to_numeric(df["geolocation_lng"], errors="coerce")
        df["geolocation_city"] = df["geolocation_city"].astype(str).str.strip().str.title()
        df["geolocation_state"] = df["geolocation_state"].astype(str).str.strip().str.upper()

        # Remove extreme lat/lng outliers (Brazil is approx lat: 5N to 34S, lng: 35W to 74W)
        valid_coords = (df["geolocation_lat"].between(-35, 6)) & (df["geolocation_lng"].between(-75, -30))
        df = df[valid_coords]

        # Group by zip prefix to obtain centroid coordinates
        geo_centroids = df.groupby("geolocation_zip_code_prefix").agg({
            "geolocation_lat": "mean",
            "geolocation_lng": "mean",
            "geolocation_city": "first",
            "geolocation_state": "first"
        }).reset_index()

        self.cleaning_stats["geolocation"] = {
            "initial_rows": init_rows,
            "final_rows": len(geo_centroids),
            "unique_zip_prefixes": len(geo_centroids)
        }
        return geo_centroids

    def clean_all(self, raw_datasets: Dict[str, pd.DataFrame], save_processed: bool = True) -> Dict[str, pd.DataFrame]:
        """Orchestrate end-to-end cleaning across all 9 datasets."""
        logger.info("Starting comprehensive data cleaning pipeline...")
        cleaned = {}

        # 1. Translation
        cleaned["category_translation"] = self.clean_category_translations(raw_datasets["category_translation"])
        # 2. Customers
        cleaned["customers"] = self.clean_customers(raw_datasets["customers"])
        # 3. Sellers
        cleaned["sellers"] = self.clean_sellers(raw_datasets["sellers"])
        # 4. Products
        cleaned["products"] = self.clean_products(raw_datasets["products"], cleaned["category_translation"])
        # 5. Orders
        cleaned["orders"] = self.clean_orders(raw_datasets["orders"])
        # 6. Order Items
        cleaned["order_items"] = self.clean_order_items(raw_datasets["order_items"])
        # 7. Order Payments
        cleaned["order_payments"] = self.clean_order_payments(raw_datasets["order_payments"])
        # 8. Order Reviews
        cleaned["order_reviews"] = self.clean_order_reviews(raw_datasets["order_reviews"])
        # 9. Geolocation
        cleaned["geolocation"] = self.clean_geolocation(raw_datasets["geolocation"])

        if save_processed:
            logger.info(f"Saving cleaned datasets to {self.processed_dir}...")
            for name, df in cleaned.items():
                csv_path = self.processed_dir / f"clean_{name}.csv"
                df.to_csv(csv_path, index=False)
                logger.info(f"Saved clean_{name}.csv ({df.shape[0]:,} rows)")

        logger.info("Data cleaning completed successfully.")
        return cleaned

if __name__ == "__main__":
    from backend.etl.data_loader import DataLoader
    loader = DataLoader()
    raw = loader.load_all_datasets()
    cleaner = DataCleaner()
    cleaned = cleaner.clean_all(raw)
