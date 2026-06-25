"""
Tableau CSV Export — Page 4: Market Basket Analysis
Standalone script — re-runs the same Apriori analysis as 06_market_basket_analysis.ipynb.

Run: python3 export_tableau_page4.py
"""

import os
import getpass
import pandas as pd
from pathlib import Path
import numpy as np
from sqlalchemy import create_engine, text
from mlxtend.frequent_patterns import apriori, association_rules

# Anchor to this script's own location so it runs from any working directory.
# scripts/ sits one level below the repo root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TABLEAU_PATH = str(PROJECT_ROOT / 'dashboard' / 'tableau_data')
os.makedirs(TABLEAU_PATH, exist_ok=True)

username = getpass.getuser()
engine = create_engine(f'postgresql+psycopg2://{username}@localhost:5432/marketing_db', future=True)

def run_query(sql):
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)

n = run_query('SELECT COUNT(*) AS n FROM customers')['n'].values[0]
print(f'Connected ✅ — {n:,} customers')

# Pull spend + CLV tier
sql = '''
SELECT
    s.customer_id, s.mnt_wines, s.mnt_fruits, s.mnt_meat,
    s.mnt_fish, s.mnt_sweets, s.mnt_gold, s.total_spend,
    CASE NTILE(3) OVER (ORDER BY s.total_spend)
        WHEN 1 THEN 'Low value' WHEN 2 THEN 'Mid value' ELSE 'High value'
    END AS clv_tier
FROM spending s
'''
spend_df = run_query(sql)

category_labels = {
    'mnt_wines': 'Wines', 'mnt_fruits': 'Fruits', 'mnt_meat': 'Meat',
    'mnt_fish': 'Fish', 'mnt_sweets': 'Sweets', 'mnt_gold': 'Gold',
}

def build_basket(df, cols=None):
    """Build above-median binary basket from a spend DataFrame."""
    result = pd.DataFrame()
    if cols is None:
        cols = category_labels
    for raw_col, label in cols.items():
        threshold = df[raw_col].median()
        result[label] = (df[raw_col] > threshold).astype(bool)
    return result.reset_index(drop=True)

def fmt_set(s):
    return ', '.join(sorted(s))

def run_apriori(basket, min_support=0.10, min_lift=1.2, min_confidence=0.5):
    itemsets = apriori(basket, min_support=min_support, use_colnames=True)
    if len(itemsets) == 0:
        return pd.DataFrame()
    rules = association_rules(itemsets, metric='lift', min_threshold=min_lift)
    rules = rules[rules['confidence'] >= min_confidence].copy()
    if len(rules) > 0:
        rules['antecedents_str'] = rules['antecedents'].apply(fmt_set)
        rules['consequents_str'] = rules['consequents'].apply(fmt_set)
        rules['rule'] = rules['antecedents_str'] + ' → ' + rules['consequents_str']
        rules = rules.sort_values('lift', ascending=False)
    return rules

# --- Overall rules ---
basket_all = build_basket(spend_df)
rules_all = run_apriori(basket_all)
save_cols = ['antecedents_str', 'consequents_str', 'rule', 'support', 'confidence', 'lift']
rules_all[save_cols].to_csv(os.path.join(TABLEAU_PATH, 'mba_rules_overall.csv'), index=False)
print(f'✅ mba_rules_overall.csv — {len(rules_all)} rules')

# --- Per-tier rules ---
tier_rows = []
for tier in ['Low value', 'Mid value', 'High value']:
    tier_spend = spend_df[spend_df['clv_tier'] == tier]
    tier_basket = build_basket(tier_spend)
    rules = run_apriori(tier_basket, min_support=0.15)
    if len(rules) > 0:
        for _, row in rules.iterrows():
            tier_rows.append({
                'clv_tier': tier,
                'antecedents_str': row['antecedents_str'],
                'consequents_str': row['consequents_str'],
                'rule': row['rule'],
                'support': round(row['support'], 4),
                'confidence': round(row['confidence'], 4),
                'lift': round(row['lift'], 4),
            })
    print(f'  {tier}: {len(rules)} rules')

tier_rules_df = pd.DataFrame(tier_rows)
tier_rules_df.to_csv(os.path.join(TABLEAU_PATH, 'mba_rules_by_tier.csv'), index=False)
print(f'✅ mba_rules_by_tier.csv — {len(tier_rules_df)} total rows')

# --- Cross-tier comparison (pivot: rule × tier → lift) ---
if len(tier_rules_df) > 0:
    pivot = tier_rules_df.pivot_table(
        index='rule', columns='clv_tier', values='lift', aggfunc='first'
    ).reset_index()
    pivot.columns.name = None
    for col in ['Low value', 'Mid value', 'High value']:
        if col not in pivot.columns:
            pivot[col] = None
    pivot = pivot[['rule', 'Low value', 'Mid value', 'High value']]
    pivot.to_csv(os.path.join(TABLEAU_PATH, 'mba_tier_comparison.csv'), index=False)
    print(f'✅ mba_tier_comparison.csv — {len(pivot)} unique rules')

# --- Rule count summary per tier (for KPI cards) ---
summary_rows = []
for tier in ['Low value', 'Mid value', 'High value']:
    tier_spend = spend_df[spend_df['clv_tier'] == tier]
    tier_basket = build_basket(tier_spend)
    rules = run_apriori(tier_basket, min_support=0.15)
    itemsets = apriori(tier_basket, min_support=0.15, use_colnames=True)
    # Top rule for this tier
    top_rule = rules.iloc[0]['rule'] if len(rules) > 0 else 'None'
    top_lift = round(rules.iloc[0]['lift'], 2) if len(rules) > 0 else None
    summary_rows.append({
        'clv_tier': tier,
        'customer_count': len(tier_spend),
        'rules_found': len(rules),
        'top_rule': top_rule,
        'top_lift': top_lift,
    })
summary_df = pd.DataFrame(summary_rows)
summary_df.to_csv(os.path.join(TABLEAU_PATH, 'mba_tier_summary.csv'), index=False)
print(f'✅ mba_tier_summary.csv')
print()
print(summary_df.to_string(index=False))

# --- Catalog-heavy segment ---
sql_catalog = '''
SELECT s.customer_id, s.mnt_wines, s.mnt_fruits, s.mnt_meat,
       s.mnt_fish, s.mnt_sweets, s.mnt_gold, ch.num_catalog_purchases
FROM spending s JOIN channels ch ON s.customer_id = ch.customer_id
'''
catalog_df = run_query(sql_catalog)
cat_median = catalog_df['num_catalog_purchases'].median()
heavy = catalog_df[catalog_df['num_catalog_purchases'] > cat_median]
heavy_basket = build_basket(heavy)
heavy_rules = run_apriori(heavy_basket, min_support=0.15)
if len(heavy_rules) > 0:
    heavy_rules[save_cols].to_csv(
        os.path.join(TABLEAU_PATH, 'mba_rules_catalog_heavy.csv'), index=False)
    print(f'✅ mba_rules_catalog_heavy.csv — {len(heavy_rules)} rules')

print(f'\nAll files saved to: {TABLEAU_PATH}')
