-- Customer behaviour: spend, reviews, geography
SELECT
    c.customer_state,
    c.customer_city,
    COUNT(DISTINCT c.customer_unique_id)        AS total_customers,
    COUNT(DISTINCT f.order_id)                  AS total_orders,
    ROUND(SUM(f.total_item_value), 2)           AS total_revenue,
    ROUND(AVG(f.total_item_value), 2)           AS avg_order_value,
    ROUND(AVG(f.review_score), 2)               AS avg_review_score,
    COUNTIF(f.review_score >= 4)                AS positive_reviews,
    COUNTIF(f.review_score <= 2)                AS negative_reviews,
    ROUND(AVG(f.delivery_days), 1)              AS avg_delivery_days,
    COUNT(DISTINCT f.product_id)                AS unique_products_bought
FROM {{ ref('fact_order_items') }} f
LEFT JOIN {{ ref('dim_customers') }} c
    ON f.customer_id = c.customer_id
WHERE f.order_status NOT IN ('canceled', 'unavailable')
GROUP BY c.customer_state, c.customer_city
ORDER BY total_orders DESC
