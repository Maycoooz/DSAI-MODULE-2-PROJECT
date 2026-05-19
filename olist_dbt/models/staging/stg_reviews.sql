SELECT
    review_id,
    order_id,
    CAST(review_score AS INT64)                        AS review_score,
    review_comment_title,
    review_comment_message,
    TIMESTAMP(review_creation_date)                    AS review_created_at,
    TIMESTAMP(review_answer_timestamp)                 AS review_answered_at
FROM {{ source('olist_raw', 'reviews') }}
WHERE review_id IS NOT NULL
  AND order_id IS NOT NULL
