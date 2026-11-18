"""
Database Manager & ETL Ingestion Pipeline
Loads CSV records into SQLite database with both normalized schema and flat reporting tables.
"""

import os
import sqlite3
import pandas as pd

DB_PATH = r"C:\Users\91740\.gemini\antigravity\scratch\profitable-app-profile-analysis\data\app_store_analytics.db"
CSV_PATH = r"C:\Users\91740\.gemini\antigravity\scratch\profitable-app-profile-analysis\data\apps_data.csv"
SCHEMA_PATH = r"C:\Users\91740\.gemini\antigravity\scratch\profitable-app-profile-analysis\sql\01_schema.sql"

def get_connection(db_path=DB_PATH):
    return sqlite3.connect(db_path)

def initialize_database():
    print(f"Initializing database at: {DB_PATH}")
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = get_connection()
    cursor = conn.cursor()

    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    cursor.executescript(schema_sql)
    conn.commit()
    print("Database schema successfully created.")
    conn.close()

def load_data_from_csv():
    print(f"Loading data from: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    print(f"Read {len(df):,} rows from CSV.")

    conn = get_connection()
    cursor = conn.cursor()

    # 1. Populate categories
    categories = sorted(df['category'].unique())
    for cat in categories:
        cursor.execute("INSERT OR IGNORE INTO categories (category_name) VALUES (?)", (cat,))
    conn.commit()

    # Get category ID map
    cat_map = {row[1]: row[0] for row in cursor.execute("SELECT category_id, category_name FROM categories").fetchall()}

    # 2. Populate normalized apps table
    apps_data = []
    monetization_data = []

    for _, row in df.iterrows():
        cat_id = cat_map[row['category']]
        apps_data.append((
            row['app_id'],
            row['app_name'],
            cat_id,
            row['category'],
            row['rating'],
            row['reviews'],
            row['size_mb'],
            row['installs'],
            row['type'],
            row['price'],
            row['content_rating'],
            row['genres'],
            row['last_updated'],
            row['min_android_ver']
        ))

        monetization_data.append((
            row['app_id'],
            int(row['has_in_app_purchases']),
            int(row['active_users_monthly']),
            float(row['est_ad_revenue']),
            float(row['est_iap_revenue']),
            float(row['est_direct_revenue']),
            float(row['total_est_revenue'])
        ))

    cursor.executemany("""
        INSERT INTO apps (
            app_id, app_name, category_id, category_name, rating, reviews, size_mb,
            installs, type, price, content_rating, genres, last_updated, min_android_ver
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, apps_data)

    cursor.executemany("""
        INSERT INTO monetization (
            app_id, has_in_app_purchases, active_users_monthly, est_ad_revenue,
            est_iap_revenue, est_direct_revenue, total_est_revenue
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, monetization_data)

    # 3. Populate apps_flat table
    df.to_sql('apps_flat', conn, if_exists='replace', index=False)

    conn.commit()
    print(f"Successfully loaded {len(apps_data):,} records into database tables.")
    
    # Verification query
    count_apps = cursor.execute("SELECT COUNT(*) FROM apps").fetchone()[0]
    count_flat = cursor.execute("SELECT COUNT(*) FROM apps_flat").fetchone()[0]
    print(f"Verified counts: apps table={count_apps:,}, apps_flat table={count_flat:,}")
    
    conn.close()

if __name__ == '__main__':
    initialize_database()
    load_data_from_csv()
