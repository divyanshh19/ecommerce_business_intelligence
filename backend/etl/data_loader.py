"""
Module: data_loader.py
Purpose: Load and inspect raw Olist Brazilian E-Commerce datasets.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Optional
import pandas as pd
from backend.etl.download_dataset import download_olist_dataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_FILES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv"
}

class DataLoader:
    def __init__(self, raw_dir: str = "data/raw"):
        self.raw_dir = Path(raw_dir).resolve()

    def ensure_files(self) -> None:
        """Verify all CSV files exist; download if missing."""
        missing = [fname for fname in RAW_FILES.values() if not (self.raw_dir / fname).exists()]
        if missing:
            logger.warning(f"Missing {len(missing)} files: {missing}. Triggering automated download...")
            download_olist_dataset(str(self.raw_dir))

    def load_dataset(self, name: str, nrows: Optional[int] = None) -> pd.DataFrame:
        """Load a single dataset by key name."""
        if name not in RAW_FILES:
            raise ValueError(f"Unknown dataset key: {name}. Expected one of {list(RAW_FILES.keys())}")
        
        file_path = self.raw_dir / RAW_FILES[name]
        if not file_path.exists():
            self.ensure_files()

        logger.info(f"Loading {name} from {file_path}...")
        # Handle potential encoding issues (Olist reviews/geolocations have portuguese accents)
        try:
            df = pd.read_csv(file_path, nrows=nrows, encoding="utf-8", low_memory=False)
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, nrows=nrows, encoding="latin1", low_memory=False)
        
        logger.info(f"Loaded {name}: {df.shape[0]} rows, {df.shape[1]} columns")
        return df

    def load_all_datasets(self, sample_geo: bool = True, nrows: Optional[int] = None) -> Dict[str, pd.DataFrame]:
        """
        Load all 9 datasets into a dictionary of DataFrames.
        Geolocation is 1M+ rows; if sample_geo is True, we can sample or aggregate to speed up ETL while retaining accuracy.
        """
        self.ensure_files()
        datasets = {}
        for name in RAW_FILES.keys():
            # For geolocation, loading 1M records is fine for pandas, but we can deduplicate by zip prefix
            datasets[name] = self.load_dataset(name, nrows=nrows)
        return datasets

    def inspect_raw_data(self, datasets: Optional[Dict[str, pd.DataFrame]] = None) -> Dict[str, dict]:
        """Inspect dimensions, column types, null counts, duplicate rows."""
        if datasets is None:
            datasets = self.load_all_datasets()

        inspection = {}
        for name, df in datasets.items():
            inspection[name] = {
                "rows": int(len(df)),
                "columns": int(len(df.columns)),
                "column_names": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "null_counts": {col: int(df[col].isnull().sum()) for col in df.columns},
                "total_nulls": int(df.isnull().sum().sum()),
                "duplicate_rows": int(df.duplicated().sum()),
                "memory_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
            }
        return inspection

if __name__ == "__main__":
    loader = DataLoader()
    loader.ensure_files()
    stats = loader.inspect_raw_data()
    for name, s in stats.items():
        print(f"[{name.upper()}] Rows: {s['rows']:,} | Cols: {s['columns']} | Nulls: {s['total_nulls']:,} | Duplicates: {s['duplicate_rows']} | Mem: {s['memory_mb']} MB")
