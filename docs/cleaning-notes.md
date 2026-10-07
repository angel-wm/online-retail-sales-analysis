# Data Cleaning Notes

## Objective

The documented data preparation turns raw UK online retail transaction lines into a model suitable for sales,
customer, and returns analysis in Power BI. The source includes cancellations, returns, missing customer
identifiers, and non-product records; not every row should contribute to every KPI.

This document explains the **decisions and assumptions** behind cleaning. For exact recorded fields and inclusion
criteria, use the [Data Dictionary](../data/data-dictionary.md). The
[original Excel dataset](../data/raw/Online%20Retail.xlsx) is committed, but the
[Power BI file](../powerbi/online-retail-sales-analysis%20.pbix) is a two-byte placeholder. Consequently, these
notes are not a runnable Power Query script or independent verification of the report's transformations.

## Main Data Quality Issues Identified

| Source condition | Why it matters for reporting |
| --- | --- |
| Cancelled invoices | Must be distinguished from ordinary completed transactions |
| Negative quantities | Represent returns or reverse movements under the documented assumptions |
| Missing customer IDs | Can affect customer counts and rankings without necessarily invalidating transaction-level sales |
| Non-product and special-code rows | Should not automatically count as normal product sales |
| Inconsistent business record types | Require classification and inclusion rules |
| Transaction dates | Need a separate calendar dimension for time-based reporting |

## Cleaning and Preparation Steps

The order below describes the project's recorded preparation decisions. It is not a reproducible sequence of Power
Query commands.

### 1. Standardized data types

Column types were reviewed for invoice/order ID, product code and description, quantity, unit price, customer ID,
country, and transaction date so fields could support modeling and calculations. Their recorded final names and
types are in the [field reference](../data/data-dictionary.md#table-online-retail).

### 2. Identified cancelled invoices

Cancelled transactions were flagged separately from regular sales activity. The recorded `Is_Cancelled` rule
identifies invoice IDs beginning with `C`. Keeping this distinction makes it possible to evaluate cancellations
without treating them as normal completed sales.

### 3. Flagged returned transactions

Negative quantities were marked for returns-related analysis. This supports comparisons between sales and returned
value, as well as product-level returns; the [measures reference](../data/data-dictionary.md#measures)
distinguishes `Returns Amount` from the product-only `Return Value`.

### 4. Classified line types

Transaction lines were classified as **Product**, **Gift Voucher**, or **Adjustment**. This separates merchandise
from special or administrative transactions and supports the **Line Type** report filter.

The exact stock-code and description rules belong in the
[`Line_Type` reference](../data/data-dictionary.md#business-rules-for-calculated-columns), rather than being
maintained in two places.

### 5. Reviewed missing values

Missing `Customer_ID` values matter for customer rankings and customer-based KPIs. Such rows may still contribute
to transaction-level sales analysis where other inclusion criteria permit it; an unknown customer should not be
counted as a known unique customer.

### 6. Created business logic flags

The recorded model distinguishes cancellation status, negative quantity, zero price, line type, record quality,
and inclusion in the main analysis. In particular, `Record_Flag` separates **Normal**, **Manual / Review**, and
**Operational / Non-Product** cases.

For the complete field definitions and combination of rules behind `Include_In_Main_Analysis`, see
[Business Rules for Calculated Columns](../data/data-dictionary.md#business-rules-for-calculated-columns).

### 7. Built a calendar table

The documented **Calendar** table uses the minimum and maximum `Online Retail[Invoice_Day]` dates. Year and month
fields support time trends, chronological sorting, and report filtering.

See the [calendar reference](../data/data-dictionary.md#table-calendar) for the recorded fields and sort keys.

### 8. Prepared fields for reporting

Preparation supports the documented measures: total and main sales, net sales, orders, unique customers, average
order value, return value, and return rate. Their calculation summaries live in the
[measure reference](../data/data-dictionary.md#measures).

## Data Modeling Notes

The documented model has an **Online Retail** transactional table and a **Calendar** date dimension. This
structure was intended for time-trend analysis, KPI reporting, and yearly filtering.

The underlying relationship settings and DAX formulas cannot currently be inspected through the committed
placeholder PBIX. The [Data Dictionary](../data/data-dictionary.md) describes the intended model; it should not be
mistaken for an export from a valid report file.

## Assumptions Used

- Negative-quantity transactions represent returns or reverse movements.
- Cancelled invoices are identified separately from regular completed sales.
- Missing customer identifiers limit customer-level analysis.
- Special-code or non-product rows should not automatically be counted as normal product sales.
- A separate calendar table supports time-based reporting in the documented Power BI model.

These are the analytical assumptions recorded for this project, not independently established characteristics of
every possible retail dataset.

## Reporting Impact

The cleaning decisions aim to improve KPI consistency, sales-versus-returns comparisons, customer analysis, filter
usability, and monthly trend reporting.

Whether the original report implements each rule exactly cannot be verified with the available PBIX. For the
preserved dashboard appearance, see the [English README](../README.md#dashboard-preview) or
[Spanish README](../README.es.md#vista-previa-del-dashboard).
