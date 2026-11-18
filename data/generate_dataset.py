"""
Dataset Generator for Profitable App Profile Analysis
Generates 6,500+ realistic mobile app store records with detailed metadata,
user engagement metrics, pricing, and revenue estimates.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_mobile_app_dataset(num_records=6500, random_seed=42):
    random.seed(random_seed)
    np.random.seed(random_seed)

    categories_config = {
        'GAME': {
            'weight': 0.22,
            'genres': ['Action', 'Arcade', 'Puzzle', 'Strategy', 'Adventure', 'Simulation', 'Casual', 'Role Playing'],
            'avg_rating': 4.25,
            'rating_std': 0.35,
            'size_range': (25.0, 320.0),
            'free_prob': 0.88,
            'iap_prob': 0.82,
            'price_choices': [0.99, 1.99, 2.99, 4.99, 9.99],
            'price_weights': [0.45, 0.25, 0.15, 0.10, 0.05],
            'ad_rpm': 4.50, # Revenue per 1k active users
            'iap_rev_mult': 2.8,
            'prefixes': ['Clash of', 'Legend of', 'Super', 'Epic', 'Pixel', 'Shadow', 'Dragon', 'Kingdom', 'Hero', 'Idle'],
            'suffixes': ['Warriors', 'Legends', 'Quest', 'Battle', 'Run', 'Craft', 'Master', 'Arena', 'Chronicles', 'Empire']
        },
        'PRODUCTIVITY': {
            'weight': 0.10,
            'genres': ['Task Management', 'Notes', 'Calendar', 'Office & PDF', 'Automation', 'Cloud Storage'],
            'avg_rating': 4.20,
            'rating_std': 0.30,
            'size_range': (12.0, 75.0),
            'free_prob': 0.85,
            'iap_prob': 0.65,
            'price_choices': [1.99, 2.99, 4.99, 7.99, 14.99],
            'price_weights': [0.30, 0.30, 0.25, 0.10, 0.05],
            'ad_rpm': 1.80,
            'iap_rev_mult': 3.5,
            'prefixes': ['Smart', 'Focus', 'Quick', 'Organize', 'Task', 'Pro', 'Flow', 'Clean', 'Sync', 'Swift'],
            'suffixes': ['Planner', 'Notes', 'WorkSpace', 'Assistant', 'Plus', 'Tracker', 'Hub', 'Desk', 'Suite', 'Manager']
        },
        'HEALTH_AND_FITNESS': {
            'weight': 0.09,
            'genres': ['Workout & Gym', 'Yoga & Meditation', 'Nutrition & Diet', 'Sleep Tracker', 'Running'],
            'avg_rating': 4.35,
            'rating_std': 0.25,
            'size_range': (18.0, 95.0),
            'free_prob': 0.87,
            'iap_prob': 0.78,
            'price_choices': [2.99, 4.99, 6.99, 9.99, 19.99],
            'price_weights': [0.35, 0.35, 0.15, 0.10, 0.05],
            'ad_rpm': 3.20,
            'iap_rev_mult': 4.2,
            'prefixes': ['Fit', 'Daily', 'Zen', 'Pulse', 'Vital', 'Cardio', 'Pure', 'Iron', 'Active', 'Calm'],
            'suffixes': ['Coach', 'Log', 'Companion', 'Guide', 'Zone', 'Health', 'Burn', 'Habit', 'Routine', 'Mind']
        },
        'FINANCE': {
            'weight': 0.08,
            'genres': ['Budget & Expense', 'Crypto & Stocks', 'Banking', 'Invoicing', 'Tax & Loans'],
            'avg_rating': 4.15,
            'rating_std': 0.40,
            'size_range': (15.0, 80.0),
            'free_prob': 0.94,
            'iap_prob': 0.60,
            'price_choices': [1.99, 3.99, 5.99, 9.99, 24.99],
            'price_weights': [0.40, 0.30, 0.15, 0.10, 0.05],
            'ad_rpm': 5.80, # High fintech RPM
            'iap_rev_mult': 5.0,
            'prefixes': ['Coin', 'Wealth', 'Budget', 'Money', 'Pocket', 'Capital', 'Cash', 'Smart', 'Ledger', 'Spend'],
            'suffixes': ['Tracker', 'Flow', 'Wallet', 'Pro', 'Vault', 'Manager', 'Advisor', 'Direct', 'Guard', 'Control']
        },
        'EDUCATION': {
            'weight': 0.09,
            'genres': ['Language Learning', 'Kids Learning', 'Coding', 'Math & Science', 'Exam Prep'],
            'avg_rating': 4.30,
            'rating_std': 0.30,
            'size_range': (20.0, 140.0),
            'free_prob': 0.82,
            'iap_prob': 0.70,
            'price_choices': [1.99, 2.99, 4.99, 6.99, 12.99],
            'price_weights': [0.35, 0.30, 0.20, 0.10, 0.05],
            'ad_rpm': 2.10,
            'iap_rev_mult': 3.8,
            'prefixes': ['Learn', 'Edu', 'Kids', 'Brain', 'Quiz', 'Smart', 'Tutor', 'Academy', 'Master', 'Speak'],
            'suffixes': ['Hub', 'Flashcards', 'Quest', 'Easy', 'Junior', 'Explorer', 'Skills', 'Prep', 'Camp', 'Studio']
        },
        'ENTERTAINMENT': {
            'weight': 0.08,
            'genres': ['Streaming', 'Comedy', 'Music Player', 'Video Editor', 'Comics'],
            'avg_rating': 4.10,
            'rating_std': 0.45,
            'size_range': (25.0, 120.0),
            'free_prob': 0.93,
            'iap_prob': 0.75,
            'price_choices': [0.99, 1.99, 2.99, 4.99],
            'price_weights': [0.50, 0.30, 0.15, 0.05],
            'ad_rpm': 3.50,
            'iap_rev_mult': 3.2,
            'prefixes': ['Binge', 'Stream', 'Cast', 'Tune', 'Show', 'Chill', 'Flicks', 'Pop', 'Vibe', 'Cinema'],
            'suffixes': ['Box', 'Play', 'Now', 'TV', 'Zone', 'Wave', 'Station', 'Room', 'Flix', 'Tube']
        },
        'PHOTOGRAPHY': {
            'weight': 0.07,
            'genres': ['Photo Editor', 'Filters & Effects', 'Camera & Selfie', 'Collage Maker', 'Video FX'],
            'avg_rating': 4.18,
            'rating_std': 0.35,
            'size_range': (20.0, 110.0),
            'free_prob': 0.86,
            'iap_prob': 0.80,
            'price_choices': [1.49, 2.99, 3.99, 4.99, 9.99],
            'price_weights': [0.35, 0.35, 0.15, 0.10, 0.05],
            'ad_rpm': 2.90,
            'iap_rev_mult': 3.6,
            'prefixes': ['Retro', 'Snap', 'Lens', 'Pixel', 'Color', 'Glam', 'Lumina', 'Chroma', 'Filter', 'Art'],
            'suffixes': ['Cam', 'Studio', 'Editor', 'Filter', 'Lab', 'Shot', 'FX', 'Frames', 'Story', 'Magic']
        },
        'TOOLS': {
            'weight': 0.09,
            'genres': ['Utilities', 'File Manager', 'Battery & Cleaner', 'Security & Antivirus', 'Calculators'],
            'avg_rating': 4.05,
            'rating_std': 0.45,
            'size_range': (5.0, 45.0),
            'free_prob': 0.91,
            'iap_prob': 0.45,
            'price_choices': [0.99, 1.49, 1.99, 2.99, 4.99],
            'price_weights': [0.45, 0.25, 0.15, 0.10, 0.05],
            'ad_rpm': 2.00,
            'iap_rev_mult': 1.8,
            'prefixes': ['Super', 'Fast', 'Power', 'Ultra', 'Smart', 'Safe', 'Easy', 'Quick', 'Turbo', 'Master'],
            'suffixes': ['Tool', 'Cleaner', 'Speed', 'Optimizer', 'Shield', 'Scan', 'Helper', 'Utility', 'Boost', 'Kit']
        },
        'SOCIAL': {
            'weight': 0.06,
            'genres': ['Chat & Messaging', 'Dating & Meet', 'Communities', 'Voice Rooms', 'Live Streams'],
            'avg_rating': 4.10,
            'rating_std': 0.40,
            'size_range': (30.0, 130.0),
            'free_prob': 0.97,
            'iap_prob': 0.85,
            'price_choices': [0.99, 1.99, 3.99],
            'price_weights': [0.60, 0.30, 0.10],
            'ad_rpm': 4.80,
            'iap_rev_mult': 4.5,
            'prefixes': ['Circle', 'Chat', 'Bond', 'Link', 'Tribe', 'Hangout', 'Echo', 'Flock', 'Sync', 'Wink'],
            'suffixes': ['App', 'Social', 'Live', 'Connect', 'Match', 'Lounge', 'Spot', 'Talk', 'Vibe', 'Network']
        },
        'BUSINESS': {
            'weight': 0.05,
            'genres': ['CRM & Sales', 'POS & Invoicing', 'Team Chat', 'Analytics & Reports', 'Hiring'],
            'avg_rating': 4.20,
            'rating_std': 0.32,
            'size_range': (18.0, 90.0),
            'free_prob': 0.88,
            'iap_prob': 0.70,
            'price_choices': [4.99, 9.99, 14.99, 19.99, 29.99],
            'price_weights': [0.35, 0.30, 0.20, 0.10, 0.05],
            'ad_rpm': 4.20,
            'iap_rev_mult': 5.5,
            'prefixes': ['Biz', 'Lead', 'Sale', 'Enterprise', 'Omni', 'Scale', 'Invoice', 'Client', 'Corp', 'Team'],
            'suffixes': ['Pro', 'CRM', 'Point', 'HQ', 'Manager', 'Command', 'Portal', 'Direct', 'Desk', 'One']
        },
        'LIFESTYLE': {
            'weight': 0.05,
            'genres': ['Home & Decor', 'Horoscope & Tarot', 'Fashion & Beauty', 'Parenting', 'DIY Crafts'],
            'avg_rating': 4.15,
            'rating_std': 0.38,
            'size_range': (15.0, 70.0),
            'free_prob': 0.90,
            'iap_prob': 0.60,
            'price_choices': [0.99, 1.99, 2.99, 4.99],
            'price_weights': [0.50, 0.30, 0.15, 0.05],
            'ad_rpm': 2.40,
            'iap_rev_mult': 2.6,
            'prefixes': ['Cozy', 'Modern', 'Style', 'Aura', 'Dream', 'Glow', 'Haven', 'Chic', 'Spirit', 'Grace'],
            'suffixes': ['Living', 'Guide', 'Daily', 'Design', 'Journal', 'Inspo', 'Look', 'Corner', 'Home', 'Path']
        }
    }

    categories = list(categories_config.keys())
    cat_weights = [categories_config[c]['weight'] for c in categories]
    cat_weights = [w / sum(cat_weights) for w in cat_weights]

    install_tiers = [
        (1000, 0.18),
        (5000, 0.14),
        (10000, 0.16),
        (50000, 0.13),
        (100000, 0.14),
        (500000, 0.09),
        (1000000, 0.08),
        (5000000, 0.04),
        (10000000, 0.025),
        (50000000, 0.012),
        (100000000, 0.003)
    ]
    install_values = [t[0] for t in install_tiers]
    install_probs = [t[1] for t in install_tiers]

    content_ratings = ['Everyone', 'Teen', 'Mature 17+', 'Everyone 10+']
    content_probs = [0.72, 0.13, 0.06, 0.09]

    min_android_versions = ['4.4 and up', '5.0 and up', '6.0 and up', '7.0 and up', '8.0 and up', '10.0 and up']
    android_probs = [0.08, 0.18, 0.24, 0.26, 0.18, 0.06]

    base_date = datetime(2026, 1, 15)

    records = []
    used_names = set()

    for i in range(1, num_records + 1):
        cat = np.random.choice(categories, p=cat_weights)
        cfg = categories_config[cat]

        # Generate unique app name
        for _ in range(50):
            pfx = random.choice(cfg['prefixes'])
            sfx = random.choice(cfg['suffixes'])
            modifier = random.choice(['', ' 3D', ' AI', ' 2026', ' Go', ' Lite', ' HD', ' X', ' Max'])
            name = f"{pfx} {sfx}{modifier}".strip()
            if name not in used_names:
                used_names.add(name)
                break
        else:
            name = f"{random.choice(cfg['prefixes'])} {random.choice(cfg['suffixes'])} #{i}"

        # Ratings: realistic bounded distribution
        raw_rating = np.random.normal(cfg['avg_rating'], cfg['rating_std'])
        rating = round(min(5.0, max(1.5, raw_rating)), 1)

        # Installs
        installs = int(np.random.choice(install_values, p=install_probs))

        # Reviews: tightly correlated with installs but variable (typically 1.5% to 8% of installs)
        review_ratio = np.random.uniform(0.015, 0.085)
        # Higher rated apps get slightly more reviews
        rating_boost = (rating / 4.0) ** 1.5
        reviews = int(max(12, installs * review_ratio * rating_boost * np.random.uniform(0.7, 1.3)))
        if reviews >= installs:
            reviews = int(installs * 0.45)

        # Size in MB
        size_min, size_max = cfg['size_range']
        size_mb = round(np.random.uniform(size_min, size_max), 1)

        # Type & Price
        is_free = np.random.random() < cfg['free_prob']
        if is_free:
            app_type = 'Free'
            price = 0.00
        else:
            app_type = 'Paid'
            price = float(np.random.choice(cfg['price_choices'], p=cfg['price_weights']))
            # Paid apps have significantly lower installs on average
            if installs > 1000000:
                installs = int(np.random.choice([10000, 50000, 100000, 500000]))
                reviews = int(max(10, installs * 0.04))

        # In-App Purchases
        has_iap = np.random.random() < cfg['iap_prob'] if is_free else (np.random.random() < 0.35)

        # Content Rating
        content_rating = np.random.choice(content_ratings, p=content_probs)
        if cat == 'GAME' and content_rating == 'Everyone':
            content_rating = np.random.choice(['Everyone', 'Teen', 'Everyone 10+'], p=[0.55, 0.25, 0.20])

        # Genre
        genre = random.choice(cfg['genres'])

        # Last Updated (within last 3 years)
        days_ago = int(np.random.exponential(scale=180)) # most apps updated recently
        days_ago = min(days_ago, 1095)
        updated_date = base_date - timedelta(days=days_ago)

        # Active Users (monthly estimated as 15% to 45% of total installs, decayed by recency)
        recency_factor = max(0.2, 1.0 - (days_ago / 1095.0) * 0.7)
        retention_ratio = np.random.uniform(0.15, 0.40) * (rating / 4.2)
        active_users = int(max(50, installs * retention_ratio * recency_factor))

        # Revenue Modeling:
        # 1. Paid app direct purchase revenue
        paid_revenue = round(installs * price * 0.70, 2) # after 30% store cut

        # 2. In-App Purchase Revenue (Freemium):
        if has_iap:
            # Payer conversion rate ~ 1.5% to 4.5% of MAU, ARPU of payers $8-$45
            payer_conversion = np.random.uniform(0.015, 0.040)
            avg_payer_spend = np.random.uniform(12.0, 38.0) * cfg['iap_rev_mult']
            iap_revenue = round((active_users * payer_conversion * avg_payer_spend) * 0.70, 2)
        else:
            iap_revenue = 0.0

        # 3. Ad Revenue:
        if is_free:
            # Impressions per active user per year * RPM / 1000
            ad_rpm = cfg['ad_rpm'] * np.random.uniform(0.85, 1.25)
            ad_revenue = round((active_users * 12 * (ad_rpm / 1000.0) * np.random.uniform(2.5, 6.0)), 2)
        else:
            ad_revenue = 0.0

        total_revenue = round(paid_revenue + iap_revenue + ad_revenue, 2)

        # Min Android Version
        min_ver = np.random.choice(min_android_versions, p=android_probs)

        records.append({
            'app_id': f"APP_{i:05d}",
            'app_name': name,
            'category': cat,
            'rating': rating,
            'reviews': reviews,
            'size_mb': size_mb,
            'installs': installs,
            'type': app_type,
            'price': price,
            'content_rating': content_rating,
            'genres': genre,
            'has_in_app_purchases': 1 if has_iap else 0,
            'active_users_monthly': active_users,
            'est_ad_revenue': ad_revenue,
            'est_iap_revenue': iap_revenue,
            'est_direct_revenue': paid_revenue,
            'total_est_revenue': total_revenue,
            'last_updated': updated_date.strftime('%Y-%m-%d'),
            'min_android_ver': min_ver
        })

    df = pd.DataFrame(records)
    return df

if __name__ == '__main__':
    target_path = r"C:\Users\91740\.gemini\antigravity\scratch\profitable-app-profile-analysis\data\apps_data.csv"
    print("Generating 6,500 mobile app records...")
    df = generate_mobile_app_dataset(num_records=6500)
    df.to_csv(target_path, index=False)
    print(f"Successfully generated {len(df):,} records and saved to {target_path}")
    print("\nDataset Sample:")
    print(df[['app_id', 'app_name', 'category', 'rating', 'installs', 'type', 'total_est_revenue']].head())
