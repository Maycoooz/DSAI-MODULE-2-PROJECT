SELECT
    seller_id,
    CAST(seller_zip_code_prefix AS STRING) AS seller_zip_code_prefix,
    INITCAP(seller_city)                   AS seller_city,
    UPPER(seller_state)                    AS seller_state
FROM {{ source('olist_raw', 'sellers') }}
WHERE seller_id IS NOT NULL
