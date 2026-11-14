-- ========================================================================
-- E-COMMERCE BUSINESS INTELLIGENCE & CUSTOMER ANALYTICS PLATFORM
-- Normalized Relational Database Schema & Analytical Views (MySQL 8+ / ANSI SQL)
-- ========================================================================

-- Drop views if exist
DROP VIEW IF EXISTS view_seller_rankings;
DROP VIEW IF EXISTS view_payment_method_breakdown;
DROP VIEW IF EXISTS view_regional_delivery_performance;
DROP VIEW IF EXISTS view_category_performance;
DROP VIEW IF EXISTS view_customer_rfm_summary;
DROP VIEW IF EXISTS view_executive_monthly_kpis;

-- Drop tables in reverse order of foreign key dependencies
DROP TABLE IF EXISTS customer_rfm_segments;
DROP TABLE IF EXISTS data_quality_logs;
DROP TABLE IF EXISTS order_reviews;
DROP TABLE IF EXISTS order_payments;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS product_category_translation;
DROP TABLE IF EXISTS sellers;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS geolocation;

-- ========================================================================
-- 1. BASE RELATIONAL TABLES
-- ========================================================================

-- Customers Table
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50) NOT NULL,
    customer_zip_code_prefix INT,
    customer_city VARCHAR(100),
    customer_state VARCHAR(10)
);
CREATE INDEX idx_customers_unique_id ON customers(customer_unique_id);
CREATE INDEX idx_customers_state ON customers(customer_state);
CREATE INDEX idx_customers_zip ON customers(customer_zip_code_prefix);

-- Sellers Table
CREATE TABLE sellers (
    seller_id VARCHAR(50) PRIMARY KEY,
    seller_zip_code_prefix INT,
    seller_city VARCHAR(100),
    seller_state VARCHAR(10)
);
CREATE INDEX idx_sellers_state ON sellers(seller_state);
CREATE INDEX idx_sellers_zip ON sellers(seller_zip_code_prefix);

-- Category Translation Table
CREATE TABLE product_category_translation (
    product_category_name VARCHAR(100) PRIMARY KEY,
    product_category_name_english VARCHAR(100) NOT NULL
);

-- Products Table
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_category_name VARCHAR(100),
    product_category_name_english VARCHAR(100),
    product_name_length INT,
    product_description_length INT,
    product_photos_qty INT,
    product_weight_g FLOAT,
    product_length_cm FLOAT,
    product_height_cm FLOAT,
    product_width_cm FLOAT
);
CREATE INDEX idx_products_category ON products(product_category_name);
CREATE INDEX idx_products_category_en ON products(product_category_name_english);

-- Geolocation Table (Aggregated by zip code prefix)
CREATE TABLE geolocation (
    geolocation_zip_code_prefix INT PRIMARY KEY,
    geolocation_lat DOUBLE,
    geolocation_lng DOUBLE,
    geolocation_city VARCHAR(100),
    geolocation_state VARCHAR(10)
);
CREATE INDEX idx_geo_state ON geolocation(geolocation_state);

-- Orders Table
CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    order_status VARCHAR(30) NOT NULL,
    order_purchase_timestamp DATETIME NOT NULL,
    order_approved_at DATETIME,
    order_delivered_carrier_date DATETIME,
    order_delivered_customer_date DATETIME,
    order_estimated_delivery_date DATETIME,
    actual_delivery_days FLOAT,
    estimated_delivery_days FLOAT,
    delivery_delay_days FLOAT,
    is_delivered INT DEFAULT 0,
    is_delayed INT DEFAULT 0,
    is_on_time INT DEFAULT 1,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_purchase_date ON orders(order_purchase_timestamp);
CREATE INDEX idx_orders_status ON orders(order_status);
CREATE INDEX idx_orders_delivery_customer ON orders(order_delivered_customer_date);

-- Order Items Table
CREATE TABLE order_items (
    order_id VARCHAR(50) NOT NULL,
    order_item_id INT NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    seller_id VARCHAR(50) NOT NULL,
    shipping_limit_date DATETIME,
    price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    freight_value DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    total_value DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    PRIMARY KEY (order_id, order_item_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
);
CREATE INDEX idx_items_product ON order_items(product_id);
CREATE INDEX idx_items_seller ON order_items(seller_id);
CREATE INDEX idx_items_price ON order_items(price);

-- Order Payments Table
CREATE TABLE order_payments (
    order_id VARCHAR(50) NOT NULL,
    payment_sequential INT NOT NULL,
    payment_type VARCHAR(30) NOT NULL,
    payment_installments INT NOT NULL DEFAULT 1,
    payment_value DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    PRIMARY KEY (order_id, payment_sequential),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
CREATE INDEX idx_payments_order ON order_payments(order_id);
CREATE INDEX idx_payments_type ON order_payments(payment_type);

-- Order Reviews Table
CREATE TABLE order_reviews (
    review_id VARCHAR(50) NOT NULL,
    order_id VARCHAR(50) NOT NULL,
    review_score INT NOT NULL,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date DATETIME,
    review_answer_timestamp DATETIME,
    PRIMARY KEY (review_id, order_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
CREATE INDEX idx_reviews_score ON order_reviews(review_score);
CREATE INDEX idx_reviews_order ON order_reviews(order_id);

-- Customer RFM Analytics Table
CREATE TABLE customer_rfm_segments (
    customer_unique_id VARCHAR(50) PRIMARY KEY,
    recency_days INT NOT NULL,
    frequency INT NOT NULL,
    monetary_value DECIMAL(12, 2) NOT NULL,
    r_score INT NOT NULL,
    f_score INT NOT NULL,
    m_score INT NOT NULL,
    rfm_score VARCHAR(10) NOT NULL,
    customer_segment VARCHAR(50) NOT NULL,
    first_purchase_date DATETIME,
    last_purchase_date DATETIME,
    avg_order_value DECIMAL(10, 2),
    calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_rfm_segment ON customer_rfm_segments(customer_segment);
CREATE INDEX idx_rfm_recency ON customer_rfm_segments(recency_days);
CREATE INDEX idx_rfm_monetary ON customer_rfm_segments(monetary_value);

-- Data Quality & Audit Logs Table
CREATE TABLE data_quality_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    total_records INT NOT NULL,
    valid_records INT NOT NULL,
    missing_values INT NOT NULL,
    duplicate_records INT NOT NULL,
    quality_score FLOAT NOT NULL,
    executed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ========================================================================
-- 2. ANALYTICAL REPORTING VIEWS
-- ========================================================================

-- View 1: Executive Monthly KPIs (Revenue, Orders, AOV, Customers)
CREATE VIEW view_executive_monthly_kpis AS
SELECT 
    DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') AS order_year_month,
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
GROUP BY DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m');

-- View 2: Category Performance View
CREATE VIEW view_category_performance AS
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

-- View 3: Regional Delivery Performance View
CREATE VIEW view_regional_delivery_performance AS
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

-- View 4: Payment Method Breakdown View
CREATE VIEW view_payment_method_breakdown AS
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

-- View 5: Customer RFM Segment Summary View
CREATE VIEW view_customer_rfm_summary AS
SELECT 
    customer_segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(recency_days), 1) AS avg_recency_days,
    ROUND(AVG(frequency), 2) AS avg_order_frequency,
    ROUND(AVG(monetary_value), 2) AS avg_customer_spend,
    ROUND(SUM(monetary_value), 2) AS total_segment_revenue,
    ROUND((COUNT(*) * 100.0) / (SELECT COUNT(*) FROM customer_rfm_segments), 2) AS pct_of_customer_base
FROM customer_rfm_segments
GROUP BY customer_segment;

-- View 6: Top Seller Rankings View
CREATE VIEW view_seller_rankings AS
SELECT 
    s.seller_id,
    s.seller_city,
    s.seller_state,
    COUNT(DISTINCT oi.order_id) AS total_orders_fulfilled,
    COUNT(oi.product_id) AS total_items_sold,
    ROUND(SUM(oi.price), 2) AS total_seller_gmv,
    ROUND(AVG(r.review_score), 2) AS avg_seller_rating,
    DENSE_RANK() OVER (ORDER BY SUM(oi.price) DESC) AS seller_revenue_rank
FROM sellers s
JOIN order_items oi ON s.seller_id = oi.seller_id
JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN order_reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY s.seller_id, s.seller_city, s.seller_state;
