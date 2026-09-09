# Smart Logistics Analytics & Delivery Performance

A hands-on data analytics project exploring logistics data, delivery lead times, and delay root causes using **Python**, **Pandas**, and **SQL**.

---

## Project Overview

In the logistics industry, on-time delivery is a critical success factor. This project analyzes heterogeneous logistics data to identify supply chain bottlenecks, uncover temporal patterns in delays, and derive data-driven insights for process optimization.

##  Data Source & Schema

The analysis is based on the open-source **[Logistics Operations Database](https://www.kaggle.com/datasets/yogape/logistics-operations-database/data)** available on Kaggle.

* **Source:** Kaggle (by Yogape)
* **Dataset Size:** ~14,800+ operational shipment records
* **Domain:** Supply Chain & Logistics Management

### Key Operational Fields:
* **Order & Timestamps:** `Order_ID`, `Order_Date`, `Ship_Date`, `Delivery_Date`
* **Logistics & Transit:** `Origin`, `Destination`, `Carrier`, `Shipping_Mode` *(e.g., Air, Sea, Road)*
* **Financials & Volume:** `Shipment_Cost`, `Order_Value`, `Weight_kg`, `Quantity`
* **Performance Metrics:** `Delivery_Status` *(On-Time, Delayed)*, `Calculated_Lead_Time`

---

### Key Objectives:
* **ETL & Data Cleaning:** Aggregating and prepping incomplete logistics datasets.
* **Exploratory Data Analysis (EDA):** Identifying Key Performance Indicators (KPIs) across regions, products, and transit modes.
* **Root Cause Analysis:** Pinpointing factors influencing shipment delays (progressing from descriptive to diagnostic analysis).

---

## Tech Stack

* **Languages:** Python 3.x, SQL
* **Libraries:** Pandas, NumPy, Matplotlib, Seaborn
* **Tools:** Jupyter Notebooks, Git / GitHub
* *(Planned: Power BI for interactive dashboards)*

---

##  Repository Structure

The analysis is structured modularly across the following key areas:

```text
├── notebooks/
│   ├── 01_delivery_performance.ipynb # 🟡 In Progress | Core KPIs, average lead times & delay rates, wip
│   ├── 02_temporal_patterns.ipynb    # ⚪ Planned     | Seasonality, trends & weekday analysis
│   ├── 03_products_categories.ipynb  # ⚪ Planned     | Top revenue items & delay-prone products
│   ├── 04_regional_analysis.ipynb    # ⚪ Planned     | Geographic distribution of volumes & times
│   └── 05_correlations.ipynb         # ⚪ Planned     | Diagnostic analysis: Key drivers of delays
├── README.md                   # Project documentation
``` 

## Roadmap & Development Milestones
* 🟡 Phase 1: Project Setup & Data Ingestion 

    * 🟢 Define repository architecture and folder layout 

    * 🟢 Dataset selection, schema definition & synthetic data generation

    * ⚪ Set up initial ETL pipeline for data cleaning and transformation 

* 🟡 Phase 2: Exploratory Data Analysis (Jupyter Notebooks) 🟡

    * 🟡 01_delivery_performance.ipynb 

    * ⚪ 02_temporal_patterns.ipynb ⚪

    * ⚪ 03_products_categories.ipynb ⚪

    * ⚪ 04_regional_analysis.ipynb ⚪

* ⚪ Phase 3: Diagnostic Analysis & Modeling ⚪

    * ⚪ 05_correlations.ipynb (Root cause analysis of shipment delays) ⚪

* ⚪ Phase 4: BI & Dashboarding ⚪

    * ⚪ Build an interactive Power BI dashboard for executive summary ⚪