# From Numbers to Narrative: A Visual Data Story of Global E-Commerce Performance

A data storytelling project analyzing four years (2021–2024) of global e-commerce performance across five regions and five product categories, built with Python. The project turns raw performance data into a narrative-driven report using six purpose-built visualizations, each paired with plain-language commentary explaining what it shows and why it matters.

## 📊 Visualizations

| # | Chart | Question it answers |
|---|-------|---------------------|
| 1 | Revenue & Profit Trend | Is growth translating into profit? |
| 2 | Regional Growth Index | Which regions are actually growing fastest? |
| 3 | Category Margin Comparison | What's profitable vs. what's just high-volume? |
| 4 | Seasonality Heatmap | Is there a predictable calendar pattern? |
| 5 | Marketing Spend vs. Revenue | Is marketing spend efficient? |
| 6 | Customer Loyalty Trend | Is the customer base becoming more loyal over time? |

All charts are in [`visuals/`](visuals/).

## 🛠️ Tools

- **Pandas** — data generation, aggregation, reshaping
- **Matplotlib** — custom layout, annotations, styling
- **Seaborn** — statistical charts and theming

## 📁 Repository Structure

```
├── scripts/
│   ├── gen_data.py     # generates the synthetic e-commerce dataset
│   └── make_viz.py     # builds all 6 visualizations
├── data/
│   └── ecommerce_data.csv
├── visuals/
│   └── *.png            # 6 final charts
└── report/
    └── DataStorytelling_Week2.pdf   # full written report
```

## ▶️ How to Run

```bash
pip install pandas numpy matplotlib seaborn

python scripts/gen_data.py    # writes data/ecommerce_data.csv
python scripts/make_viz.py    # writes visuals/*.png
```

## 📄 Full Report

The complete write-up — including methodology, chart-by-chart analysis, and business implications — is available in [`report/DataStorytelling_Week2.pdf`](report/DataStorytelling_Week2.pdf).

## 📝 Data Note

The dataset used in this project is synthetically generated but engineered to reflect realistic, well-documented e-commerce patterns (holiday seasonality, regional growth divergence, category margin differences, and diminishing marketing returns). The visualization and storytelling techniques demonstrated apply directly to real transactional datasets.
