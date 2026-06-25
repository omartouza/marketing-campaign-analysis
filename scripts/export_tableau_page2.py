"""
Tableau CSV Export — Page 2: CLV & Targeting
Standalone script — re-trains the same models as 04_clv_prediction.ipynb
to produce per-customer predictions and model comparison tables for Tableau.

Run: python3 export_tableau_page2.py
"""

import os
import getpass
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.dummy import DummyRegressor, DummyClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import (
    RandomForestRegressor, GradientBoostingRegressor,
    RandomForestClassifier, GradientBoostingClassifier,
)
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, roc_auc_score, recall_score,
)
from sklearn.utils.class_weight import compute_sample_weight

PROJECT_ROOT = os.path.expanduser('~/Desktop/marketing-campaign-analysis')
TABLEAU_PATH = os.path.join(PROJECT_ROOT, 'dashboard', 'tableau_data')
os.makedirs(TABLEAU_PATH, exist_ok=True)

username = getpass.getuser()
engine = create_engine(f'postgresql+psycopg2://{username}@localhost:5432/marketing_db', future=True)

def run_query(sql):
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)

n = run_query('SELECT COUNT(*) AS n FROM customers')['n'].values[0]
print(f'Connected ✅ — {n:,} customers')
if n != 2212:
    print(f'⚠️  Expected 2,212. Got {n:,}. Re-run Phase 2 first.')

# --- Pull features (same query as Phase 4 notebook) ---
sql = '''
SELECT
    cu.customer_id, s.total_spend, cu.age, cu.income, cu.education,
    cu.marital_status, cu.total_children, cu.has_children,
    cu.tenure_days, cu.recency, ch.num_web_visits_month,
    ca.total_hist_campaigns_accepted, ca.response,
    ch.num_web_purchases, ch.num_store_purchases,
    ch.num_catalog_purchases, ch.num_deals_purchases, ch.total_purchases,
    NTILE(3) OVER (ORDER BY s.total_spend) AS clv_tier_num,
    CASE NTILE(3) OVER (ORDER BY s.total_spend)
        WHEN 1 THEN 'Low value' WHEN 2 THEN 'Mid value' ELSE 'High value' END AS clv_tier
FROM customers cu
JOIN channels  ch ON cu.customer_id = ch.customer_id
JOIN campaigns ca ON cu.customer_id = ca.customer_id
JOIN spending  s  ON cu.customer_id = s.customer_id
'''
df = run_query(sql)
print(f'Features loaded: {df.shape}')

# --- One-hot encode ---
edu_dummies = pd.get_dummies(df['education'], prefix='edu', drop_first=True)
mar_dummies = pd.get_dummies(df['marital_status'], prefix='marital', drop_first=True)
df = pd.concat([df, edu_dummies, mar_dummies], axis=1)

# --- CLV regression (leakage-free features) ---
clv_features = ['age', 'income', 'total_children', 'has_children',
                 'tenure_days', 'recency', 'num_web_visits_month',
                 'total_hist_campaigns_accepted'] + list(edu_dummies.columns) + list(mar_dummies.columns)

X = df[clv_features].values
y = df['total_spend'].values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train_s, X_test_s = scaler.fit_transform(X_train), scaler.transform(X_test)

reg_models = {
    'Baseline (mean)': DummyRegressor(strategy='mean'),
    'Linear Regression': LinearRegression(),
    'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
    'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
}
reg_rows, reg_trained = [], {}
for name, m in reg_models.items():
    is_lin = name in ('Baseline (mean)', 'Linear Regression')
    Xtr, Xte = (X_train_s, X_test_s) if is_lin else (X_train, X_test)
    m.fit(Xtr, y_train)
    preds = m.predict(Xte)
    reg_rows.append({
        'model': name,
        'mae': round(mean_absolute_error(y_test, preds), 2),
        'rmse': round(np.sqrt(mean_squared_error(y_test, preds)), 2),
        'r2': round(r2_score(y_test, preds), 4),
    })
    reg_trained[name] = m
reg_comparison = pd.DataFrame(reg_rows)
best_reg_name = reg_comparison[reg_comparison['model'] != 'Baseline (mean)'].sort_values('r2', ascending=False).iloc[0]['model']
best_reg_model = reg_trained[best_reg_name]
print(f'Regression winner: {best_reg_name}')

# Feature importance from winner
if hasattr(best_reg_model, 'feature_importances_'):
    importance = best_reg_model.feature_importances_
elif hasattr(best_reg_model, 'coef_'):
    importance = np.abs(best_reg_model.coef_)
else:
    importance = np.zeros(len(clv_features))
feature_importance = pd.DataFrame({
    'feature': clv_features, 'importance': importance
}).sort_values('importance', ascending=False).reset_index(drop=True)
feature_importance['model'] = best_reg_name

# Predicted spend for ALL customers (for the dashboard, not just test set)
X_all = df[clv_features].values
X_all_input = scaler.transform(X_all) if best_reg_name in ('Baseline (mean)', 'Linear Regression') else X_all
df['predicted_spend'] = best_reg_model.predict(X_all_input)

# --- Response classifier ---
clf_features = clv_features + ['total_spend', 'num_web_purchases', 'num_store_purchases',
                                'num_catalog_purchases', 'num_deals_purchases', 'total_purchases']
X_clf = df[clf_features].values
y_clf = df['response'].values
Xc_train, Xc_test, yc_train, yc_test = train_test_split(X_clf, y_clf, test_size=0.2, random_state=42, stratify=y_clf)
scaler_clf = StandardScaler()
Xc_train_s, Xc_test_s = scaler_clf.fit_transform(Xc_train), scaler_clf.transform(Xc_test)
weights = compute_sample_weight(class_weight='balanced', y=yc_train)

clf_models = {
    'Baseline (random)': DummyClassifier(strategy='stratified', random_state=42),
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
}
clf_rows, clf_trained = [], {}
for name, clf in clf_models.items():
    is_lin = name in ('Baseline (random)', 'Logistic Regression')
    Xtr, Xte = (Xc_train_s, Xc_test_s) if is_lin else (Xc_train, Xc_test)
    if name == 'Baseline (random)':
        clf.fit(Xtr, yc_train)
    else:
        clf.fit(Xtr, yc_train, sample_weight=weights)
    preds = clf.predict(Xte)
    proba = clf.predict_proba(Xte)[:, 1]
    clf_rows.append({
        'model': name,
        'recall_respond': round(recall_score(yc_test, preds, pos_label=1), 4),
        'recall_not_respond': round(recall_score(yc_test, preds, pos_label=0), 4),
        'accuracy': round(accuracy_score(yc_test, preds), 4),
        'auc_roc': round(roc_auc_score(yc_test, proba), 4),
    })
    clf_trained[name] = clf
clf_comparison = pd.DataFrame(clf_rows)
candidates = clf_comparison[clf_comparison['model'] != 'Baseline (random)'].sort_values(
    ['recall_respond', 'auc_roc'], ascending=[False, False])
best_clf_name = candidates.iloc[0]['model']
best_clf = clf_trained[best_clf_name]
print(f'Classifier winner: {best_clf_name}')

# Predicted probability for ALL customers
X_clf_all_input = scaler_clf.transform(X_clf) if best_clf_name in ('Baseline (random)', 'Logistic Regression') else X_clf
df['response_prob'] = best_clf.predict_proba(X_clf_all_input)[:, 1]

# --- Exports ---
out_cols = ['customer_id', 'age', 'income', 'education', 'marital_status',
            'clv_tier', 'total_spend', 'predicted_spend', 'response', 'response_prob']
df[out_cols].to_csv(os.path.join(TABLEAU_PATH, 'customer_clv_predictions.csv'), index=False)
print('✅ customer_clv_predictions.csv')

reg_comparison.to_csv(os.path.join(TABLEAU_PATH, 'clv_regression_model_comparison.csv'), index=False)
print('✅ clv_regression_model_comparison.csv')

clf_comparison.to_csv(os.path.join(TABLEAU_PATH, 'response_classifier_comparison.csv'), index=False)
print('✅ response_classifier_comparison.csv')

feature_importance.to_csv(os.path.join(TABLEAU_PATH, 'clv_feature_importance.csv'), index=False)
print('✅ clv_feature_importance.csv')

targeting = df.groupby('clv_tier').agg(
    customer_count=('customer_id', 'count'),
    avg_spend=('total_spend', 'mean'),
    avg_response_prob=('response_prob', 'mean'),
    actual_response_rate=('response', 'mean'),
).round(4).reset_index()
order_map = {'High value': 0, 'Mid value': 1, 'Low value': 2}
targeting['sort_order'] = targeting['clv_tier'].map(order_map)
targeting = targeting.sort_values('sort_order')
targeting.to_csv(os.path.join(TABLEAU_PATH, 'targeting_priority_matrix.csv'), index=False)
print('✅ targeting_priority_matrix.csv')

print()
print(f'Selected models — Regression: {best_reg_name}, Classifier: {best_clf_name}')
print(f'All files saved to: {TABLEAU_PATH}')
