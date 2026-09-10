# Smart Logistics Analytics & Delivery Performance

A hands-on data analytics project exploring logistics data, delivery lead times, and delay root causes using **Python**, **Pandas**, and **SQL** *(planned)*.

---

## Project Overview

In the logistics industry, on-time delivery is a critical success factor. This project analyzes heterogeneous logistics data to identify supply chain bottlenecks, uncover temporal patterns in delays, and derive data-driven insights for process optimization.

##  Data Source & Schema

The analysis is based on the open-source **[Logistics Operations Database](https://www.kaggle.com/datasets/yogape/logistics-operations-database/data)** available on Kaggle.

* **Source:** Kaggle (by Yogape)
* **Dataset Size:** ~14,800+ operational shipment records
* **Domain:** Supply Chain & Logistics Management

### Key Operational Fields:
* **IDs & Relations:** `load_id`, `route_id`, `trip_id`
* **Event Tracking:** `event_type` *(Pickup, Delivery)*, `scheduled_datetime`, `actual_datetime`, `on_time_flag`, `detention_minutes`
* **Location:** `facility_id`, `location_city`, `location_state`
* **Derived Metrics:** `delivery_duration_hours`, `delivery_delay_hours`, `is_delayed_delivery`



### Key Objectives:
* **ETL & Data Cleaning:** AIntegrating, cleaning, transforming, and preparing logistics data for analysis.
* **Exploratory Data Analysis (EDA):** Identifying Key Performance Indicators (KPIs) across regions, products, and transit modes.
* **Delay Analysis:** Pinpointing factors influencing shipment delays (progressing from descriptive to diagnostic analysis).



## Key Insights

 *Will be added once `01_delivery_performance.ipynb` is finalized, e.g. average lead time, on-time delivery rate, and the main drivers of delay.*
 - Average delivery lead time: X hours
- On-time delivery rate: X%
- X% of deliveries were delayed
- Region X showed the highest average delay
- Transport type X had the shortest/longest average delivery time

---

## Tech Stack

* **Languages:** Python 3.12.1
* **Libraries:** Pandas, NumPy, Matplotlib, Seaborn
* **Tools:** Jupyter Notebooks, Git / GitHub
* *(Planned: Power BI for interactive dashboards)*

---

##  Repository Structure

The analysis is structured modularly across the following key areas:

```text
├── data/
│   ├── raw/                          # Raw input data (not tracked in git)
│   └── processed/                    # Cleaned output from the ETL pipeline
├── notebooks/
│   ├── 01_delivery_performance.ipynb # 🟡 In Progress | Core KPIs, average lead times & delay rates
│   ├── 02_temporal_patterns.ipynb    # ⚪ Planned     | Seasonality, trends & weekday analysis
│   ├── 03_products_categories.ipynb  # ⚪ Planned     | Top revenue items & delay-prone products
│   ├── 04_regional_analysis.ipynb    # ⚪ Planned     | Geographic distribution of volumes & times
│   └── 05_correlations.ipynb         # ⚪ Planned     | Diagnostic analysis: key drivers of delays
├── src/
│   └── delivery_pipeline.py          # Extract/transform/load logic
├── tests/
│   └── test_pipeline.py              # Unit tests for the ETL pipeline
├── requirements.txt
└── README.md
```

---

## Getting Started

1. Clone the repo:
```bash
   git clone <repo-url>
   cd <repo-name>
```
2. Create a virtual environment:
```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS/Linux
```
3. Install dependencies:
```bash
   pip install -r requirements.txt
```
4. Download the raw data from the [Logistics Operations Database](https://www.kaggle.com/datasets/yogape/logistics-operations-database/data)
   on Kaggle and place the CSV files in `data/raw/`
   (`loads.csv`, `trips.csv`, `delivery_events.csv`, `routes.csv`).
5. Run the ETL pipeline:
```bash
   python src/delivery_pipeline.py
```
6. Start Jupyter and open the notebooks in `notebooks/` to explore the analysis:
```bash
   jupyter notebook
```

---

## Roadmap & Development Milestones
* 🟡 Phase 1: Project Setup & Data Ingestion 

    * 🟢 Define repository architecture and folder layout 

    * 🟢 Dataset selection & schema definition 

    * ⚪ Set up initial ETL pipeline for data cleaning and transformation 

* 🟡 Phase 2: Exploratory Data Analysis (Jupyter Notebooks) 

    * 🟡 01_delivery_performance.ipynb 

    * ⚪ 02_temporal_patterns.ipynb 

    * ⚪ 03_products_categories.ipynb 

    * ⚪ 04_regional_analysis.ipynb 

* ⚪ Phase 3: Diagnostic Analysis & Modeling 

    * ⚪ 05_correlations.ipynb (Root cause analysis of shipment delays) 

* ⚪ Phase 4: BI & Dashboarding 

    * ⚪ Build an interactive Power BI dashboard for executive summary 

---

## Author

*Stefanie Häberle*

M.Sc. Informatik · Data Engineering & Data Analytics

[LinkedIn](https://www.linkedin.com/in/stefanie-haeberle-msc) · [GitHub](https://github.com/NowhereOutThere) · stefanie.haeberle@freenet.de