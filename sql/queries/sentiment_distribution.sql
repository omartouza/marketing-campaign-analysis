SELECT
    sentiment,
    COUNT(*)                                              AS review_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2)    AS pct
FROM reviews
WHERE review_text IS NOT NULL
GROUP BY sentiment
ORDER BY review_count DESC