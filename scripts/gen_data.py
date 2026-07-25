import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

# ---------------------------------------------------------------
# Build a synthetic but realistic Global E-Commerce dataset
# Monthly grain, 2021-01 through 2024-12, across 5 regions and
# 5 product categories, with marketing spend and customer mix.
# ---------------------------------------------------------------

regions = ["North America", "Europe", "Asia-Pacific", "Latin America", "Middle East & Africa"]
categories = ["Electronics", "Apparel", "Home & Garden", "Beauty & Personal Care", "Sports & Outdoors"]

dates = pd.date_range("2021-01-01", "2024-12-01", freq="MS")

# Region growth profiles: (base_monthly_revenue_k, annual_growth_rate, volatility)
region_profile = {
    "North America":        (2200, 0.09, 0.05),
    "Europe":                (1600, 0.07, 0.05),
    "Asia-Pacific":          (900,  0.28, 0.07),   # fastest-growing
    "Latin America":         (420,  0.19, 0.09),
    "Middle East & Africa":  (300,  0.22, 0.10),
}

# Category profile: (share_of_revenue, gross_margin, margin_trend_per_year)
category_profile = {
    "Electronics":              (0.34, 0.18, -0.004),  # thin, shrinking margin
    "Apparel":                  (0.22, 0.42,  0.006),
    "Home & Garden":            (0.16, 0.36,  0.003),
    "Beauty & Personal Care":   (0.16, 0.52,  0.010),  # rising margin, strong
    "Sports & Outdoors":        (0.12, 0.31,  0.002),
}

seasonal_index = {  # multiplier by month (holiday shopping bump, summer dip in some regions)
    1: 0.86, 2: 0.83, 3: 0.90, 4: 0.92, 5: 0.95, 6: 0.98,
    7: 0.97, 8: 0.99, 9: 1.02, 10: 1.10, 11: 1.42, 12: 1.55,
}

rows = []
for region, (base, growth, vol) in region_profile.items():
    for cat, (share, margin0, margin_trend) in category_profile.items():
        for d in dates:
            years_elapsed = (d.year - 2021) + (d.month - 1) / 12
            trend = (1 + growth) ** years_elapsed
            season = seasonal_index[d.month]
            noise = rng.normal(1.0, vol)
            revenue_k = base * share * trend * season * noise

            # COVID-recovery / macro shock: mild dip in mid-2022 for all regions (inflation shock)
            if d.year == 2022 and d.month in (6, 7, 8):
                revenue_k *= 0.90

            # Supply chain disruption hit Electronics harder in early 2021
            if cat == "Electronics" and d.year == 2021 and d.month in (2, 3, 4):
                revenue_k *= 0.85

            margin = margin0 + margin_trend * years_elapsed
            margin = np.clip(margin + rng.normal(0, 0.01), 0.05, 0.65)
            profit_k = revenue_k * margin

            # marketing spend: correlated with revenue but with diminishing-returns noise
            marketing_k = (revenue_k * rng.uniform(0.06, 0.11)) * (1 + rng.normal(0, 0.15))
            marketing_k = max(marketing_k, 1)

            units = revenue_k * 1000 / rng.uniform(28, 95)  # avg order value varies by category

            # customer mix: new vs returning; returning share slowly rises with region maturity
            maturity = min(0.75, 0.30 + 0.05 * years_elapsed + (0.05 if region in ("North America", "Europe") else 0))
            returning_share = np.clip(maturity + rng.normal(0, 0.03), 0.15, 0.8)

            rows.append({
                "date": d,
                "region": region,
                "category": cat,
                "revenue_k_usd": round(revenue_k, 2),
                "profit_k_usd": round(profit_k, 2),
                "gross_margin": round(margin, 4),
                "marketing_spend_k_usd": round(marketing_k, 2),
                "units_sold": int(units),
                "returning_customer_share": round(returning_share, 4),
            })

df = pd.DataFrame(rows)
df.to_csv("/home/claude/ecommerce_data.csv", index=False)
print(df.shape)
print(df.head())
print("Total revenue ($k):", df["revenue_k_usd"].sum().round(1))
