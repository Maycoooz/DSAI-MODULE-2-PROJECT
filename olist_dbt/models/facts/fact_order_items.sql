SELECT
    oi.order_id,
    oi.order_item_id,
    oi.product_id,
    oi.seller_id,
    o.customer_id,
    o.order_status,
    o.ordered_at,
    o.approved_at,
    o.delivered_to_carrier_at,
    o.delivered_to_customer_at,
    o.estimated_delivery_at,
    o.delivery_days,
    DATE(o.ordered_at)                                          AS order_date,
    oi.price,
    oi.freight_value,
    oi.total_item_value,
    oi.shipping_limit_at,
    p.payment_type,
    p.payment_installments,
    p.payment_value,
    r.review_score,
    CASE
        WHEN o.delivery_days IS NULL                            THEN 'not_delivered'
        WHEN o.delivered_to_customer_at <= o.estimated_delivery_at THEN 'on_time'
        ELSE 'late'
    END                                                         AS delivery_status,
    DATE_DIFF(
        DATE(o.estimated_delivery_at),
        DATE(o.delivered_to_customer_at),
        DAY
    )                                                           AS days_early_or_late
FROM {{ ref('stg_order_items') }} oi
LEFT JOIN {{ ref('stg_orders') }} o
    ON oi.order_id = o.order_id
LEFT JOIN {{ ref('stg_payments') }} p
    ON oi.order_id = p.order_id
    AND p.payment_sequential = 1
LEFT JOIN {{ ref('stg_reviews') }} r
    ON oi.order_id = r.order_id
