SELECT
    -- Identity & target
    cu.customer_id,
    s.total_spend,

    -- Demographics
    cu.age,
    cu.income,
    cu.education,
    cu.marital_status,
    cu.total_children,
    cu.has_children,
    cu.tenure_days,
    cu.recency,

    -- Web visit behaviour (NOT a spend proxy — measures intent, not purchases)
    ch.num_web_visits_month,

    -- Historical campaign behaviour (leakage-safe — excludes response)
    ca.total_hist_campaigns_accepted,

    -- Classification target
    ca.response,

    -- Behavioural proxies — present here for the CLASSIFIER only, not the CLV regression
    -- (We will split features per task below)
    ch.num_web_purchases,
    ch.num_store_purchases,
    ch.num_catalog_purchases,
    ch.num_deals_purchases,
    ch.total_purchases
FROM customers cu
JOIN channels  ch ON cu.customer_id = ch.customer_id
JOIN campaigns ca ON cu.customer_id = ca.customer_id
JOIN spending  s  ON cu.customer_id = s.customer_id