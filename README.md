![CI](https://github.com/omartouza/marketing-campaign-analysis/actions/workflows/notebooks-ci.yml/badge.svg)

# Marketing Campaign Analysis

End-to-end marketing analytics project covering customer lifetime value prediction, sentiment analysis, market basket analysis, and campaign performance — built across 6 analytical phases and visualised in an interactive Tableau dashboard.

**[View the live dashboard →](https://public.tableau.com/app/profile/touzani.omar/viz/Marketing_campaign_analysis/CampaignPerformance?publish=yes)**

---

## Project overview

This project analyses a marketing campaign dataset alongside Amazon product reviews to answer four core business questions:

- Which campaigns are most cost-efficient, and which customers are responding?
- Which customers are most valuable, and how likely are they to respond to future campaigns?
- Which product categories are purchased together, and how does this vary by customer value tier?
- What do customers say about products, and which sentiment model best identifies complaints?

---

## Data limitations

### The two datasets are not related
The marketing campaign dataset (2,240 customers, 2,212 after cleaning) and the Amazon reviews dataset (28,332 raw reviews, 25,673 after cleaning) share no customers, no product IDs, and no way to join them. The Amazon reviews were brought in specifically to demonstrate NLP skills, since the campaign dataset contains no text data. The sentiment findings are standalone insights that cannot be directly connected to CLV tiers or campaign response rates.

A combined dataset — linking customer demographics, purchase history, and written product reviews for the same customers — would require a company to publish data that raises serious privacy concerns. In a production environment this analysis would be performed on reviews tied to the same customer IDs as the campaign data, enabling questions such as: do high-value customers who leave negative reviews respond differently to campaigns?

### No individual transaction records
The marketing campaign dataset contains total spend per category over 2 years — not individual purchase transactions. Market basket analysis normally operates on transaction-level data (one row per purchase). Here each customer is treated as a single basket, so the analysis identifies customer-level category co-occurrence rather than true transaction-level product associations. In a retail environment with individual receipts, the basket analysis would be significantly more granular.

### Class imbalance in sentiment data
90.2% of reviews are Positive (4–5 stars), 5.6% Negative (1–2 stars), and 4.3% Neutral (3 stars). This severe imbalance limits the model's ability to detect the minority classes. Model selection prioritises recall on the Negative (complaint) class over headline accuracy, and `class_weight='balanced'` mitigates — but does not eliminate — the imbalance.

### CLV proxy
Total historical spend is used as a proxy for Customer Lifetime Value. This is a reasonable approximation but does not account for purchase frequency, recency weighting, customer tenure, or predicted future behaviour. A true CLV model would require transaction-level timestamps and ideally a longer observation window.

---

## Dashboard

Built in Tableau Public — 4 interactive pages with filters and highlighters.

| Page | What it shows |
|---|---|
| Campaign performance | Acceptance rates, cost-efficiency, responder profiles, channel volumes |
| CLV & Targeting | Customer value tiers, response probability, feature importance, income vs spend |
| Market basket analysis | Category co-purchase heatmap, association rules by lift, tier-level basket profiles |
| Sentiment analysis | Sentiment distribution, top words per class, negative rates by category, model comparison |

---

## Tech stack

| Tool | Purpose |
|---|---|
| Python 3.11 | Data processing, modelling, NLP |
| PostgreSQL | Relational database — all clean data stored and queried here |
| VS Code + SQLTools | Database connection and SQL development |
| pandas, numpy | Data manipulation |
| scikit-learn | CLV regression, campaign response classifier, sentiment classification |
| mlxtend | Apriori and FP-Growth market basket analysis |
| nltk | Text preprocessing — tokenisation, stopword removal, stemming |
| matplotlib, seaborn, wordcloud | Visualisations and charts |
| Tableau Public | Interactive dashboard |
| Git + GitHub | Version control |

---

## Datasets

**Dataset 1 — Marketing Campaign**
- 2,240 customers (2,212 after cleaning)
- Demographics, spending across 6 product categories, purchase-channel behaviour, campaign response history
- Tab-separated CSV (`marketing_campaign.csv`)
- Source: [Marketing Campaign dataset on Kaggle](https://www.kaggle.com/datasets/rodsaldanha/arketing-campaign)
- Used in: Phases 1, 2, 3, 4, 6

**Dataset 2 — Amazon Product Reviews**
- 28,332 raw reviews (25,673 after cleaning)
- Review text, star rating, product category (`Datafiniti_Amazon_Consumer_Reviews_of_Amazon_Products_May19.csv`)
- Source: Datafiniti Amazon Consumer Reviews (May 2019 release) — *add exact dataset link*
- Used in: Phase 5 only

---

## Phases

### Phase 1 — Exploratory data analysis
Exploration of the marketing campaign dataset — distributions, missing values, outliers, correlations — plus a first look at the review data.

**Key findings:**
- 24 customers (1.07%) have missing income; flagged for removal in Phase 2
- 3 customers have a birth year ≤ 1900 and 1 has income > $200K (`$666,666`) — flagged as outliers
- Spending is dominated by Wines ($680,816) and Meat ($373,968) across the 6 categories
- Store is the dominant channel (12,970 purchases); Deals the weakest (5,208)
- Campaign acceptance ranges from 1.34% (Campaign 2) to 14.91% (the most recent campaign)
- Reviews skew heavily positive: 70.2% are 5-star, only 5.6% are 1–2 star
- 1,669 review rows are duplicate (product, text) pairs — flagged for de-duplication

---

### Phase 2 — Data cleaning & database loading
Full cleaning pipeline followed by loading into PostgreSQL in a normalised 5-table schema. Raw files are SHA-256-checksummed before processing.

**Cleaning trail (logged row-by-row):**
- Campaign: 2,240 → drop 24 missing-income → 2,216 → drop 3 age outliers → 2,213 → drop 1 income outlier → **2,212** (28 rows / 1.25% removed)
- Reviews: 28,332 → drop reviews under 20 characters (and empties) → **25,673** (2,659 / 9.39% removed)

**Schema (loaded row counts):**
```
customers (2,212 rows) — demographics
spending  (2,212 rows) — category spend
channels  (2,212 rows) — purchase channel behaviour
campaigns (2,212 rows) — campaign response history
reviews  (25,673 rows) — Amazon product reviews (cleaned)
```
Cleaned class balance: 89.6% Positive, 5.9% Negative, 4.4% Neutral.

---

### Phase 3 — Campaign performance analysis
SQL-driven analysis of all 6 campaigns. Cost-efficiency is expressed as a **break-even ratio** — the minimum revenue-to-cost ratio each campaign needs to be worthwhile — rather than a fabricated ROI, since the dataset contains no campaign cost or revenue figures. A scenario table (conservative / moderate / optimistic cost-per-contact assumptions) makes the break-even tangible.

**Key findings:**
- The most recent campaign is both the best-accepted (15.05%) and the most cost-efficient (breaks even at 6.6× revenue:cost)
- Campaign 2 is the worst on both counts: 1.36% acceptance, break-even at 73.7×
- Responders spend 82.6% more than non-responders ($986 vs $540) and accept far more past campaigns (0.99 vs 0.18)
- Catalog is the luxury channel — high spenders use it ~20× more than low spenders
- 97.8% of customers who visit the web channel buy online; only ~20 are heavy visitors who never purchase

---

### Phase 4 — Customer lifetime value prediction

**Regression — CLV prediction (leakage-free, 16 features):**
- Models: Linear Regression, Random Forest, Gradient Boosting + a mean baseline
- **Best model: Random Forest — R² = 0.859, MAE = $151.58** (baseline R² ≈ 0, confirming the model learns real signal)
- The target (`total_spend`) is excluded from the feature set to prevent leakage

**Classification — campaign response (22 features):**
- Evaluation order: confusion matrix → classification report → AUC-ROC; all models evaluated before selection
- Selection driven by recall on the responder class, not headline accuracy

| Model | Recall (Respond) | Recall (Not) | Accuracy | AUC-ROC |
|---|---|---|---|---|
| **Logistic Regression** | **0.746** | 0.822 | 0.810 | 0.882 |
| Gradient Boosting | 0.687 | 0.851 | 0.826 | 0.879 |
| Random Forest | 0.269 | 0.984 | 0.876 | 0.872 |

- **Selected model: Logistic Regression** — catches 75% of responders. Random Forest posts the highest accuracy (0.876) but catches only 27% of responders — the accuracy trap
- High-value customers respond at 44.6% vs 23.7% for low-value (≈1.9× lift)

---

### Phase 5 — Sentiment analysis
NLP text classification on Amazon reviews using TF-IDF (unigrams + bigrams, max 10k features). All splits and models are seeded.

**Evaluation order: confusion matrix → classification report → AUC-ROC**

| Model | Accuracy | AUC-ROC (macro) | Neg recall | Neu recall | Pos recall |
|---|---|---|---|---|---|
| Naive Bayes | 0.930 | 0.938 | 0.580 | 0.137 | 0.992 |
| **Logistic Regression** | **0.895** | **0.936** | **0.813** | **0.723** | **0.909** |
| Linear SVC | 0.948 | 0.937 | 0.728 | 0.361 | 0.991 |

**Selected model: Logistic Regression.**
Selection prioritises recall on the Negative (complaint) class — the business-critical class for review sentiment. Logistic Regression catches 81% of negative reviews (248 of 305) versus Linear SVC's 73% (222) — ~26 more complaints caught — and handles the hard Neutral class far better (0.723 vs 0.361). Linear SVC has the highest accuracy, but on data that is 90% Positive, accuracy rewards competence on the easy majority class — exactly the trap recall-first selection avoids.

**Key findings:**
- Battery performance is a top signal across all three sentiment classes
- Health & Beauty generates a higher negative-review rate than Electronics
- Negative reviews run longer on average than positive ones

---

### Phase 6 — Market basket analysis
Association-rule mining on customer category-spending profiles using Apriori and FP-Growth (categories with spend above a $10 threshold treated as basket items).

**Results:**
- **63 frequent itemsets** at min_support = 0.10 — **identical for both Apriori and FP-Growth** (an internal consistency check)
- **591 association rules** (lift ≥ 1.2, confidence ≥ 0.5)
- Strongest rule: **Fish + Gold + Meat → Fruits + Sweets + Wines** (support 0.24, confidence 0.74, **lift 2.30**)
- No anti-associations (no pair with lift < 0.9)

**Per CLV tier** (min_support 0.15): Low-value 55 rules, Mid-value 108, High-value 25. **Zero rules are unique to the High-value tier** — top customers buy *more* of the same gourmet basket, not different things, which is the cross-sell signature.

**Key findings:**
- Wines and Meat are the most common single categories (50.0% / 49.6% of customers)
- The strongest associations cluster the full gourmet basket (Fish, Gold, Meat, Fruits, Sweets, Wines)
- Co-purchase lift is highest in the Low/Mid tiers and compresses toward 1.0 in the High tier (top customers buy everything, so pairs are less "surprising")

---

## Reproducibility

This project is built to reproduce: with the same raw data loaded into the same database, running the notebooks in order yields the figures reported above.

### Data
The raw datasets are **not included** in this repository (licensing). Download them and place both files in `data/raw/`:
- `marketing_campaign.csv` (tab-separated)
- `Datafiniti_Amazon_Consumer_Reviews_of_Amazon_Products_May19.csv`

**Snapshot integrity.** `02_data_cleaning_db_loading.ipynb` prints a SHA-256 checksum for each raw file before processing. If your checksums differ from the table below, you have a different version of the data and results may differ.

| File | SHA-256 (first 12) |
|---|---|
| marketing_campaign.csv | `cd0affa36b1b` |
| Datafiniti_Amazon_Consumer_Reviews_of_Amazon_Products_May19.csv | `9778f5b1a7e5` |

### Environment
- **Python:** 3.11.7
- Install pinned dependencies: `pip install -r requirements.txt`

### Database (required for Phases 2–6)
The cleaned data is loaded into a local PostgreSQL database that the analysis phases query directly. You need PostgreSQL running locally with:
- a database named `marketing_db`
- local trust authentication (the notebooks connect as your system user with no password, via `postgresql+psycopg2://<user>@localhost:5432/marketing_db`)

Without a running database, only Phase 1 (EDA on the raw CSVs) will run.

### Randomness
All stochastic operations use a fixed seed (`RANDOM_STATE = 42`): the train/test splits and models in Phase 4 (CLV regression and response classifier) and Phase 5 (sentiment classifiers). Phases 3 and 6 (SQL analysis, Apriori / FP-Growth) are deterministic by construction.

### How to reproduce
1. Clone the repository and place the two raw files in `data/raw/`.
2. Create a fresh environment and run `pip install -r requirements.txt`.
3. Start PostgreSQL locally and create an empty database named `marketing_db`.
4. Run the notebooks **in order**, each from inside the repository:
   1. `01_exploratory_data_analysis.ipynb`
   2. `02_data_cleaning_db_loading.ipynb` — cleans the data and loads it into PostgreSQL
   3. `03_campaign_performance_analysis.ipynb`
   4. `04_clv_prediction.ipynb`
   5. `05_sentiment_analysis.ipynb` — downloads NLTK corpora at runtime (needs internet on first run)
   6. `06_market_basket_analysis.ipynb`
5. Regenerate the dashboard data (requires the database from step 3–4). Each script reads from `marketing_db` and writes CSVs to `dashboard/tableau_data/`:
   ```bash
   python scripts/export_tableau_page1.py   # Campaign performance
   python scripts/export_tableau_page2.py   # CLV & targeting (re-trains the Phase 4 models)
   python scripts/export_tableau_page3.py   # Sentiment (re-trains the Phase 5 models)
   python scripts/export_tableau_page4.py   # Market basket
   python scripts/export_mba_pairs_only.py  # Pair-only basket rules
   ```
   The page2 and page3 scripts re-train the same seeded models as the Phase 4/5 notebooks, so their outputs match the notebook results.
6. Open `dashboard/dashboard_marketing_campaign_analysis.twbx` to explore the views locally, or use the live dashboard link above.

---

## Project structure

```
marketing-campaign-analysis/
├── data/
│   ├── raw/                    # Original CSV files (not tracked by git)
│   └── processed/              # Cleaned data and model outputs
├── notebooks/
│   ├── 01_exploratory_data_analysis.ipynb
│   ├── 02_data_cleaning_db_loading.ipynb
│   ├── 03_campaign_performance_analysis.ipynb
│   ├── 04_clv_prediction.ipynb
│   ├── 05_sentiment_analysis.ipynb
│   └── 06_market_basket_analysis.ipynb
├── sql/
│   ├── queries/                # All SQL queries saved as .sql files
│   └── schema/                 # Database schema definition
├── scripts/                    # Standalone scripts that export PostgreSQL results to dashboard CSVs
│   ├── export_tableau_page1.py … page4.py
│   └── export_mba_pairs_only.py
├── dashboard/
│   ├── dashboard_marketing_campaign_analysis.twbx
│   └── tableau_data/           # CSV exports the dashboard reads
├── docs/                       # Charts and visualisation exports
├── reports/                    # One PDF report per phase
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Author

**Omar Touzani**
[GitHub](https://github.com/omartouza) · [Tableau Public](https://public.tableau.com/app/profile/touzani.omar)

Other portfolio projects: [E-Commerce Customer Analytics](https://github.com/omartouza/ecommerce-customer-analytics) · [Retail Customer Analysis](https://github.com/omartouza/retail-customer-analysis)

*Google certificates: Data Analytics, Advanced Data Analytics, Business Intelligence · Associate Degree in Statistics and Data Analytics, University of Lille*