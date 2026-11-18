"""
Analytical Visualizations Suite
Generates 11 publication-quality charts uncovering user engagement, pricing,
and revenue patterns across mobile app segments.
"""

import os
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

DB_PATH = r"C:\Users\91740\.gemini\antigravity\scratch\profitable-app-profile-analysis\data\app_store_analytics.db"
OUTPUT_DIR = r"C:\Users\91740\.gemini\antigravity\scratch\profitable-app-profile-analysis\reports\figures"

# Set publication style
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['figure.autolayout'] = True
plt.rcParams['axes.edgecolor'] = '#CCCCCC'
plt.rcParams['axes.linewidth'] = 0.8

PRIMARY_PALETTE = sns.color_palette("mako", 12)
ACCENT_COLOR = "#2b5c8f"
HIGHLIGHT_COLOR = "#e76f51"

def load_data():
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT 
            app_id, app_name, category, rating, reviews, size_mb, installs,
            type, price, content_rating, genres, has_in_app_purchases,
            active_users_monthly, est_ad_revenue, est_iap_revenue,
            est_direct_revenue, total_est_revenue, last_updated
        FROM apps_flat
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    df['last_updated'] = pd.to_datetime(df['last_updated'])
    df['review_ratio_pct'] = (df['reviews'] / df['installs']) * 100.0
    return df

def generate_all_visualizations():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = load_data()
    print(f"Loaded {len(df):,} records for visualization generation.")

    # --------------------------------------------------------------------------
    # Figure 1: Market Saturation & App Share by Category
    # --------------------------------------------------------------------------
    print("Generating Fig 1: Market Share by Category...")
    plt.figure(figsize=(10, 6), dpi=300)
    cat_counts = df['category'].value_counts()
    ax = sns.barplot(x=cat_counts.values, y=cat_counts.index, palette="Blues_r")
    for i, v in enumerate(cat_counts.values):
        pct = (v / len(df)) * 100
        ax.text(v + 15, i, f"{v:,} ({pct:.1f}%)", va='center', fontsize=9, fontweight='semibold')
    plt.title("Market Saturation: Mobile App Count by Category", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Number of Apps", fontsize=10)
    plt.ylabel("Category", fontsize=10)
    plt.xlim(0, max(cat_counts.values) * 1.18)
    plt.savefig(os.path.join(OUTPUT_DIR, "01_market_share_by_category.png"))
    plt.close()

    # --------------------------------------------------------------------------
    # Figure 2: User Rating Distribution by Category
    # --------------------------------------------------------------------------
    print("Generating Fig 2: User Rating Distribution...")
    plt.figure(figsize=(11, 6), dpi=300)
    order = df.groupby('category')['rating'].median().sort_values(ascending=False).index
    sns.boxplot(data=df, x='rating', y='category', order=order, palette="crest", linewidth=1.1, fliersize=2)
    plt.axvline(x=4.0, color='red', linestyle='--', alpha=0.7, label='Benchmark: 4.0 Stars')
    plt.title("User Satisfaction: Rating Distribution Across App Categories", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Average User Rating (1.0 - 5.0)", fontsize=10)
    plt.ylabel("Category", fontsize=10)
    plt.legend(loc='lower left')
    plt.savefig(os.path.join(OUTPUT_DIR, "02_user_rating_distribution.png"))
    plt.close()

    # --------------------------------------------------------------------------
    # Figure 3: Free vs Paid Monetization Split
    # --------------------------------------------------------------------------
    print("Generating Fig 3: Free vs Paid Monetization Split...")
    plt.figure(figsize=(11, 6), dpi=300)
    type_split = df.groupby(['category', 'type']).size().unstack(fill_value=0)
    type_pct = type_split.div(type_split.sum(axis=1), axis=0) * 100
    type_pct = type_pct.sort_values(by='Paid', ascending=False)
    
    ax = type_pct.plot(kind='barh', stacked=True, color=['#457b9d', '#e63946'], figsize=(11, 6))
    plt.title("Monetization Model Distribution: Free vs Paid Apps (%)", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Percentage of Apps (%)", fontsize=10)
    plt.ylabel("Category", fontsize=10)
    plt.legend(['Free', 'Paid'], loc='lower right')
    plt.xlim(0, 100)
    plt.savefig(os.path.join(OUTPUT_DIR, "03_free_vs_paid_monetization_split.png"))
    plt.close()

    # --------------------------------------------------------------------------
    # Figure 4: Paid App Price Point Sweet Spot & Elasticity
    # --------------------------------------------------------------------------
    print("Generating Fig 4: Price Point Sweet Spot...")
    paid_apps = df[df['type'] == 'Paid'].copy()
    paid_apps['price_bin'] = pd.cut(
        paid_apps['price'],
        bins=[0, 1.00, 2.00, 3.00, 5.00, 10.00, 35.00],
        labels=['$0.99', '$1.49 - $1.99', '$2.99', '$3.99 - $4.99', '$5.99 - $9.99', '$10.00+']
    )
    price_analysis = paid_apps.groupby('price_bin', observed=False).agg(
        app_count=('app_id', 'count'),
        avg_installs=('installs', 'mean'),
        avg_revenue=('est_direct_revenue', 'mean')
    ).reset_index()

    fig, ax1 = plt.subplots(figsize=(10, 6), dpi=300)
    ax2 = ax1.twinx()
    sns.barplot(data=price_analysis, x='price_bin', y='avg_installs', ax=ax1, color='#a8dadc', alpha=0.85)
    sns.lineplot(data=price_analysis, x='price_bin', y='avg_revenue', ax=ax2, color='#e63946', marker='o', linewidth=2.5)
    ax1.set_ylabel("Average Installs", color='#1d3557', fontsize=10)
    ax2.set_ylabel("Average Direct Revenue ($)", color='#e63946', fontsize=10)
    ax1.set_xlabel("Price Tier", fontsize=10)
    plt.title("Price Elasticity: Installs vs Direct Revenue per Paid App", fontsize=13, fontweight='bold', pad=12)
    plt.savefig(os.path.join(OUTPUT_DIR, "04_price_point_sweet_spot.png"))
    plt.close()

    # --------------------------------------------------------------------------
    # Figure 5: Revenue Stream Breakdown by Category (Ad vs IAP vs Direct)
    # --------------------------------------------------------------------------
    print("Generating Fig 5: Revenue Stream Breakdown...")
    plt.figure(figsize=(11, 6), dpi=300)
    rev_streams = df.groupby('category')[['est_ad_revenue', 'est_iap_revenue', 'est_direct_revenue']].sum() / 1e6
    rev_streams['total'] = rev_streams.sum(axis=1)
    rev_streams = rev_streams.sort_values(by='total', ascending=True).drop(columns=['total'])
    
    ax = rev_streams.plot(kind='barh', stacked=True, color=['#2a9d8f', '#e76f51', '#264653'], figsize=(11, 6))
    plt.title("Total Estimated Market Revenue Stream Breakdown ($ Millions)", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Total Revenue ($ Millions)", fontsize=10)
    plt.ylabel("Category", fontsize=10)
    plt.legend(['Ad Revenue', 'In-App Purchases (Freemium)', 'Paid App Downloads'], loc='lower right')
    plt.savefig(os.path.join(OUTPUT_DIR, "05_revenue_breakdown_by_category.png"))
    plt.close()

    # --------------------------------------------------------------------------
    # Figure 6: User Engagement - Review-to-Install Ratio
    # --------------------------------------------------------------------------
    print("Generating Fig 6: User Engagement Ratio...")
    plt.figure(figsize=(10, 6), dpi=300)
    engagement = df.groupby('category')['review_ratio_pct'].mean().sort_values(ascending=False)
    ax = sns.barplot(x=engagement.values, y=engagement.index, palette="viridis")
    for i, v in enumerate(engagement.values):
        ax.text(v + 0.05, i, f"{v:.2f}%", va='center', fontsize=9, fontweight='semibold')
    plt.title("User Engagement Index: Average Review-to-Install Ratio (%)", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Average Review / Install Ratio (%)", fontsize=10)
    plt.ylabel("Category", fontsize=10)
    plt.xlim(0, max(engagement.values) * 1.15)
    plt.savefig(os.path.join(OUTPUT_DIR, "06_user_engagement_review_ratio.png"))
    plt.close()

    # --------------------------------------------------------------------------
    # Figure 7: App Size vs Rating & Installs
    # --------------------------------------------------------------------------
    print("Generating Fig 7: App Size vs Rating...")
    plt.figure(figsize=(10, 6), dpi=300)
    sample_df = df.sample(n=min(1200, len(df)), random_state=42)
    sns.scatterplot(
        data=sample_df,
        x='size_mb',
        y='rating',
        size='installs',
        hue='type',
        sizes=(20, 250),
        alpha=0.6,
        palette={'Free': '#1d3557', 'Paid': '#e63946'}
    )
    plt.axhline(y=4.0, color='gray', linestyle=':', alpha=0.6)
    plt.title("Impact of App File Size (MB) on User Rating & Install Scale", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("App Size (MB)", fontsize=10)
    plt.ylabel("User Rating (1.0 - 5.0)", fontsize=10)
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.savefig(os.path.join(OUTPUT_DIR, "07_app_size_vs_rating_and_installs.png"))
    plt.close()

    # --------------------------------------------------------------------------
    # Figure 8: Monetization across Content Rating Audiences
    # --------------------------------------------------------------------------
    print("Generating Fig 8: Content Rating Performance...")
    plt.figure(figsize=(9, 5), dpi=300)
    cr_summary = df.groupby('content_rating').agg(
        avg_revenue=('total_est_revenue', 'mean'),
        app_count=('app_id', 'count')
    ).reset_index().sort_values(by='avg_revenue', ascending=False)
    ax = sns.barplot(data=cr_summary, x='content_rating', y='avg_revenue', palette="rocket")
    for i, row in cr_summary.iterrows():
        idx = cr_summary.index.get_loc(i)
        ax.text(idx, row['avg_revenue'] + 500, f"${row['avg_revenue']:,.0f}", ha='center', fontsize=9, fontweight='bold')
    plt.title("Average Annual Revenue per App by Content Rating Demographic", fontsize=13, fontweight='bold', pad=12)
    plt.ylabel("Average Total Revenue ($)", fontsize=10)
    plt.xlabel("Target Audience Content Rating", fontsize=10)
    plt.savefig(os.path.join(OUTPUT_DIR, "08_content_rating_monetization.png"))
    plt.close()

    # --------------------------------------------------------------------------
    # Figure 9: Update Recency vs User Satisfaction
    # --------------------------------------------------------------------------
    print("Generating Fig 9: Update Recency Impact...")
    plt.figure(figsize=(10, 5), dpi=300)
    now_date = pd.to_datetime('2026-01-15')
    df['days_since_update'] = (now_date - df['last_updated']).dt.days
    df['update_cohort'] = pd.cut(
        df['days_since_update'],
        bins=[-1, 60, 180, 365, 730, 1500],
        labels=['< 2 Months', '2 - 6 Months', '6 - 12 Months', '1 - 2 Years', '> 2 Years']
    )
    cohort_rating = df.groupby('update_cohort', observed=False)['rating'].mean().reset_index()
    sns.lineplot(data=cohort_rating, x='update_cohort', y='rating', marker='s', color='#2a9d8f', linewidth=2.5)
    plt.title("User Satisfaction Decay: Star Rating vs Maintenance Recency", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Time Since Last App Update", fontsize=10)
    plt.ylabel("Average User Rating", fontsize=10)
    plt.ylim(3.8, 4.4)
    plt.savefig(os.path.join(OUTPUT_DIR, "09_update_recency_impact.png"))
    plt.close()

    # --------------------------------------------------------------------------
    # Figure 10: Profitable Profile Strategic Quadrant (Demand vs Monetization)
    # --------------------------------------------------------------------------
    print("Generating Fig 10: Strategic Opportunity Quadrant...")
    plt.figure(figsize=(11, 7), dpi=300)
    cat_matrix = df.groupby('category').agg(
        avg_installs=('installs', 'mean'),
        avg_rev=('total_est_revenue', 'mean'),
        app_count=('app_id', 'count')
    ).reset_index()

    med_installs = cat_matrix['avg_installs'].median()
    med_rev = cat_matrix['avg_rev'].median()

    sns.scatterplot(
        data=cat_matrix,
        x='avg_installs',
        y='avg_rev',
        size='app_count',
        sizes=(100, 600),
        color='#3a86ff',
        alpha=0.85
    )

    # Label each point
    for _, row in cat_matrix.iterrows():
        plt.text(
            row['avg_installs'] * 1.03,
            row['avg_rev'] * 1.02,
            row['category'],
            fontsize=8.5,
            fontweight='bold',
            color='#14213d'
        )

    plt.axvline(x=med_installs, color='gray', linestyle='--', alpha=0.5)
    plt.axhline(y=med_rev, color='gray', linestyle='--', alpha=0.5)

    # Quadrant annotations
    plt.text(cat_matrix['avg_installs'].max() * 0.75, cat_matrix['avg_rev'].max() * 0.92,
             "★ HIGH DEMAND / HIGH REVENUE\n(Golden Profile: Games, Social)", fontsize=9, color='darkgreen', fontweight='bold')
    plt.text(cat_matrix['avg_installs'].min() * 1.1, cat_matrix['avg_rev'].max() * 0.92,
             "◆ NICHE HIGH-ARPU\n(Finance, Health, Business)", fontsize=9, color='purple', fontweight='bold')

    plt.title("Category Opportunity Matrix: Average Installs (Scale) vs Revenue (Monetization)", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Average Installs per App", fontsize=10)
    plt.ylabel("Average Total Revenue per App ($)", fontsize=10)
    plt.savefig(os.path.join(OUTPUT_DIR, "10_profitable_profile_quadrant.png"))
    plt.close()

    # --------------------------------------------------------------------------
    # Figure 11: Correlation Heatmap
    # --------------------------------------------------------------------------
    print("Generating Fig 11: Correlation Heatmap...")
    plt.figure(figsize=(9, 7), dpi=300)
    num_cols = ['rating', 'reviews', 'size_mb', 'installs', 'price', 'active_users_monthly', 'total_est_revenue']
    corr = df[num_cols].corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap='Blues', vmin=-0.1, vmax=1.0, cbar=True, square=True)
    plt.title("Correlation Matrix of Quantitative App Store Metrics", fontsize=13, fontweight='bold', pad=12)
    plt.savefig(os.path.join(OUTPUT_DIR, "11_correlation_matrix.png"))
    plt.close()

    print(f"\nAll 11 analytical figures successfully generated and saved to:\n{OUTPUT_DIR}")

if __name__ == '__main__':
    generate_all_visualizations()
