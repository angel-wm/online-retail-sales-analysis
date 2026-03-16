# Data Dictionary

## Overview

This Power BI model is built around two main tables:

- **Online Retail**: transactional fact table containing invoice, product, customer, quantity, and pricing data.
- **Calendar**: date dimension table created from the minimum and maximum values of `Online Retail[Invoice_Day]`.

The model also includes a set of business measures grouped under a **Measures** display folder.

---

## Table: `Calendar`

### Purpose
Date dimension used for time-based analysis, filtering, sorting, and monthly trend reporting.

| Field | Data Type | Description | Business / Technical Notes |
|---|---|---|---|
| `Date` | Date | Base calendar date. | Primary date field of the calendar table. |
| `Year` | Whole Number | Calendar year extracted from `Date`. | Used for yearly aggregation. |
| `Trimester` | Text | Quarter label in the format `T1`, `T2`, `T3`, `T4`. | Built from the quarter number of `Date`. |
| `Month#` | Whole Number | Numeric month from 1 to 12. | Used for chronological sorting. |
| `Month` | Text | Full month name. | Example: January, February. |
| `Month_short` | Text | Abbreviated month name. | Example: Jan, Feb. |
| `Year_Month` | Text | Year-month key in `YYYY-MM` format. | Useful for compact monthly grouping. |
| `YearMonthSort` | Whole Number | Sort key built as `Year * 100 + Month#`. | Ensures correct chronological sorting of month labels. |
| `YearMonth_Label` | Text | Friendly month-year label in `MMM yyyy` format. | Example: Jan 2011. Typically used on chart axes. |
| `Day` | Whole Number | Day of month extracted from `Date`. | Values from 1 to 31. |
| `Weekday#` | Whole Number | Weekday number with Monday = 1. | Useful for weekday ordering. |
| `Weekday` | Text | Full weekday name. | Example: Monday, Tuesday. |

### Notes
- The `Calendar` table is generated using:
  - `MIN('Online Retail'[Invoice_Day])`
  - `MAX('Online Retail'[Invoice_Day])`
- `YearMonth_Label` should be sorted by `YearMonthSort`.
- `Month` or `Month_short` should be sorted by `Month#`.

---

## Table: `Online Retail`

### Purpose
Main transactional table containing invoice-level retail data used for sales, orders, customer, and return analysis.

| Field | Data Type | Description | Business / Technical Notes |
|---|---|---|---|
| `Invoice_ID` | Text | Unique invoice identifier. | Cancelled invoices are identified when the invoice code starts with `C`. |
| `Invoice_Date` | Date/Time | Original invoice timestamp. | Raw transaction date-time field. |
| `Invoice_Day` | Date | Date-only version of the invoice date. | Used to build the `Calendar` table and likely to relate transactions to dates. |
| `Customer_ID` | Text / Whole Number | Customer identifier. | Can contain blank values. Distinct customer analysis excludes blanks in the main customer measure. |
| `Country` | Text | Customer or transaction country. | Used for geographic sales and return analysis. |
| `Stock_Code` | Text | Product or transaction code. | Used to classify rows into product, gift voucher, or adjustment. |
| `Product_Name` | Text | Product description/name. | Also used in record classification logic. |
| `Quantity` | Whole Number | Number of units in the transaction line. | Negative values represent return-like rows. |
| `Unit_Price` | Decimal Number | Unit price of the transaction line. | Zero values are flagged separately. |
| `Sales_Amount` | Decimal Number | Calculated line amount as `Quantity * Unit_Price`. | Rounded to 2 decimals. Can be negative for returned items. |
| `Line_Type` | Text | Business classification of the transaction line. | Possible values: `Product`, `Gift Voucher`, `Adjustment`. |
| `Record_Flag` | Text | Data quality / business rule classification of the row. | Possible values: `Normal`, `Manual / Review`, `Operational / Non-Product`. |
| `Is_Cancelled` | TRUE/FALSE | Indicates whether the invoice was cancelled. | `TRUE` when `Invoice_ID` starts with `C`. |
| `Is_Negative_Qty` | TRUE/FALSE | Flags rows where quantity is negative. | Used to identify return-related transactions. |
| `Is_Zero_Price` | TRUE/FALSE | Flags rows where unit price equals zero. | Used for quality checks and exclusion from main analysis. |
| `Include_In_Main_Analysis` | TRUE/FALSE | Final inclusion flag for core KPIs. | Only rows meeting all main-analysis rules are included. |

---

## Business Rules for Calculated Columns

### `Line_Type`
Classifies each row into one of three categories:

- **Gift Voucher**
  - `Stock_Code` starts with `GIFT_`, or
  - `Product_Name` contains `GIFT VOUCHER`

- **Adjustment**
  - `Stock_Code` is one of: `M`, `S`, `POST`, `AMAZON FEE`, `BANK CHARGES`, `D`, `DOT`, `C2`, `B`, `CRUK`, or
  - `Product_Name` equals `EBAY`

- **Product**
  - Any row not classified as Gift Voucher or Adjustment

### `Record_Flag`
Classifies records according to data quality / operational patterns:

- **Manual / Review**
  - `Product_Name` starts with `*`
  - and there is no `Customer_ID`

- **Operational / Non-Product**
  - no `Customer_ID`
  - and `Product_Name` contains operational markers such as:
    - `?`
    - `MISSING`
    - `LOST`
    - `DAMAGE`
    - `DISPLAY`
    - `SOLD AS SETS`
  - and `Unit_Price` is null or 0

- **Normal**
  - all other rows

### `Include_In_Main_Analysis`
A row is included in the main business analysis only when all of the following are true:

- `Line_Type = "Product"`
- `Record_Flag = "Normal"`
- `Is_Cancelled = FALSE`
- `Is_Negative_Qty = FALSE`
- `Is_Zero_Price = FALSE`

This flag is the core filter behind the main sales KPIs.

---

## Measures

### Purpose
These measures summarize performance for sales, orders, customers, returns, and data quality tracking.

| Measure | Format | Description | Logic Summary |
|---|---|---|---|
| `Total Sales` | Currency / Decimal | Total sales amount across all rows. | Sum of `Sales_Amount`, rounded to 2 decimals. |
| `Main Sales` | Currency / Decimal | Sales from valid core business transactions only. | `Total Sales` filtered by `Include_In_Main_Analysis = TRUE()`. |
| `Returns Amount` | Currency / Decimal | Absolute value of returned sales. | Absolute value of `Total Sales` for rows with `Is_Negative_Qty = TRUE()`. |
| `Net Sales` | Currency / Decimal | Main sales minus returns. | `Main Sales - Returns Amount`. |
| `Orders` | Whole Number | Distinct order count for valid business transactions. | Distinct count of `Invoice_ID` where `Include_In_Main_Analysis = TRUE()`. |
| `Cancelled Orders` | Whole Number | Distinct count of cancelled orders. | Distinct count of `Invoice_ID` where `Is_Cancelled = TRUE()`. |
| `Units Sold` | Whole Number | Total quantity sold in the main analysis scope. | Sum of `Quantity` where `Include_In_Main_Analysis = TRUE()`. |
| `Unique Customers` | Whole Number | Distinct customer count in the main analysis scope. | Distinct count of non-blank `Customer_ID` where `Include_In_Main_Analysis = TRUE()`. |
| `Average Order Value` | Currency / Decimal | Average value per valid order. | `Net Sales / Orders`, rounded using `MROUND(..., 2)`. |
| `Return rate` | Percentage | Share of returns relative to main sales. | `Returns Amount / Main Sales`, rounded to 2 decimals. |
| `Return Value` | Currency / Decimal | Absolute value of returned product lines. | Sum of absolute `Sales_Amount` where `Is_Negative_Qty = TRUE()` and `Line_Type = "Product"`. |
| `Zero Price Records` | Whole Number | Count of rows with zero unit price. | Count of rows where `Is_Zero_Price = TRUE()`. |

---

## KPI Interpretation Notes

| Metric | Interpretation |
|---|---|
| `Main Sales` | Best measure for clean commercial sales analysis because it excludes cancelled, negative, zero-price, non-normal, and non-product rows. |
| `Net Sales` | More conservative measure of realized sales because it subtracts returns from main sales. |
| `Orders` | Counts only valid orders included in the main analysis logic. |
| `Cancelled Orders` | Useful for operational monitoring and order-quality review. |
| `Return rate` | Indicates how much returned value exists relative to clean sales. |
| `Zero Price Records` | Data quality signal that helps identify free items, bad records, or unusual operational transactions. |

---

## Recommended Formatting / Modeling Notes

- Sort `Month` and `Month_short` by `Month#`.
- Sort `YearMonth_Label` by `YearMonthSort`.
- Use `Invoice_Day` as the transaction date key for time intelligence.
- Use `Include_In_Main_Analysis` as the standard filter for executive KPIs.
- Use `Return Value` or `Returns Amount` for return-focused visuals, depending on whether the analysis is product-only or broader sales-impact oriented.

---

## Naming Notes

This dictionary documents the model using the final field names shown in Power BI:

- `Line_Type`
- `Record_Flag`
- `Is_Cancelled`
- `Is_Negative_Qty`
- `Is_Zero_Price`
- `Include_In_Main_Analysis`

Some uploaded formulas used lowercase or slightly different spellings, but this document standardizes names to match the model view.
