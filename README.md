English | [Español](README.es.md)

# UK Online Retail Sales Analysis

## Overview

This project explores sales performance, customer behavior, product demand, and returns in transactional data from
a UK online retailer. It demonstrates a business intelligence workflow: inspect the source data, classify
transaction lines, model time-based measures, and communicate findings through a two-page Power BI report.

The repository is useful for reviewing the **analytical approach and dashboard design**. It contains the original
Excel dataset, model and cleaning documentation, and dashboard screenshots. **It does not currently contain an
openable Power BI report:** the committed `powerbi/online-retail-sales-analysis .pbix` is a two-byte placeholder.
The screenshots are visual evidence, not an interactive dashboard.

## How to Use

1. **Preview the report:** inspect the two [dashboard screenshots](#dashboard-preview) below. No software
   installation is needed to view them on GitHub.
2. **Inspect the source:** open or download [Online Retail.xlsx](data/raw/Online%20Retail.xlsx) with a compatible
   spreadsheet application. The dataset includes cancellations, negative quantities, missing customer identifiers,
   and special transaction codes.
3. **Understand the processing:** read [Data Cleaning Notes](docs/cleaning-notes.md) for the documented
   classification and preparation decisions.
4. **Interpret the model:** use the [Data Dictionary](data/data-dictionary.md) for documented field names,
   inclusion rules, measures, and KPI definitions.

Power BI Desktop is relevant to the original report workflow, but the committed `.pbix` cannot be opened or
refreshed. Reproducing the interactive report requires a valid report file or a separate reconstruction; neither
is provided as a runnable procedure here.

## Dashboard Preview

These screenshots document the layout of the original two-page report. Their metrics are not supplied as
independently validated numerical findings in this repository.

### Sales Overview

![Power BI Sales Overview page showing commercial KPIs and sales trends](dashboard/sales-overview.png)

The executive page brings together sales, orders, unique customers, average order value, return rate, net sales
over time, country performance, top ten products by net sales, and monthly order volume.

### Product & Customer Insights

![Power BI Product and Customer Insights page showing customer and returns comparisons](dashboard/product-customer-insights.png)

This page compares the top ten customers by net sales, returned value by country, highest-returned products by
value, and sales versus returns by product.

The documented report uses **Year**, **Country**, and **Line Type** filters. Filtering requires the original
interactive report; the committed screenshots are static.

## Business Questions

The analysis was designed to explore:

- How do sales and order volume change over time?
- Which products and customers contribute most to net sales?
- Which countries account for orders and returned value?
- How do returns differ across products and countries?
- How does average order value vary over time?

These are questions the dashboard is designed to investigate, **not independently verified findings**. Do not
interpret possible concentration or return patterns as measured results without the underlying report or an
analysis of the raw data.

## Tools Used

- **Excel:** initial source-data inspection.
- **Power Query:** documented data preparation, classification, and transformation.
- **Power BI / DAX:** documented data model, measures, and visual reporting.

## Dataset

The versioned source is [`data/raw/Online Retail.xlsx`](data/raw/Online%20Retail.xlsx). Its transaction fields
cover invoice identifiers and dates, stock codes, product descriptions, quantities, unit prices, customer
identifiers, and countries.

Cancelled invoices, negative-quantity lines, blank customer IDs, and special codes require different treatment
depending on the metric. The [cleaning notes](docs/cleaning-notes.md) explain the decisions; the
[data dictionary](data/data-dictionary.md) specifies the documented fields and rules.

## Data Cleaning and Preparation

The documented workflow standardizes data types, identifies cancellations and returns, distinguishes products from
gift vouchers and adjustments, reviews missing values, and prepares a calendar table for time-based reporting.

The key inclusion rule, `Include_In_Main_Analysis`, limits the core sales scope to normal, non-cancelled,
non-negative-quantity, non-zero-price **Product** lines. Returns are tracked separately. For the complete
classification and rule details, see the
[Data Dictionary](data/data-dictionary.md#business-rules-for-calculated-columns).

## Data Model

The documented model consists of an **Online Retail** transactional table and a **Calendar** date table derived
from `Invoice_Day`.

Its measures cover main and net sales, orders, unique customers, average order value, return value, and return
rate. The authoritative documentation of the *reported* model is the
[field and measure reference](data/data-dictionary.md); these definitions cannot be independently checked against
the placeholder PBIX.

## Documentation Map

| If you want to… | Go to… |
| --- | --- |
| See what the report looked like | [Sales Overview](dashboard/sales-overview.png) or [Product & Customer Insights](dashboard/product-customer-insights.png) |
| Examine the original data | [Online Retail.xlsx](data/raw/Online%20Retail.xlsx) |
| Understand preparation decisions and assumptions | [Data Cleaning Notes](docs/cleaning-notes.md) |
| Look up model fields, classifications, or measures | [Data Dictionary](data/data-dictionary.md) |

The main checked-in paths are:

```text
README.md
README.es.md
dashboard/
  sales-overview.png
  product-customer-insights.png
data/
  raw/Online Retail.xlsx
  data-dictionary.md
docs/
  cleaning-notes.md
powerbi/
  online-retail-sales-analysis .pbix   # two-byte placeholder; not a runnable report
```

## Project Status

The repository documents a completed **analytical and dashboard design exercise** through its descriptions and
screenshots. It does **not** provide an independently runnable Power BI deliverable: the only tracked `.pbix` is a
placeholder, and source-to-report transformation steps are documented conceptually rather than supplied as a
complete executable pipeline.

This distinction preserves the available project evidence without implying that the interactive dashboard can be
reproduced directly from the committed files.

## Author

**Angel W. Miller** — Junior Data Analyst focused on business intelligence, analytics, and dashboard development.

## Contact

- GitHub: [angel-wm](https://github.com/angel-wm)
- LinkedIn: [Angel W. Miller](https://www.linkedin.com/in/angel-w-miller/)
