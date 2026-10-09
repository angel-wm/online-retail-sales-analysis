"""Validate authored report/model references and layout, without rendering Power BI."""
from pathlib import Path
import itertools
import json
import re

REPO = Path(__file__).resolve().parents[1]
PROJECT = REPO / "powerbi"
REPORT = PROJECT / "uk-online-retail-sales-analysis.Report"
TOM = json.loads((REPO / "evidence/validation/final-tom.json").read_text(encoding="utf-8"))
TABLES = {t["name"]: {kind: {x["name"] for x in t[key]} for kind, key in [("Column", "columns"), ("Measure", "measures")]} for t in TOM["tables"]}
ERRORS = []
COUNTS = {"column_references": 0, "measure_references": 0, "source_entities": 0}

def require(condition, message):
    if not condition:
        ERRORS.append(message)

def scan(obj, scope, location):
    if isinstance(obj, list):
        for i, value in enumerate(obj):
            scan(value, scope, f"{location}/{i}")
    elif isinstance(obj, dict):
        scope = dict(scope)
        for source in obj.get("From", []):
            scope[source["Name"]] = source.get("Entity")
        for kind in ("Column", "Measure"):
            if kind not in obj:
                continue
            field = obj[kind]
            ref = field.get("Expression", {}).get("SourceRef", {})
            entity = ref.get("Entity") or scope.get(ref.get("Source"))
            COUNTS[kind.lower() + "_references"] += 1
            require(entity in TABLES, f"{location}: unresolved {kind} table {ref}")
            if entity in TABLES:
                require(field["Property"] in TABLES[entity][kind], f"{location}: missing {entity}[{field['Property']}]")
        if "SourceRef" in obj and "Entity" in obj["SourceRef"]:
            COUNTS["source_entities"] += 1
            require(obj["SourceRef"]["Entity"] in TABLES, f"{location}: unknown entity")
        for key in ("queryRef", "metadata"):
            value = obj.get(key)
            if not isinstance(value, str):
                continue
            for table in TABLES:
                if value.startswith(table + "."):
                    field = value[len(table) + 1:]
                    require(field in TABLES[table]["Column"] | TABLES[table]["Measure"], f"{location}: stale {key} {value}")
        for key, value in obj.items():
            scan(value, scope, f"{location}/{key}")

def walk(obj):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from walk(value)

def intersects(a, b):
    return min(a["x"] + a["width"], b["x"] + b["width"]) > max(a["x"], b["x"]) + .1 and min(a["y"] + a["height"], b["y"] + b["height"]) > max(a["y"], b["y"]) + .1

pbip = json.loads((REPO / "uk-online-retail-sales-analysis.pbip").read_text(encoding="utf-8"))
require((REPO / pbip["artifacts"][0]["report"]["path"]).resolve() == REPORT.resolve(), "PBIP report path")
pbir = json.loads((REPORT / "definition.pbir").read_text(encoding="utf-8"))
require((REPORT / pbir["datasetReference"]["byPath"]["path"] / "definition.pbism").exists(), "PBIR semantic model path")
baseline = json.loads((REPO / "evidence/baseline/original_manifest.json").read_text(encoding="utf-8"))
original = {tuple(Path(r["path"].replace("\\", "/")).parts[-4:-1:2]) for r in baseline if r["path"].endswith("visual.json")}
# The original key is (page ID, visual ID); comparison uses original immutable manifest.
require(len(original) == 31, "Expected original 31 visual identifiers")
pages = []
present = set()
all_sync = []
for pagefile in sorted((REPORT / "definition/pages").glob("*/page.json")):
    page = json.loads(pagefile.read_text(encoding="utf-8"))
    visuals = [json.loads(f.read_text(encoding="utf-8")) for f in sorted(pagefile.parent.glob("visuals/*/visual.json"))]
    ids = {j["name"] for j in visuals}
    require(len(ids) == len(visuals), f"Duplicate visual ID: {page['displayName']}")
    present.update((pagefile.parent.name, identity) for identity in ids)
    require(len({j["position"]["tabOrder"] for j in visuals}) == len(visuals), "Duplicate tab order")
    meaningful = [j for j in visuals if j["visual"]["visualType"] != "shape"]
    for a, b in itertools.combinations(meaningful, 2):
        require(not intersects(a["position"], b["position"]), f"Container overlap: {page['displayName']} {a['name']} / {b['name']}")
    for j in visuals:
        p = j["position"]
        require(p["width"] > 0 and p["height"] > 0 and p["x"] >= 0 and p["y"] >= 0 and p["x"] + p["width"] <= page["width"] + .1 and p["y"] + p["height"] <= page["height"] + .1, f"Outside canvas: {j['name']}")
        scan(j, {}, j["name"])
        v = j["visual"]
        if v["visualType"] == "slicer":
            group = v["syncGroup"]
            require(group["fieldChanges"] and group["filterChanges"], "Incomplete slicer sync")
            all_sync.append(group["groupName"])
        if v["visualType"] == "actionButton":
            require(any(n.get("Value") == "'ClearAllSlicers'" for n in walk(v)), "Reset action changed")
        if v["visualType"] == "scatterChart":
            require(v["query"]["queryState"]["Size"]["projections"][0]["field"]["Measure"]["Property"] == "Orders", "Scatter bubble encoding")
        if v["visualType"] in {"clusteredBarChart", "scatterChart"} and any(n.get("Property") == "Product_Label" for n in walk(v)):
            filters = j["filterConfig"]["filters"]
            require(len(filters) == 1 and filters[0]["field"]["Column"]["Expression"]["SourceRef"]["Entity"] == "DimProduct", "Product ranking dimension filter")
        if v["visualType"] == "clusteredBarChart" and j["name"] in {"fc81c2d8bc82287d528b", "5f1c21068041053e9103"}:
            require(len(j["filterConfig"]["filters"]) == 1 and j["filterConfig"]["filters"][0]["type"] == "TopN", "Country ranking has an undeclared exclusion/threshold")
    pairs = set()
    for interaction in page["visualInteractions"]:
        pair = interaction["source"], interaction["target"]
        require(pair[0] in ids and pair[1] in ids and pair[0] != pair[1], "Invalid interaction reference")
        require(pair not in pairs, "Duplicate interaction")
        pairs.add(pair)
    charts = [j for j in visuals if j["visual"]["visualType"] in {"clusteredBarChart", "clusteredColumnChart", "lineChart", "scatterChart"}]
    slicers = [j for j in visuals if j["visual"]["visualType"] == "slicer"]
    targets = [j for j in visuals if j["visual"]["visualType"] in {"cardVisual", "tableEx"}] + charts
    actual = {(i["source"], i["target"]): i["type"] for i in page["visualInteractions"]}
    for source in charts + slicers:
        for target in targets:
            if source["name"] != target["name"]:
                require(actual.get((source["name"], target["name"])) == "DataFilter", "Missing quantitative filter interaction")
    for source in charts:
        for target in slicers:
            require(actual.get((source["name"], target["name"])) == "NoFilter", "Chart changed slicer list")
    pages.append({"page": page["displayName"], "visuals": len(visuals), "width": page["width"], "height": page["height"], "interaction_pairs": len(pairs), "container_overlaps_excluding_background_shapes": 0})
require(len(pages) == 2 and len(present) == 38, "Expected two pages / 38 visuals")
require(original <= present, "Original visual removed")
report_definition = json.loads((REPORT / "definition/report.json").read_text(encoding="utf-8"))
for package in report_definition.get("resourcePackages", []):
    for item in package["items"]:
        require((REPORT / "StaticResources" / package["name"] / item["path"]).exists(), f"Missing report resource: {item['path']}")
require(sorted(all_sync) == sorted(["Retail_Year", "Retail_Country", "Retail_Line_Type"] * 2), "Slicer sync groups")
dependencies = {}
for table in TOM["tables"]:
    for m in table["measures"]:
        deps = []
        for qualified, field in re.findall(r"(?:'([^']+)'\s*)?\[([^]]+)\]", m["expression"]):
            owner = qualified or table["name"]
            require(owner in TABLES and field in TABLES[owner]["Column"] | TABLES[owner]["Measure"], f"DAX reference {owner}[{field}]")
            if owner in TABLES and field in TABLES[owner]["Measure"]:
                deps.append(field)
        dependencies[m["name"]] = deps
def visit(name, stack):
    require(name not in stack, f"Circular measure dependency {name}")
    if name in stack:
        return
    for child in dependencies.get(name, []):
        visit(child, stack + [name])
for name in dependencies:
    visit(name, [])
out = {"status": "FAIL" if ERRORS else "PASS", "native_engine_or_render_executed": False, "pages": pages, "original_visuals_retained": len(original & present), "new_visuals": len(present - original), "references_checked": COUNTS, "measure_dependency_graph": dependencies, "errors": ERRORS}
(REPO / "evidence/validation/report-checks.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, indent=2))
raise SystemExit(bool(ERRORS))
