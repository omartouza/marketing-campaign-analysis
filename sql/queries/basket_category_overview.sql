SELECT
    -- Total spend per category across all customers
    SUM(mnt_wines)   AS total_wines,
    SUM(mnt_fruits)  AS total_fruits,
    SUM(mnt_meat)    AS total_meat,
    SUM(mnt_fish)    AS total_fish,
    SUM(mnt_sweets)  AS total_sweets,
    SUM(mnt_gold)    AS total_gold,

    -- Average spend per customer per category
    ROUND(AVG(mnt_wines)::NUMERIC,  0) AS avg_wines,
    ROUND(AVG(mnt_fruits)::NUMERIC, 0) AS avg_fruits,
    ROUND(AVG(mnt_meat)::NUMERIC,   0) AS avg_meat,
    ROUND(AVG(mnt_fish)::NUMERIC,   0) AS avg_fish,
    ROUND(AVG(mnt_sweets)::NUMERIC, 0) AS avg_sweets,
    ROUND(AVG(mnt_gold)::NUMERIC,   0) AS avg_gold,

    -- Number of customers who genuinely buy each category (spend > $10)
    SUM(CASE WHEN mnt_wines  > 10 THEN 1 ELSE 0 END) AS buyers_wines,
    SUM(CASE WHEN mnt_fruits > 10 THEN 1 ELSE 0 END) AS buyers_fruits,
    SUM(CASE WHEN mnt_meat   > 10 THEN 1 ELSE 0 END) AS buyers_meat,
    SUM(CASE WHEN mnt_fish   > 10 THEN 1 ELSE 0 END) AS buyers_fish,
    SUM(CASE WHEN mnt_sweets > 10 THEN 1 ELSE 0 END) AS buyers_sweets,
    SUM(CASE WHEN mnt_gold   > 10 THEN 1 ELSE 0 END) AS buyers_gold,

    COUNT(*) AS total_customers
FROM spending