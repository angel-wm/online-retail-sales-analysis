# Metrics and interpretation

The report distinguishes eligible merchandise activity from administrative and other movements. Amounts are in **GBP (£)**, the original source currency; no currency conversion is applied.

The definitions below describe the current model. Exact DAX expressions and formats live in [Online Retail.tmdl](../powerbi/uk-online-retail-sales-analysis.SemanticModel/definition/tables/Online%20Retail.tmdl), with a machine-readable contract in [measure_definitions.json](../evidence/financial/measure_definitions.json). Field-level eligibility rules have one reference in the [data dictionary](../data/data-dictionary.md#eligibility-flags).

## Merchandise values

| Model measure | Meaning in the selected context |
| --- | --- |
| `Main Sales` | Gross value of eligible positive merchandise lines. |
| `Returns Amount` | Positive magnitude of eligible negative merchandise lines, counted once. |
| `Return Value` | Alias of `Returns Amount`, preserving the original measure name. |
| `Net Sales` | Gross merchandise value less merchandise reversal value. |
| `Administrative Adjustments` | Signed value of administrative and special-code lines. This is not a profit or expense measure. |
| `Other Movements` | Signed gift-voucher and residual excluded movements. |
| `Total Sales` | Signed value of all loaded lines; used to reconcile the whole source. |

The financial bridge is:

```text
Net Sales + Administrative Adjustments + Other Movements = Total Sales
```

A cancellation prefix and a negative quantity describe the same recorded line in different ways. The model subtracts an eligible negative line once. The source does not link it reliably to a delivered item, a physical return, the original sale or a reason for reversal.

## Counts and ratios

| Model measure | Definition |
| --- | --- |
| `Orders` | Distinct invoices with at least one eligible positive merchandise line. |
| `Unique Customers` | Distinct nonblank customer IDs on eligible sales. |
| `Units Sold` | Quantity on eligible positive merchandise lines. |
| `Units Reversed` | Positive magnitude of quantity on eligible negative merchandise lines. |
| `Cancelled Orders` | Distinct invoices with eligible negative merchandise lines. All such invoices in this source have the `C` prefix. |
| `Average Order Value` | `Net Sales / Orders`: net value per sale invoice in the posting period. |
| `Return rate` | `Returns Amount / Main Sales`: reversal value relative to gross sales in the posting period. |
| `Zero Price Records` | Loaded lines with zero unit price, across all line types. |

Invoice and customer counts are distinct counts in the current context. Adding product or country counts can count the same invoice or customer more than once. AOV is a period ratio, because reversals are dated when posted and are not matched to original sale invoices. The reversal ratio is a value ratio, not the probability of a physical return; it can exceed 100% in a narrow period or selection.

## Customer coverage

| Model measure | Definition |
| --- | --- |
| `Unidentified Net Sales` | Net merchandise value on lines with a blank customer ID. |
| `Identified Sales Share` | Gross eligible sales with a nonblank customer ID divided by all gross eligible sales. |

Anonymous sales remain in commercial totals. They are excluded from known-customer counts and rankings because the source cannot identify distinct anonymous buyers. The coverage percentage uses **gross** sales; the unidentified value card uses **net** sales. They are not complementary parts of the same numerator.

## Precision

Each line amount uses the full source unit price, multiplies by quantity, then rounds to two decimal places with half-even rounding. The result is stored as Currency. Unit prices are not rounded before multiplication; the source includes values such as `0.001`.

AOV no longer rounds to multiples of two, and the reversal and coverage ratios no longer round their inputs prematurely. Display formats show two currency decimals or percentage decimals. Native Currency has four decimal places, so the checked global AOV is `495.2507` and displays as `£495.25`; the source reconstruction retains the mathematical quotient `495.25067668…`. Ratios retain Double precision. See [Microsoft's fixed decimal type documentation](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-data-types#fixed-decimal-number).

## Filters and blank values

Measure eligibility intersects the current Year, Country, Line Type, product, customer and invoice filters through `KEEPFILTERS`. Selecting Adjustment or Gift Voucher does not silently replace that choice with Product lines.

A missing eligible population or denominator can return **BLANK**, rather than an invented zero. If both gross sales and reversals are blank, net sales is blank. A reversal-only context can have negative net sales with blank AOV and reversal ratio. A selection with only anonymous sales has blank `Unique Customers`.

The scatter's log axis requires positive reversal values. Products with blank reversal measures can disappear under a filter; the displayed point count need not remain 30. No blank measure was replaced with zero, and no outlier was removed to spread the points.

## Reference values

These values cover all source dates and countries with no external selection. They are reconstructed from the unchanged Excel source and checked against native DAX; provenance and comparison policy are in [Validation](VALIDATION.md#recorded-desktop-checks).

| Metric | Value |
| --- | ---: |
| Gross eligible merchandise sales | £10,271,315.81 |
| Merchandise reversals | £478,724.18 |
| Net merchandise sales | £9,792,591.63 |
| Administrative adjustments | −£45,646.76 |
| Other movements | £803.06 |
| All signed movements | £9,747,747.93 |
| Sale invoices | 19,773 |
| Known customers | 4,334 |
| Net value per sale invoice, displayed | £495.25 |
| Reversal value / gross sales, displayed | 4.66% |
| Unidentified net merchandise sales | £1,505,928.31 |
| Gross sales with known customer IDs, displayed | 85.30% |

The [financial reconciliation](../evidence/financial/RECONCILIATION.md) explains the original-to-current differences. The CSV and JSON evidence retain the full before/after comparison, monthly totals, country totals, special-code review and product identity.

## Period coverage

The source spans **1 December 2010 at 08:26 through 9 December 2011 at 12:50**. The Calendar has 374 continuous dates; its boundaries are source boundaries, not full calendar years. There are 13 monthly points.

November 2011 has £1,432,734.99 net sales over its full 30-day calendar span. December has £441,366.51 through day 9. The apparent monthly fall of 69.19% compares unequal coverage and does not establish a collapse over a complete month.

For the first nine calendar days of each month, source totals are £435,185.39 in November and £441,366.51 in December, a descriptive increase of 1.42%. December still stops at 12:50 on the ninth. This comparison has no seasonal adjustment or extrapolation. [The monthly check](../evidence/validation/monthly-chart-check.json) records the Excel, native DAX and chart-binding agreement.

Read [Cleaning notes](cleaning-notes.md) for preparation decisions and [Model](MODEL.md) for relationships and ranking identity.
