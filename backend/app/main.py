"""
Module: main.py
Purpose: FastAPI entry point for E-Commerce BI Platform.
"""

import sys
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.database import engine
from backend.app.routes.api import router as analytics_router

app = FastAPI(
    title="E-Commerce Business Intelligence & Customer Analytics API",
    description="Enterprise Analytics API powering executive dashboards, RFM customer segmentation, logistics monitoring, and automated reporting on the Olist Brazilian E-Commerce dataset.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend applications (Vite default port 5173, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Analytics API Router
app.include_router(analytics_router)

@app.get("/", tags=["System"])
def root():
    """Platform health and API status."""
    return {
        "platform": "E-Commerce Business Intelligence & Customer Analytics Platform",
        "dataset": "Brazilian E-Commerce Public Dataset by Olist",
        "status": "ONLINE",
        "docs_url": "/docs",
        "database_engine": str(engine.url).split(":")[0]
    }

@app.get("/health", tags=["System"])
def health_check():
    """Verify database connectivity and table readiness."""
    try:
        with engine.connect() as conn:
            orders_count = conn.execute(text("SELECT COUNT(*) FROM orders;")).scalar()
            customers_count = conn.execute(text("SELECT COUNT(*) FROM customers;")).scalar()
        return {
            "status": "HEALTHY",
            "database_connected": True,
            "orders_loaded": orders_count,
            "customers_loaded": customers_count
        }
    except Exception as e:
        return {
            "status": "DEGRADED",
            "database_connected": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
