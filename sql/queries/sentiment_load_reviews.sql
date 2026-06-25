SELECT
    review_text,
    review_title,
    rating,
    sentiment,
    product_name,
    category,
    review_length
FROM reviews
WHERE review_text IS NOT NULL
  AND TRIM(review_text) != ''
ORDER BY RANDOM()