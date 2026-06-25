WITH customer_tiers AS (
    SELECT
        s.customer_id,
        s.mnt_wines,
        s.mnt_fruits,
        s.mnt_meat,
        s.mnt_fish,
        s.mnt_sweets,
        s.mnt_gold,
        s.total_spend,
        NTILE(3) OVER (ORDER BY s.total_spend) AS clv_tier_num
    FROM spending s
)
SELECT
    customer_id,
    mnt_wines, mnt_fruits, mnt_meat, mnt_fish, mnt_sweets, mnt_gold,
    total_spend,
    CASE clv_tier_num
        WHEN 1 THEN 'Low value'
        WHEN 2 THEN 'Mid value'
        WHEN 3 THEN 'High value'
    END AS clv_tier
FROM customer_tiers