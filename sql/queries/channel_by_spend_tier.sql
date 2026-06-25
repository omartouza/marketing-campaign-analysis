WITH customer_tiers AS (
    SELECT
        s.customer_id,
        s.total_spend,
        NTILE(3) OVER (ORDER BY s.total_spend) AS spend_tier
    FROM spending s
)
SELECT
    CASE spend_tier
        WHEN 1 THEN 'Low spenders'
        WHEN 2 THEN 'Mid spenders'
        WHEN 3 THEN 'High spenders'
    END AS spend_tier,
    ROUND(AVG(ch.num_web_purchases), 2)     AS avg_web,
    ROUND(AVG(ch.num_store_purchases), 2)   AS avg_store,
    ROUND(AVG(ch.num_catalog_purchases), 2) AS avg_catalog,
    ROUND(AVG(ch.num_deals_purchases), 2)   AS avg_deals,
    COUNT(*) AS customer_count
FROM customer_tiers ct
JOIN channels ch ON ct.customer_id = ch.customer_id
GROUP BY spend_tier
ORDER BY MIN(ct.spend_tier)