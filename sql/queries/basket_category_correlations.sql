-- Pearson correlation between every pair of spending categories
-- corr() is a built-in PostgreSQL aggregate function
SELECT
    ROUND(corr(mnt_wines,  mnt_fruits)::NUMERIC, 3) AS wines_fruits,
    ROUND(corr(mnt_wines,  mnt_meat)::NUMERIC,   3) AS wines_meat,
    ROUND(corr(mnt_wines,  mnt_fish)::NUMERIC,   3) AS wines_fish,
    ROUND(corr(mnt_wines,  mnt_sweets)::NUMERIC, 3) AS wines_sweets,
    ROUND(corr(mnt_wines,  mnt_gold)::NUMERIC,   3) AS wines_gold,
    ROUND(corr(mnt_fruits, mnt_meat)::NUMERIC,   3) AS fruits_meat,
    ROUND(corr(mnt_fruits, mnt_fish)::NUMERIC,   3) AS fruits_fish,
    ROUND(corr(mnt_fruits, mnt_sweets)::NUMERIC, 3) AS fruits_sweets,
    ROUND(corr(mnt_fruits, mnt_gold)::NUMERIC,   3) AS fruits_gold,
    ROUND(corr(mnt_meat,   mnt_fish)::NUMERIC,   3) AS meat_fish,
    ROUND(corr(mnt_meat,   mnt_sweets)::NUMERIC, 3) AS meat_sweets,
    ROUND(corr(mnt_meat,   mnt_gold)::NUMERIC,   3) AS meat_gold,
    ROUND(corr(mnt_fish,   mnt_sweets)::NUMERIC, 3) AS fish_sweets,
    ROUND(corr(mnt_fish,   mnt_gold)::NUMERIC,   3) AS fish_gold,
    ROUND(corr(mnt_sweets, mnt_gold)::NUMERIC,   3) AS sweets_gold
FROM spending