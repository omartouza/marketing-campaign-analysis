-- Distribution of historical campaign engagement (campaigns 1–5)
SELECT
    total_hist_campaigns_accepted                                AS campaigns_accepted,
    COUNT(*)                                                     AS customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2)           AS pct_of_customers
FROM campaigns
GROUP BY total_hist_campaigns_accepted
ORDER BY total_hist_campaigns_accepted