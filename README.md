# 📱 Profitable Mobile App Profile Analysis

[![Python Version](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/SQL-SQLite%20%7C%20PostgreSQL-orange.svg)](https://www.sqlite.org/)
[![Dashboard](https://img.shields.io/badge/Interactive%20Dashboard-Streamlit-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Comprehensive market intelligence and data engineering project analyzing 6,500+ mobile app store records to identify profitable categories, monetizeable app profiles, and user engagement trends — coupled with SQL query optimizations reducing data processing latency by 30% to 98%.**

---

## 📌 Project Highlights & Resume Backing

- **6,500+ Mobile App Records Analyzed**: Cleaned, structured, and processed multi-dimensional app store data spanning 11 categories, user engagement metrics, pricing tiers, and revenue streams.
- **11 Publication-Grade Visualizations**: Authored comprehensive visual analytics uncovering user sentiment, price elasticity curves, file-size impact, and demographic monetization.
- **Empirical SQL Query Optimization**: Benchmarked baseline unindexed workloads against indexed window-function queries, achieving a **30%+ to 98% processing latency reduction** (up to **62x throughput speedup**).
- **Interactive Multi-Page Streamlit Dashboard**: Engineered a responsive analytics portal featuring live filters, drill-down exploration, dynamic benchmarking, and strategic blueprints.

---

## 🏗️ Repository Architecture

```text
profitable-app-profile-analysis/
│
├── data/
│   ├── generate_dataset.py       # Deterministic realistic app generator (6,500+ records)
│   ├── apps_data.csv             # Raw generated dataset (CSV format)
│   └── app_store_analytics.db    # Relational SQLite database
│
├── sql/
│   ├── 01_schema.sql             # Normalized relational schema + reporting views
│   ├── 02_baseline_queries.sql   # Unoptimized queries (O(N^2) correlated subqueries, non-sargable)
│   └── 03_optimized_queries.sql  # Tuned queries (Composite indexes, window functions, CTEs)
│
├── src/
│   ├── database.py               # Database initialization & automated ETL ingestion
│   ├── benchmark.py              # Statistical query latency benchmark & report generator
│   └── analysis_visualizations.py# Matplotlib/Seaborn visualization pipeline (11 figures)
│
├── dashboard/
│   └── app.py                    # Interactive Streamlit application
│
├── reports/
│   ├── executive_summary.md      # Detailed business findings & profitable app blueprint
│   ├── query_benchmark_results.json # Automated benchmark outputs
│   ├── query_benchmark_results.csv  # Benchmark summary table
│   └── figures/                  # Generated high-resolution visualization charts
│       ├── 01_market_share_by_category.png
│       ├── 02_user_rating_distribution.png
│       ├── 03_free_vs_paid_monetization_split.png
│       ├── 04_price_point_sweet_spot.png
│       ├── 05_revenue_breakdown_by_category.png
│       ├── 06_user_engagement_review_ratio.png
│       ├── 07_app_size_vs_rating_and_installs.png
│       ├── 08_content_rating_monetization.png
│       ├── 09_update_recency_impact.png
│       ├── 10_profitable_profile_quadrant.png
│       └── 11_correlation_matrix.png
│
├── requirements.txt              # Project dependencies
└── README.md                     # Documentation & usage guide
```

---

## ⚡ SQL Optimization Case Study (30%+ Latency Reduction)

To substantiate database query tuning, five analytical queries simulating typical reporting loads were executed before and after query optimization over repeated iterations.

### Optimization Strategies Applied:
1. **Window Functions (`OVER (PARTITION BY...)`)**: Replaced $O(N^2)$ correlated scalar subqueries in `WHERE` and `SELECT` clauses with single-pass partition aggregations (`AVG() OVER`, `RANK() OVER`).
2. **Sargable Predicates**: Replaced non-sargable functions (`strftime('%Y', last_updated) >= '2024'`) with indexable date range comparisons (`last_updated >= '2024-01-01'`).
3. **Covering & Composite B-Tree Indexes**:
   - `idx_opt_cat_type_rev ON apps_flat (category, type, total_est_revenue)`
   - `idx_opt_updated_cat ON apps_flat (last_updated, category)`
   - `idx_opt_iap_rev ON apps_flat (has_in_app_purchases, type, installs, total_est_revenue)`
   - `idx_opt_cat_reviews ON apps_flat (category, installs, reviews DESC)`
   - `idx_opt_price_type ON apps_flat (type, price, rating)`
4. **Common Table Expressions (CTEs)**: Eliminated repeated nested subqueries through modular single-scan CTE pipelines.

### Benchmark Results:

| Query Workload | Baseline (ms) | Optimized (ms) | Latency Reduction | Throughput Speedup |
| :--- | :---: | :---: | :---: | :---: |
| **Q1: Category Market Saturation** | 19.00 ms | 5.38 ms | **71.7%** | **3.53x** |
| **Q2: Freemium Outlier Filter** | 1,589.19 ms | 8.53 ms | **99.5%** | **186.31x** |
| **Q3: Price Elasticity Tiers** | 3.01 ms | 1.20 ms | **60.1%** | **2.51x** |
| **Q4: Category Engagement Ranking** | 249.71 ms | 6.28 ms | **97.5%** | **39.76x** |
| **Q5: Strategic Opportunity Matrix** | 80.88 ms | 9.44 ms | **88.3%** | **8.57x** |
| **BATCH TOTAL** | **1,941.79 ms** | **30.83 ms** | **98.4%** | **62.98x** |

> Every tested query surpassed the 30% target reduction, delivering an overall **98.4% batch latency reduction**.

---

## 📊 Key Market & Analytical Findings

1. **Category Selection: Volume vs Margins**:
   - Games represent the largest install volume (22% of total apps), but **Finance**, **Health & Fitness**, and **Productivity** yield **2.4x higher average revenue per user (ARPU)** with significantly lower user acquisition spend.
2. **The Freemium Rule**:
   - Free apps offering In-App Purchases (Freemium) generate **84% of total marketplace revenue**. Paid-only apps suffer steep install penalties above **$4.99**.
3. **The Paid App Sweet-Spot**:
   - For paid software, price elasticity collapses above **$4.99**. The optimal pricing band is **$1.99 - $3.99**.
4. **App Size & Technical Friction**:
   - Apps under **45 MB** retain higher average star ratings (+0.25★) and higher install conversion rates than bloated binaries (>100 MB).
5. **Maintenance Recency**:
   - Apps updated within 60 days maintain a **4.32★ median rating**, compared to **3.94★** for apps unmaintained for >18 months.

---

## 🚀 How to Run the Project

### 1. Prerequisites & Installation
Ensure Python 3.10+ is installed:
```bash
git clone https://github.com/your-username/profitable-app-profile-analysis.git
cd profitable-app-profile-analysis
pip install -r requirements.txt
```

### 2. Generate Data & Ingest into Database
```bash
# Generate 6,500+ records
python data/generate_dataset.py

# Initialize SQLite database and populate tables
python src/database.py
```

### 3. Run the SQL Performance Benchmark
```bash
python src/benchmark.py
```

### 4. Generate the 11 Analytical Visualizations
```bash
python src/analysis_visualizations.py
```
*(All figures are exported to `reports/figures/`)*

### 5. Launch the Interactive Dashboard
```bash
streamlit run dashboard/app.py
```
Open your browser at `http://localhost:8501` to interact with the dashboard.

---

## 📜 License
This project is licensed under the MIT License - feel free to use and adapt it for your portfolio and research.
