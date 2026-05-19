SELECT
    customer_id,
    customer_unique_id,
    CAST(customer_zip_code_prefix AS STRING) AS customer_zip_code_prefix,
    INITCAP(customer_city)                   AS customer_city,
    UPPER(customer_state)                    AS customer_state
FROM {{ source('olist_raw', 'customers') }}
WHERE customer_id IS NOT NULL
