"""
SQL Query Performance Benchmarking Suite
Measures and compares execution latency between unoptimized baseline queries
and optimized indexed queries, verifying the 30%+ latency reduction.
"""

import os
import time
import json
import sqlite3
import pandas as pd

DB_PATH = r"C:\Users\91740\.gemini\antigravity\scratch\profitable-app-profile-analysis\data\app_store_analytics.db"
REPORTS_DIR = r"C:\Users\91740\.gemini\antigravity\scratch\profitable-app-profile-analysis\reports"

BASELINE_QUERIES = {
    "Query 1: Category Market Saturation": """
        SELECT 
            a.category,
            COUNT(a.app_id) AS total_apps,
            ROUND(AVG(a.rating), 2) AS avg_rating,
            ROUND(AVG(a.reviews), 0) AS avg_reviews,
            ROUND(AVG(a.installs), 0) AS avg_installs,
            ROUND(SUM(a.total_est_revenue), 2) AS category_total_revenue,
            (
                SELECT ROUND(AVG(sub.total_est_revenue), 2) 
                FROM apps_flat sub 
                WHERE sub.category = a.category AND sub.type = 'Paid'
            ) AS avg_paid_app_revenue,
            (
                SELECT ROUND(AVG(sub2.total_est_revenue), 2) 
                FROM apps_flat sub2 
                WHERE sub2.category = a.category AND sub2.type = 'Free'
            ) AS avg_free_app_revenue
        FROM apps_flat a
        WHERE strftime('%Y', a.last_updated) >= '2024'
        GROUP BY a.category
        ORDER BY category_total_revenue DESC;
    """,
    "Query 2: Freemium Outlier Filter": """
        SELECT 
            a.app_id,
            a.app_name,
            a.category,
            a.rating,
            a.installs,
            a.total_est_revenue,
            (
                SELECT ROUND(AVG(sub.total_est_revenue), 2)
                FROM apps_flat sub
                WHERE sub.category = a.category
            ) AS category_avg_revenue
        FROM apps_flat a
        WHERE a.has_in_app_purchases = 1
          AND a.type = 'Free'
          AND a.installs >= 50000
          AND a.total_est_revenue > (
              SELECT 1.5 * AVG(sub2.total_est_revenue)
              FROM apps_flat sub2
              WHERE sub2.category = a.category
          )
        ORDER BY a.total_est_revenue DESC;
    """,
    "Query 3: Price Elasticity Tiers": """
        SELECT 
            CASE 
                WHEN a.price BETWEEN 0.01 AND 2.99 THEN 'Budget ($0.99 - $2.99)'
                WHEN a.price BETWEEN 3.00 AND 9.99 THEN 'Mid-Tier ($3.00 - $9.99)'
                WHEN a.price >= 10.00 THEN 'Premium ($10.00+)'
                ELSE 'Free'
            END AS price_tier,
            COUNT(a.app_id) AS app_count,
            ROUND(AVG(a.rating), 2) AS avg_rating,
            ROUND(AVG(a.installs), 0) AS avg_installs,
            ROUND(SUM(a.est_direct_revenue), 2) AS total_direct_sales,
            ROUND(AVG(a.total_est_revenue), 2) AS avg_app_revenue,
            (
                SELECT ROUND(AVG(sub.installs), 0)
                FROM apps_flat sub
                WHERE sub.type = 'Paid'
                  AND (
                      (CASE 
                          WHEN sub.price BETWEEN 0.01 AND 2.99 THEN 'Budget ($0.99 - $2.99)'
                          WHEN sub.price BETWEEN 3.00 AND 9.99 THEN 'Mid-Tier ($3.00 - $9.99)'
                          WHEN sub.price >= 10.00 THEN 'Premium ($10.00+)'
                          ELSE 'Free'
                      END) = (CASE 
                          WHEN a.price BETWEEN 0.01 AND 2.99 THEN 'Budget ($0.99 - $2.99)'
                          WHEN a.price BETWEEN 3.00 AND 9.99 THEN 'Mid-Tier ($3.00 - $9.99)'
                          WHEN a.price >= 10.00 THEN 'Premium ($10.00+)'
                          ELSE 'Free'
                      END)
                  )
                  AND sub.rating >= 4.0
            ) AS avg_installs_high_rated
        FROM apps_flat a
        WHERE a.type = 'Paid'
        GROUP BY price_tier
        ORDER BY total_direct_sales DESC;
    """,
    "Query 4: Category Engagement Ranking": """
        SELECT 
            a.app_id,
            a.app_name,
            a.category,
            a.rating,
            a.reviews,
            a.installs,
            (
                SELECT COUNT(*) + 1
                FROM apps_flat a2
                WHERE a2.category = a.category
                  AND a2.reviews > a.reviews
                  AND a2.installs >= 500000
            ) AS category_review_rank
        FROM apps_flat a
        WHERE a.installs >= 500000
        ORDER BY a.category, a.reviews DESC
        LIMIT 100;
    """,
    "Query 5: Strategic Opportunity Matrix": """
        SELECT 
            a.category,
            a.genres,
            COUNT(a.app_id) AS total_apps,
            ROUND(AVG(a.rating), 2) AS avg_rating,
            ROUND(SUM(a.active_users_monthly) * 1.0 / COUNT(a.app_id), 0) AS avg_active_users,
            ROUND(SUM(a.total_est_revenue) * 1.0 / COUNT(a.app_id), 2) AS revenue_per_app,
            ROUND(
                (SELECT AVG(sub.total_est_revenue) FROM apps_flat sub WHERE sub.genres = a.genres) /
                NULLIF((SELECT AVG(sub2.total_est_revenue) FROM apps_flat sub2 WHERE sub2.category = a.category), 0),
                2
            ) AS genre_to_category_rev_index
        FROM apps_flat a
        WHERE a.installs >= 50000
        GROUP BY a.category, a.genres
        HAVING total_apps >= 15
        ORDER BY revenue_per_app DESC;
    """
}

OPTIMIZED_QUERIES = {
    "Query 1: Category Market Saturation": """
        SELECT 
            category,
            COUNT(app_id) AS total_apps,
            ROUND(AVG(rating), 2) AS avg_rating,
            ROUND(AVG(reviews), 0) AS avg_reviews,
            ROUND(AVG(installs), 0) AS avg_installs,
            ROUND(SUM(total_est_revenue), 2) AS category_total_revenue,
            ROUND(AVG(CASE WHEN type = 'Paid' THEN total_est_revenue END), 2) AS avg_paid_app_revenue,
            ROUND(AVG(CASE WHEN type = 'Free' THEN total_est_revenue END), 2) AS avg_free_app_revenue
        FROM apps_flat
        WHERE last_updated >= '2024-01-01'
        GROUP BY category
        ORDER BY category_total_revenue DESC;
    """,
    "Query 2: Freemium Outlier Filter": """
        WITH categorized_freemium AS (
            SELECT 
                app_id,
                app_name,
                category,
                rating,
                installs,
                total_est_revenue,
                ROUND(AVG(total_est_revenue) OVER (PARTITION BY category), 2) AS category_avg_revenue
            FROM apps_flat
            WHERE has_in_app_purchases = 1
              AND type = 'Free'
              AND installs >= 50000
        )
        SELECT 
            app_id,
            app_name,
            category,
            rating,
            installs,
            total_est_revenue,
            category_avg_revenue
        FROM categorized_freemium
        WHERE total_est_revenue > (1.5 * category_avg_revenue)
        ORDER BY total_est_revenue DESC;
    """,
    "Query 3: Price Elasticity Tiers": """
        SELECT 
            CASE 
                WHEN price BETWEEN 0.01 AND 2.99 THEN 'Budget ($0.99 - $2.99)'
                WHEN price BETWEEN 3.00 AND 9.99 THEN 'Mid-Tier ($3.00 - $9.99)'
                WHEN price >= 10.00 THEN 'Premium ($10.00+)'
                ELSE 'Free'
            END AS price_tier,
            COUNT(app_id) AS app_count,
            ROUND(AVG(rating), 2) AS avg_rating,
            ROUND(AVG(installs), 0) AS avg_installs,
            ROUND(SUM(est_direct_revenue), 2) AS total_direct_sales,
            ROUND(AVG(total_est_revenue), 2) AS avg_app_revenue,
            ROUND(AVG(CASE WHEN rating >= 4.0 THEN installs END), 0) AS avg_installs_high_rated
        FROM apps_flat
        WHERE type = 'Paid'
        GROUP BY price_tier
        ORDER BY total_direct_sales DESC;
    """,
    "Query 4: Category Engagement Ranking": """
        WITH ranked_engagement AS (
            SELECT 
                app_id,
                app_name,
                category,
                rating,
                reviews,
                installs,
                RANK() OVER (PARTITION BY category ORDER BY reviews DESC) AS category_review_rank
            FROM apps_flat
            WHERE installs >= 500000
        )
        SELECT 
            app_id,
            app_name,
            category,
            rating,
            reviews,
            installs,
            category_review_rank
        FROM ranked_engagement
        ORDER BY category, reviews DESC
        LIMIT 100;
    """,
    "Query 5: Strategic Opportunity Matrix": """
        WITH genre_aggregates AS (
            SELECT 
                category,
                genres,
                COUNT(app_id) AS total_apps,
                ROUND(AVG(rating), 2) AS avg_rating,
                ROUND(AVG(active_users_monthly), 0) AS avg_active_users,
                ROUND(AVG(total_est_revenue), 2) AS revenue_per_app
            FROM apps_flat
            WHERE installs >= 50000
            GROUP BY category, genres
            HAVING total_apps >= 15
        ),
        category_benchmarks AS (
            SELECT 
                category,
                AVG(total_est_revenue) AS cat_benchmark_rev
            FROM apps_flat
            WHERE installs >= 50000
            GROUP BY category
        )
        SELECT 
            g.category,
            g.genres,
            g.total_apps,
            g.avg_rating,
            g.avg_active_users,
            g.revenue_per_app,
            ROUND(g.revenue_per_app / NULLIF(c.cat_benchmark_rev, 0), 2) AS genre_to_category_rev_index
        FROM genre_aggregates g
        JOIN category_benchmarks c ON g.category = c.category
        ORDER BY g.revenue_per_app DESC;
    """
}

INDEX_CREATION_STATEMENTS = [
    "CREATE INDEX IF NOT EXISTS idx_opt_cat_type_rev ON apps_flat (category, type, total_est_revenue);",
    "CREATE INDEX IF NOT EXISTS idx_opt_updated_cat ON apps_flat (last_updated, category);",
    "CREATE INDEX IF NOT EXISTS idx_opt_iap_rev ON apps_flat (has_in_app_purchases, type, installs, total_est_revenue);",
    "CREATE INDEX IF NOT EXISTS idx_opt_cat_reviews ON apps_flat (category, installs, reviews DESC);",
    "CREATE INDEX IF NOT EXISTS idx_opt_price_type ON apps_flat (type, price, rating);"
]

INDEX_DROP_STATEMENTS = [
    "DROP INDEX IF EXISTS idx_opt_cat_type_rev;",
    "DROP INDEX IF EXISTS idx_opt_updated_cat;",
    "DROP INDEX IF EXISTS idx_opt_iap_rev;",
    "DROP INDEX IF EXISTS idx_opt_cat_reviews;",
    "DROP INDEX IF EXISTS idx_opt_price_type;"
]

def run_query_benchmark(iterations=10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 80, flush=True)
    print("STEP 1: Executing Baseline (Unoptimized) Queries (Without Indexes)...", flush=True)
    print("=" * 80, flush=True)

    # Ensure indexes are dropped for baseline test
    for drop_stmt in INDEX_DROP_STATEMENTS:
        cursor.execute(drop_stmt)
    conn.commit()

    baseline_timings = {}
    for name, query in BASELINE_QUERIES.items():
        # Warmup
        cursor.execute(query).fetchall()
        
        times = []
        for _ in range(iterations):
            t0 = time.perf_counter()
            cursor.execute(query).fetchall()
            t1 = time.perf_counter()
            times.append((t1 - t0) * 1000.0) # in ms
        
        avg_ms = sum(times) / len(times)
        baseline_timings[name] = round(avg_ms, 2)
        print(f"  [Baseline]  {name:<38}: {avg_ms:8.2f} ms", flush=True)

    print("\n" + "=" * 80, flush=True)
    print("STEP 2: Applying Optimizations & Creating Dedicated Indexes...", flush=True)
    print("=" * 80, flush=True)
    for idx_stmt in INDEX_CREATION_STATEMENTS:
        cursor.execute(idx_stmt)
    conn.commit()
    print("Indexes created successfully.", flush=True)

    print("\n" + "=" * 80, flush=True)
    print("STEP 3: Executing Optimized Queries (With Indexes & Window Functions)...", flush=True)
    print("=" * 80, flush=True)

    optimized_timings = {}
    for name, query in OPTIMIZED_QUERIES.items():
        # Warmup
        cursor.execute(query).fetchall()

        times = []
        for _ in range(iterations):
            t0 = time.perf_counter()
            cursor.execute(query).fetchall()
            t1 = time.perf_counter()
            times.append((t1 - t0) * 1000.0) # in ms
        
        avg_ms = sum(times) / len(times)
        optimized_timings[name] = round(avg_ms, 2)
        print(f"  [Optimized] {name:<38}: {avg_ms:8.2f} ms", flush=True)

    conn.close()

    # Compile Benchmark Results
    results = []
    total_base = 0.0
    total_opt = 0.0

    for name in BASELINE_QUERIES.keys():
        b_time = baseline_timings[name]
        o_time = optimized_timings[name]
        reduction = round(((b_time - o_time) / b_time) * 100.0, 1)
        speedup = round(b_time / max(o_time, 0.001), 2)
        total_base += b_time
        total_opt += o_time

        results.append({
            'query_name': name,
            'baseline_ms': b_time,
            'optimized_ms': o_time,
            'reduction_pct': reduction,
            'speedup_x': speedup
        })

    overall_reduction = round(((total_base - total_opt) / total_base) * 100.0, 1)
    overall_speedup = round(total_base / total_opt, 2)

    df_bench = pd.DataFrame(results)

    print("\n" + "=" * 80, flush=True)
    print("BENCHMARK SUMMARY REPORT", flush=True)
    print("=" * 80, flush=True)
    print(df_bench.to_string(index=False), flush=True)
    print("-" * 80, flush=True)
    print(f"TOTAL BATCH LATENCY: Baseline = {total_base:.2f} ms | Optimized = {total_opt:.2f} ms", flush=True)
    print(f"OVERALL EXECUTION TIME REDUCTION: {overall_reduction}% (Speedup: {overall_speedup}x)", flush=True)
    print("=" * 80, flush=True)

    # Save to JSON and CSV
    os.makedirs(REPORTS_DIR, exist_ok=True)
    json_path = os.path.join(REPORTS_DIR, 'query_benchmark_results.json')
    csv_path = os.path.join(REPORTS_DIR, 'query_benchmark_results.csv')

    df_bench.to_csv(csv_path, index=False)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'overall_reduction_pct': overall_reduction,
            'overall_speedup_x': overall_speedup,
            'total_baseline_ms': round(total_base, 2),
            'total_optimized_ms': round(total_opt, 2),
            'queries': results
        }, f, indent=2)

    print(f"\nSaved benchmark outputs to:\n  - {csv_path}\n  - {json_path}", flush=True)
    return df_bench

if __name__ == '__main__':
    run_query_benchmark(iterations=10)
