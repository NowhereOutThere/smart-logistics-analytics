# Smart Logistics Analytics & Delivery Performance

A hands-on data analytics project exploring logistics data, delivery lead times, and delay root causes using **Python**, **Pandas**, with **SQL** and **Power BI** planned for a later phase.

---

## Project Overview

In the logistics industry, on-time delivery is a critical success factor. This project analyzes heterogeneous logistics data to identify supply chain bottlenecks, uncover temporal patterns in delays, and derive data-driven insights for process optimization.

## Data Source & Schema

The analysis is based on the open-source **[Logistics Operations Database](https://www.kaggle.com/datasets/yogape/logistics-operations-database/data)** available on Kaggle.

* **Source:** Kaggle (by Yogape)
* **Dataset Size:** ~85,000+ operational shipment records
* **Domain:** Supply Chain & Logistics Management

The full schema covers 14 tables across drivers, fleet equipment, customers, facilities, routes, shipments, trips, fuel purchases, maintenance, delivery events, and safety incidents. Each notebook uses a subset of these -- see the "Data Basis" section at the top of each notebook for the exact fields and tables used.

Additional tables (`drivers`, `trucks`, `trailers`, `customers`, `fuel_purchases`, `maintenance_records`, `safety_incidents`, ...) will be brought in progressively as further notebooks are added - see [Roadmap](#roadmap--development-milestones).



### Key Objectives:
* **ETL & Data Cleaning:** Integrating, cleaning, transforming, and preparing logistics data for analysis.
* **Exploratory Data Analysis (EDA):** Identifying Key Performance Indicators (KPIs) across regions, transport types, and customers
* **Delay Analysis:** Pinpointing factors influencing shipment delays (progressing from descriptive to diagnostic analysis).



## Key Insights
- Average delivery time: 26.68 hours 
- 67.04% of deliveries were delayed
- Average delay (delayed deliveries only): 3.00 hours

---


## Dashboard

An interactive Power BI dashboard complements the notebook analysis --
see [`dashboard/README.md`](dashboard/README.md) for details and screenshots.


---

## Tech Stack

* **Languages:** Python 3.12.1, SQL *(planned)*
* **Libraries:** Pandas, Matplotlib, Seaborn, Pytest
* **Tools:** Jupyter Notebooks, Git / GitHub
* *(Planned: Power BI for interactive dashboards)*

---

## Repository Structure

```text
├── dashboard/
│   ├── README.md                          # Index linking to individual dashboards
│   └── 01_delivery_performance/
│       ├── delivery_performance.pbix
│       ├── README.md                      # Dashboard-specific details
│       └── screenshots/
├── data/
│   ├── raw/                              # Raw input data (not tracked in git)
│   └── processed/                        # Cleaned output from the ETL pipeline (not tracked in git)
├── notebooks/
│   ├── 01_delivery_performance.ipynb     # 🟢 Finished    | Core KPIs: avg. lead time & delay rates
│   ├── 02_temporal_patterns.ipynb        # ⚪ Planned     | Seasonality, trends & weekday analysis
│   ├── 03_fleet_equipment_analysis.ipynb # ⚪ Planned     | Delay/duration by truck, trailer & fuel efficiency
│   ├── 04_regional_analysis.ipynb        # ⚪ Planned     | Region & facility-level performance
│   ├── 05_customer_analysis.ipynb        # ⚪ Planned     | Delay/revenue by customer segment
│   ├── 06_driver_safety_analysis.ipynb   # ⚪ Optional    | Driver performance & safety incidents
│   └── 07_correlations.ipynb             # ⚪ Planned     | Diagnostic analysis: key drivers of delays
├── src/
│   └── delivery_pipeline.py              # Extract/transform/load logic
├── tests/
│   └── test_delivery_pipeline.py         # Unit tests for the ETL pipeline
├── pytest.ini
├── README.md
└── requirements.txt
```

---

## Getting Started

1. Clone the repo:
```bash
   git clone <repo-url>
   cd <repo-name>
```
2. (Optional but recommended) Create a virtual environment:
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
* 🟢 Phase 1: Project Setup & Data Ingestion 

    * 🟢 Define repository architecture and folder layout 
    * 🟢 Dataset selection & schema definition 
    * 🟢 Set up initial ETL pipeline for data cleaning and transformation 

* 🟡 **Phase 2: Exploratory Data Analysis (Jupyter Notebooks)**
  * 🟢 `01_delivery_performance.ipynb` - core KPIs, average lead times & delay rates
  * ⚪ `02_temporal_patterns.ipynb` - seasonality, trends & weekday analysis
  * ⚪ `03_fleet_equipment_analysis.ipynb` - delay/duration by truck, trailer & fuel efficiency
  * ⚪ `04_regional_analysis.ipynb` - region & facility-level performance
  * ⚪ `05_customer_analysis.ipynb` - delay/revenue by customer segment

* ⚪ **Phase 3: Diagnostic Analysis & Modeling**
  * ⚪ `06_driver_safety_analysis.ipynb` *(optional)* - driver performance & safety incidents
  * ⚪ `07_correlations.ipynb` - root cause analysis of shipment delays across all dimensions

* ⚪ **Phase 4: BI & Dashboarding**
  * ⚪ Build an interactive Power BI dashboard for executive summary

---

## Testing

The ETL pipeline is covered by automated unit tests.

To run the tests:
```bash
pytest
``` 

---

## Author

*Stefanie Häberle* -  M.Sc. Informatik · aspiring Data Engineer