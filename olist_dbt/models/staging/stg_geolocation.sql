SELECT
    CAST(geolocation_zip_code_prefix AS STRING) AS zip_code_prefix,
    CAST(geolocation_lat AS FLOAT64)            AS latitude,
    CAST(geolocation_lng AS FLOAT64)            AS longitude,
    INITCAP(geolocation_city)                   AS city,
    UPPER(geolocation_state)                    AS state
FROM {{ source('olist_raw', 'geolocation') }}
WHERE geolocation_zip_code_prefix IS NOT NULL
