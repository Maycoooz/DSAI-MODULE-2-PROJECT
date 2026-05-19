WITH date_spine AS (
    SELECT
        DATE_ADD(DATE '2016-01-01', INTERVAL n DAY) AS date_day
    FROM UNNEST(GENERATE_ARRAY(0, 1460)) AS n  -- covers 2016–2020
)

SELECT
    date_day,
    EXTRACT(YEAR FROM date_day)                             AS year,
    EXTRACT(MONTH FROM date_day)                            AS month,
    EXTRACT(DAY FROM date_day)                              AS day,
    EXTRACT(QUARTER FROM date_day)                          AS quarter,
    EXTRACT(DAYOFWEEK FROM date_day)                        AS day_of_week,
    FORMAT_DATE('%A', date_day)                             AS day_name,
    FORMAT_DATE('%B', date_day)                             AS month_name,
    FORMAT_DATE('%Y-%m', date_day)                          AS year_month,
    CASE WHEN EXTRACT(DAYOFWEEK FROM date_day) IN (1, 7)
        THEN TRUE ELSE FALSE END                            AS is_weekend
FROM date_spine
