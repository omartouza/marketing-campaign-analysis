SELECT
    sentiment,
    COUNT(*)                                AS review_count,
    ROUND(AVG(rating)::NUMERIC, 2)          AS avg_rating,
    ROUND(AVG(review_length)::NUMERIC, 0)   AS avg_length
FROM reviews
GROUP BY sentiment
ORDER BY avg_rating DESC