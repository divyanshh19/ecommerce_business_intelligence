"""
Script: download_dataset.py
Purpose: Securely download and cache the official Brazilian E-Commerce Public Dataset by Olist
Source: HuggingFace mirror of the authentic Kaggle Olist dataset
"""

import os
import sys
import logging
from pathlib import Path
from huggingface_hub import hf_hub_download

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

REPO_ID = "miminmoons/olist-ecommerce-for-delivery-and-review-prediction"
DATA_FILES = [
    "data/olist_customers_dataset.csv",
    "data/olist_geolocation_dataset.csv",
    "data/olist_order_items_dataset.csv",
    "data/olist_order_payments_dataset.csv",
    "data/olist_order_reviews_dataset.csv",
    "data/olist_orders_dataset.csv",
    "data/olist_products_dataset.csv",
    "data/olist_sellers_dataset.csv",
    "data/product_category_name_translation.csv"
]

def download_olist_dataset(target_dir: str = "data/raw"):
    target_path = Path(target_dir).resolve()
    target_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Target raw directory: {target_path}")
    downloaded = []
    
    for remote_file in DATA_FILES:
        filename = Path(remote_file).name
        dest_file = target_path / filename
        
        if dest_file.exists() and dest_file.stat().st_size > 100:
            logger.info(f"File already exists: {filename} ({dest_file.stat().st_size / (1024*1024):.2f} MB)")
            downloaded.append(dest_file)
            continue
            
        logger.info(f"Downloading {filename} from {REPO_ID}...")
        try:
            downloaded_temp = hf_hub_download(
                repo_id=REPO_ID,
                filename=remote_file,
                repo_type="dataset",
                local_dir=str(target_path / "temp_hf")
            )
            # Move file to target_dir directly
            import shutil
            shutil.copy2(downloaded_temp, str(dest_file))
            logger.info(f"Saved {filename} ({dest_file.stat().st_size / (1024*1024):.2f} MB)")
            downloaded.append(dest_file)
        except Exception as e:
            logger.error(f"Failed to download {filename}: {e}")
            raise e

    # Clean temp_hf folder
    temp_hf = target_path / "temp_hf"
    if temp_hf.exists():
        import shutil
        shutil.rmtree(str(temp_hf), ignore_errors=True)
        
    logger.info(f"Successfully ensured all {len(downloaded)} Olist dataset files in {target_path}")
    return downloaded

if __name__ == "__main__":
    download_olist_dataset()
