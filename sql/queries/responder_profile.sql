SELECT
    CASE ca.response
        WHEN 1 THEN 'Responded'
        ELSE 'Did not respond'
    END                                                     AS response_group,
    COUNT(*)                                                AS customer_count,
    ROUND(AVG(cu.age)::NUMERIC, 1)                          AS avg_age,
    ROUND(AVG(cu.income)::NUMERIC, 0)                       AS avg_income,
    ROUND(AVG(s.total_spend)::NUMERIC, 0)                   AS avg_total_spend,
    ROUND(AVG(s.mnt_wines)::NUMERIC, 0)                     AS avg_wine_spend,
    ROUND(AVG(s.mnt_meat)::NUMERIC, 0)                      AS avg_meat_spend,
    ROUND(AVG(ch.total_purchases)::NUMERIC, 1)              AS avg_total_purchases,
    ROUND(AVG(ch.num_web_purchases)::NUMERIC, 1)            AS avg_web_purchases,
    ROUND(AVG(ch.num_catalog_purchases)::NUMERIC, 1)        AS avg_catalog_purchases,
    ROUND(AVG(ch.num_store_purchases)::NUMERIC, 1)          AS avg_store_purchases,
    ROUND(AVG(cu.recency)::NUMERIC, 1)                      AS avg_recency_days,
    ROUND(AVG(cu.tenure_days)::NUMERIC, 0)                  AS avg_tenure_days,
    ROUND(AVG(cu.total_children)::NUMERIC, 2)               AS avg_children,
    ROUND(AVG(ca.total_hist_campaigns_accepted)::NUMERIC, 2) AS avg_past_campaigns_accepted
FROM campaigns ca
JOIN customers cu ON ca.customer_id = cu.customer_id
JOIN spending  s  ON ca.customer_id = s.customer_id
JOIN channels  ch ON ca.customer_id = ch.customer_id
GROUP BY ca.response
ORDER BY ca.response DESC