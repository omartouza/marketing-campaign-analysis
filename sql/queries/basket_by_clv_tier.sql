-- Co-purchase rates for key category pairs, broken down by CLV tier
WITH customer_tiers AS (
    SELECT
        customer_id,
        NTILE(3) OVER (ORDER BY total_spend) AS tier
    FROM spending
)
SELECT
    CASE ct.tier
        WHEN 1 THEN 'Low value'
        WHEN 2 THEN 'Mid value'
        WHEN 3 THEN 'High value'
    END AS clv_tier,
    COUNT(*) AS customers,

    -- What % buy wines at all
    ROUND(AVG(CASE WHEN s.mnt_wines  > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS pct_buy_wines,
    ROUND(AVG(CASE WHEN s.mnt_fruits > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS pct_buy_fruits,
    ROUND(AVG(CASE WHEN s.mnt_meat   > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS pct_buy_meat,
    ROUND(AVG(CASE WHEN s.mnt_fish   > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS pct_buy_fish,
    ROUND(AVG(CASE WHEN s.mnt_sweets > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS pct_buy_sweets,
    ROUND(AVG(CASE WHEN s.mnt_gold   > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS pct_buy_gold,

    -- Key co-purchase rates by tier
    ROUND(AVG(CASE WHEN s.mnt_wines > 10 AND s.mnt_meat   > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS wines_and_meat,
    ROUND(AVG(CASE WHEN s.mnt_wines > 10 AND s.mnt_fruits > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS wines_and_fruits,
    ROUND(AVG(CASE WHEN s.mnt_wines > 10 AND s.mnt_gold   > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS wines_and_gold
FROM customer_tiers ct
JOIN spending s ON ct.customer_id = s.customer_id
GROUP BY ct.tier
ORDER BY ct.tier