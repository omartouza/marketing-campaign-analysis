SELECT
    -- What proportion of customers buy online at all?
    ROUND(
        SUM(CASE WHEN num_web_purchases > 0 THEN 1 ELSE 0 END)::NUMERIC
        / COUNT(*)::NUMERIC * 100, 2
    ) AS pct_customers_who_buy_online,

    -- Average monthly web visits
    ROUND(AVG(num_web_visits_month)::NUMERIC, 2) AS avg_monthly_visits,

    -- Average web purchases (total, over 2 years)
    ROUND(AVG(num_web_purchases)::NUMERIC, 2) AS avg_web_purchases,

    -- Customers who visit regularly (>5/month) but never buy online
    -- These are the highest-opportunity customers for web conversion
    SUM(CASE WHEN num_web_visits_month > 5
             AND num_web_purchases = 0
        THEN 1 ELSE 0 END) AS frequent_visitors_never_buy,

    -- Customers who never visit the website at all
    SUM(CASE WHEN num_web_visits_month = 0
        THEN 1 ELSE 0 END) AS never_visit_website,

    COUNT(*) AS total_customers
FROM channels