SELECT
    -- AVG of a 0/1 column gives the proportion of 1s — multiply by 100 for percentage
    ROUND(AVG(accepted_cmp1) * 100, 2) AS campaign_1,
    ROUND(AVG(accepted_cmp2) * 100, 2) AS campaign_2,
    ROUND(AVG(accepted_cmp3) * 100, 2) AS campaign_3,
    ROUND(AVG(accepted_cmp4) * 100, 2) AS campaign_4,
    ROUND(AVG(accepted_cmp5) * 100, 2) AS campaign_5,
    ROUND(AVG(response)      * 100, 2) AS latest_campaign,
    COUNT(*) AS total_customers
FROM campaigns