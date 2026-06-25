WITH campaign_rates AS (
    SELECT 'Campaign 1' AS campaign, AVG(accepted_cmp1)::NUMERIC AS rate, SUM(accepted_cmp1) AS responders FROM campaigns
    UNION ALL
    SELECT 'Campaign 2', AVG(accepted_cmp2)::NUMERIC, SUM(accepted_cmp2) FROM campaigns
    UNION ALL
    SELECT 'Campaign 3', AVG(accepted_cmp3)::NUMERIC, SUM(accepted_cmp3) FROM campaigns
    UNION ALL
    SELECT 'Campaign 4', AVG(accepted_cmp4)::NUMERIC, SUM(accepted_cmp4) FROM campaigns
    UNION ALL
    SELECT 'Campaign 5', AVG(accepted_cmp5)::NUMERIC, SUM(accepted_cmp5) FROM campaigns
    UNION ALL
    SELECT 'Latest campaign', AVG(response)::NUMERIC, SUM(response) FROM campaigns
)
SELECT
    campaign,
    responders,
    ROUND(rate * 100, 2)               AS acceptance_rate_pct,
    -- Minimum revenue : cost ratio needed to break even
    -- Lower = more efficient
    ROUND(1.0 / NULLIF(rate, 0), 2)    AS breakeven_revenue_cost_ratio
FROM campaign_rates
ORDER BY breakeven_revenue_cost_ratio ASC