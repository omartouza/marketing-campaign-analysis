"""
Tableau CSV Export — Page 1: Campaign Performance
Standalone script. Run independently of any notebook:

    python3 export_tableau_page1.py

Requires: pandas, sqlalchemy, psycopg2
Connects to the same local PostgreSQL marketing_db used throughout the project
(local trust auth, no password — current OS user).
"""

import os
import getpass
import pandas as pd
from sqlalchemy import create_engine, text

# --- Setup (self-contained — no dependency on any notebook kernel) ---
PROJECT_ROOT = os.path.expanduser('~/Desktop/marketing-campaign-analysis')
TABLEAU_PATH = os.path.join(PROJECT_ROOT, 'data', 'tableau')
os.makedirs(TABLEAU_PATH, exist_ok=True)

username = getpass.getuser()
engine = create_engine(
    f'postgresql+psycopg2://{username}@localhost:5432/marketing_db',
    future=True
)

def run_query(sql):
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)

# Sanity check the connection before doing anything else
test = run_query('SELECT COUNT(*) AS n FROM customers')
n_customers = test['n'].values[0]
print(f'Connected ✅ — {n_customers:,} customers in database')
if n_customers != 2212:
    print(f'⚠️  Expected 2,212 customers (post-Phase-2 cleaned count). '
          f'Got {n_customers:,}. Re-run Phase 2 before exporting.')

# ---------------------------------------------------------------
# Export 1: customer_master.csv
# ---------------------------------------------------------------
sql_export_master = '''
SELECT
    cu.customer_id,
    cu.age,
    cu.education,
    cu.marital_status,
    cu.income,
    cu.kidhome,
    cu.teenhome,
    cu.total_children,
    cu.has_children,
    cu.dt_customer,
    cu.tenure_days,
    cu.recency,
    cu.complain,

    s.mnt_wines,
    s.mnt_fruits,
    s.mnt_meat,
    s.mnt_fish,
    s.mnt_sweets,
    s.mnt_gold,
    s.total_spend,

    ch.num_web_purchases,
    ch.num_catalog_purchases,
    ch.num_store_purchases,
    ch.num_deals_purchases,
    ch.num_web_visits_month,
    ch.total_purchases,
    ch.avg_spend_per_purchase,

    ca.accepted_cmp1,
    ca.accepted_cmp2,
    ca.accepted_cmp3,
    ca.accepted_cmp4,
    ca.accepted_cmp5,
    ca.response,
    ca.total_hist_campaigns_accepted,

    NTILE(3) OVER (ORDER BY s.total_spend) AS clv_tier_num,
    CASE NTILE(3) OVER (ORDER BY s.total_spend)
        WHEN 1 THEN 'Low value'
        WHEN 2 THEN 'Mid value'
        WHEN 3 THEN 'High value'
    END AS clv_tier

FROM customers cu
JOIN spending  s  ON cu.customer_id = s.customer_id
JOIN channels  ch ON cu.customer_id = ch.customer_id
JOIN campaigns ca ON cu.customer_id = ca.customer_id
'''

customer_master = run_query(sql_export_master)
out_path = os.path.join(TABLEAU_PATH, 'customer_master.csv')
customer_master.to_csv(out_path, index=False)
print(f'✅ customer_master.csv — {len(customer_master):,} rows, {customer_master.shape[1]} columns')

# ---------------------------------------------------------------
# Export 2: campaign_acceptance_long.csv
# ---------------------------------------------------------------
sql_export_campaigns_long = '''
SELECT customer_id, 'Campaign 1' AS campaign_name, accepted_cmp1 AS accepted FROM campaigns
UNION ALL
SELECT customer_id, 'Campaign 2', accepted_cmp2 FROM campaigns
UNION ALL
SELECT customer_id, 'Campaign 3', accepted_cmp3 FROM campaigns
UNION ALL
SELECT customer_id, 'Campaign 4', accepted_cmp4 FROM campaigns
UNION ALL
SELECT customer_id, 'Campaign 5', accepted_cmp5 FROM campaigns
UNION ALL
SELECT customer_id, 'Latest Campaign', response FROM campaigns
'''

campaign_long = run_query(sql_export_campaigns_long)
sort_order = {
    'Campaign 1': 1, 'Campaign 2': 2, 'Campaign 3': 3,
    'Campaign 4': 4, 'Campaign 5': 5, 'Latest Campaign': 6
}
campaign_long['sort_order'] = campaign_long['campaign_name'].map(sort_order)

out_path = os.path.join(TABLEAU_PATH, 'campaign_acceptance_long.csv')
campaign_long.to_csv(out_path, index=False)
print(f'✅ campaign_acceptance_long.csv — {len(campaign_long):,} rows')

# ---------------------------------------------------------------
# Export 3: campaign_breakeven.csv
# ---------------------------------------------------------------
sql_breakeven = '''
WITH campaign_rates AS (
    SELECT 'Campaign 1' AS campaign_name, 1 AS sort_order, AVG(accepted_cmp1)::NUMERIC AS rate FROM campaigns
    UNION ALL
    SELECT 'Campaign 2', 2, AVG(accepted_cmp2)::NUMERIC FROM campaigns
    UNION ALL
    SELECT 'Campaign 3', 3, AVG(accepted_cmp3)::NUMERIC FROM campaigns
    UNION ALL
    SELECT 'Campaign 4', 4, AVG(accepted_cmp4)::NUMERIC FROM campaigns
    UNION ALL
    SELECT 'Campaign 5', 5, AVG(accepted_cmp5)::NUMERIC FROM campaigns
    UNION ALL
    SELECT 'Latest Campaign', 6, AVG(response)::NUMERIC FROM campaigns
)
SELECT
    campaign_name,
    sort_order,
    ROUND(rate * 100, 2)            AS acceptance_rate_pct,
    ROUND(1.0 / NULLIF(rate, 0), 2) AS breakeven_revenue_cost_ratio,
    ROUND((rate * 20) - 5, 2) AS net_profit_conservative,
    ROUND((rate * 30) - 3, 2) AS net_profit_moderate,
    ROUND((rate * 50) - 2, 2) AS net_profit_optimistic
FROM campaign_rates
ORDER BY sort_order
'''

breakeven = run_query(sql_breakeven)
out_path = os.path.join(TABLEAU_PATH, 'campaign_breakeven.csv')
breakeven.to_csv(out_path, index=False)
print(f'✅ campaign_breakeven.csv — {len(breakeven):,} rows')
print()
print(breakeven.to_string(index=False))

print()
print('=' * 60)
print(f'All Page 1 exports saved to: {TABLEAU_PATH}')
print('=' * 60)
