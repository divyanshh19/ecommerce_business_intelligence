# 🛒 E-Commerce Business Intelligence & Customer Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4+-06B6D4?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Supported-003B57?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Tests](https://img.shields.io/badge/Tests-20%20Passed-10b981?style=flat&logo=pytest&logoColor=white)]()

An industry-level, end-to-end Business Intelligence & Customer Analytics Platform designed for modern e-commerce enterprises. Built using the authentic **Brazilian E-Commerce Public Dataset by Olist** (~100,000 orders across 9 relational tables), this platform converts raw transactional, operational, and customer data into interactive executive dashboards, granular RFM customer segmentations, logistics bottleneck analyses, and automated PDF/Excel reports.

Developed to showcase senior practical competencies in **Data Engineering, SQL Analytics, Python Development, Business Intelligence Architecture, and Predictive Insights** for a Data Analyst / Business Analyst role at **Nineleaps**.

---

## 📌 Executive Summary & Key Empirical Findings

From the end-to-end analysis of 100,000 real customer orders, the platform uncovers critical operational and commercial insights:
1. **The Delivery Delay Review Penalty:** Delivery delays represent the single largest driver of customer dissatisfaction. Orders delivered on-time or early boast an average rating of **4.25 to 4.35 ★** (with <7% negative reviews). When a delivery is delayed by 1–3 days, customer satisfaction drops precipitously to **2.30 ★**; orders delayed past 7 days collapse to **1.80 ★** with over **72% 1-star reviews**.
2. **Customer Retention Deficit:** Across the 94,697 unique buyers, the repeat customer rate is only **3.04%** (typical e-commerce benchmarks hover between 15% and 25%), demonstrating an acute need for post-purchase lifecycle retention flows.
3. **Credit Financing Dependency:** Credit cards represent **75.8% of platform GMV** with an average installment financing duration of **3.5 months**. High-ticket categories (Computers, Health & Beauty, Furniture) exhibit installment averages exceeding 5.4 months.
4. **Geographical Logistics Divide:** The Southeast hub (São Paulo - SP) achieves an average delivery transit time of **8.3 days** with a **92.1% on-time delivery rate**. In contrast, Northeast and North territories (Bahia - BA, Ceará - CE, Rio de Janeiro - RJ) average transit times between **16.5 and 20.8 days** with delay rates exceeding 14%.

---

## 🏗️ System Architecture

```
Raw Olist CSV Dataset (9 Files, ~100k Orders)
                    │
                    ▼
       Python Data Ingestion (data_loader.py)
                    │
                    ▼
 Data Cleaning, Imputation & Date Parsing (data_cleaning.py)
                    │
                    ▼
 Referential Integrity & Validation Audit (data_validation.py)
                    │
                    ▼
 Normalized Relational Database (MySQL 8+ / SQLite dual-engine)
                    │
                    ▼
 SQL Analytics & Materialized Views (28 Production Queries)
                    │
                    ▼
     FastAPI Backend API Layer (Uvicorn REST Endpoints)
                    │
                    ▼
   React + Vite + Tailwind + Recharts BI Dashboard (6 Pages)
                    │
                    ▼
 Automated Reporting Center (Downloadable PDF & Multi-Sheet Excel)
```

---

## 🛠️ Technology Stack

| Layer | Technologies | Purpose |
| :--- | :--- | :--- |
| **Backend & Analytics** | Python 3.11+, Pandas, NumPy, Scikit-learn, SQLAlchemy | Data processing, RFM modeling, statistical aggregations, data validation |
| **API Layer** | FastAPI, Uvicorn, Pydantic v2 | High-performance asynchronous RESTful APIs, Swagger/OpenAPI documentation |
| **Database** | MySQL 8.0+ / SQLite 3 (Dual Engine Support) | Normalized relational storage, indexes, views, relational constraints |
| **Frontend Dashboard** | React 18, Vite, Tailwind CSS, Lucide React | Modern executive SaaS web application, reactive state filtering, responsive layout |
| **Visualizations** | Recharts | Interactive Area charts, Bar charts, Donut pies, and Histograms |
| **Automated Reports** | ReportLab, OpenPyXL | Programmatic executive PDF generation and multi-tab Excel workbooks |
| **Testing** | Pytest, FastAPI TestClient | Comprehensive unit tests, ETL tests, SQL validation, and API testing |

---

## 📊 Relational Database Design

The relational database is normalized with strict primary keys, foreign keys, and indexes on join and filter columns (`order_purchase_timestamp`, `customer_id`, `product_id`, `seller_id`, `order_status`):

### Core Tables
1. **`customers`**: `customer_id` (PK), `customer_unique_id`, `customer_zip_code_prefix`, `customer_city`, `customer_state`.
2. **`orders`**: `order_id` (PK), `customer_id` (FK), `order_status`, `order_purchase_timestamp`, `order_approved_at`, `order_delivered_carrier_date`, `order_delivered_customer_date`, `order_estimated_delivery_date`, `actual_delivery_days`, `estimated_delivery_days`, `delivery_delay_days`, `is_delayed`, `is_on_time`.
3. **`order_items`**: `order_id` (FK), `order_item_id`, `product_id` (FK), `seller_id` (FK), `shipping_limit_date`, `price`, `freight_value`, `total_value`.
4. **`products`**: `product_id` (PK), `product_category_name`, `product_category_name_english`, dimensions (`length`, `weight`, `photos`).
5. **`sellers`**: `seller_id` (PK), `seller_zip_code_prefix`, `seller_city`, `seller_state`.
6. **`order_payments`**: `order_id` (FK), `payment_sequential`, `payment_type`, `payment_installments`, `payment_value`.
7. **`order_reviews`**: `review_id`, `order_id` (FK), `review_score` (1-5), comments, timestamps.
8. **`geolocation`**: `geolocation_zip_code_prefix` (PK), representative centroid `lat`, `lng`, `city`, `state`.
9. **`customer_rfm_segments`**: `customer_unique_id` (PK), `recency_days`, `frequency`, `monetary_value`, `r_score`, `f_score`, `m_score`, `rfm_score`, `customer_segment`.
10. **`data_quality_logs`**: Audit trail of ETL execution, completeness, uniqueness, and validity.

---

## 📈 Dashboard Pages (All 6 Implemented)

### 1. Executive Overview (`/`)
- **Headline KPI Scorecard:** Total Gross Revenue, Total Delivered Orders, Unique Active Customers, Average Order Value (AOV), Average Review Score (CSAT), and On-Time Delivery Rate.
- **Monthly Revenue & Order Trajectory:** Interactive multi-year Area Chart displaying monthly sales volume and seasonal peaks.
- **Top Product Categories:** Horizontal ranking of primary merchandise categories.
- **Top 10 Revenue-Generating SKUs:** Detailed listing with category tags, unit velocity, gross revenue, and customer ratings.
- **Regional Performance:** State-by-state order volumes, on-time delivery rates, and average delivery durations.

### 2. Customer Intelligence & RFM Segmentation
- **RFM Quintile Classification:** Custom behavioral segmentation tailored to e-commerce dynamics:
  - *Champions*, *Loyal Customers*, *Potential Loyalists*, *New Customers*, *Promising*, *Need Attention*, *High-Value At Risk*, *At Risk*, and *Lost Customers*.
- **Customer Metrics:** Repeat purchase rate (3.04%), Average Customer Spend (R$ 165.20), Average Frequency (1.03), and Customer Lifetime Value (CLV proxy).
- **Segment Revenue Contribution:** Bar chart comparing total monetary revenue generated by each customer cohort.
- **Prescriptive Marketing Strategies Table:** Prescribed retention actions for each cohort (VIP access, onboarding nurture, win-back discounts).

### 3. Product Analytics
- **Best-Selling Products:** Top revenue-generating products with price, units sold, and star ratings.
- **Underperforming Listings:** Identification of lowest-velocity SKUs indicating pricing resistance or catalog friction.
- **Price Tier Distribution:** Revenue contribution across pricing brackets (Under R$ 25 to Over R$ 500).
- **Category Comparison:** Side-by-side performance of leading merchandise sectors.

### 4. Operations & Logistics Analytics
- **Delivery SLAs:** Average actual delivery days (12.5 days) vs promised delivery date (23.4 days).
- **Regional Fulfillment Disparity:** Comparative analysis of São Paulo (8.3 days, 92% on-time) vs remote states (BA, CE, RJ at 18–21 days).
- **Delivery Delay vs Customer Satisfaction Correlation:** Visualizing the catastrophic drop in review ratings from 4.3★ down to 1.8★ when deliveries exceed promised dates.
- **Fulfillment Funnel:** Order processing stages from order creation to final customer handover.

### 5. Payment Analytics
- **Checkout Rail Market Share:** Credit Card (75.8%), Boleto Bancário (19.0%), Voucher (3.8%), Debit Card (1.4%).
- **Credit Card Installments Breakdown:** Frequency distribution of customer financing duration (1x up to 24x installments).
- **Ticket Economics:** Comparison of average ticket size (AOV) across payment methods.

### 6. Data Quality & Automated Reporting
- **Data Quality Scorecard (97.8% EXCELLENT):** Transparent weighted calculation:
  $$\text{Quality Score} = (0.30 \times \text{Completeness}) + (0.35 \times \text{Integrity}) + (0.25 \times \text{Validity}) + (0.10 \times \text{Uniqueness})$$
- **Table-by-Table Audit Log:** Track records processed (664,474 total), missing values handled, and duplicates removed.
- **Automated Reporting Center:** One-click download of:
  1. Formal **Executive PDF Business Report** (generated with ReportLab).
  2. Multi-tab **Excel Workbook (`.xlsx`)** structured for Power BI import.
  3. Cleaned relational **CSV Datasets**.

---

## 🗄️ SQL Analytics (28 Production Queries)

The file [`backend/sql/analytical_queries.sql`](file:///c:/Desktop/Business%20analyze/backend/sql/analytical_queries.sql) contains **28 heavily annotated SQL queries** demonstrating advanced analytical SQL capabilities:

- **Common Table Expressions (CTEs):** Multi-stage cohort retention, daily moving averages, Pareto cumulative distribution.
- **Window Functions:**
  - `LAG()`: Month-over-Month (MoM) revenue growth calculation.
  - `SUM() OVER (ORDER BY ... ROWS UNBOUNDED PRECEDING)`: Cumulative running lifetime revenue.
  - `ROW_NUMBER() OVER (PARTITION BY category ORDER BY sales DESC)`: Top 3 products within each merchandise category.
  - `NTILE(5)`: Quintile scoring for Recency, Frequency, and Monetary dimensions.
  - `DENSE_RANK()`, `RANK()`: Seller revenue performance ranking.
- **Analytical Joins & Aggregations:** Self-joins for product cross-selling affinity, conditional aggregations (`CASE WHEN`), datetime timestamp difference math.

---

## 🚀 Installation & Local Setup

### 1. Prerequisites
- Python 3.11+
- Node.js v18+ and npm
- (Optional) MySQL 8.0+ if using MySQL backend (the system auto-defaults to high-performance indexed SQLite for zero-config immediate execution)

### 2. Clone and Setup Environment
```bash
# Clone the repository
git clone <repository_url>
cd "Business analyze"

# Install backend dependencies
python -m pip install -r backend/requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 3. Environment Configuration (`.env`)
Create a `.env` file in the root directory (or use `.env.example`):
```ini
# Default SQLite configuration (Ready immediately)
DATABASE_URL=sqlite:///data/olist_bi.db

# Or for MySQL 8+:
# DATABASE_URL=mysql+pymysql://root:password@localhost:3306/olist_bi
```

### 4. Run the Python ETL Pipeline
The ETL pipeline automatically checks for the authentic Olist CSV files, downloads them if missing, cleans and imputes missing attributes, verifies referential integrity, computes customer RFM quintiles, populates the database, and creates analytical views:
```bash
python backend/etl/etl_pipeline.py
```

### 5. Start the Application

#### Start Backend API (FastAPI)
```bash
python backend/app/main.py
# Or using uvicorn directly:
# uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation (Swagger UI) is accessible at: **`http://localhost:8000/docs`**

#### Start Frontend Dashboard (React + Vite)
In a separate terminal:
```bash
cd frontend
npm run dev
```
Open your browser at: **`http://localhost:5173`**

---

## 🧪 Test Execution & Validation

Run the complete automated test suite covering data cleaning, quality audits, SQL analytical queries, and API endpoints:
```bash
python -m pytest tests/ -v
```

### Test Suite Summary:
- **`tests/test_cleaning.py`**: Unit tests for customer deduplication, order datetime conversion, metric derivation, and product translation imputation.
- **`tests/test_validation.py`**: Referential integrity checks, constraint adherence, and quality score calculations.
- **`tests/test_sql_queries.py`**: Real database query tests validating top products, category GMV, RFM distribution, and delay correlation.
- **`tests/test_api.py`**: End-to-end integration tests verifying all 12 FastAPI endpoints return actual database records.

Result: **20 passed in 95s (100% test pass rate)**.

---

## 💡 Prescriptive Business Recommendations

Based on the empirical analysis of the Olist e-commerce dataset:

1. **Decentralized Regional Fulfillment in the Northeast:**
   - *Problem:* Deliveries to Bahia (BA) and Ceará (CE) average 18 to 21 days with 14%+ delay rates, compared to São Paulo's 8.3 days.
   - *Action:* Partner with regional 3PL logistics centers in Salvador and Recife to pre-position top-selling SKUs (Health & Beauty, Bed & Bath), cutting transit times by up to 60%.
2. **Automated CRM Journeys for Single-Order Buyers:**
   - *Problem:* A repeat purchase rate of only 3.04% indicates massive customer attrition post-first transaction.
   - *Action:* Trigger automated lifecycle marketing sequences at Day 25 post-delivery offering an exclusive 10% discount on complementary categories for *Potential Loyalists* and *New Customers*.
3. **Proactive Delivery Delay Mitigation:**
   - *Problem:* Ratings drop from 4.3★ to 1.8★ when deliveries are delayed past 3 days.
   - *Action:* Implement automated tracking webhooks that alert customers 24 hours prior to an impending delay and automatically credit R$ 15 in platform freight vouchers before negative sentiment is posted.
4. **Co-Marketed Installment Financing for High-Ticket Goods:**
   - *Problem:* Credit card orders represent 75.8% of GMV with an average of 3.5 installments.
   - *Action:* Partner with payment gateways to offer subsidized 6x–10x interest-free financing on tickets above R$ 250, lowering barrier-to-entry for furniture and electronics.
5. **Seller Packaging Standards in High-Defect Categories:**
   - *Problem:* Office Furniture and Bed Bath Table experience elevated return and negative review rates.
   - *Action:* Institute mandatory packaging certification standards for sellers in fragile/heavy categories to minimize transit damage.

---

## 🔮 Future Improvements

1. **Predictive Churn Modeling:** Implement a Machine Learning classification model (Random Forest / XGBoost) predicting customer churn probability based on browsing and order recency.
2. **Real-time Kafka / CDC Pipeline:** Transition from batch ETL to streaming change data capture (Debezium/Kafka) for real-time order tracking.
3. **Automated Sentiment Analysis on Customer Reviews:** Integrate NLP sentiment models (DistilBERT / VADER) to extract granular root-cause topics from Portuguese review messages.
4. **Interactive Geospatial Map Visualizations:** Integrate Mapbox / Leaflet to visualize live delivery routes and seller-to-buyer geographic vector flows.

---

## 👨‍💻 Project Developer Information
- **Role Target:** Data Analyst / Business Analyst (Nineleaps)
- **Primary Competencies:** Python, SQL, Data Modeling, ETL Pipelines, Business Intelligence Architecture, FastAPI, React Dashboard Engineering.
