"""
Tableau CSV Export — Page 3: Sentiment Analysis
Standalone script — re-runs the same NLP pipeline as 05_sentiment_analysis.ipynb.

Run: python3 export_tableau_page3.py
"""

import os
import re
import getpass
import numpy as np
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import confusion_matrix, accuracy_score, roc_auc_score, recall_score
from sklearn.preprocessing import label_binarize

# Anchor to this script's own location so it runs from any working directory.
# scripts/ sits one level below the repo root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TABLEAU_PATH = str(PROJECT_ROOT / 'dashboard' / 'tableau_data')
os.makedirs(TABLEAU_PATH, exist_ok=True)

nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

username = getpass.getuser()
engine = create_engine(f'postgresql+psycopg2://{username}@localhost:5432/marketing_db', future=True)

def run_query(sql):
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)

n = run_query('SELECT COUNT(*) AS n FROM reviews')['n'].values[0]
print(f'Connected ✅ — {n:,} reviews')

# ---------------------------------------------------------------
# SQL-based exports (no model training needed)
# ---------------------------------------------------------------
dist = run_query('''
    SELECT sentiment, COUNT(*) AS review_count,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct
    FROM reviews WHERE review_text IS NOT NULL
    GROUP BY sentiment ORDER BY review_count DESC
''')
dist.to_csv(os.path.join(TABLEAU_PATH, 'sentiment_distribution.csv'), index=False)
print('✅ sentiment_distribution.csv')

category = run_query('''
    SELECT category, COUNT(*) AS total_reviews,
        SUM(CASE WHEN sentiment='Positive' THEN 1 ELSE 0 END) AS positive,
        SUM(CASE WHEN sentiment='Neutral'  THEN 1 ELSE 0 END) AS neutral,
        SUM(CASE WHEN sentiment='Negative' THEN 1 ELSE 0 END) AS negative,
        ROUND(SUM(CASE WHEN sentiment='Negative' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)::NUMERIC, 2) AS negative_pct,
        ROUND(AVG(rating)::NUMERIC, 2) AS avg_rating
    FROM reviews WHERE category IS NOT NULL AND TRIM(category) != ''
    GROUP BY category HAVING COUNT(*) >= 100
    ORDER BY negative_pct DESC LIMIT 10
''')
category.to_csv(os.path.join(TABLEAU_PATH, 'sentiment_by_category.csv'), index=False)
print('✅ sentiment_by_category.csv')

rating_profile = run_query('''
    SELECT sentiment, COUNT(*) AS review_count,
           ROUND(AVG(rating)::NUMERIC, 2) AS avg_rating,
           ROUND(AVG(review_length)::NUMERIC, 0) AS avg_length
    FROM reviews GROUP BY sentiment ORDER BY avg_rating DESC
''')
rating_profile.to_csv(os.path.join(TABLEAU_PATH, 'sentiment_rating_profile.csv'), index=False)
print('✅ sentiment_rating_profile.csv')

# ---------------------------------------------------------------
# NLP pipeline — re-train models (same as Phase 5 notebook)
# ---------------------------------------------------------------
reviews = run_query('''
    SELECT review_text, rating, sentiment, product_name, category
    FROM reviews WHERE review_text IS NOT NULL AND TRIM(review_text) != ''
    ORDER BY md5(review_text || COALESCE(review_title, '') || COALESCE(product_name, ''))
''')
for col in ['review_text', 'sentiment', 'product_name', 'category']:
    reviews[col] = reviews[col].astype(str).fillna('').astype(object)

stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))
stop_words.update({'product','item','bought','buy','purchase','ordered','amazon','price',
                    'shipping','arrived','received','use','used','using','one','get','got',
                    'would','could','also','even','still','well','just','like','really'})

def preprocess(t):
    t = str(t)
    if not t.strip() or t in ('nan', 'None', ''):
        return ''
    t = t.lower()
    t = re.sub(r'http\S+|www\S+', '', t)
    t = re.sub(r'[^a-z\s]', '', t)
    tokens = word_tokenize(t)
    tokens = [tok for tok in tokens if tok not in stop_words and len(tok) > 2]
    return ' '.join(stemmer.stem(tok) for tok in tokens)

print('Preprocessing text...')
reviews['clean_text'] = reviews['review_text'].apply(preprocess).astype(object)
reviews = reviews[reviews['clean_text'].str.strip() != ''].reset_index(drop=True)
print(f'Reviews after cleaning: {len(reviews):,}')

X = reviews['clean_text'].to_numpy(dtype=str)
y = reviews['sentiment'].to_numpy(dtype=str)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1,2), min_df=3, sublinear_tf=True)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

classes = sorted(np.unique(y_train).tolist())
classifiers = {
    'Naive Bayes': MultinomialNB(alpha=0.1),
    'Logistic Regression': LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42, C=1.0),
    'Linear SVC': CalibratedClassifierCV(LinearSVC(class_weight='balanced', max_iter=2000, random_state=42, C=1.0)),
}

predictions, probabilities, rows = {}, {}, []
for name, clf in classifiers.items():
    clf.fit(X_train_tfidf, y_train)
    preds = clf.predict(X_test_tfidf)
    proba = clf.predict_proba(X_test_tfidf)
    predictions[name] = preds
    probabilities[name] = proba
    y_bin = label_binarize(y_test, classes=classes)
    rows.append({
        'model': name,
        'accuracy': round(accuracy_score(y_test, preds), 4),
        'auc_roc': round(roc_auc_score(y_bin, proba, multi_class='ovr', average='macro'), 4),
        'negative_recall': round(recall_score(y_test, preds, labels=['Negative'], average='macro'), 4),
        'neutral_recall': round(recall_score(y_test, preds, labels=['Neutral'], average='macro'), 4),
        'positive_recall': round(recall_score(y_test, preds, labels=['Positive'], average='macro'), 4),
    })
    print(f'{name} trained ✅')

model_comparison = pd.DataFrame(rows)
model_comparison.to_csv(os.path.join(TABLEAU_PATH, 'sentiment_model_comparison.csv'), index=False)
print('✅ sentiment_model_comparison.csv')

candidates = model_comparison.sort_values(['negative_recall', 'auc_roc'], ascending=[False, False])
best_name = candidates.iloc[0]['model']
print(f'Selected model: {best_name}')

# Confusion matrix for selected model (long format for Tableau heatmap)
cm = confusion_matrix(y_test, predictions[best_name], labels=classes)
cm_rows = []
for i, actual in enumerate(classes):
    for j, predicted in enumerate(classes):
        cm_rows.append({'actual': actual, 'predicted': predicted, 'count': int(cm[i, j])})
cm_df = pd.DataFrame(cm_rows)
cm_df['model'] = best_name
cm_df.to_csv(os.path.join(TABLEAU_PATH, 'sentiment_confusion_matrix.csv'), index=False)
print('✅ sentiment_confusion_matrix.csv')

# Top words per sentiment
feature_names = vectorizer.get_feature_names_out()
top_words_rows = []
for sentiment in classes:
    mask = y_train == sentiment
    subset = X_train_tfidf[mask]
    mean_scores = np.asarray(subset.mean(axis=0)).flatten()
    top_idx = mean_scores.argsort()[-15:][::-1]
    for rank, i in enumerate(top_idx, 1):
        top_words_rows.append({
            'sentiment': sentiment, 'rank': rank,
            'word': feature_names[i], 'tfidf_score': round(float(mean_scores[i]), 4)
        })
pd.DataFrame(top_words_rows).to_csv(os.path.join(TABLEAU_PATH, 'sentiment_top_words.csv'), index=False)
print('✅ sentiment_top_words.csv')

print()
print(f'All files saved to: {TABLEAU_PATH}')
print(f'Selected production model: {best_name}')
