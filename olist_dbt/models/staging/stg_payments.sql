SELECT
    order_id,
    CAST(payment_sequential AS INT64)     AS payment_sequential,
    payment_type,
    CAST(payment_installments AS INT64)   AS payment_installments,
    CAST(payment_value AS FLOAT64)        AS payment_value
FROM {{ source('olist_raw', 'payments') }}
WHERE order_id IS NOT NULL
