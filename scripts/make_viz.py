import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

sns.set_theme(style="whitegrid", context="talk")
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#444444"
plt.rcParams["figure.facecolor"] = "white"

df = pd.read_csv("/home/claude/ecommerce_data.csv", parse_dates=["date"])
OUT = "/home/claude/viz"

PALETTE_REGION = {
    "North America": "#2E5EAA",
    "Europe": "#5FA8D3",
    "Asia-Pacific": "#E07A5F",
    "Latin America": "#81B29A",
    "Middle East & Africa": "#F2CC8F",
}


def add_titles(fig, title, subtitle, title_size=19, top=0.85, title_y=0.975, sub_y=0.925):
    """Figure-level title + subtitle placed OUTSIDE the axes, with the plot
    area reserved below them via subplots_adjust — prevents any overlap
    regardless of how tall the title text renders."""
    fig.suptitle(title, x=0.045, y=title_y, ha="left", fontsize=title_size,
                 fontweight="bold", color="#1a1a1a")
    fig.text(0.045, sub_y, subtitle, ha="left", fontsize=12.5, color="#555555")
    fig.subplots_adjust(top=top, left=0.08, right=0.96, bottom=0.12)


# ============================================================
# CHART 1 — Global monthly revenue & profit trend with annotations
# ============================================================
monthly = df.groupby("date", as_index=False)[["revenue_k_usd", "profit_k_usd"]].sum()

fig, ax = plt.subplots(figsize=(13, 7))
ax.plot(monthly["date"], monthly["revenue_k_usd"], color="#2E5EAA", linewidth=2.6, label="Revenue")
ax.fill_between(monthly["date"], monthly["revenue_k_usd"], color="#2E5EAA", alpha=0.08)
ax.plot(monthly["date"], monthly["profit_k_usd"], color="#E07A5F", linewidth=2.6, label="Gross Profit")
ax.fill_between(monthly["date"], monthly["profit_k_usd"], color="#E07A5F", alpha=0.10)

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.1f}M"))
ax.set_xlabel("")
ax.set_ylabel("")
ax.legend(loc="upper left", frameon=False, fontsize=12.5)

dip = monthly[(monthly.date.dt.year == 2022) & (monthly.date.dt.month.isin([6, 7, 8]))]
ax.annotate("Inflation shock\ndampens mid-2022 demand", xy=(dip.date.iloc[1], dip.revenue_k_usd.iloc[1]),
            xytext=(dip.date.iloc[1], dip.revenue_k_usd.iloc[1] - 3800),
            fontsize=11, ha="center", color="#333333",
            arrowprops=dict(arrowstyle="->", color="#333333", lw=1.3))

peak = monthly[monthly.date.dt.month == 12]
last_peak = peak.iloc[-1]
ax.annotate("Nov–Dec holiday\nsurge, every year", xy=(last_peak.date, last_peak.revenue_k_usd),
            xytext=(last_peak.date - pd.Timedelta(days=500), last_peak.revenue_k_usd - 1200),
            fontsize=11, ha="center", color="#333333",
            arrowprops=dict(arrowstyle="->", color="#333333", lw=1.3))

add_titles(fig, "Revenue Climbs Steadily, but Profit Growth Lags Behind",
           "Global monthly revenue and gross profit, Jan 2021 – Dec 2024", top=0.84)
sns.despine(left=False, bottom=False)
plt.savefig(f"{OUT}/01_revenue_profit_trend.png", dpi=180)
plt.close()

# ============================================================
# CHART 2 — Regional growth trajectories (indexed to 100)
# ============================================================
reg_monthly = df.groupby(["date", "region"], as_index=False)["revenue_k_usd"].sum()
base = reg_monthly[reg_monthly.date == reg_monthly.date.min()][["region", "revenue_k_usd"]].rename(
    columns={"revenue_k_usd": "base"})
reg_monthly = reg_monthly.merge(base, on="region")
reg_monthly["index"] = reg_monthly["revenue_k_usd"] / reg_monthly["base"] * 100
reg_monthly = reg_monthly.sort_values(["region", "date"])
reg_monthly["index_smooth"] = reg_monthly.groupby("region")["index"].transform(lambda s: s.rolling(3, min_periods=1).mean())

region_order = ["Asia-Pacific", "Middle East & Africa", "Latin America", "North America", "Europe"]
fig, ax = plt.subplots(figsize=(13, 7.3))
for region in region_order:
    d = reg_monthly[reg_monthly.region == region]
    ax.plot(d.date, d.index_smooth, label=region, color=PALETTE_REGION[region], linewidth=2.6)
    ax.text(d.date.iloc[-1] + pd.Timedelta(days=25), d.index_smooth.iloc[-1], region,
            color=PALETTE_REGION[region], fontsize=11.5, va="center", fontweight="bold")

ax.axhline(100, color="#999999", linestyle="--", linewidth=1)
ax.set_xlim(reg_monthly.date.min(), reg_monthly.date.max() + pd.Timedelta(days=330))
ax.set_ylabel("Index (Jan 2021 = 100)")
add_titles(fig, "Asia-Pacific and Emerging Regions Are Outgrowing the Core Markets",
           "Regional revenue indexed to Jan 2021 = 100 (3-month rolling average)", title_size=18, top=0.84)
sns.despine()
plt.savefig(f"{OUT}/02_regional_growth_index.png", dpi=180)
plt.close()

# ============================================================
# CHART 3 — Category profitability: margin vs revenue contribution
# ============================================================
cat_summary = df.groupby("category", as_index=False).agg(
    revenue_k_usd=("revenue_k_usd", "sum"),
    profit_k_usd=("profit_k_usd", "sum"),
)
cat_summary["margin"] = cat_summary["profit_k_usd"] / cat_summary["revenue_k_usd"]
cat_summary = cat_summary.sort_values("margin", ascending=True)

fig, ax = plt.subplots(figsize=(12.5, 7.3))
colors = ["#E07A5F" if m < cat_summary["margin"].median() else "#3D8361" for m in cat_summary["margin"]]
bars = ax.barh(cat_summary["category"], cat_summary["margin"] * 100, color=colors, height=0.6)

for bar, rev in zip(bars, cat_summary["revenue_k_usd"]):
    ax.text(bar.get_width() + 0.6, bar.get_y() + bar.get_height() / 2,
            f"${rev/1000:,.0f}M revenue", va="center", fontsize=11.5, color="#333333")

ax.set_xlabel("Gross Margin (%)")
ax.set_xlim(0, 62)
add_titles(fig, "Electronics Drives Volume but Beauty & Personal Care Drives Margin",
           "Gross margin (%) by category, 2021–2024, with total revenue contribution labeled",
           title_size=17.5, top=0.84)
sns.despine(left=True)
ax.tick_params(left=False)
plt.savefig(f"{OUT}/03_category_margin.png", dpi=180)
plt.close()

# ============================================================
# CHART 4 — Seasonality heatmap (month x year revenue)
# ============================================================
df["year"] = df.date.dt.year
df["month"] = df.date.dt.month
heat = df.groupby(["year", "month"], as_index=False)["revenue_k_usd"].sum()
pivot = heat.pivot(index="year", columns="month", values="revenue_k_usd")
month_labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
pivot.columns = month_labels

fig, ax = plt.subplots(figsize=(13, 5.6))
sns.heatmap(pivot, cmap="YlOrRd", annot=True, fmt=".0f", cbar_kws={"label": "Revenue ($k)"},
            linewidths=1, linecolor="white", ax=ax, annot_kws={"fontsize": 10})
ax.set_xlabel("")
ax.set_ylabel("")
add_titles(fig, "The Holiday Quarter Is Growing Faster Than the Rest of the Year",
           "Total monthly revenue ($k) by year — November & December consistently peak",
           title_size=17.5, top=0.80, title_y=0.96, sub_y=0.87)
plt.savefig(f"{OUT}/04_seasonality_heatmap.png", dpi=180)
plt.close()

# ============================================================
# CHART 5 — Marketing spend vs revenue (diminishing returns), by region
# ============================================================
fig, ax = plt.subplots(figsize=(12.5, 7.6))
for region in region_order:
    d = df[df.region == region]
    ax.scatter(d.marketing_spend_k_usd, d.revenue_k_usd, s=26, alpha=0.45, color=PALETTE_REGION[region], label=region)

x = df["marketing_spend_k_usd"].values
y = df["revenue_k_usd"].values
coeffs = np.polyfit(np.log(x), y, 1)
xs = np.linspace(x.min(), x.max(), 200)
ys = coeffs[0] * np.log(xs) + coeffs[1]
ax.plot(xs, ys, color="#222222", linewidth=2.8, linestyle="--", label="Overall trend (log fit)")

ax.set_xlabel("Marketing Spend ($k / month)")
ax.set_ylabel("Revenue ($k / month)")
ax.legend(loc="upper left", frameon=False, fontsize=10.5, ncol=2)
add_titles(fig, "Marketing Spend Pays Off — But With Diminishing Returns",
           "Monthly marketing spend vs. revenue across all region–category combinations, 2021–2024",
           title_size=18, top=0.84)
sns.despine()
plt.savefig(f"{OUT}/05_marketing_vs_revenue.png", dpi=180)
plt.close()

# ============================================================
# CHART 6 — Returning customer share over time (loyalty maturity)
# ============================================================
loy = df.groupby(["date", "region"], as_index=False)["returning_customer_share"].mean()
loy_wide = loy.pivot(index="date", columns="region", values="returning_customer_share")[region_order[::-1]]

fig, ax = plt.subplots(figsize=(13, 7.6))
colors_stack = [PALETTE_REGION[r] for r in loy_wide.columns]
ax.stackplot(loy_wide.index, [loy_wide[c] * 100 / 5 for c in loy_wide.columns],
             labels=loy_wide.columns, colors=colors_stack, alpha=0.9)
ax.set_ylabel("Composite Returning-Customer Index")
ax.legend(loc="upper left", frameon=False, fontsize=10.5, ncol=3, bbox_to_anchor=(0, -0.13))
add_titles(fig, "Customer Loyalty Is Strengthening Across Every Region",
           "Average returning-customer share by region (stacked, illustrative composite), 2021–2024",
           title_size=18, top=0.84)
sns.despine()
plt.savefig(f"{OUT}/06_loyalty_trend.png", dpi=180)
plt.close()

print("All charts regenerated with fixed spacing.")
