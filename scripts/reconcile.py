"""Recalculate source rules in integer pennies; this does not execute DAX or M."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP
import argparse
import hashlib
import json
import math
import re
import pandas as pd
import numpy as np

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "data/raw/Online Retail.xlsx"
OUTPUT = REPO / "evidence/financial"
CACHE = REPO / ".cache"
OLD_ADJUSTMENTS = {"M", "S", "POST", "AMAZON FEE", "BANK CHARGES", "D", "DOT", "C2", "B", "CRUK"}
ADJUSTMENTS = OLD_ADJUSTMENTS | {"AMAZONFEE"}

def save(name, obj):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")

def text_id(value):
    if pd.isna(value):
        return ""
    return str(int(value)) if isinstance(value, (int, float)) and float(value).is_integer() else str(value)

def read_source(fresh=False):
    CACHE.mkdir(exist_ok=True)
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    cached = CACHE / (digest + ".pkl")
    if cached.exists() and not fresh:
        return pd.read_pickle(cached), digest
    data = pd.read_excel(SOURCE, engine="openpyxl")
    data["Invoice_ID"] = data.InvoiceNo.map(text_id)
    data["Stock_Code"] = data.StockCode.map(text_id).str.strip().str.upper()
    data["Customer_ID"] = data.CustomerID.map(text_id)
    data["Amount_Cents"] = [int((Decimal(str(q)) * Decimal(str(p))).quantize(Decimal(".01"), rounding=ROUND_HALF_EVEN) * 100) for q, p in zip(data.Quantity, data.UnitPrice)]
    data.to_pickle(cached)
    return data, digest

def classify(data, corrected=True):
    d = data.loc[data.Description.notna()].copy()
    name = d.Description.str.strip().str.upper()
    code = d.Stock_Code
    gift = code.str.startswith("GIFT_") | name.str.contains("GIFT VOUCHER", regex=False)
    adjustment = code.isin(ADJUSTMENTS if corrected else OLD_ADJUSTMENTS) | name.eq("EBAY")
    d["Line_Type"] = np.select([gift, adjustment], ["Gift Voucher", "Adjustment"], default="Product")
    anonymous = d.Customer_ID.eq("")
    manual = anonymous & name.str.startswith("*")
    operational = anonymous & name.str.contains(r"\?|MISSING|LOST|DAMAGE|DISPLAY|SOLD AS SETS", regex=True) & (d.UnitPrice.isna() | d.UnitPrice.eq(0))
    d["Record_Flag"] = np.select([manual, operational], ["Manual / Review", "Operational / Non-Product"], default="Normal")
    d["Is_Cancelled"] = d.Invoice_ID.str.strip().str.upper().str.startswith("C")
    d["Is_Negative_Qty"] = d.Quantity.lt(0)
    d["Is_Zero_Price"] = d.UnitPrice.eq(0)
    if corrected:
        d["Include_In_Main_Analysis"] = d.Line_Type.eq("Product") & d.Record_Flag.eq("Normal") & ~d.Is_Cancelled & d.Quantity.gt(0) & d.UnitPrice.gt(0)
        d["Is_Merchandise_Reversal"] = d.Line_Type.eq("Product") & d.Record_Flag.eq("Normal") & d.Quantity.lt(0) & d.UnitPrice.gt(0)
        d["Movement_Type"] = np.select([d.Include_In_Main_Analysis, d.Is_Merchandise_Reversal, d.Line_Type.eq("Adjustment"), d.Line_Type.eq("Gift Voucher")], ["Merchandise sale", "Merchandise cancellation / reversal", "Administrative adjustment", "Gift voucher movement"], default="Other / excluded movement")
    else:
        d["Include_In_Main_Analysis"] = d.Line_Type.eq("Product") & d.Record_Flag.eq("Normal") & ~d.Is_Cancelled & ~d.Is_Negative_Qty & ~d.Is_Zero_Price
    return d

def stats(d, corrected=True):
    sales = d.loc[d.Include_In_Main_Analysis]
    negative = d.loc[d.Is_Merchandise_Reversal if corrected else d.Is_Negative_Qty]
    product_negative = negative if corrected else negative.loc[negative.Line_Type.eq("Product")]
    gross = int(sales.Amount_Cents.sum())
    reversal = int(product_negative.Amount_Cents.abs().sum()) if corrected else abs(int(negative.Amount_Cents.sum()))
    net = gross - reversal
    orders = int(sales.Invoice_ID.nunique())
    rate = reversal / gross if gross else None
    aov = net / 100 / orders if orders else None
    return {
        "Total Sales": int(d.Amount_Cents.sum()) / 100,
        "Main Sales": gross / 100,
        "Returns Amount": reversal / 100,
        "Return Value": int(product_negative.Amount_Cents.abs().sum()) / 100,
        "Net Sales": net / 100,
        "Orders": orders,
        "Unique Customers": int(sales.loc[sales.Customer_ID.ne(""), "Customer_ID"].nunique()),
        "Average Order Value": aov if corrected else (2 * math.floor(aov / 2 + .5) if aov is not None and aov >= 0 else None),
        "Return rate": rate if corrected else (float(Decimal(str(rate)).quantize(Decimal(".01"), rounding=ROUND_HALF_UP)) if rate is not None else None),
        "Units Sold": int(sales.Quantity.sum()),
        "Cancelled Orders": int(negative.Invoice_ID.nunique()) if corrected else int(d.loc[d.Is_Cancelled, "Invoice_ID"].nunique()),
        "Zero Price Records": int(d.Is_Zero_Price.sum()),
        "Administrative Adjustments": int(d.loc[d.Line_Type.eq("Adjustment"), "Amount_Cents"].sum()) / 100,
        "Other Movements": int(d.loc[~d.Include_In_Main_Analysis & ~(d.Is_Merchandise_Reversal if corrected else d.Is_Negative_Qty) & ~d.Line_Type.eq("Adjustment"), "Amount_Cents"].sum()) / 100,
        "Unidentified Net Sales": int(d.loc[d.Customer_ID.eq("") & d.Include_In_Main_Analysis, "Amount_Cents"].sum() - (d.loc[d.Customer_ID.eq("") & d.Is_Merchandise_Reversal, "Amount_Cents"].abs().sum() if corrected else d.loc[d.Customer_ID.eq("") & d.Is_Negative_Qty, "Amount_Cents"].sum() * -1)) / 100,
    }

def run(fresh=False):
    raw, digest = read_source(fresh)
    old = classify(raw, False)
    current = classify(raw, True)
    before, after = stats(old, False), stats(current, True)
    baseline = json.loads((REPO / "evidence/baseline/data_reconciliation.json").read_text(encoding="utf-8"))["overall"]
    mapping = {"Main Sales": "main_sales", "Total Sales": "total_sales", "Returns Amount": "returns_amount", "Return Value": "return_value_product", "Net Sales": "net_sales", "Orders": "orders", "Unique Customers": "customers", "Units Sold": "units", "Cancelled Orders": "cancelled_orders", "Zero Price Records": "zero_price_rows", "Average Order Value": "aov_mround2", "Return rate": "return_rate_DAX_round2"}
    assert all(before[k] == baseline[v] for k, v in mapping.items()), (before, baseline)
    assert len(raw) == 541909 and len(current) == 540455
    assert after["Total Sales"] == round(after["Net Sales"] + after["Administrative Adjustments"] + after["Other Movements"], 2)
    assert not current.loc[current.Stock_Code.eq("AMAZONFEE"), "Include_In_Main_Analysis"].any()
    assert not current.loc[current.Is_Merchandise_Reversal, "Amount_Cents"].gt(0).any()
    changes = []
    for k in mapping:
        delta = after[k] - before[k]
        changes.append({"kpi": k, "before": before[k], "after": after[k], "absolute_change": round(delta, 10), "percentage_change": delta / abs(before[k]) * 100 if before[k] else None, "percentage_point_change": delta * 100 if k == "Return rate" else None})
    save("before_after.json", {"source_sha256": digest, "population": "All source dates, countries and line types; original null-description exclusion preserved", "dax_or_m_executed": False, "before": before, "after": after, "changes": changes})
    pd.DataFrame(changes).to_csv(OUTPUT / "before_after.csv", index=False)
    code_records = []
    for code, g in current.groupby("Stock_Code", sort=True):
        if not re.fullmatch(r"[0-9]{5}[A-Z]*", code):
            code_records.append({"code": code, "descriptions": sorted(g.Description.unique().tolist()), "classifications": sorted(g.Line_Type.unique().tolist()), "rows": len(g), "positive_gbp": int(g.loc[g.Amount_Cents.gt(0), "Amount_Cents"].sum()) / 100, "negative_gbp": int(g.loc[g.Amount_Cents.lt(0), "Amount_Cents"].sum()) / 100})
    save("special_codes.json", code_records)
    by_month = []
    for month, g in current.groupby(current.InvoiceDate.dt.strftime("%Y-%m")):
        b = stats(old.loc[old.InvoiceDate.dt.strftime("%Y-%m").eq(month)], False)
        a = stats(g)
        by_month.append({"month": month, "gross_gbp": a["Main Sales"], "reversals_gbp": a["Returns Amount"], "net_gbp": a["Net Sales"], "orders": a["Orders"], "aov_gbp": a["Average Order Value"], "rate": a["Return rate"], "old_net_gbp": b["Net Sales"]})
    pd.DataFrame(by_month).to_csv(OUTPUT / "monthly.csv", index=False)
    coverage = {
        "raw_rows": len(raw), "loaded_rows": len(current),
        "excluded_null_description_rows": int(raw.Description.isna().sum()),
        "excluded_null_description_cents": int(raw.loc[raw.Description.isna(), "Amount_Cents"].sum()),
        "source_min_date": str(raw.InvoiceDate.min()), "source_max_date": str(raw.InvoiceDate.max()),
        "missing_customer_rows": int(raw.CustomerID.isna().sum()),
        "exact_duplicate_excess": int(raw.duplicated(subset=["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"]).sum()),
        "rows_kept_including_repetitions": True,
        "gross_unidentified_sales_gbp": int(current.loc[current.Include_In_Main_Analysis & current.Customer_ID.eq(""), "Amount_Cents"].sum()) / 100,
        "merchandise_reversal_invoices_without_C": int(current.loc[current.Is_Merchandise_Reversal & ~current.Is_Cancelled, "Invoice_ID"].nunique()),
        "positive_cancelled_product_value_cents": int(current.loc[current.Is_Cancelled & current.Line_Type.eq("Product") & current.Amount_Cents.gt(0), "Amount_Cents"].sum()),
        "product_reversal_excluded_by_flag_cents": int(current.loc[current.Line_Type.eq("Product") & current.Is_Negative_Qty & ~current.Record_Flag.eq("Normal"), "Amount_Cents"].sum()),
        "product_codes_multiple_eligible_names": int(current.loc[current.Include_In_Main_Analysis].groupby("Stock_Code").Description.apply(lambda s: s.str.strip().str.upper().nunique()).gt(1).sum()),
        "movement_classes": current.groupby("Movement_Type").agg(rows=("Amount_Cents", "size"), cents=("Amount_Cents", "sum")).reset_index().to_dict("records"),
    }
    save("coverage.json", coverage)
    country = [{"country": key, **stats(g)} for key, g in current.groupby("Country")]
    save("countries.json", country)
    print(json.dumps({"before": before, "after": after, "special_codes": code_records, "coverage": coverage}, indent=2), flush=True)
    return raw, current

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--fresh", action="store_true", help="Read XLSX again rather than using the hash-keyed local cache")
    args = p.parse_args()
    run(args.fresh)
