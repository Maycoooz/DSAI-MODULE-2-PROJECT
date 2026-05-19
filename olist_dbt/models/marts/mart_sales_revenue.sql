-- Monthly sales and revenue trends
SELECT
    d.year_month,
    d.year,
    d.month,
    d.month_name,
    COUNT(DISTINCT f.order_id)          AS total_orders,
    COUNT(f.order_item_id)              AS total_items_sold,
    ROUND(SUM(f.price), 2)              AS total_revenue,
    ROUND(SUM(f.freight_value), 2)      AS total_freight,
    ROUND(SUM(f.total_item_value), 2)   AS total_gmv,
    ROUND(AVG(f.price), 2)              AS avg_item_price,
    ROUND(AVG(f.payment_value), 2)      AS avg_order_value,
    COUNT(DISTINCT f.product_id)        AS unique_products_sold,
    COUNT(DISTINCT f.seller_id)         AS active_sellers
FROM {{ ref('fact_order_items') }} f
LEFT JOIN {{ ref('dim_date') }} d
    ON f.order_date = d.date_day
WHERE f.order_status NOT IN ('canceled', 'unavailable')
GROUP BY d.year_month, d.year, d.month, d.month_name
ORDER BY d.year_month
