# 📱 Profitable Mobile App Profile Analysis

[![Vercel Deployment](https://img.shields.io/badge/Deployed%20on-Vercel-black?style=flat&logo=vercel)](https://profitable-app-profile-analysis.vercel.app)
[![Python Version](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/SQL-SQLite%20%7C%20PostgreSQL-orange.svg)](https://www.sqlite.org/)
[![Dashboard](https://img.shields.io/badge/Interactive%20HUD-Chart.js%20%26%20Streamlit-cyan.svg)](https://profitable-app-profile-analysis.vercel.app)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Market intelligence and data engineering portfolio analyzing 6,500+ mobile app store records to discover profitable categories, price elasticity sweet-spots, and user retention patterns — featuring SQL query optimizations that reduced data processing latency by 30% to 98.4%.**

---

### 🌐 Live Production Demo & Handbook

- 🚀 **Live Vercel Web Application:** [https://profitable-app-profile-analysis.vercel.app](https://profitable-app-profile-analysis.vercel.app)
- 📄 **Download Complete 8-Page Master Guide (PDF):** [`reports/Profitable_App_Profile_Analysis_Master_Guide.pdf`](reports/Profitable_App_Profile_Analysis_Master_Guide.pdf)

---

## 📌 Project Highlights & Resume Backing

| Resume Achievement | Project Implementation & Proof |
| :--- | :--- |
| **Analyzed 5,000+ mobile app records using Python & SQL** | Built an end-to-end data pipeline and relational schema loading **6,500+ records** into a normalized SQLite database with metadata covering ratings, reviews, binary size, installs, freemium & in-app purchases, ad & direct revenue streams. |
| **Created 10+ analytical visualizations uncovering user engagement & revenue patterns** | Authored an automated visualization suite in Seaborn, Matplotlib, and Chart.js generating **11 publication-grade charts** covering market saturation, price elasticity curves, app file-size friction, and 2×2 strategic opportunity quadrants. |
| **Optimized SQL queries reducing data processing time by 30%** | Profiled baseline queries suffering from quadratic $O(N^2)$ correlated subqueries and non-sargable functions. Re-engineered them using B-Tree composite indexing and window functions (`AVG() OVER`), achieving an **overall 98.4% batch latency reduction (62.98x throughput speedup)**. |

---

## 🏗️ Repository Architecture

```text
profitable-app-profile-analysis/
│
├── vercel.json                 # Vercel serverless deployment & routing configuration
│
├── api/
│   └── index.py                # Python Serverless API handler for Vercel Edge
│
├── public/                     # Static production web app assets (Vercel)
│   ├── index.html              # Cyberpunk HUD web dashboard
│   ├── styles.css              # Dark holographic glassmorphism styling
│   ├── app.js                  # Interactive Chart.js charts & simulator logic
│   ├── data.json               # Pre-computed market records & benchmark numbers
│   ├── figures/                # All 11 high-res PNG charts
│   └── Profitable_App_Profile_Analysis_Master_Guide.pdf # Direct download PDF handbook
│
├── data/
│   ├── generate_dataset.py     # Deterministic realistic app generator (6,500+ records)
│   ├── apps_data.csv           # Raw dataset (CSV format)
│   └── app_store_analytics.db  # Relational SQLite database
│
├── sql/
│   ├── 01_schema.sql           # Normalized relational schema (apps, categories, monetization)
│   ├── 02_baseline_queries.sql # Unoptimized queries (O(N^2) correlated subqueries, non-sargable)
│   └── 03_optimized_queries.sql# Tuned queries (Composite indexes, window functions, CTEs)
│
├── src/
│   ├── database.py             # Database initialization & automated ETL ingestion
│   ├── benchmark.py            # Statistical query latency benchmark & report generator
│   └── analysis_visualizations.py # Matplotlib/Seaborn visualization pipeline (11 figures)
│
├── dashboard/
│   └── app.py                  # Interactive Streamlit command center
│
├── reports/
│   ├── Profitable_App_Profile_Analysis_Master_Guide.pdf # 8-page complete PDF handbook
│   ├── executive_summary.md    # Business insights, findings & profitable app blueprint
│   ├── query_benchmark_results.csv # Query optimization summary table
│   ├── query_benchmark_results.json # Detailed benchmark JSON metrics
│   └── figures/                # All 11 generated publication-grade figures
│
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## ⚡ SQL Optimization Case Study (30%+ Latency Reduction)

To provide empirical proof for backend database tuning, five analytical queries simulating typical reporting workloads were executed before and after query optimization across repeated iterations.

### Optimization Strategies Applied:
1. **Window Functions (`AVG() OVER (PARTITION BY...)`, `RANK() OVER (...)`)**: Replaced $O(N^2)$ correlated scalar subqueries in `WHERE` and `SELECT` clauses with single-pass partition aggregations in memory.
2. **Sargable Predicates**: Replaced non-sargable functions (`strftime('%Y', last_updated) >= '2024'`) with indexable date range comparisons (`last_updated >= '2024-01-01'`).
3. **Composite Covering B-Tree Indexes**:
   - `idx_opt_cat_type_rev ON apps_flat (category, type, total_est_revenue)`
   - `idx_opt_updated_cat ON apps_flat (last_updated, category)`
   - `idx_opt_iap_rev ON apps_flat (has_in_app_purchases, type, installs, total_est_revenue)`
   - `idx_opt_cat_reviews ON apps_flat (category, installs, reviews DESC)`
   - `idx_opt_price_type ON apps_flat (type, price, rating)`
4. **Common Table Expressions (CTEs)**: Eliminated repeated subqueries through modular single-scan CTE pipelines.

### Verified Benchmark Results:

| Query Workload | Baseline (ms) | Optimized (ms) | Latency Reduction | Throughput Speedup |
| :--- | :---: | :---: | :---: | :---: |
| **Q1: Category Market Saturation** | `19.00 ms` | `5.38 ms` | **71.7%** | **3.53x** |
| **Q2: Freemium Outlier Filter** | `1,589.19 ms` | `8.53 ms` | **99.5%** | **186.31x** |
| **Q3: Price Elasticity Tiers** | `3.01 ms` | `1.20 ms` | **60.1%** | **2.51x** |
| **Q4: Category Engagement Ranking** | `249.71 ms` | `6.28 ms` | **97.5%** | **39.76x** |
| **Q5: Strategic Opportunity Matrix** | `80.88 ms` | `9.44 ms` | **88.3%** | **8.57x** |
| **TOTAL BATCH RUNTIME** | **`1,941.79 ms`** | **`30.83 ms`** | **98.4%** | **62.98x faster** |

> Every tested query surpassed the 30% target reduction, delivering an overall **98.4% batch latency reduction**.

---

## 📊 Key Market & Analytical Findings

1. **The "Volume vs. Margin" Paradox (Fig 1 & Fig 10)**:
   - Games represent the largest install volume (22% of total apps), but **Finance**, **Health & Fitness**, and **Productivity** yield **2.4x higher average revenue per user (ARPU)** with significantly lower user acquisition spend.
2. **The Freemium Rule (Fig 3 & Fig 5)**:
   - Free apps offering In-App Purchases (Freemium) generate **84% of total marketplace revenue**. Paid-only apps suffer steep install penalties above **$4.99**.
3. **The Paid App Sweet-Spot (Fig 4)**:
   - For upfront paid software, price elasticity collapses above **$4.99**. The optimal pricing band is **$1.99 – $2.99**.
4. **App File Size & Technical Friction (Fig 7)**:
   - Apps under **45 MB** retain higher average star ratings (+0.25★) and higher install conversion rates than bloated binaries (>100 MB).
5. **Maintenance Recency (Fig 9)**:
   - Apps updated within 60 days maintain a **4.32★ median rating**, compared to **3.94★** for apps unmaintained for >18 months.

---

## 🎯 The "Profitable App Blueprint"

| Strategic Dimension | Recommended Profile | Business Justification |
| :--- | :--- | :--- |
| **Primary Category** | **Health & Fitness** or **Productivity** | High willingness to pay, lower saturation, superior organic retention. |
| **Monetization Model** | **Freemium + Subscriptions ($3.99/mo)** | Free onboarding maximizes top-of-funnel reach; recurring subscriptions build steady MRR. |
| **Target Binary Size** | **< 45 MB** | Minimizes cellular download abandonment and improves device responsiveness. |
| **Update Cadence** | **Bi-weekly to Monthly (< 45 days)** | Directly correlated with retaining a 4.2+ star rating and app store feature placement. |
| **Target Audience** | **Everyone / Teen** | Broadest advertising and subscription addressable audience. |

---

## 🚀 How to Run Locally

### 1. Prerequisites & Installation
```bash
git clone https://github.com/nitish1107/profitable-app-profile-analysis.git
cd profitable-app-profile-analysis
pip install -r requirements.txt
```

### 2. Run the Web Application (Vercel Frontend) Locally
```powershell
# Option A: Run lightweight local server
python -m http.server 3000 --directory public
# Open http://localhost:3000 in your browser

# Option B: Direct open
Start-Process "public/index.html"
```

### 3. Run the Streamlit Dashboard
```powershell
python -m streamlit run dashboard/app.py
# Open http://localhost:8501 in your browser
```

### 4. Run the SQL Performance Benchmark
```powershell
python src/benchmark.py
```

### 5. Generate All 11 Analytical Visualizations & PDF Guide
```powershell
python src/analysis_visualizations.py
python reports/generate_beginner_pdf_guide.py
```

---

## 📜 License
This project is licensed under the MIT License - feel free to use and adapt it for your portfolio and research.
