-- ==============================================================================
-- BASELINE (UNOPTIMIZED) QUERIES
-- Characteristics:
--  - Full table scans on unindexed tables
--  - Non-sargable functions in WHERE clauses (e.g. strftime, string manipulation)
--  - Correlated subqueries causing O(N^2) quadratic row-by-row lookups
--  - Redundant repeated aggregations and self-joins
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Query 1: Category Performance & Market Saturation
-- Analyzes market share, average rating, and revenue metrics across categories
-- Flaws: Uses non-sargable strftime(), unindexed grouping, repeated subqueries
-- ------------------------------------------------------------------------------
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

-- ------------------------------------------------------------------------------
-- Query 2: High-Value Freemium Segment Identification
-- Identifies standout apps generating more than twice the category average revenue
-- Flaws: Correlated subquery in WHERE and SELECT executed for EVERY individual row
-- ------------------------------------------------------------------------------
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
  AND a.total_est_revenue > (
      SELECT 2.0 * AVG(sub2.total_est_revenue)
      FROM apps_flat sub2
      WHERE sub2.category = a.category
  )
ORDER BY a.total_est_revenue DESC;

-- ------------------------------------------------------------------------------
-- Query 3: Price Elasticity & Revenue Yield
-- Analyzes paid app pricing sweet-spots ($0.99 - $2.99 vs $3.00 - $9.99 vs $10.00+)
-- Flaws: Evaluated with multiple correlated UNION / sub-select scans without indexes
-- ------------------------------------------------------------------------------
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

-- ------------------------------------------------------------------------------
-- Query 4: Category Rank & Engagement Leaders (Correlated Rank)
-- Ranks apps by review count and rating within each category
-- Flaws: Emulates rank using correlated COUNT(*) subqueries (O(N^2) complexity)
-- ------------------------------------------------------------------------------
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
    ) AS category_review_rank
FROM apps_flat a
WHERE a.installs >= 100000
ORDER BY a.category, category_review_rank
LIMIT 100;

-- ------------------------------------------------------------------------------
-- Query 5: Strategic Opportunity Matrix (High Demand, Moderate Competition)
-- Identifies genres with high user ratings, active engagement, and strong monetization
-- Flaws: Redundant multi-table join and non-indexed text aggregations
-- ------------------------------------------------------------------------------
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
