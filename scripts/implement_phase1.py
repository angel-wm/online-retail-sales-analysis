"""One-time, scoped migration of the recovered financial definitions."""
from pathlib import Path
import json
import re
import uuid

REPO = Path(__file__).resolve().parents[1]
MODEL = REPO / "powerbi/project/uk-online-retail-sales-analysis.SemanticModel/definition"
path = MODEL / "tables/Online Retail.tmdl"
s = path.read_text(encoding="utf-8-sig")
gbp = "£#,0.00;(£#,0.00);£0.00"
definitions = {
    "Total Sales": ("SUM('Online Retail'[Sales_Amount])", "Signed total of all loaded movements in the current filter context. Reconciliation measure; GBP.", gbp),
    "Main Sales": ("CALCULATE([Total Sales], KEEPFILTERS('Online Retail'[Include_In_Main_Analysis] = TRUE()))", "Gross eligible merchandise sales. Product, Normal, quantity and price positive, invoice not cancelled; GBP.", gbp),
    "Returns Amount": ("-CALCULATE([Total Sales], KEEPFILTERS('Online Retail'[Is_Merchandise_Reversal] = TRUE()))", "Magnitude of negative eligible merchandise movements, counted once. Cancellation/reversal proxy, not proof of physical returns; GBP.", gbp),
    "Return Value": ("[Returns Amount]", "Compatibility alias for Returns Amount. Same merchandise scope in every visual; GBP.", gbp),
    "Net Sales": ("VAR Gross = [Main Sales]\nVAR Reversals = [Returns Amount]\nRETURN\n    IF(ISBLANK(Gross) && ISBLANK(Reversals), BLANK(), COALESCE(Gross, 0) - COALESCE(Reversals, 0))", "Gross eligible merchandise sales less merchandise cancellations/reversals. Administrative adjustments and other movements excluded; GBP.", gbp),
    "Orders": ("CALCULATE(DISTINCTCOUNTNOBLANK('Online Retail'[Invoice_ID]), KEEPFILTERS('Online Retail'[Include_In_Main_Analysis] = TRUE()))", "Distinct invoices with at least one eligible positive merchandise line. Cancellation invoices excluded. Counts are not additive across products/countries.", "#,0"),
    "Unique Customers": ("CALCULATE(DISTINCTCOUNTNOBLANK('Online Retail'[Customer_ID]), KEEPFILTERS('Online Retail'[Include_In_Main_Analysis] = TRUE()))", "Distinct identified customers with eligible merchandise sales in the current context. Anonymous buyers cannot be counted.", "#,0"),
    "Average Order Value": ("DIVIDE([Net Sales], [Orders])", "Net merchandise value per eligible sale invoice in the selected period. Reversals are dated at posting, not matched to original orders. Not a physical basket average; GBP.", gbp),
    "Return rate": ("DIVIDE([Returns Amount], [Main Sales])", "Merchandise cancellation/reversal amount divided by gross eligible merchandise sales in the selected period. Posting-period value ratio, not physical return probability; blank if denominator absent.", "0.00%;-0.00%;0.00%"),
    "Units Sold": ("CALCULATE(SUM('Online Retail'[Quantity]), KEEPFILTERS('Online Retail'[Include_In_Main_Analysis] = TRUE()))", "Positive eligible merchandise units. Administrative/gift voucher quantities excluded.", "#,0"),
    "Cancelled Orders": ("CALCULATE(DISTINCTCOUNTNOBLANK('Online Retail'[Invoice_ID]), KEEPFILTERS('Online Retail'[Is_Merchandise_Reversal] = TRUE()))", "Distinct invoices containing eligible negative merchandise movements. All such invoices in this source have prefix C; no claim of physical returns or original-order linkage.", "#,0"),
    "Zero Price Records": ("CALCULATE(COUNTROWS('Online Retail'), KEEPFILTERS('Online Retail'[Is_Zero_Price] = TRUE()))", "Loaded lines with zero unit price. Quality diagnostic across all line types, respecting current filters.", "#,0"),
    "Administrative Adjustments": ("CALCULATE([Total Sales], KEEPFILTERS('Online Retail'[Line_Type] = \"Adjustment\"))", "Signed administrative and special-code movements, including commissions, postage, discounts, manual adjustments, samples and bad debt. Not recognized profit or operating expenses; GBP.", gbp),
    "Other Movements": ("CALCULATE([Total Sales], KEEPFILTERS('Online Retail'[Movement_Type] IN {\"Gift voucher movement\", \"Other / excluded movement\"}))", "Signed gift voucher and residual excluded movements. Completes the bridge Net Sales + Administrative Adjustments + Other Movements = Total Sales; GBP.", gbp),
    "Units Reversed": ("-CALCULATE(SUM('Online Retail'[Quantity]), KEEPFILTERS('Online Retail'[Is_Merchandise_Reversal] = TRUE()))", "Magnitude of merchandise units on negative cancellation/reversal lines. Not verified physical returned units.", "#,0"),
    "Unidentified Net Sales": ("CALCULATE([Net Sales], KEEPFILTERS(ISBLANK('Online Retail'[Customer_ID])))", "Net merchandise value where customer ID is blank. Included in commercial totals but not identified-customer rankings; GBP.", gbp),
    "Identified Sales Share": ("DIVIDE(CALCULATE([Main Sales], KEEPFILTERS(NOT(ISBLANK('Online Retail'[Customer_ID])))), [Main Sales])", "Share of gross eligible merchandise sales with a known customer ID in the current context. Financial coverage, not share of all buyers.", "0.00%;-0.00%;0.00%"),
}
for name, (expr, description, fmt) in definitions.items():
    quoted = "'" + name + "'" if " " in name else name
    pattern = r"(?m)^\tmeasure (?:'" + re.escape(name) + r"'|" + re.escape(name) + r") =.*?(?=^\t(?:measure|column|partition) |\Z)"
    match = re.search(pattern, s, flags=re.S | re.M)
    lineage = re.search(r"lineageTag: ([^\n]+)", match.group(0)).group(1).strip() if match else str(uuid.uuid5(uuid.NAMESPACE_URL, "retail/measure/" + name))
    block = "\t/// " + description + "\n\tmeasure " + quoted + " =\n" + "\n".join("\t\t\t" + line for line in expr.splitlines()) + f"\n\t\tformatString: {fmt}\n\t\tdisplayFolder: Measures\n\t\tlineageTag: {lineage}\n\n"
    if match:
        s = s[:match.start()] + block + s[match.end():]
    else:
        ix = s.index("\tcolumn Invoice_ID")
        s = s[:ix] + block + s[ix:]
s = s.replace('"POST","AMAZON FEE"', '"POST","AMAZONFEE","AMAZON FEE"')
s = s.replace("and negativeQty = false", "and [Quantity] > 0").replace("and zeroprice = false", "and [Unit_Price] > 0")
for name, dtype in [("Is_Merchandise_Reversal", "boolean"), ("Movement_Type", "string")]:
    ix = s.index("\tpartition 'Online Retail' = m")
    block = f"\tcolumn {name}\n\t\tdataType: {dtype}\n\t\tlineageTag: {uuid.uuid5(uuid.NAMESPACE_URL, 'retail/column/' + name)}\n\t\tsummarizeBy: none\n\t\tsourceColumn: {name}\n\n"
    s = s[:ix] + block + s[ix:]
s = s.replace('    #"Changed Type1" = Table.TransformColumnTypes(#"Added Custom",{{"Include_In_Main_Analysis", type logical}})', '''    #"Changed Type1" = Table.TransformColumnTypes(#"Added Custom",{{"Include_In_Main_Analysis", type logical}}),
    #"Merchandise reversals" = Table.AddColumn(#"Changed Type1", "Is_Merchandise_Reversal", each [Line_Type] = "Product" and [Record_Flag] = "Normal" and [Quantity] < 0 and [Unit_Price] > 0, type logical),
    #"Movement classification" = Table.AddColumn(#"Merchandise reversals", "Movement_Type", each if [Include_In_Main_Analysis] then "Merchandise sale" else if [Is_Merchandise_Reversal] then "Merchandise cancellation / reversal" else if [Line_Type] = "Adjustment" then "Administrative adjustment" else if [Line_Type] = "Gift Voucher" then "Gift voucher movement" else "Other / excluded movement", type text)'''.replace("\n", "\n\t\t\t\t"))
s = s.replace('    #"Changed Type1"\n', '    #"Movement classification"\n')
s = "\n".join(line.rstrip() for line in s.splitlines()).rstrip() + "\n"
path.write_text(s, encoding="utf-8")
(REPO / "evidence/financial/measure_definitions.json").write_text(json.dumps({k: {"dax": v[0], "definition": v[1], "format": v[2]} for k, v in definitions.items()}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("Phase 1 financial definitions applied; original measure names and lineage retained.")
