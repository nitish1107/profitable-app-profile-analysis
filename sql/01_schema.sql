-- ==============================================================================
-- Schema Definition: Mobile App Store Analytics Database
-- Supports both baseline (unindexed) and optimized (indexed) query workloads
-- ==============================================================================

-- 1. Dim Categories
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- 2. Fact Apps
CREATE TABLE IF NOT EXISTS apps (
    app_id TEXT PRIMARY KEY,
    app_name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    category_name TEXT NOT NULL,
    rating REAL,
    reviews INTEGER,
    size_mb REAL,
    installs INTEGER,
    type TEXT CHECK (type IN ('Free', 'Paid')),
    price REAL DEFAULT 0.00,
    content_rating TEXT,
    genres TEXT,
    last_updated DATE,
    min_android_ver TEXT,
    FOREIGN KEY (category_id) REFERENCES categories (category_id)
);

-- 3. Fact Monetization
CREATE TABLE IF NOT EXISTS monetization (
    app_id TEXT PRIMARY KEY,
    has_in_app_purchases INTEGER DEFAULT 0,
    active_users_monthly INTEGER DEFAULT 0,
    est_ad_revenue REAL DEFAULT 0.00,
    est_iap_revenue REAL DEFAULT 0.00,
    est_direct_revenue REAL DEFAULT 0.00,
    total_est_revenue REAL DEFAULT 0.00,
    FOREIGN KEY (app_id) REFERENCES apps (app_id)
);

-- Denormalized Flat Table for Direct Fast Analytics & Baseline Comparison
CREATE TABLE IF NOT EXISTS apps_flat (
    app_id TEXT PRIMARY KEY,
    app_name TEXT NOT NULL,
    category TEXT NOT NULL,
    rating REAL,
    reviews INTEGER,
    size_mb REAL,
    installs INTEGER,
    type TEXT,
    price REAL,
    content_rating TEXT,
    genres TEXT,
    has_in_app_purchases INTEGER,
    active_users_monthly INTEGER,
    est_ad_revenue REAL,
    est_iap_revenue REAL,
    est_direct_revenue REAL,
    total_est_revenue REAL,
    last_updated DATE,
    min_android_ver TEXT
);

-- View: Consolidated App Profile Summary
CREATE VIEW IF NOT EXISTS v_app_full_summary AS
SELECT 
    a.app_id,
    a.app_name,
    a.category_name,
    a.rating,
    a.reviews,
    a.size_mb,
    a.installs,
    a.type,
    a.price,
    a.content_rating,
    a.genres,
    m.has_in_app_purchases,
    m.active_users_monthly,
    m.est_ad_revenue,
    m.est_iap_revenue,
    m.est_direct_revenue,
    m.total_est_revenue,
    a.last_updated,
    a.min_android_ver
FROM apps a
LEFT JOIN monetization m ON a.app_id = m.app_id;
