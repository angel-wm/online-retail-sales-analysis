# Data preparation and limitations

The model transforms the unchanged [UCI source workbook](../data/raw/Online%20Retail.xlsx) into a merchandise-focused report while retaining administrative and other movements for reconciliation. The implemented Power Query steps are in [Online Retail.tmdl](../powerbi/uk-online-retail-sales-analysis.SemanticModel/definition/tables/Online%20Retail.tmdl).

This page explains preparation decisions. Exact field and classification rules live in the [data dictionary](../data/data-dictionary.md); metric meanings and numerical interpretation live in [Metrics](METRICS.md).

## Preserve the source and repeated lines

The workbook contains 541,909 transaction lines. It is not rewritten by configuration or validation scripts. The recovered model's null-description rule excludes 1,454 lines, leaving 540,455 loaded lines. Their combined rounded amount is zero; this is a documented exclusion, not evidence that missing descriptions are harmless in every dataset.

The source has 5,268 excess exact duplicate rows across its eight raw fields. They are retained because there is no source line identifier establishing whether they are accidental duplicates or repeated entries. Deduplicating them would change counts and amounts. No additional exclusion, winsorization or outlier removal is applied to improve the appearance of a chart.

[coverage.json](../evidence/financial/coverage.json) records row counts, exclusions, repetitions and economic categories. The retained [raw profile](../evidence/baseline/raw_profile.json) describes the original workbook, rather than the loaded fact population.

## Prepare types and classifications

The transformation sequence is:

1. Read the **Online Retail** sheet, promote headers and rename the eight source columns.
2. Apply explicit types using the `en-GB` culture. Invoice, stock and customer identifiers become text; quantity becomes a whole number; timestamp and price retain their appropriate types.
3. Exclude null descriptions and normalize stock codes by trimming and uppercasing. Keep each original fact description.
4. Derive line type, invoice day, record-quality flag, cancellation flag, negative-quantity flag and zero-price flag.
5. Multiply quantity by the original unit price and half-even round the line amount to two decimals. Store the result as Currency.
6. Derive separate eligible-sale and eligible-reversal flags, then assign the reconciliation movement category.

The [classification reference](../data/data-dictionary.md#classification-rules) defines the order and explicit code list. `AMAZONFEE` and `AMAZON FEE` are administrative. A code containing letters does not by itself justify removing it from merchandise.

Keeping sale and reversal populations separate ensures a negative merchandise line is counted once. Administrative adjustments and gift vouchers remain available in the loaded table and signed reconciliation measures; exclusion from merchandise KPIs does not mean deletion from the source.

## Preserve price precision

Unit prices retain their source precision before multiplication, including the `PADS` price of `0.001`. Rounding that price to two decimals first would destroy the line's value. Line-level rounding uses `RoundingMode.ToEven`; ratios use the resulting totals without premature percentage rounding. [Precision in the metric reference](METRICS.md#precision) distinguishes calculation, native type and display format.

## Handle unknown customers without inventing buyers

There are 135,080 raw lines with missing customer IDs. Eligible anonymous merchandise activity remains in sales and reversal totals. Known-customer counts and rankings exclude blank IDs; the model does not fabricate one shared buyer or a count of distinct anonymous buyers.

The coverage cards expose the resulting gap using unidentified net sales and the share of gross sales with known IDs. Their numerators differ, as explained in [Customer coverage](METRICS.md#customer-coverage).

## Keep product identity stable

Descriptions can vary within one stock code, or match across different codes. The dimension therefore groups by stock code and chooses a deterministic representative source description, retaining the original fact descriptions and a variant count. See [Product identity](MODEL.md#product-identity) for the algorithm and its limits.

## Respect what the data can establish

The cancellation prefix and negative quantities support an analysis of recorded reversals. They do not establish physical returned goods, delivery status, customer dissatisfaction, a reversal reason or a reliable link to the original invoice. Administrative amounts are not treated as recognized profit or expenses.

The source dates do not form complete 2010 and 2011 calendar years. December 2011 ends on the ninth; its monthly total remains a partial-month observation. No projection or zero-fill beyond the source boundary is applied. Read [Period coverage](METRICS.md#period-coverage) before interpreting the final monthly drop.

## Verification

The [source reconciliation](../evidence/financial/before_after.json) reconstructs the original and current rules in integer pennies. A second reader parses the XLSX XML independently and checks selected totals. Native DAX checks then compare the model against reconstructed values under multiple contexts, with explicit handling of Currency and BLANK.

These are distinct checks. A source reconstruction does not execute Power Query or render a visual. Their results, dated Desktop observations and remaining acceptance scope are recorded in [Validation](VALIDATION.md).
