-- Delivery performance by seller state and month
SELECT
    s.seller_state,
    d.year_month,
    d.year,
    d.month,
    COUNT(DISTINCT f.order_id)                          AS total_orders,
    COUNTIF(f.delivery_status = 'on_time')              AS on_time_deliveries,
    COUNTIF(f.delivery_status = 'late')                 AS late_deliveries,
    COUNTIF(f.delivery_status = 'not_delivered')        AS not_delivered,
    ROUND(
        COUNTIF(f.delivery_status = 'on_time') * 100.0
        / NULLIF(COUNTIF(f.delivery_status IN ('on_time', 'late')), 0), 2
    )                                                   AS on_time_pct,
    ROUND(AVG(f.delivery_days), 1)                      AS avg_delivery_days,
    ROUND(AVG(f.review_score), 2)                       AS avg_review_score,
    ROUND(AVG(
        CASE WHEN f.delivery_status = 'late'
        THEN ABS(f.days_early_or_late) END), 1)         AS avg_days_late
FROM {{ ref('fact_order_items') }} f
LEFT JOIN {{ ref('dim_sellers') }} s
    ON f.seller_id = s.seller_id
LEFT JOIN {{ ref('dim_date') }} d
    ON f.order_date = d.date_day
WHERE f.order_status = 'delivered'
GROUP BY s.seller_state, d.year_month, d.year, d.month
ORDER BY d.year_month, s.seller_state
