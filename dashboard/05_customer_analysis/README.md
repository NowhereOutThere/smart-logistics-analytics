# Dashboard: Customer Analysis

An interactive Power BI dashboard visualizing the customer, revenue, service level and
revenue concentration findings from
[`05_customer_analysis.ipynb`](../../notebooks/05_customer_analysis.ipynb).

## Data Source

Built on four small, aggregated CSV files in [`data/`](data/), exported from the appendix
of [`05_customer_analysis.ipynb`](../../notebooks/05_customer_analysis.ipynb) (which runs
the ETL pipeline in [`src/delivery_pipeline.py`](../../src/delivery_pipeline.py) with
`include_customers=True`), so the numbers match the notebook:

- **`customer_stats.csv`** (200 rows) - one row per customer: loads, revenue (total, mean
  per load, per mile), billed amount, miles and the customer attributes (customer type,
  account status, primary freight type, credit terms, annual revenue potential). Used on
  pages 1 and 2.
- **`segment_stats.csv`** (12 rows) - loads, revenue and miles per segment value (booking
  type, load type, customer type, credit terms). Used on page 2.
- **`customer_service.csv`** (200 rows) - events, on-time events and total detention per
  customer. Used on page 3.
- **`customer_concentration.csv`** (200 rows) - customers ranked by total revenue with
  their cumulative share of customers and revenue. Used on page 4.

Each page works on its own table, so no relationships between the tables are needed.
Weighted measures (on-time rate, average detention, revenue per mile) are calculated in
Power BI from the sums (DAX), not as averages of averages. The Gini coefficient on page 4
is taken from the notebook (section 7.1) and not recalculated in Power BI.

## What's in the Dashboard

**Page 1 - Customer Overview**
- **KPI cards:** number of customers, loads, revenue per mile, total revenue
- **Bar chart:** customers by customer type and account status (active / inactive)
- **Slicers:** customer type and account status

**Page 2 - Revenue**
- **Revenue per mile by segment** (booking type, credit terms, customer type, load type),
  grouped in one bar chart
- **Annual revenue potential against total revenue** per customer (scatter plot)
- **Key findings:** revenue per mile is the same in all segments (about 2.15 $, maximum
  difference 0.4 %, permutation tests p = 0.12-0.82), and the annual revenue potential does
  not predict the actual revenue (Spearman rho = -0.08, p = 0.27)

**Page 3 - Service Level**
- **On-time rate and average detention against number of events** per customer (two
  scatter plots with the overall value as reference line)
- **Top and bottom 5 customers by on-time rate**
- **Key finding:** on-time rates (50.0-60.7 %) and detention (85.9-98.8 min) vary between
  customers as much as random fluctuation would (permutation tests p = 0.77 and p = 0.58)

**Page 4 - Concentration**
- **Cumulative revenue share** by customers, largest first, against the line of equal
  distribution
- **KPI cards:** revenue share of the top 10 % (11.2 %) and top 20 % (21.9 %) of the
  customers, share of the largest customer (0.59 %), Gini coefficient (0.039)
- **Top and bottom 10 customers by total revenue**
- **Key finding:** revenue is spread almost evenly, there is no relevant customer
  concentration risk

The data are simulated, so the missing differences between customers mainly show that the
simulation did not build customer effects in.

## Screenshots

![Dashboard overview](screenshots/customer_overview.png)
*Page 1: KPI cards, customers by type and status, and slicers.*

<details>
<summary>Revenue, service level & concentration</summary>

![Revenue](screenshots/revenue.png)

![Service level](screenshots/service_level.png)

![Concentration](screenshots/concentration.png)

</details>

## Opening the Dashboard

Requires [Power BI Desktop](https://powerbi.microsoft.com/desktop/) (free).
Open [`customer_analysis.pbix`](customer_analysis.pbix) directly. It reads from the CSV
files in [`data/`](data/); if Power BI cannot find them, update the file path under
*Transform data > Data source settings*. To regenerate the files, run the appendix of
[`05_customer_analysis.ipynb`](../../notebooks/05_customer_analysis.ipynb) and refresh the
data in Power BI.

## Status

🟢 Finished. Covers the customer, revenue, service level and concentration findings from
`05_customer_analysis.ipynb`. Other dashboards live in their own subfolders - see the
[dashboard index](../README.md) for the full list.