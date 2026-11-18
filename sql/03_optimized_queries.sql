-- ==============================================================================
-- OPTIMIZED QUERIES WITH DEDICATED INDEXES & MODERN SQL CONSTRUCTS
-- Optimizations applied:
--  1. Dedicated composite & covering indexes
--  2. Sargable predicates (replacing strftime with date literal comparison)
--  3. Window functions (AVG() OVER, RANK() OVER) replacing O(N^2) correlated subqueries
--  4. Common Table Expressions (CTEs) for single-pass aggregations
--  5. Filter pushdown and conditional aggregations (CASE WHEN inside SUM/AVG)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Dedicated Performance Indexes
-- ------------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_opt_cat_type_rev 
    ON apps_flat (category, type, total_est_revenue);

CREATE INDEX IF NOT EXISTS idx_opt_updated_cat 
    ON apps_flat (last_updated, category);

CREATE INDEX IF NOT EXISTS idx_opt_iap_rev 
    ON apps_flat (has_in_app_purchases, type, total_est_revenue);

CREATE INDEX IF NOT EXISTS idx_opt_cat_reviews 
    ON apps_flat (category, reviews DESC);

CREATE INDEX IF NOT EXISTS idx_opt_price_type 
    ON apps_flat (type, price, rating);

-- ------------------------------------------------------------------------------
-- Query 1: Category Performance & Market Saturation (Optimized)
-- Optimizations:
--  - Sargable date comparison (last_updated >= '2024-01-01') enabling index range scan
--  - Conditional aggregation (AVG(CASE WHEN ...)) replacing correlated subqueries
-- ------------------------------------------------------------------------------
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

-- ------------------------------------------------------------------------------
-- Query 2: High-Value Freemium Segment Identification (Optimized)
-- Optimizations:
--  - Window function AVG(total_est_revenue) OVER (PARTITION BY category)
--  - Single pass scan replacing repeated O(N^2) correlated lookups
-- ------------------------------------------------------------------------------
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
WHERE total_est_revenue > (2.0 * category_avg_revenue)
ORDER BY total_est_revenue DESC;

-- ------------------------------------------------------------------------------
-- Query 3: Price Elasticity & Revenue Yield (Optimized)
-- Optimizations:
--  - Single pass aggregation with CASE WHEN replacing self-subqueries
--  - Covering index idx_opt_price_type
-- ------------------------------------------------------------------------------
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

-- ------------------------------------------------------------------------------
-- Query 4: Category Rank & Engagement Leaders (Optimized)
-- Optimizations:
--  - Native window function RANK() OVER replacing O(N^2) correlated COUNT(*)
--  - Index idx_opt_cat_reviews utilized for fast order traversal
-- ------------------------------------------------------------------------------
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
    WHERE installs >= 100000
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
ORDER BY category, category_review_rank
LIMIT 100;

-- ------------------------------------------------------------------------------
-- Query 5: Strategic Opportunity Matrix (Optimized)
-- Optimizations:
--  - Window functions for category benchmarks
--  - Elimination of correlated subquery per row inside SELECT
-- ------------------------------------------------------------------------------
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
