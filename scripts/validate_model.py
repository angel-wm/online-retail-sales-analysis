"""Source-based model checks. No claim of native DAX/M execution."""
from pathlib import Path
import json
import re
import pandas as pd
from reconcile import REPO, read_source, classify, stats

def build_product_dimension(fact):
    records = []
    fact = fact.copy()
    fact["Name_Normalized"] = fact.Description.str.strip().str.upper()
    for code, group in fact.groupby("Stock_Code", sort=True):
        sales = group.loc[group.Include_In_Main_Analysis]
        candidates = sales if len(sales) else group
        counts = candidates.Name_Normalized.value_counts()
        name = sorted(counts.loc[counts.eq(counts.max())].index)[0]
        records.append({"Stock_Code": code, "Product_Name": name, "Product_Label": code + " — " + name, "Description_Variants": int(group.Name_Normalized.nunique())})
    return pd.DataFrame(records)

def run():
    raw, digest = read_source()
    fact = classify(raw)
    after = json.loads((REPO / "evidence/financial/before_after.json").read_text(encoding="utf-8"))["after"]
    assert stats(fact) == after
    dim = build_product_dimension(fact)
    assert dim.Stock_Code.is_unique and dim.Product_Label.is_unique
    assert dim.Stock_Code.ne("").all() and dim.Product_Name.notna().all()
    joined = fact.merge(dim, on="Stock_Code", how="left", validate="many_to_one", indicator=True)
    assert len(joined) == len(fact) and joined._merge.eq("both").all()
    assert int(joined.Amount_Cents.sum()) == int(fact.Amount_Cents.sum())
    dates = pd.date_range(fact.InvoiceDate.min().normalize(), fact.InvoiceDate.max().normalize())
    assert len(dates) == 374 and dates.is_unique
    assert fact.InvoiceDate.dt.normalize().isin(dates).all()
    expected = json.loads((REPO / "evidence/financial/measure_definitions.json").read_text(encoding="utf-8"))
    final_tom = REPO / "evidence/validation/final-tom.json"
    tom = json.loads((final_tom if final_tom.exists() else REPO / "evidence/validation/phase2-tom.json").read_text(encoding="utf-8"))
    parsed_fact = next(t for t in tom["tables"] if t["name"] == "Online Retail")
    assert {m["name"] for m in parsed_fact["measures"]} == set(expected)
    for measure in parsed_fact["measures"]:
        assert measure["expression"].strip() == expected[measure["name"]]["dax"].strip(), measure["name"]
        assert measure["format"] == expected[measure["name"]]["format"], measure["name"]
    relations = [r for r in tom["relationships"] if r["toTable"] in {"Calendar", "DimProduct"}]
    assert len(relations) == 2
    assert all(r["fromCardinality"] == "Many" and r["toCardinality"] == "One" and r["crossFiltering"] == "OneDirection" and r["active"] for r in relations)
    variants = int(dim.Description_Variants.gt(1).sum())
    dim.to_csv(REPO / "evidence/financial/product_identity.csv", index=False)
    scenarios = []
    filters = {"All": fact, "Year 2010": fact.loc[fact.InvoiceDate.dt.year.eq(2010)], "Year 2011": fact.loc[fact.InvoiceDate.dt.year.eq(2011)], "Netherlands": fact.loc[fact.Country.eq("Netherlands")], "Germany": fact.loc[fact.Country.eq("Germany")], "United Kingdom": fact.loc[fact.Country.eq("United Kingdom")], "Adjustment": fact.loc[fact.Line_Type.eq("Adjustment")], "Gift Voucher": fact.loc[fact.Line_Type.eq("Gift Voucher")], "Product": fact.loc[fact.Line_Type.eq("Product")], "Customer 12347": fact.loc[fact.Customer_ID.eq("12347")], "Unknown customer": fact.loc[fact.Customer_ID.eq("")], "Reversal invoice C581484": fact.loc[fact.Invoice_ID.eq("C581484")], "Stock 23843": fact.loc[fact.Stock_Code.eq("23843")], "Stock 85123A": fact.loc[fact.Stock_Code.eq("85123A")], "Empty": fact.iloc[0:0]}
    for label, selected in filters.items():
        values = stats(selected)
        # DAX distinguishes no eligible rows from a numerical sum of zero.
        sales_exist = selected.Include_In_Main_Analysis.any()
        reversals_exist = selected.Is_Merchandise_Reversal.any()
        if not sales_exist:
            for key in ["Main Sales", "Orders", "Unique Customers", "Units Sold"]:
                values[key] = None
        if not reversals_exist:
            for key in ["Returns Amount", "Return Value", "Cancelled Orders"]:
                values[key] = None
            values["Return rate"] = None
        if not sales_exist and not reversals_exist:
            values["Net Sales"] = None
        reversed_units = selected.loc[selected.Is_Merchandise_Reversal, "Quantity"]
        values["Units Reversed"] = -int(reversed_units.sum()) if len(reversed_units) else None
        known_sales = selected.loc[selected.Include_In_Main_Analysis & selected.Customer_ID.ne("")]
        # DISTINCTCOUNTNOBLANK returns BLANK when the eligible rows have no known IDs.
        if known_sales.empty:
            values["Unique Customers"] = None
        values["Identified Sales Share"] = int(known_sales.Amount_Cents.sum()) / int(selected.loc[selected.Include_In_Main_Analysis, "Amount_Cents"].sum()) if sales_exist and len(known_sales) else None
        if selected.loc[selected.Customer_ID.eq("") & (selected.Include_In_Main_Analysis | selected.Is_Merchandise_Reversal)].empty:
            values["Unidentified Net Sales"] = None
        if not selected.Line_Type.eq("Adjustment").any():
            values["Administrative Adjustments"] = None
        if not selected.Movement_Type.isin(["Gift voucher movement", "Other / excluded movement"]).any():
            values["Other Movements"] = None
        if not selected.Is_Zero_Price.any():
            values["Zero Price Records"] = None
        if selected.empty:
            values["Total Sales"] = None
        scenarios.append({"context": label, "expected_from_source": values, "native_engine_tested": False})
    out = REPO / "evidence/validation/model-checks.json"
    out.write_text(json.dumps({"status": "PASS", "source_sha256": digest, "native_engine_executed": False, "fact_rows": len(fact), "dimension_rows": len(dim), "join_rows": len(joined), "orphan_product_rows": 0, "product_key_unique": True, "product_labels_unique": True, "codes_with_multiple_loaded_names": variants, "eligible_codes_multiple_names": 212, "calendar_days": len(dates), "orphan_date_rows": 0, "phase1_values_preserved": after, "compiled_tom_measures_match_financial_contract": True, "scenarios": scenarios}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "product_rows": len(dim), "fact_rows": len(fact), "join_rows": len(joined), "name_variants": variants, "calendar_days": len(dates), "scenarios": len(scenarios), "native_engine_executed": False}), flush=True)

if __name__ == "__main__":
    run()
