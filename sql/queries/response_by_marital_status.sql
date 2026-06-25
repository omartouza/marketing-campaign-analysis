SELECT
    cu.marital_status,
    COUNT(*)                            AS total_customers,
    SUM(ca.response)                    AS total_responses,
    ROUND(AVG(ca.response) * 100, 2)    AS response_rate_pct,
    ROUND(AVG(s.total_spend), 0)        AS avg_spend
FROM customers cu
JOIN campaigns ca ON cu.customer_id = ca.customer_id
JOIN spending  s  ON cu.customer_id = s.customer_id
GROUP BY cu.marital_status
ORDER BY response_rate_pct DESC