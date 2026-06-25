WITH ranked_customers AS (
    SELECT
        ca.customer_id,
        ca.total_hist_campaigns_accepted,
        ca.response AS latest_response,
        s.total_spend,
        cu.age,
        cu.education,
        cu.income,
        ROW_NUMBER() OVER (
            ORDER BY ca.total_hist_campaigns_accepted DESC,
                     s.total_spend DESC
        ) AS engagement_rank
    FROM campaigns ca
    JOIN spending  s  ON ca.customer_id = s.customer_id
    JOIN customers cu ON ca.customer_id = cu.customer_id
)
SELECT *
FROM ranked_customers
WHERE engagement_rank <= 10
ORDER BY engagement_rank