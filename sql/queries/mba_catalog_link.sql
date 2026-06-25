SELECT
    s.customer_id,
    s.mnt_wines, s.mnt_fruits, s.mnt_meat,
    s.mnt_fish,  s.mnt_sweets, s.mnt_gold,
    ch.num_catalog_purchases
FROM spending s
JOIN channels ch ON s.customer_id = ch.customer_id