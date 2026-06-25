WITH customer_tiers AS (
    SELECT
        s.customer_id,
        s.total_spend,
        NTILE(3) OVER (ORDER BY s.total_spend) AS clv_tier
    FROM spending s
)
SELECT
    CASE ct.clv_tier
        WHEN 1 THEN 'Low value'
        WHEN 2 THEN 'Mid value'
        WHEN 3 THEN 'High value'
    END                                                      AS clv_tier,
    COUNT(*)                                                 AS customer_count,
    ROUND(MIN(ct.total_spend)::NUMERIC, 0)                   AS min_spend,
    ROUND(MAX(ct.total_spend)::NUMERIC, 0)                   AS max_spend,
    ROUND(AVG(ct.total_spend)::NUMERIC, 0)                   AS avg_spend,
    ROUND(AVG(cu.income)::NUMERIC, 0)                        AS avg_income,
    ROUND(AVG(cu.age)::NUMERIC, 1)                           AS avg_age,
    ROUND(AVG(cu.recency)::NUMERIC, 1)                       AS avg_recency,
    ROUND(AVG(ch.total_purchases)::NUMERIC, 1)               AS avg_purchases,
    ROUND(AVG(ca.total_hist_campaigns_accepted)::NUMERIC, 2) AS avg_hist_campaigns
FROM customer_tiers ct
JOIN customers cu ON ct.customer_id = cu.customer_id
JOIN channels  ch ON ct.customer_id = ch.customer_id
JOIN campaigns ca ON ct.customer_id = ca.customer_id
GROUP BY ct.clv_tier
ORDER BY ct.clv_tier