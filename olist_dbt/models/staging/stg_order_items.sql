SELECT
    order_id,
    order_item_id,
    product_id,
    seller_id,
    TIMESTAMP(shipping_limit_date)  AS shipping_limit_at,
    CAST(price AS FLOAT64)          AS price,
    CAST(freight_value AS FLOAT64)  AS freight_value,
    CAST(price AS FLOAT64) + CAST(freight_value AS FLOAT64) AS total_item_value
FROM {{ source('olist_raw', 'order_items') }}
WHERE order_id IS NOT NULL
