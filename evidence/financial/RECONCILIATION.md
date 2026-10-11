# Financial reconciliation

This evidence compares reconstructed original calculations with the current merchandise scope, using the unchanged Excel source, all dates and countries, and no external selection. Amounts are GBP. The reconstruction does not execute DAX or Power Query; native comparisons have a separate record in [Validation](../../docs/VALIDATION.md#recorded-desktop-checks).

## Key original-to-current differences

| Measure | Original | Current |
| --- | ---: | ---: |
| Main Sales | £10,285,076.90 | £10,271,315.81 |
| Returns Amount | £896,812.49 | £478,724.18 |
| Return Value | £714,005.77 | £478,724.18 |
| Net Sales | £9,388,264.41 | £9,792,591.63 |
| Orders | 19,775 | 19,773 |
| Average Order Value, displayed | £474.00 | £495.25 |
| Return rate, displayed | 9.00% | 4.66% |
| Total Sales | £9,747,747.93 | £9,747,747.93 |

The [full CSV comparison](before_after.csv) and [JSON comparison](before_after.json) retain all reconstructed values, absolute changes, relative changes and percentage-point changes. [The metric reference](../../docs/METRICS.md) defines the current business scope and interpretation.

## Why the values changed

Two positive `AMAZONFEE` commission lines are administrative, reducing gross merchandise sales by £13,761.09 and sale-invoice count by two. Merchandise reversal value excludes £418,088.31 of administrative negatives, including £235,281.59 previously classified as product under `AMAZONFEE`.

Using the same merchandise scope for gross sales and reversals increases net merchandise value by £404,327.22. The signed value of all loaded movements remains unchanged. Net merchandise value plus administrative adjustments and other movements reconciles to that total; [the current reference values](../../docs/METRICS.md#reference-values) show the components.

The original AOV calculation rounded to multiples of two. Its unrounded quotient was £474.75420531; its implemented result was £474. The current source quotient is £495.25067668… and the native Currency value is £495.2507, displayed as £495.25.

The original reversal ratio before rounding was 8.71955065%; the implemented original ratio was 9.000000%. The current source ratio is 4.66078727%, a decrease of 4.33921273 percentage points against that implemented value. This combines the corrected merchandise scope and removal of premature ratio rounding.

## Supporting files

| Evidence | Contents |
| --- | --- |
| [coverage.json](coverage.json) | Row population, exclusions, repetitions and economic categories. |
| [monthly.csv](monthly.csv) | Current monthly values and original net comparison. |
| [countries.json](countries.json) | Current metrics by country. |
| [special_codes.json](special_codes.json) | Source descriptions, classifications and signed values for special codes. |
| [product_identity.csv](product_identity.csv) | Unique stock-code labels and description variant counts. |
| [measure_definitions.json](measure_definitions.json) | Exact current measure expressions, descriptions and display formats. |

Reproduce the values with the [source/static validation procedure](../../docs/VALIDATION.md#run-source-and-static-checks). The [preparation notes](../../docs/cleaning-notes.md) explain retained duplicates, missing descriptions and unknown customers.
