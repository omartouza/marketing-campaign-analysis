-- Co-purchase rate for every pair of the 6 categories
-- Each value = % of customers who spend > $10 on BOTH categories
SELECT
    ROUND(AVG(CASE WHEN mnt_wines  > 10 AND mnt_fruits > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS wines_fruits,
    ROUND(AVG(CASE WHEN mnt_wines  > 10 AND mnt_meat   > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS wines_meat,
    ROUND(AVG(CASE WHEN mnt_wines  > 10 AND mnt_fish   > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS wines_fish,
    ROUND(AVG(CASE WHEN mnt_wines  > 10 AND mnt_sweets > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS wines_sweets,
    ROUND(AVG(CASE WHEN mnt_wines  > 10 AND mnt_gold   > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS wines_gold,
    ROUND(AVG(CASE WHEN mnt_fruits > 10 AND mnt_meat   > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS fruits_meat,
    ROUND(AVG(CASE WHEN mnt_fruits > 10 AND mnt_fish   > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS fruits_fish,
    ROUND(AVG(CASE WHEN mnt_fruits > 10 AND mnt_sweets > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS fruits_sweets,
    ROUND(AVG(CASE WHEN mnt_fruits > 10 AND mnt_gold   > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS fruits_gold,
    ROUND(AVG(CASE WHEN mnt_meat   > 10 AND mnt_fish   > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS meat_fish,
    ROUND(AVG(CASE WHEN mnt_meat   > 10 AND mnt_sweets > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS meat_sweets,
    ROUND(AVG(CASE WHEN mnt_meat   > 10 AND mnt_gold   > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS meat_gold,
    ROUND(AVG(CASE WHEN mnt_fish   > 10 AND mnt_sweets > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS fish_sweets,
    ROUND(AVG(CASE WHEN mnt_fish   > 10 AND mnt_gold   > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS fish_gold,
    ROUND(AVG(CASE WHEN mnt_sweets > 10 AND mnt_gold   > 10 THEN 1.0 ELSE 0 END)::NUMERIC * 100, 1) AS sweets_gold
FROM spending