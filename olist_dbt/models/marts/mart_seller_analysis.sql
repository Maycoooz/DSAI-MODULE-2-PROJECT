-- Seller performance: revenue, ratings, delivery
SELECT
    f.seller_id,
    s.seller_state,
    s.seller_city,
    COUNT(DISTINCT f.order_id)                      AS total_orders,
    COUNT(f.order_item_id)                          AS total_items_sold,
    ROUND(SUM(f.price), 2)                          AS total_revenue,
    ROUND(AVG(f.price), 2)                          AS avg_item_price,
    ROUND(AVG(f.review_score), 2)                   AS avg_review_score,
    COUNTIF(f.review_score >= 4)                    AS positive_reviews,
    COUNTIF(f.review_score <= 2)                    AS negative_reviews,
    COUNTIF(f.delivery_status = 'on_time')          AS on_time_deliveries,
    COUNTIF(f.delivery_status = 'late')             AS late_deliveries,
    ROUND(
        COUNTIF(f.delivery_status = 'on_time') * 100.0
        / NULLIF(COUNT(f.order_id), 0), 2
    )                                               AS on_time_pct,
    ROUND(AVG(f.delivery_days), 1)                  AS avg_delivery_days,
    COUNT(DISTINCT f.product_id)                    AS unique_products,
    COUNT(DISTINCT f.customer_id)                   AS unique_customers
FROM {{ ref('fact_order_items') }} f
LEFT JOIN {{ ref('dim_sellers') }} s
    ON f.seller_id = s.seller_id
WHERE f.order_status NOT IN ('canceled', 'unavailable')
GROUP BY f.seller_id, s.seller_state, s.seller_city
ORDER BY total_revenue DESC
