# Data dictionary

This reference describes the current editable model, verified by its [TMDL parser output](../evidence/validation/final-tom.json). For business meanings and reference totals, use [Metrics](../docs/METRICS.md); for table relationships and product identity, use [Model](../docs/MODEL.md).

## Source fields

The workbook's **Online Retail** sheet contains the following eight fields. The [original workbook](raw/Online%20Retail.xlsx) is preserved without edits; renaming and derived columns occur in Power Query.

| Source field → model field | Meaning |
| --- | --- |
| `InvoiceNo` → `Invoice_ID` | Invoice identifier; multiple lines can share one invoice. |
| `StockCode` → `Stock_Code` | Stock or transaction code. |
| `Description` → `Product_Name` | Original line description. |
| `Quantity` → `Quantity` | Signed unit quantity. |
| `InvoiceDate` → `Invoice_Date` | Original transaction timestamp. |
| `UnitPrice` → `Unit_Price` | GBP unit price, with original precision. |
| `CustomerID` → `Customer_ID` | Customer identifier; blank values occur. |
| `Country` → `Country` | Country recorded on the transaction. |

## Table: Online Retail

The fact table holds loaded invoice lines. Stock code and original product name are hidden from the report field list in favor of `DimProduct`; hidden fields remain available for diagnostics and calculations.

| Field | Model type and role |
| --- | --- |
| `Invoice_ID` | Text; distinct-invoice key for counts. |
| `Stock_Code` | Text; trimmed, uppercased relationship key to `DimProduct`. |
| `Product_Name` | Text; original source description, not replaced by the dimension label. |
| `Quantity` | Whole number; signed quantity on the line. |
| `Invoice_Date` | Date/time; original timestamp. |
| `Invoice_Day` | Date represented as DateTime; date-only key to Calendar. |
| `Unit_Price` | Decimal number (Double); original price precision. |
| `Customer_ID` | Text; identifiers are not treated as quantities. |
| `Country` | Text; country filter and grouping field. |
| `Sales_Amount` | Fixed decimal (Currency); signed quantity × full-precision price, half-even rounded to two decimals. |
| `Line_Type` | Text; Product, Gift Voucher or Adjustment. |
| `Record_Flag` | Text; Normal, Manual / Review or Operational / Non-Product. |
| `Is_Cancelled` | Boolean; trimmed, uppercased invoice ID begins with `C`. |
| `Is_Negative_Qty` | Boolean; nonnull quantity is below zero. |
| `Is_Zero_Price` | Boolean; nonnull unit price equals zero. |
| `Include_In_Main_Analysis` | Boolean; eligible positive merchandise sale. |
| `Is_Merchandise_Reversal` | Boolean; eligible negative merchandise movement. |
| `Movement_Type` | Text; mutually exclusive economic category for reconciliation. |

## Classification rules

### Line type

Classification uses trimmed, uppercased stock code and description, in this order:

1. **Gift Voucher:** the code starts with `GIFT_` or the description contains `GIFT VOUCHER`.
2. **Adjustment:** the code is in the explicit list below, or the normalized description equals `EBAY`.
3. **Product:** all remaining lines.

```text
M, S, POST, AMAZONFEE, AMAZON FEE, BANK CHARGES, D, DOT, C2, B, CRUK
```

Alphabetic codes alone do not imply administrative activity. Codes such as `PADS`, `DCGS`, `DCGSSBOY` and `DCGSSGIRL` follow the same explicit rules. [special_codes.json](../evidence/financial/special_codes.json) records their source descriptions and classifications.

### Record flag

`Record_Flag` uses the normalized description and whether the customer ID is null or empty, in this order:

1. **Manual / Review:** the description starts with `*` and the customer ID is absent.
2. **Operational / Non-Product:** the customer ID is absent, unit price is null or zero, and the description contains `?`, `MISSING`, `LOST`, `DAMAGE`, `DISPLAY` or `SOLD AS SETS`.
3. **Normal:** all remaining lines.

### Eligibility flags

| Flag | Required conditions |
| --- | --- |
| `Include_In_Main_Analysis` | Line type Product; record flag Normal; invoice not cancelled; quantity > 0; unit price > 0. |
| `Is_Merchandise_Reversal` | Line type Product; record flag Normal; quantity < 0; unit price > 0. |

The reversal flag uses the signed quantity and price. The cancellation prefix remains a diagnostic; it is not subtracted as a separate second charge. Zero-price and nonnormal lines cannot enter either eligible merchandise population.

### Movement type

The first matching category determines `Movement_Type`:

| Category | Condition |
| --- | --- |
| `Merchandise sale` | Eligible positive merchandise flag is true. |
| `Merchandise cancellation / reversal` | Eligible reversal flag is true. |
| `Administrative adjustment` | Line type is Adjustment. |
| `Gift voucher movement` | Line type is Gift Voucher. |
| `Other / excluded movement` | Any remaining loaded line. |

## Table: Calendar

The calculated date dimension spans the minimum and maximum loaded `Invoice_Day`. Sort keys are part of the current implementation.

| Field | Meaning and sorting |
| --- | --- |
| `Date` | Date key; one row for every day in the source span. |
| `Year` | Calendar year, whole number. |
| `Trimester` | Quarter label `T1`–`T4`. |
| `Month#` | Month number 1–12. |
| `Month` | Full month name; sorted by `Month#`. |
| `Month_short` | Abbreviated month name; sorted by `Month#`. |
| `Year_Month` | `YYYY-MM` label; sorted by `YearMonthSort`. |
| `YearMonthSort` | Whole-number key `Year * 100 + Month#`. |
| `YearMonth_Label` | `MMM yyyy` label; sorted by `YearMonthSort`, used on monthly chart axes. |
| `Day` | Day of month 1–31. |
| `Weekday#` | Weekday number, Monday = 1. |
| `Weekday` | Full weekday name; sorted by `Weekday#`. |

## Table: DimProduct

| Field | Type and role |
| --- | --- |
| `Stock_Code` | Text; unique dimension key. |
| `Product_Name` | Text; representative normalized source description. |
| `Product_Label` | Text; stock code and representative description, separated by an em dash. |
| `Description_Variants` | Whole number; distinct normalized descriptions in loaded lines for that code. |

The label-selection algorithm and its limitations belong in [Product identity](../docs/MODEL.md#product-identity). The dimension covers all loaded stock codes, including codes whose lines are excluded from merchandise KPIs.

## Measures

All 17 measures live on `Online Retail`, under the Measures display folder. The [metric reference](../docs/METRICS.md) defines their commercial scope, counts, ratios, blank behavior and interpretation. [measure_definitions.json](../evidence/financial/measure_definitions.json) contains the exact expression and format contract used by the model validator.

Monetary measures display GBP with two decimals; unit, invoice, customer and record counts use whole-number formats; the two ratio measures display percentages. Formatting does not change the underlying calculation. Hidden automatic date tables and their preserved relationship are described in [Model](../docs/MODEL.md#main-tables-and-filter-paths).
