SELECT
    order_id,
    customer_id,
    order_status,
    TIMESTAMP(order_purchase_timestamp) AS ordered_at,
    TIMESTAMP(order_approved_at) AS approved_at,
    TIMESTAMP(order_delivered_carrier_date) AS delivered_to_carrier_at,
    TIMESTAMP(order_delivered_customer_date) AS delivered_to_customer_at,
    TIMESTAMP(order_estimated_delivery_date) AS estimated_delivery_at,
    DATE_DIFF(
        DATE(order_delivered_customer_date),
        DATE(order_purchase_timestamp),
        DAY
    ) AS delivery_days
FROM {{ source('olist_raw', 'orders') }}
WHERE order_id IS NOT NULL