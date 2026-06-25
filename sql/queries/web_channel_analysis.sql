SELECT
    -- What proportion of customers buy online at all (over 2 years)?
    ROUND(
        SUM(CASE WHEN num_web_purchases > 0 THEN 1 ELSE 0 END)::NUMERIC
        / COUNT(*)::NUMERIC * 100, 2
    ) AS pct_who_buy_online,

    -- Average web visits per month
    ROUND(AVG(num_web_visits_month)::NUMERIC, 2)    AS avg_monthly_visits,

    -- Average web purchases (total, last 2 years)
    ROUND(AVG(num_web_purchases)::NUMERIC, 2)       AS avg_web_purchases_2yr,

    -- Implied purchase-per-visit ratio (assuming 24 months of visits at avg rate)
    ROUND(
        AVG(num_web_purchases)::NUMERIC
        / NULLIF(AVG(num_web_visits_month) * 24, 0)::NUMERIC,
        4
    ) AS implied_visit_to_purchase_ratio,

    -- Heavy visitors who never buy online — top web-opportunity segment
    SUM(CASE WHEN num_web_visits_month > 5 AND num_web_purchases = 0 THEN 1 ELSE 0 END) AS heavy_visitors_never_buy,

    -- Customers who never visit at all (likely store-loyal)
    SUM(CASE WHEN num_web_visits_month = 0 THEN 1 ELSE 0 END) AS never_visit,

    COUNT(*) AS total_customers
FROM channels