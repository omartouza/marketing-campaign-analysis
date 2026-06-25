
-- marketing_db schema for Phase 2

-- Drop in reverse FK order so children go first
DROP TABLE IF EXISTS campaigns;
DROP TABLE IF EXISTS channels;
DROP TABLE IF EXISTS spending;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS customers;

-- Table 1: customer demographics (parent)
CREATE TABLE customers (
    customer_id     INTEGER PRIMARY KEY,
    year_birth      INTEGER,
    age             INTEGER,
    education       VARCHAR(50),
    marital_status  VARCHAR(50),
    income          NUMERIC(12,2),
    kidhome         INTEGER,
    teenhome        INTEGER,
    total_children  INTEGER,
    has_children    INTEGER,
    dt_customer     DATE,
    tenure_days     INTEGER,
    recency         INTEGER,
    complain        INTEGER
);

-- Table 2: product spending
CREATE TABLE spending (
    customer_id  INTEGER PRIMARY KEY REFERENCES customers(customer_id),
    mnt_wines    NUMERIC(10,2),
    mnt_fruits   NUMERIC(10,2),
    mnt_meat     NUMERIC(10,2),
    mnt_fish     NUMERIC(10,2),
    mnt_sweets   NUMERIC(10,2),
    mnt_gold     NUMERIC(10,2),
    total_spend  NUMERIC(10,2)
);

-- Table 3: purchase channels
CREATE TABLE channels (
    customer_id             INTEGER PRIMARY KEY REFERENCES customers(customer_id),
    num_web_purchases       INTEGER,
    num_catalog_purchases   INTEGER,
    num_store_purchases     INTEGER,
    num_deals_purchases     INTEGER,
    num_web_visits_month    INTEGER,
    total_purchases         INTEGER,
    avg_spend_per_purchase  NUMERIC(10,2)
);

-- Table 4: campaign response history
-- Z_CostContact and Z_Revenue dropped — they were constants in source data
CREATE TABLE campaigns (
    customer_id                  INTEGER PRIMARY KEY REFERENCES customers(customer_id),
    accepted_cmp1                INTEGER,
    accepted_cmp2                INTEGER,
    accepted_cmp3                INTEGER,
    accepted_cmp4                INTEGER,
    accepted_cmp5                INTEGER,
    response                     INTEGER,
    total_hist_campaigns_accepted INTEGER
);

-- Table 5: Amazon reviews (standalone — no FK to campaign tables)
CREATE TABLE reviews (
    product_name   TEXT,
    brand          TEXT,
    category       TEXT,
    rating         NUMERIC(3,1),
    review_title   TEXT,
    review_text    TEXT,
    review_date    DATE,
    review_length  INTEGER,
    sentiment      VARCHAR(20)
);
