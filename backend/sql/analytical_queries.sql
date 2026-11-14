-- ========================================================================
-- E-COMMERCE BUSINESS INTELLIGENCE & CUSTOMER ANALYTICS PLATFORM
-- 28 Comprehensive SQL Analytical Queries
-- Demonstrating: CTEs, Window Functions, Joins, Aggregations, Cohorts, Trends
-- ========================================================================

-- ------------------------------------------------------------------------
-- QUERY 1: Top 10 Revenue-Generating Products
-- Demonstrates: INNER JOIN, GROUP BY, Aggregation, ORDER BY, LIMIT
-- Business Question: Which specific products generated the highest cumulative revenue?
-- ------------------------------------------------------------------------
SELECT 
    p.product_id,
    COALESCE(p.product_category_name_english, 'Other') AS category,
    COUNT(oi.order_item_id) AS units_sold,
    ROUND(SUM(oi.price), 2) AS total_revenue,
    ROUND(AVG(oi.price), 2) AS avg_unit_price,
    ROUND(AVG(r.review_score), 2) AS avg_rating
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN order_reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY p.product_id, p.product_category_name_english
ORDER BY total_revenue DESC
LIMIT 10;

-- ------------------------------------------------------------------------
-- QUERY 2: Monthly Revenue, Order Volume, and Month-over-Month (MoM) Growth
-- Demonstrates: CTE, LAG() Window Function, Date formatting, Percentage calculation
-- Business Question: How has revenue progressed monthly, and what is our MoM growth rate?
-- ------------------------------------------------------------------------
WITH MonthlySales AS (
    SELECT 
        DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') AS sales_month,
        COUNT(DISTINCT o.order_id) AS total_orders,
        ROUND(SUM(oi.price), 2) AS monthly_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status <> 'canceled'
    GROUP BY DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m')
)
SELECT 
    sales_month,
    total_orders,
    monthly_revenue,
    LAG(monthly_revenue, 1) OVER (ORDER BY sales_month) AS previous_month_revenue,
    ROUND(
        ((monthly_revenue - LAG(monthly_revenue, 1) OVER (ORDER BY sales_month)) / 
        NULLIF(LAG(monthly_revenue, 1) OVER (ORDER BY sales_month), 0)) * 100.0, 
        2
    ) AS mom_growth_pct
FROM MonthlySales
ORDER BY sales_month;

-- ------------------------------------------------------------------------
-- QUERY 3: Cumulative Running Monthly Revenue
-- Demonstrates: Window Function SUM() OVER (ORDER BY ...)
-- Business Question: What is the cumulative lifetime sales trajectory across months?
-- ------------------------------------------------------------------------
WITH MonthlyTotals AS (
    SELECT 
        DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') AS year_month,
        ROUND(SUM(oi.price + oi.freight_value), 2) AS monthly_gross_revenue,
        COUNT(DISTINCT o.order_id) AS orders_count
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m')
)
SELECT 
    year_month,
    monthly_gross_revenue,
    orders_count,
    ROUND(SUM(monthly_gross_revenue) OVER (ORDER BY year_month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS running_total_revenue
FROM MonthlyTotals
ORDER BY year_month;

-- ------------------------------------------------------------------------
-- QUERY 4: Repeat Customers and Multi-Purchase Frequency Distribution
-- Demonstrates: Subquery, GROUP BY, HAVING, CASE statement
-- Business Question: What proportion of our customer base purchases more than once?
-- ------------------------------------------------------------------------
WITH CustomerOrderCounts AS (
    SELECT 
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS total_purchases,
        SUM(oi.price) AS total_spend
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
)
SELECT 
    CASE 
        WHEN total_purchases = 1 THEN '1 Single Purchase'
        WHEN total_purchases = 2 THEN '2 Repeat Purchases'
        WHEN total_purchases BETWEEN 3 AND 5 THEN '3-5 Frequent Purchases'
        ELSE '6+ VIP Purchases'
    END AS purchase_frequency_tier,
    COUNT(*) AS customer_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM CustomerOrderCounts), 2) AS customer_share_pct,
    ROUND(AVG(total_spend), 2) AS avg_segment_spend
FROM CustomerOrderCounts
GROUP BY purchase_frequency_tier
ORDER BY customer_count DESC;

-- ------------------------------------------------------------------------
-- QUERY 5: Overall and Yearly Average Order Value (AOV)
-- Demonstrates: Multi-level aggregation, YEAR() extraction
-- Business Question: How does our ticket size / AOV vary by operational year?
-- ------------------------------------------------------------------------
SELECT 
    YEAR(o.order_purchase_timestamp) AS order_year,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(oi.price), 2) AS total_items_value,
    ROUND(SUM(oi.freight_value), 2) AS total_freight_value,
    ROUND(SUM(oi.price + oi.freight_value), 2) AS total_order_value,
    ROUND(SUM(oi.price + oi.freight_value) / COUNT(DISTINCT o.order_id), 2) AS average_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY YEAR(o.order_purchase_timestamp)
ORDER BY order_year;

-- ------------------------------------------------------------------------
-- QUERY 6: Category Performance Ranked by Revenue
-- Demonstrates: DENSE_RANK() Window Function, GROUP BY, Aggregations
-- Business Question: What are our leading revenue categories and their rank?
-- ------------------------------------------------------------------------
SELECT 
    COALESCE(p.product_category_name_english, 'Other') AS category_name,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    COUNT(oi.product_id) AS total_items_sold,
    ROUND(SUM(oi.price), 2) AS total_gmv,
    ROUND(AVG(oi.price), 2) AS avg_item_price,
    DENSE_RANK() OVER (ORDER BY SUM(oi.price) DESC) AS category_revenue_rank
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY COALESCE(p.product_category_name_english, 'Other')
ORDER BY category_revenue_rank
LIMIT 15;

-- ------------------------------------------------------------------------
-- QUERY 7: Dormant / At-Risk Customer Identification (> 180 Days Inactive)
-- Demonstrates: DATEDIFF, Subqueries, Reference Anchor Date
-- Business Question: Who are high-value customers who haven't ordered recently?
-- ------------------------------------------------------------------------
WITH CustomerActivity AS (
    SELECT 
        c.customer_unique_id,
        c.customer_state,
        MAX(o.order_purchase_timestamp) AS last_purchase_date,
        COUNT(DISTINCT o.order_id) AS lifetime_orders,
        ROUND(SUM(oi.price), 2) AS lifetime_spend
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id, c.customer_state
)
SELECT 
    customer_unique_id,
    customer_state,
    last_purchase_date,
    DATEDIFF((SELECT MAX(order_purchase_timestamp) FROM orders), last_purchase_date) AS days_since_last_purchase,
    lifetime_orders,
    lifetime_spend
FROM CustomerActivity
WHERE DATEDIFF((SELECT MAX(order_purchase_timestamp) FROM orders), last_purchase_date) > 180
  AND lifetime_spend > 250.00
ORDER BY lifetime_spend DESC
LIMIT 20;

-- ------------------------------------------------------------------------
-- QUERY 8: Top Sellers Ranked by Revenue and Rating
-- Demonstrates: RANK(), DENSE_RANK(), HAVING, Multi-table JOIN
-- Business Question: Who are our top-performing merchants driving gross volume?
-- ------------------------------------------------------------------------
SELECT 
    s.seller_id,
    s.seller_state,
    COUNT(DISTINCT oi.order_id) AS orders_handled,
    COUNT(oi.product_id) AS units_sold,
    ROUND(SUM(oi.price), 2) AS total_revenue_generated,
    ROUND(AVG(r.review_score), 2) AS seller_avg_rating,
    RANK() OVER (ORDER BY SUM(oi.price) DESC) AS seller_rank
FROM sellers s
JOIN order_items oi ON s.seller_id = oi.seller_id
JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN order_reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY s.seller_id, s.seller_state
HAVING total_revenue_generated >= 5000.00
ORDER BY seller_rank
LIMIT 15;

-- ------------------------------------------------------------------------
-- QUERY 9: Delivery Delay Rate and Average Delay by Destination State
-- Demonstrates: CASE WHEN, Conditional Aggregation, Ordering
-- Business Question: Which destination states face the highest delivery delay risk?
-- ------------------------------------------------------------------------
SELECT 
    c.customer_state,
    COUNT(o.order_id) AS total_deliveries,
    SUM(CASE WHEN o.is_delayed = 1 THEN 1 ELSE 0 END) AS delayed_orders,
    ROUND(SUM(CASE WHEN o.is_delayed = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(o.order_id), 2) AS delay_rate_pct,
    ROUND(AVG(o.actual_delivery_days), 1) AS avg_delivery_days,
    ROUND(AVG(CASE WHEN o.is_delayed = 1 THEN o.delivery_delay_days ELSE NULL END), 1) AS avg_days_overdue
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
GROUP BY c.customer_state
HAVING total_deliveries >= 50
ORDER BY delay_rate_pct DESC;

-- ------------------------------------------------------------------------
-- QUERY 10: Empirical Correlation Between Delivery Delays and Review Scores
-- Demonstrates: CASE WHEN classification, Aggregation, Cross-Module BI
-- Business Question: Exactly how severely does delivery lateness penalize ratings?
-- ------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN o.delivery_delay_days <= -7 THEN 'More than 7 Days Early'
        WHEN o.delivery_delay_days BETWEEN -6.99 AND -1 THEN '1 to 6 Days Early'
        WHEN o.delivery_delay_days BETWEEN -0.99 AND 0 THEN 'Exact On-Time'
        WHEN o.delivery_delay_days BETWEEN 0.01 AND 3 THEN '1 to 3 Days Late'
        WHEN o.delivery_delay_days BETWEEN 3.01 AND 7 THEN '4 to 7 Days Late'
        ELSE 'More than 7 Days Severely Late'
    END AS delivery_performance_bucket,
    COUNT(r.review_id) AS total_reviews,
    ROUND(AVG(r.review_score), 2) AS avg_review_score,
    ROUND(SUM(CASE WHEN r.review_score = 5 THEN 1 ELSE 0 END) * 100.0 / COUNT(r.review_id), 1) AS five_star_pct,
    ROUND(SUM(CASE WHEN r.review_score <= 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(r.review_id), 1) AS negative_review_pct
FROM orders o
JOIN order_reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
GROUP BY delivery_performance_bucket
ORDER BY avg_review_score DESC;

-- ------------------------------------------------------------------------
-- QUERY 11: Customer RFM Quintile Scoring with NTILE()
-- Demonstrates: CTE, NTILE(5) Window Function for Recency, Frequency, Monetary
-- Business Question: How do customers rank across empirical 1-5 RFM tiers?
-- ------------------------------------------------------------------------
WITH CustomerAggs AS (
    SELECT 
        c.customer_unique_id,
        DATEDIFF((SELECT MAX(order_purchase_timestamp) FROM orders), MAX(o.order_purchase_timestamp)) AS recency,
        COUNT(DISTINCT o.order_id) AS frequency,
        SUM(oi.price) AS monetary
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
),
RFMTiers AS (
    SELECT 
        customer_unique_id,
        recency,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY recency DESC) AS r_tile,
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_tile,
        NTILE(5) OVER (ORDER BY monetary ASC) AS m_tile
    FROM CustomerAggs
)
SELECT 
    customer_unique_id,
    recency,
    frequency,
    ROUND(monetary, 2) AS monetary,
    r_tile,
    f_tile,
    m_tile,
    CONCAT(r_tile, f_tile, m_tile) AS rfm_composite
FROM RFMTiers
LIMIT 20;

-- ------------------------------------------------------------------------
-- QUERY 12: Top 3 Best-Selling Products per Category using ROW_NUMBER()
-- Demonstrates: ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)
-- Business Question: What are the top 3 items within each product category?
-- ------------------------------------------------------------------------
WITH CategoryRankedProducts AS (
    SELECT 
        COALESCE(p.product_category_name_english, 'Other') AS category,
        p.product_id,
        COUNT(oi.order_item_id) AS units_sold,
        ROUND(SUM(oi.price), 2) AS gmv,
        ROW_NUMBER() OVER (
            PARTITION BY COALESCE(p.product_category_name_english, 'Other') 
            ORDER BY SUM(oi.price) DESC
        ) AS rank_in_category
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY COALESCE(p.product_category_name_english, 'Other'), p.product_id
)
SELECT 
    category,
    product_id,
    units_sold,
    gmv,
    rank_in_category
FROM CategoryRankedProducts
WHERE rank_in_category <= 3
ORDER BY category, rank_in_category;

-- ------------------------------------------------------------------------
-- QUERY 13: Payment Method Distribution and Installment Analysis
-- Demonstrates: Aggregation, Installment distribution, Payment share
-- Business Question: What is the preferred payment rail and average financing term?
-- ------------------------------------------------------------------------
SELECT 
    payment_type,
    COUNT(*) AS total_transactions,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM order_payments), 2) AS transaction_share_pct,
    ROUND(SUM(payment_value), 2) AS total_payment_volume,
    ROUND(SUM(payment_value) * 100.0 / (SELECT SUM(payment_value) FROM order_payments), 2) AS gmv_share_pct,
    ROUND(AVG(payment_installments), 1) AS avg_installments,
    MAX(payment_installments) AS max_installments
FROM order_payments
GROUP BY payment_type
ORDER BY total_payment_volume DESC;

-- ------------------------------------------------------------------------
-- QUERY 14: Freight-to-Price Ratio Analysis by Customer State
-- Demonstrates: Mathematical ratios, Freight burden analysis
-- Business Question: Where does shipping cost form an excessive friction barrier?
-- ------------------------------------------------------------------------
SELECT 
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(oi.price), 2) AS total_merchandise_val,
    ROUND(SUM(oi.freight_value), 2) AS total_freight_val,
    ROUND(AVG(oi.freight_value), 2) AS avg_freight_per_item,
    ROUND((SUM(oi.freight_value) / NULLIF(SUM(oi.price), 0)) * 100.0, 2) AS freight_burden_pct
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
HAVING total_orders >= 100
ORDER BY freight_burden_pct DESC;

-- ------------------------------------------------------------------------
-- QUERY 15: Average Operational Handling Time: Purchase to Carrier Dispatch
-- Demonstrates: Date math, Timestamp differences, Fulfillment efficiency
-- Business Question: How long does dispatch take before handing to carrier?
-- ------------------------------------------------------------------------
SELECT 
    DATE_FORMAT(order_purchase_timestamp, '%Y-%m') AS order_month,
    COUNT(order_id) AS total_shipped_orders,
    ROUND(AVG(TIMESTAMPDIFF(HOUR, order_purchase_timestamp, order_approved_at)), 1) AS avg_hours_to_approve,
    ROUND(AVG(TIMESTAMPDIFF(HOUR, order_approved_at, order_delivered_carrier_date) / 24.0), 1) AS avg_days_to_carrier,
    ROUND(AVG(actual_delivery_days), 1) AS avg_total_delivery_days
FROM orders
WHERE order_status = 'delivered'
  AND order_approved_at IS NOT NULL
  AND order_delivered_carrier_date IS NOT NULL
GROUP BY DATE_FORMAT(order_purchase_timestamp, '%Y-%m')
ORDER BY order_month;

-- ------------------------------------------------------------------------
-- QUERY 16: Customer Retention and Cohort First-Purchase Activity
-- Demonstrates: Cohort grouping, CTE, Multi-period customer tracking
-- Business Question: When did our active customers originate, and how many repeat?
-- ------------------------------------------------------------------------
WITH CustomerCohorts AS (
    SELECT 
        c.customer_unique_id,
        DATE_FORMAT(MIN(o.order_purchase_timestamp), '%Y-%m') AS cohort_month,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(oi.price) AS lifetime_value
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
)
SELECT 
    cohort_month,
    COUNT(customer_unique_id) AS cohort_size,
    SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) AS repeat_customers_count,
    ROUND(SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(customer_unique_id), 2) AS cohort_retention_rate_pct,
    ROUND(AVG(lifetime_value), 2) AS avg_cohort_clv
FROM CustomerCohorts
GROUP BY cohort_month
ORDER BY cohort_month;

-- ------------------------------------------------------------------------
-- QUERY 17: Product Categories with the Highest Negative Review Concentration
-- Demonstrates: CASE WHEN, Negative ratio calculation, HAVING
-- Business Question: Which categories suffer from quality or description mismatches?
-- ------------------------------------------------------------------------
SELECT 
    COALESCE(p.product_category_name_english, 'Other') AS category,
    COUNT(r.review_id) AS total_reviews,
    ROUND(AVG(r.review_score), 2) AS avg_score,
    SUM(CASE WHEN r.review_score IN (1, 2) THEN 1 ELSE 0 END) AS negative_reviews,
    ROUND(SUM(CASE WHEN r.review_score IN (1, 2) THEN 1 ELSE 0 END) * 100.0 / COUNT(r.review_id), 2) AS negative_review_pct
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
JOIN order_reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY COALESCE(p.product_category_name_english, 'Other')
HAVING total_reviews >= 100
ORDER BY negative_review_pct DESC
LIMIT 15;

-- ------------------------------------------------------------------------
-- QUERY 18: High-Value Orders Exceeding the 95th Percentile Order Value
-- Demonstrates: Subqueries, Statistical boundary detection
-- Business Question: What items and categories comprise our highest-value baskets?
-- ------------------------------------------------------------------------
WITH OrderTotals AS (
    SELECT 
        order_id,
        SUM(price + freight_value) AS order_gross_val
    FROM order_items
    GROUP BY order_id
)
SELECT 
    o.order_id,
    c.customer_state,
    ot.order_gross_val,
    p.payment_type,
    p.payment_installments
FROM OrderTotals ot
JOIN orders o ON ot.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN order_payments p ON o.order_id = p.order_id
WHERE ot.order_gross_val >= 500.00
ORDER BY ot.order_gross_val DESC
LIMIT 20;

-- ------------------------------------------------------------------------
-- QUERY 19: Cross-Selling Affinity: Product Categories Purchased in Same Order
-- Demonstrates: Self-Join on order_items, Condition oi1.category < oi2.category
-- Business Question: Which category pairs are most frequently co-purchased?
-- ------------------------------------------------------------------------
SELECT 
    p1.product_category_name_english AS category_a,
    p2.product_category_name_english AS category_b,
    COUNT(DISTINCT oi1.order_id) AS co_occurrence_count
FROM order_items oi1
JOIN order_items oi2 ON oi1.order_id = oi2.order_id AND oi1.order_item_id < oi2.order_item_id
JOIN products p1 ON oi1.product_id = p1.product_id
JOIN products p2 ON oi2.product_id = p2.product_id
WHERE p1.product_category_name_english <> p2.product_category_name_english
GROUP BY p1.product_category_name_english, p2.product_category_name_english
ORDER BY co_occurrence_count DESC
LIMIT 10;

-- ------------------------------------------------------------------------
-- QUERY 20: Seller Fulfillment Velocity by Seller State
-- Demonstrates: Geo-operational speed across origins
-- Business Question: Which seller states have the fastest dispatch dispatch times?
-- ------------------------------------------------------------------------
SELECT 
    s.seller_state,
    COUNT(DISTINCT oi.order_id) AS fulfilled_orders,
    ROUND(AVG(TIMESTAMPDIFF(HOUR, o.order_approved_at, o.order_delivered_carrier_date) / 24.0), 1) AS avg_seller_dispatch_days,
    ROUND(AVG(o.actual_delivery_days), 1) AS avg_total_customer_delivery_days
FROM sellers s
JOIN order_items oi ON s.seller_id = oi.seller_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
  AND o.order_approved_at IS NOT NULL
  AND o.order_delivered_carrier_date IS NOT NULL
GROUP BY s.seller_state
HAVING fulfilled_orders >= 50
ORDER BY avg_seller_dispatch_days ASC;

-- ------------------------------------------------------------------------
-- QUERY 21: Full Order Funnel and Cancellation Rate
-- Demonstrates: CASE WHEN, Funnel stage attribution
-- Business Question: What is our pipeline drop-off and cancellation percentage?
-- ------------------------------------------------------------------------
SELECT 
    order_status,
    COUNT(*) AS order_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders), 2) AS pct_of_total_orders
FROM orders
GROUP BY order_status
ORDER BY order_count DESC;

-- ------------------------------------------------------------------------
-- QUERY 22: Daily Sales Trend and 7-Day Moving Average Revenue
-- Demonstrates: CTE, Window Frame ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
-- Business Question: What is our smoothed 7-day moving trend of sales?
-- ------------------------------------------------------------------------
WITH DailySales AS (
    SELECT 
        DATE(o.order_purchase_timestamp) AS sale_date,
        COUNT(DISTINCT o.order_id) AS daily_orders,
        ROUND(SUM(oi.price), 2) AS daily_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY DATE(o.order_purchase_timestamp)
)
SELECT 
    sale_date,
    daily_orders,
    daily_revenue,
    ROUND(AVG(daily_revenue) OVER (
        ORDER BY sale_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) AS seven_day_moving_avg_revenue
FROM DailySales
ORDER BY sale_date DESC
LIMIT 30;

-- ------------------------------------------------------------------------
-- QUERY 23: Multi-Payment & Split Payment Transaction Analysis
-- Demonstrates: HAVING COUNT(payment_sequential) > 1, Subquery
-- Business Question: How frequently do customers split tickets across multiple cards/vouchers?
-- ------------------------------------------------------------------------
WITH MultiPaymentOrders AS (
    SELECT 
        order_id,
        COUNT(payment_sequential) AS payment_splits_count,
        SUM(payment_value) AS total_paid
    FROM order_payments
    GROUP BY order_id
    HAVING COUNT(payment_sequential) > 1
)
SELECT 
    payment_splits_count,
    COUNT(*) AS orders_count,
    ROUND(AVG(total_paid), 2) AS avg_split_ticket_value,
    ROUND(SUM(total_paid), 2) AS total_volume
FROM MultiPaymentOrders
GROUP BY payment_splits_count
ORDER BY payment_splits_count;

-- ------------------------------------------------------------------------
-- QUERY 24: Estimated Delivery Date Accuracy: Carrier Buffer Analysis
-- Demonstrates: AVG variance between estimated delivery date and actual arrival
-- Business Question: How accurate is our logistics promise date?
-- ------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN actual_delivery_days < estimated_delivery_days THEN 'Delivered Early'
        WHEN actual_delivery_days = estimated_delivery_days THEN 'Delivered Exactly on Promised Day'
        ELSE 'Delivered Past Promised Day'
    END AS promise_fulfillment_category,
    COUNT(*) AS total_orders,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders WHERE order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL), 2) AS share_pct,
    ROUND(AVG(actual_delivery_days), 1) AS avg_actual_days,
    ROUND(AVG(estimated_delivery_days), 1) AS avg_promised_days
FROM orders
WHERE order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL
GROUP BY promise_fulfillment_category;

-- ------------------------------------------------------------------------
-- QUERY 25: Bottom 10 Underperforming Product Categories by GMV
-- Demonstrates: Bottom ranking with activity threshold
-- Business Question: Which categories generate the least traction despite active listings?
-- ------------------------------------------------------------------------
SELECT 
    COALESCE(p.product_category_name_english, 'Other') AS category_name,
    COUNT(oi.order_item_id) AS items_sold,
    ROUND(SUM(oi.price), 2) AS total_revenue,
    ROUND(AVG(r.review_score), 2) AS avg_rating
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN order_reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY COALESCE(p.product_category_name_english, 'Other')
HAVING items_sold >= 5
ORDER BY total_revenue ASC
LIMIT 10;

-- ------------------------------------------------------------------------
-- QUERY 26: Pareto 80/20 Rule: Cumulative Revenue Concentration
-- Demonstrates: SUM() OVER(), Cumulative percentage of revenue across products
-- Business Question: Do 20% of products generate 80% of total revenue?
-- ------------------------------------------------------------------------
WITH ProductRevenue AS (
    SELECT 
        product_id,
        SUM(price) AS product_sales
    FROM order_items
    GROUP BY product_id
),
RankedProducts AS (
    SELECT 
        product_id,
        product_sales,
        ROW_NUMBER() OVER (ORDER BY product_sales DESC) AS prod_rank,
        COUNT(*) OVER () AS total_products,
        SUM(product_sales) OVER () AS total_platform_sales,
        SUM(product_sales) OVER (ORDER BY product_sales DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cum_sales
    FROM ProductRevenue
)
SELECT 
    prod_rank,
    ROUND(prod_rank * 100.0 / total_products, 2) AS percentile_of_catalog,
    ROUND(cum_sales * 100.0 / total_platform_sales, 2) AS cumulative_gmv_share_pct
FROM RankedProducts
WHERE prod_rank IN (10, 50, 100, 500, 1000, 2000, 5000)
ORDER BY prod_rank;

-- ------------------------------------------------------------------------
-- QUERY 27: Purchasing Seasonality by Day of Week and Peak Hours
-- Demonstrates: DAYOFWEEK(), HOUR() date extraction, heat-map data extraction
-- Business Question: At what hours and days do customers place the most orders?
-- ------------------------------------------------------------------------
SELECT 
    DAYNAME(order_purchase_timestamp) AS day_of_week,
    HOUR(order_purchase_timestamp) AS hour_of_day,
    COUNT(order_id) AS total_orders,
    ROUND(SUM(order_id) / 1000.0, 1) AS volume_index
FROM orders
WHERE order_status = 'delivered'
GROUP BY DAYNAME(order_purchase_timestamp), HOUR(order_purchase_timestamp)
ORDER BY total_orders DESC
LIMIT 15;

-- ------------------------------------------------------------------------
-- QUERY 28: Review Answer Latency Impact on Customer Satisfaction
-- Demonstrates: Response latency correlation to sentiment
-- Business Question: Does delayed customer review acknowledgment affect relationship?
-- ------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN TIMESTAMPDIFF(HOUR, review_creation_date, review_answer_timestamp) <= 24 THEN 'Within 24 Hours'
        WHEN TIMESTAMPDIFF(HOUR, review_creation_date, review_answer_timestamp) <= 72 THEN '1 to 3 Days'
        WHEN TIMESTAMPDIFF(HOUR, review_creation_date, review_answer_timestamp) <= 168 THEN '4 to 7 Days'
        ELSE 'Over 1 Week Latency'
    END AS answer_latency_tier,
    COUNT(*) AS total_reviews,
    ROUND(AVG(review_score), 2) AS avg_score,
    ROUND(SUM(CASE WHEN review_score = 5 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS five_star_pct
FROM order_reviews
WHERE review_answer_timestamp >= review_creation_date
GROUP BY answer_latency_tier
ORDER BY avg_score DESC;
