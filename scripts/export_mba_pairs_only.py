"""
Regenerate mba_rules_overall.csv with pair rules only (single-category antecedent AND consequent).
Run: python3 export_mba_pairs_only.py
"""

import os
import getpass
import pandas as pd
from sqlalchemy import create_engine, text
from mlxtend.frequent_patterns import apriori, association_rules

PROJECT_ROOT = os.path.expanduser('~/Desktop/marketing-campaign-analysis')
TABLEAU_PATH = os.path.join(PROJECT_ROOT, 'dashboard', 'tableau_data')

username = getpass.getuser()
engine = create_engine(f'postgresql+psycopg2://{username}@localhost:5432/marketing_db', future=True)

def run_query(sql):
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)

sql = '''
SELECT s.customer_id, s.mnt_wines, s.mnt_fruits, s.mnt_meat,
       s.mnt_fish, s.mnt_sweets, s.mnt_gold
FROM spending s
'''
spend_df = run_query(sql)

category_labels = {
    'mnt_wines': 'Wines', 'mnt_fruits': 'Fruits', 'mnt_meat': 'Meat',
    'mnt_fish': 'Fish', 'mnt_sweets': 'Sweets', 'mnt_gold': 'Gold',
}

basket = pd.DataFrame()
for raw_col, label in category_labels.items():
    basket[label] = (spend_df[raw_col] > spend_df[raw_col].median()).astype(bool)

itemsets = apriori(basket, min_support=0.10, use_colnames=True)
rules = association_rules(itemsets, metric='lift', min_threshold=1.2)
rules = rules[rules['confidence'] >= 0.5].copy()

# Keep only pair rules: 1 item in antecedent AND 1 item in consequent
rules = rules[
    (rules['antecedents'].apply(len) == 1) &
    (rules['consequents'].apply(len) == 1)
].copy()

rules['antecedents_str'] = rules['antecedents'].apply(lambda s: ', '.join(sorted(s)))
rules['consequents_str'] = rules['consequents'].apply(lambda s: ', '.join(sorted(s)))
rules['rule'] = rules['antecedents_str'] + ' → ' + rules['consequents_str']
rules = rules.sort_values('lift', ascending=False)

save_cols = ['antecedents_str', 'consequents_str', 'rule', 'support', 'confidence', 'lift']
out = os.path.join(TABLEAU_PATH, 'mba_rules_pairs_only.csv')
rules[save_cols].to_csv(out, index=False)
print(f'✅ mba_rules_pairs_only.csv — {len(rules)} pair rules')
print(rules[save_cols].head(10).to_string(index=False))
