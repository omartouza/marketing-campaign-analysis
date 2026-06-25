SELECT
    SUM(num_web_purchases)               AS web_total,
    SUM(num_store_purchases)             AS store_total,
    SUM(num_catalog_purchases)           AS catalog_total,
    SUM(num_deals_purchases)             AS deals_total,
    ROUND(AVG(num_web_purchases), 2)     AS web_avg,
    ROUND(AVG(num_store_purchases), 2)   AS store_avg,
    ROUND(AVG(num_catalog_purchases), 2) AS catalog_avg,
    ROUND(AVG(num_deals_purchases), 2)   AS deals_avg
FROM channels