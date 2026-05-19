SELECT
    product_category_name,
    product_category_name_english
FROM {{ source('olist_raw', 'category_translation') }}
WHERE product_category_name IS NOT NULL
