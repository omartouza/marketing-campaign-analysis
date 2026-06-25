SELECT
    category,
    COUNT(*)                                                  AS total_reviews,
    SUM(CASE WHEN sentiment = 'Positive' THEN 1 ELSE 0 END)   AS positive,
    SUM(CASE WHEN sentiment = 'Neutral'  THEN 1 ELSE 0 END)   AS neutral,
    SUM(CASE WHEN sentiment = 'Negative' THEN 1 ELSE 0 END)   AS negative,
    ROUND(
        SUM(CASE WHEN sentiment = 'Negative' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*)::NUMERIC, 2
    )                                                         AS negative_pct,
    ROUND(AVG(rating)::NUMERIC, 2)                            AS avg_rating
FROM reviews
WHERE category IS NOT NULL AND TRIM(category) != ''
GROUP BY category
HAVING COUNT(*) >= 100
ORDER BY negative_pct DESC
LIMIT 10