"""Independent scalar reconstruction from the XLSX XML, without pandas/helpers."""
from pathlib import Path
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_EVEN
from lxml import etree
import json
import zipfile

REPO = Path(__file__).resolve().parents[1]
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
totals = Counter()
orders, customers, reversal_invoices = set(), set(), set()
source = REPO / "data/raw/Online Retail.xlsx"
with zipfile.ZipFile(source) as z:
    shared = ["".join(si.itertext()) for si in etree.fromstring(z.read("xl/sharedStrings.xml"))]
    with z.open("xl/worksheets/sheet1.xml") as stream:
        for _, row in etree.iterparse(stream, events=("end",), tag=NS + "row"):
            if row.get("r") == "1":
                row.clear()
                continue
            cells = {}
            for c in row:
                value = c.find(NS + "v")
                if value is not None:
                    cells[c.get("r").rstrip("0123456789")] = shared[int(value.text)] if c.get("t") == "s" else value.text
            inv, code, name, qty, price, customer = [cells.get(k) for k in ("A", "B", "C", "D", "F", "G")]
            qty = int(Decimal(qty))
            price = Decimal(price)
            cents = int((qty * price).quantize(Decimal(".01"), rounding=ROUND_HALF_EVEN) * 100)
            totals["raw_rows"] += 1
            if name is not None:
                totals["loaded_rows"] += 1
                totals["total_cents"] += cents
                code, name = code.strip().upper(), name.strip().upper()
                gift = code.startswith("GIFT_") or "GIFT VOUCHER" in name
                admin = not gift and (code in {"M", "S", "POST", "AMAZONFEE", "AMAZON FEE", "BANK CHARGES", "D", "DOT", "C2", "B", "CRUK"} or name == "EBAY")
                normal = not ((not customer and name.startswith("*")) or (not customer and any(v in name for v in ["?", "MISSING", "LOST", "DAMAGE", "DISPLAY", "SOLD AS SETS"]) and price == 0))
                cancelled = inv.strip().upper().startswith("C")
                gross = not admin and not gift and normal and not cancelled and qty > 0 and price > 0
                reversal = not admin and not gift and normal and qty < 0 and price > 0
                if gross:
                    totals["gross_cents"] += cents
                    totals["units_sold"] += qty
                    orders.add(inv)
                    if customer:
                        customers.add(customer)
                    else:
                        totals["unidentified_gross_cents"] += cents
                if reversal:
                    totals["reversal_cents"] -= cents
                    totals["units_reversed"] -= qty
                    reversal_invoices.add(inv)
                    if not customer:
                        totals["unidentified_reversal_cents"] -= cents
                if admin:
                    totals["admin_cents"] += cents
                elif not gross and not reversal:
                    totals["other_cents"] += cents
                totals["zero_price_rows"] += price == 0
            row.clear()
            while row.getprevious() is not None:
                del row.getparent()[0]
expected = json.loads((REPO / "evidence/financial/before_after.json").read_text(encoding="utf-8"))["after"]
checks = {
    "Total Sales": totals["total_cents"] / 100,
    "Main Sales": totals["gross_cents"] / 100,
    "Returns Amount": totals["reversal_cents"] / 100,
    "Return Value": totals["reversal_cents"] / 100,
    "Net Sales": (totals["gross_cents"] - totals["reversal_cents"]) / 100,
    "Orders": len(orders), "Unique Customers": len(customers), "Cancelled Orders": len(reversal_invoices),
    "Units Sold": totals["units_sold"], "Zero Price Records": totals["zero_price_rows"],
    "Administrative Adjustments": totals["admin_cents"] / 100,
    "Other Movements": totals["other_cents"] / 100,
    "Unidentified Net Sales": (totals["unidentified_gross_cents"] - totals["unidentified_reversal_cents"]) / 100,
}
assert checks == {k: expected[k] for k in checks}, (checks, expected)
assert totals["total_cents"] == totals["gross_cents"] - totals["reversal_cents"] + totals["admin_cents"] + totals["other_cents"]
result = {"status": "PASS", "independent_paths": ["openpyxl + pandas + integer pennies", "lxml XLSX XML + scalar Decimal + integer pennies"], "engine_executed": False, "checked": checks, "xml_totals": dict(totals)}
out = REPO / "evidence/validation/independent_xml.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print("Independent XLSX XML cross-check PASS:", json.dumps(checks), flush=True)
