SELECT
    c.customer_unique_id,
    c.customer_id,
    c.customer_city,
    c.customer_state,
    c.customer_zip_code_prefix,
    COUNT(DISTINCT o.order_id)          AS total_orders,
    MIN(o.ordered_at)                   AS first_order_at,
    MAX(o.ordered_at)                   AS last_order_at,
    DATE_DIFF(
        DATE(MAX(o.ordered_at)),
        DATE(MIN(o.ordered_at)),
        DAY
    )                                   AS customer_lifespan_days
FROM {{ ref('stg_customers') }} c
LEFT JOIN {{ ref('stg_orders') }} o
    ON c.customer_id = o.customer_id
GROUP BY
    c.customer_unique_id,
    c.customer_id,
    c.customer_city,
    c.customer_state,
    c.customer_zip_code_prefix
