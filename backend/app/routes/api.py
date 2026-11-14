"""
Module: api.py
Purpose: FastAPI REST endpoints for the E-Commerce Business Intelligence Platform.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse

from backend.app.services.analytics_service import AnalyticsService
from backend.reports.report_generator import ReportGenerator

router = APIRouter(prefix="/api", tags=["Analytics"])
analytics_service = AnalyticsService()
report_generator = ReportGenerator()

@router.get("/dashboard/overview")
def get_dashboard_overview(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    category: Optional[str] = Query(None, description="Category filter"),
    state: Optional[str] = Query(None, description="State code filter (e.g. SP, RJ)")
):
    """Headline KPIs, revenue trends, top categories, and geographical distribution."""
    return analytics_service.get_executive_overview(
        start_date=start_date,
        end_date=end_date,
        category=category,
        state=state
    )

@router.get("/sales/trends")
def get_sales_trends(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Daily sales trajectory and 7-day rolling average."""
    return analytics_service.get_sales_trends(start_date=start_date, end_date=end_date)

@router.get("/sales/categories")
def get_sales_categories(
    limit: int = Query(25, ge=1, le=100, description="Number of categories to return")
):
    """Category breakdown by order volume, GMV, and customer review scores."""
    return analytics_service.get_category_analytics(limit=limit)

@router.get("/customers/segments")
def get_customer_segments():
    """RFM customer segmentation counts, revenue contributions, and averages."""
    rfm_data = analytics_service.get_rfm_analytics()
    return rfm_data.get("segments", [])

@router.get("/customers/rfm")
def get_customer_rfm():
    """Complete RFM intelligence including distributions, repeat rate, and CLV proxy."""
    return analytics_service.get_rfm_analytics()

@router.get("/products/top")
def get_top_products(
    limit: int = Query(10, ge=1, le=50, description="Top products limit")
):
    """Top revenue-generating products across the platform."""
    data = analytics_service.get_product_analytics(limit=limit)
    return data.get("top_products", [])

@router.get("/products/performance")
def get_product_performance(
    limit: int = Query(15, ge=1, le=50, description="Limit for top/bottom lists")
):
    """Comprehensive product analytics: top-sellers, lowest-sellers, and price distribution."""
    return analytics_service.get_product_analytics(limit=limit)

@router.get("/operations/delivery")
def get_operations_delivery(
    state: Optional[str] = Query(None, description="State code filter")
):
    """Delivery operational performance, on-time rates, regional transit times, and delay impact."""
    return analytics_service.get_delivery_operations(state=state)

@router.get("/payments/analysis")
def get_payment_analysis():
    """Payment methods breakdown, installment usage, and trends."""
    return analytics_service.get_payment_analytics()

@router.get("/reviews/analysis")
def get_reviews_analysis():
    """Customer satisfaction distribution, category ratings, and sentiment metrics."""
    return analytics_service.get_review_analytics()

@router.get("/data-quality")
def get_data_quality():
    """Data quality scorecard, completeness, uniqueness, and referential integrity audit."""
    return analytics_service.get_data_quality_report()

@router.get("/reports/export")
def export_reports(
    format: str = Query("pdf", pattern="^(pdf|excel|csv)$", description="Export format: pdf, excel, or csv")
):
    """Download executive PDF report, multi-sheet Excel workbook, or processed CSVs."""
    try:
        if format == "pdf":
            pdf_path = report_generator.generate_pdf_report("Executive_BI_Report.pdf")
            return FileResponse(
                path=pdf_path,
                filename="Executive_BI_Report.pdf",
                media_type="application/pdf"
            )
        elif format == "excel":
            excel_path = report_generator.export_all_tables_to_excel("Olist_BI_Analytical_Export.xlsx")
            return FileResponse(
                path=excel_path,
                filename="Olist_BI_Analytical_Export.xlsx",
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        elif format == "csv":
            csv_path = Path("data/processed/clean_orders.csv")
            if not csv_path.exists():
                raise HTTPException(status_code=404, detail="Processed CSV not found. Please run ETL first.")
            return FileResponse(
                path=str(csv_path),
                filename="clean_orders.csv",
                media_type="text/csv"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report export failed: {str(e)}")
