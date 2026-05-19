-- Customer churn: one-time vs repeat buyers, recency
WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        c.customer_state,
        COUNT(DISTINCT f.order_id)          AS total_orders,
        MIN(DATE(f.ordered_at))             AS first_order_date,
        MAX(DATE(f.ordered_at))             AS last_order_date,
        ROUND(SUM(f.total_item_value), 2)   AS total_spend,
        ROUND(AVG(f.review_score), 2)       AS avg_review_score
    FROM {{ ref('fact_order_items') }} f
    LEFT JOIN {{ ref('dim_customers') }} c
        ON f.customer_id = c.customer_id
    WHERE f.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY c.customer_unique_id, c.customer_state
)

SELECT
    customer_unique_id,
    customer_state,
    total_orders,
    first_order_date,
    last_order_date,
    total_spend,
    avg_review_score,
    DATE_DIFF(DATE '2018-10-01', last_order_date, DAY)  AS days_since_last_order,
    CASE
        WHEN total_orders = 1                           THEN 'one_time'
        WHEN total_orders BETWEEN 2 AND 4               THEN 'occasional'
        ELSE 'loyal'
    END                                                 AS customer_segment,
    CASE
        WHEN DATE_DIFF(DATE '2018-10-01', last_order_date, DAY) > 180
            THEN 'churned'
        WHEN DATE_DIFF(DATE '2018-10-01', last_order_date, DAY) > 90
            THEN 'at_risk'
        ELSE 'active'
    END                                                 AS churn_status
FROM customer_orders
ORDER BY total_spend DESC
