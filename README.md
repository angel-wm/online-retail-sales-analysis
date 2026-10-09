English | [Español](README.es.md)

# UK Online Retail Sales Analysis

## Overview

This project explores sales, product performance, customer coverage and merchandise cancellations/reversals in the UK Online Retail dataset through a two-page Power BI report.

The working project is [uk-online-retail-sales-analysis.pbip](uk-online-retail-sales-analysis.pbip), directly in the repository root. Its report and model components are in `powerbi/`. The corrections previously authored in a separate `review` checkout have been consolidated into this original project; there is one active PBIP entry point. See [Project structure](docs/PROJECT_STRUCTURE.md) for the current folders and recovery copies.

This is a local review branch. Native verification status and remaining visual/interaction checks are recorded in [Desktop acceptance](docs/revision/DESKTOP_ACCEPTANCE.md). The original screenshots below show the previous report.

## How to Use

1. Open [uk-online-retail-sales-analysis.pbip](uk-online-retail-sales-analysis.pbip) in Power BI Desktop. Do not open the archived PBIX placeholder.
2. If the project has moved, close Desktop and run `python scripts/configure_source.py` from the new root. This sets `SourceFilePath` to the local `data/raw/Online Retail.xlsx`. Reopen the same root PBIP and refresh.
3. Explore **Sales Overview** and **Product & Customer Insights**. Year, Country and Line Type selectors are synchronized across the two pages.
4. Review [financial changes](docs/revision/PHASE_1.md), [model changes](docs/revision/PHASE_2.md), [reproduction commands](docs/revision/REPRODUCE.md) and [remaining Desktop checks](docs/revision/DESKTOP_ACCEPTANCE.md).

The recovered original PBIX is retained in the local `backups` folder as a historical snapshot. PBIP edits do not update that binary; an updated PBIX must be saved from the accepted project in Desktop.

## Dashboard Preview

These screenshots document the layout of the original two-page report. Their metrics are not supplied as
independently validated numerical findings in this repository.

### Sales Overview

![Power BI Sales Overview page showing commercial KPIs and sales trends](screenshots/sales-overview.png)

The executive page brings together sales, orders, unique customers, average order value, return rate, net sales
over time, country performance, top ten products by net sales, and monthly order volume.

### Product & Customer Insights

![Power BI Product and Customer Insights page showing customer and returns comparisons](screenshots/product-customer-insights.png)

This page compares the top ten customers by net sales, returned value by country, highest-returned products by
value, and sales versus returns by product.

The original report used **Year**, **Country**, and **Line Type** filters. The current PBIP provides interactive filtering; these historical screenshots are static.

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

The source is the **Online Retail** dataset published by the UCI Machine Learning Repository and created by
Daqing Chen. UCI identifies it as 541,909 transactions from 1 December 2010 through 9 December 2011 for a
UK-based registered non-store retailer.

**Dataset citation:** Chen, D. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository.
https://doi.org/10.24432/C5BW33

The dataset is licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**. The copy stored in
this repository remains under that dataset license; see [Dataset License and Attribution](DATA_LICENSE.md).

Cancelled invoices, negative-quantity lines, blank customer IDs, and special codes require different treatment
depending on the metric. The [cleaning notes](docs/cleaning-notes.md) explain the decisions; the
[data dictionary](data/data-dictionary.md) specifies the documented fields and rules.

## Data Cleaning and Preparation

The Excel source is retained byte for byte. The model excludes the 1,454 rows with null descriptions under the recovered quality rule, leaving 540,455 fact rows. Repeated transaction lines are retained.

Gross merchandise sales require normal Product lines, positive quantity and price, and a non-cancelled invoice. Merchandise reversals require negative quantity and positive price on normal Product lines. Net merchandise sales subtract these reversals from gross merchandise sales; administrative and other movements remain separate. `AMAZONFEE` is classified as administrative. Monetary measures use GBP (£); ratio measures preserve their full calculation precision.

See [Phase 1](docs/revision/PHASE_1.md), [Phase 2](docs/revision/PHASE_2.md) and the [before/after reconciliation](evidence/financial/before_after.csv) for current definitions and evidence. The [original cleaning notes](docs/cleaning-notes.md) describe the historical implementation and may differ from the revised model.

## Data Model

The current model contains the **Online Retail** fact table, **Calendar**, and **DimProduct**, plus the two preserved hidden automatic date tables. There are 17 measures and three relationships. Product identity uses stock code and a deterministic representative description; the original description variants remain inspectable.

The authoritative implementation is the TMDL source in `powerbi/uk-online-retail-sales-analysis.SemanticModel/definition/`. [Phase 2](docs/revision/PHASE_2.md) explains the relationships, description selection and source parameter. The [original data dictionary](data/data-dictionary.md) is retained as a historical reference.

## Documentation Map

| Purpose | Location |
| --- | --- |
| Open the current project | [Root PBIP](uk-online-retail-sales-analysis.pbip) |
| Understand folders and backups | [Project structure](docs/PROJECT_STRUCTURE.md) |
| Examine original source data | [Online Retail.xlsx](data/raw/Online%20Retail.xlsx) |
| Review corrected measures and reconciliation | [Phase 1](docs/revision/PHASE_1.md), [before/after](evidence/financial/before_after.csv) |
| Review model and product identity | [Phase 2](docs/revision/PHASE_2.md) |
| Reproduce validation | [Reproduction guide](docs/revision/REPRODUCE.md) |
| Check remaining native acceptance | [Desktop acceptance](docs/revision/DESKTOP_ACCEPTANCE.md) |
| Verify data attribution and licensing | [Dataset license](DATA_LICENSE.md) |

```text
uk-online-retail-sales-analysis.pbip
powerbi/          # report PBIR and semantic model TMDL
data/raw/        # original Excel source
docs/revision/   # decisions, phase changes and acceptance
docs/archive/    # recovered historical PDF, measures and theme
screenshots/     # original report images
scripts/         # source configuration and validation
evidence/        # baseline, reconciliation and validation receipts
backups/         # local recovery archives; excluded from Git
```

## Project Status

Corrections are implemented locally on `codex/retail-dashboard-corrections`. No push, merge or Power BI Service publication has occurred. Source-based reconciliation, TMDL parsing, JSON schema coverage, references and recovery checks have reproducible receipts in `evidence/validation`.

Native refresh is recorded in `desktop-native-refresh.json` and final measure checks in `desktop-native-check.json`; they do not prove rendered labels, dropdowns or report interactions. Follow [Desktop acceptance](docs/revision/DESKTOP_ACCEPTANCE.md) before final integration. The images remain historical; no new PBIX export or new dashboard screenshots are claimed.

## License

Repository-authored project materials are released under the [MIT License](LICENSE).

The source dataset is **not relicensed under MIT**. `data/raw/Online Retail.xlsx` is the UCI **Online Retail**
dataset by Daqing Chen and remains licensed under **CC BY 4.0**. Attribution and reuse details are documented in
[DATA_LICENSE.md](DATA_LICENSE.md).

## Author

**Angel W. Miller** — Junior Data Analyst focused on business intelligence, analytics, and dashboard development.

## Contact

- GitHub: [angel-wm](https://github.com/angel-wm)
- LinkedIn: [Angel W. Miller](https://www.linkedin.com/in/angel-w-miller/)
