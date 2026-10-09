"""Scoped PBIR revision. Native rendering/interaction acceptance is still required."""
from pathlib import Path
import copy
import json
import uuid

REPO = Path(__file__).resolve().parents[1]
REPORT = REPO / "powerbi/project/uk-online-retail-sales-analysis.Report"
PAGES = REPORT / "definition/pages"
SALES = PAGES / "e2e71b2b39b7e00b93de"
INSIGHTS = PAGES / "9ce4074e277290a594b7"

def walk(obj):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from walk(value)

def literal(value):
    return {"expr": {"Literal": {"Value": value}}}

def string(value):
    return literal("'" + value.replace("'", "''") + "'")

def color(value):
    return {"solid": {"color": string(value)}}

def prop(j, group, name, value, container=False):
    key = "visualContainerObjects" if container else "objects"
    objects = j["visual"].setdefault(key, {})
    entries = objects.setdefault(group, [{"properties": {}}])
    for entry in entries:
        entry.setdefault("properties", {})[name] = value

def position(j, x, y, width, height):
    j["position"].update(x=x, y=y, width=width, height=height)

def column(table, name, alias=None):
    return {"Column": {"Expression": {"SourceRef": {"Source" if alias else "Entity": alias or table}}, "Property": name}}

def measure(name, alias=None):
    return {"Measure": {"Expression": {"SourceRef": {"Source" if alias else "Entity": alias or "Online Retail"}}, "Property": name}}

def projection(name, display=None, table="Online Retail", kind="Measure"):
    field = measure(name) if kind == "Measure" else column(table, name)
    p = {"field": field, "queryRef": table + "." + name, "nativeQueryRef": display or name}
    if display:
        p["displayName"] = display
    return p

def top_filter(table, col, metric, n):
    # Separate dimension and measure aliases. No fact/dimension identity conflation.
    col_alias = "d" if table == "DimProduct" else "o"
    sources = [{"Name": col_alias, "Entity": table, "Type": 0}]
    if col_alias != "o":
        sources.append({"Name": "o", "Entity": "Online Retail", "Type": 0})
    inner = {"Version": 2, "From": sources, "Select": [{**column(table, col, col_alias), "Name": "field"}], "OrderBy": [{"Direction": 2, "Expression": measure(metric, "o")}], "Top": n}
    return {"name": uuid.uuid5(uuid.NAMESPACE_URL, f"retail/top/{table}/{col}/{metric}/{n}").hex[:20], "field": column(table, col), "type": "TopN", "filter": {"Version": 2, "From": [{"Name": "subquery", "Expression": {"Subquery": {"Query": inner}}, "Type": 2}] + sources, "Where": [{"Condition": {"In": {"Expressions": [column(table, col, col_alias)], "Table": {"SourceRef": {"Source": "subquery"}}}}}]}}

def title(j, text, subtitle=None):
    prop(j, "title", "show", literal("true"), True)
    prop(j, "title", "text", string(text), True)
    prop(j, "title", "fontSize", literal("12D"), True)
    prop(j, "title", "fontFamily", string("Segoe UI Semibold"), True)
    prop(j, "title", "fontColor", color("#1F3A5F"), True)
    if subtitle:
        prop(j, "subTitle", "show", literal("true"), True)
        prop(j, "subTitle", "text", string(subtitle), True)
        prop(j, "subTitle", "fontSize", literal("9D"), True)
        prop(j, "subTitle", "fontColor", color("#475569"), True)

def text(j, lines, size=10, ink="#1F3A5F"):
    paragraphs = [{"textRuns": [{"value": line, "textStyle": {"fontFamily": "Segoe UI", "fontSize": str(size) + "pt", "color": ink}}]} for line in lines]
    j["visual"].setdefault("objects", {})["general"] = [{"properties": {"paragraphs": paragraphs}}]
    prop(j, "title", "show", literal("false"), True)

def save(page, j):
    folder = page / "visuals" / j["name"]
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "visual.json").write_text(json.dumps(j, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def new_text(template, identity, lines, x, y, width, height, size=10, ink="#1F3A5F"):
    j = copy.deepcopy(template)
    j["name"] = identity
    position(j, x, y, width, height)
    text(j, lines, size, ink)
    return j

def query_tooltips(j, products=False):
    projections = [projection("Main Sales", "Gross merchandise (£)"), projection("Returns Amount", "Cancellations / reversals (£)"), projection("Net Sales", "Net merchandise (£)"), projection("Return rate", "Reversal value / gross"), projection("Orders", "Sale invoices"), projection("Cancelled Orders", "Reversal invoices"), projection("Units Reversed", "Reversed units")]
    if products:
        projections = [projection("Stock_Code", "Stock code", "DimProduct", "Column"), projection("Product_Name", "Full representative name", "DimProduct", "Column"), projection("Description_Variants", "Source name variants", "DimProduct", "Column")] + projections
    j["visual"]["query"]["queryState"]["Tooltips"] = {"projections": projections}

changes = []
for page in (SALES, INSIGHTS):
    visuals = {f.parent.name: json.loads(f.read_text(encoding="utf-8")) for f in page.glob("visuals/*/visual.json")}
    pagefile = page / "page.json"
    p = json.loads(pagefile.read_text(encoding="utf-8"))
    p["height"] = 920
    # Existing titles, backgrounds, six slicers and both native reset buttons are retained.
    for j in visuals.values():
        v = j["visual"]
        kind = v["visualType"]
        prop(j, "dropShadow", "show", literal("false"), True)
        if kind in {"cardVisual", "clusteredBarChart", "clusteredColumnChart", "lineChart", "scatterChart"}:
            prop(j, "border", "show", literal("false"), True)
            prop(j, "background", "show", literal("true"), True)
            prop(j, "background", "color", color("#FFFFFF"), True)
        if kind == "shape" and j["position"]["x"] < 100:
            position(j, 16, 0, 176, 920)
        if kind == "slicer":
            fields = [x for x in walk(v["query"]) if "Column" in x]
            field = fields[0]["Column"]["Property"]
            y = {"Year": 64, "Country": 208, "Line_Type": 320}[field]
            position(j, 32, y, 144, 128 if field == "Year" else 96)
            v["syncGroup"] = {"groupName": "Retail_" + field, "fieldChanges": True, "filterChanges": True}
        if kind == "actionButton":
            position(j, 32, 432, 144, 34)
            prop(j, "text", "text", string("Clear selectors"))
            prop(j, "text", "fontSize", literal("10D"))
            # Preserve ClearAllSlicers action; it does not clear a chart's point selection or Top N.
        if kind == "cardVisual":
            prop(j, "value", "fontSize", literal("23D"))
            prop(j, "label", "fontSize", literal("10D"))
            prop(j, "value", "labelDisplayUnits", literal("0D"))
        if kind in {"clusteredBarChart", "clusteredColumnChart", "lineChart", "scatterChart"}:
            for axis in ("categoryAxis", "valueAxis"):
                prop(j, axis, "fontSize", literal("10D"))
            prop(j, "labels", "fontSize", literal("9D"))
            prop(j, "labels", "labelPrecision", literal("1L"))
            prop(j, "labels", "labelDisplayUnits", literal("1000D"))
            prop(j, "valueAxis", "labelPrecision", literal("0L"))
            prop(j, "valueAxis", "labelDisplayUnits", literal("1000D"))
        # Clean old misleading metadata query names, without changing measure ownership.
        for obj in walk(j):
            if obj.get("queryRef") == "Calendar.Return Value":
                obj["queryRef"] = "Online Retail.Return Value"

    if page == SALES:
        position(visuals["5aa06803ebeac0c1cbba"], 215, 10, 1095, 35)
        position(visuals["eb470f7e84ed9703a8d8"], 215, 50, 1095, 26)
        text(visuals["5aa06803ebeac0c1cbba"], ["Online Retail Sales Dashboard"], 20, "#FFFFFF")
        text(visuals["eb470f7e84ed9703a8d8"], ["Merchandise in GBP. 2010: December only. December 2011: through 9 December."], 10, "#FFFFFF")
        cards = ["dd400a8a673caa8ed6a7", "c6a83e50232cca065cd5", "0d43bab4e45532bcc190", "b7f03dd49cd6692b1d55", "1efd5c26d1b097445d63"]
        for i, key in enumerate(cards):
            position(visuals[key], 200 + i * 227, 88, 218, 96)
        net = visuals[cards[0]]
        for obj in walk(net):
            if obj.get("Property") == "Main Sales":
                obj["Property"] = "Net Sales"
            for k, value in list(obj.items()):
                if value == "Online Retail.Main Sales":
                    obj[k] = "Online Retail.Net Sales"
        net["visual"]["query"]["queryState"]["Data"]["projections"][0].update(nativeQueryRef="Net merchandise sales", displayName="Net merchandise sales")
        prop(net, "value", "labelDisplayUnits", literal("1000000D"))
        prop(net, "value", "decimalPlaces", literal("2L"))
        visuals[cards[2]]["visual"]["query"]["queryState"]["Data"]["projections"][0].update(nativeQueryRef="Known customers", displayName="Known customers")
        aov = visuals[cards[3]]
        aov["visual"]["query"]["queryState"]["Data"]["projections"][0].update(nativeQueryRef="Net value / sale invoice", displayName="Net value / sale invoice")
        prop(aov, "value", "decimalPlaces", literal("2L"))
        rate = visuals[cards[4]]
        rate["visual"]["query"]["queryState"]["Data"]["projections"][0].update(nativeQueryRef="Reversal value / gross", displayName="Reversal value / gross")
        prop(rate, "value", "decimalPlaces", literal("2L"))
        trend = visuals["c1e7baf0796e55151039"]
        position(trend, 200, 216, 736, 284)
        title(trend, "Net merchandise sales by month (£)")
        prop(trend, "valueAxis", "labelDisplayUnits", literal("1000000D"))
        prop(trend, "valueAxis", "labelPrecision", literal("1L"))
        prop(trend, "labels", "show", literal("false"))
        prop(trend, "lineStyles", "lineChartType", string("straight"))
        prop(trend, "lineStyles", "areaShow", literal("false"))
        prop(trend, "lineStyles", "strokeWidth", literal("3D"))
        query_tooltips(trend)
        trend["visual"]["query"]["queryState"]["Tooltips"]["projections"].append(projection("Average Order Value", "Net value / sale invoice (£)"))
        country = visuals["5f1c21068041053e9103"]
        position(country, 952, 216, 374, 284)
        country["visual"]["query"]["queryState"]["Y"]["projections"] = [projection("Net Sales", "Net merchandise (£)")]
        country["visual"]["query"]["sortDefinition"] = {"sort": [{"field": measure("Net Sales"), "direction": "Descending"}]}
        country["filterConfig"] = {"filters": [top_filter("Online Retail", "Country", "Net Sales", 10)]}
        title(country, "Top 10 countries by net sales (£)")
        prop(country, "categoryAxis", "maxSize", literal("38D"))
        query_tooltips(country)
        products = visuals["103453003bcd8ca655ca"]
        position(products, 200, 508, 736, 316)
        products["visual"]["query"]["queryState"]["Category"]["projections"] = [projection("Product_Label", "Stock code and product", "DimProduct", "Column")]
        products["filterConfig"] = {"filters": [top_filter("DimProduct", "Product_Label", "Net Sales", 10)]}
        title(products, "Top 10 products by net merchandise sales (£)")
        prop(products, "categoryAxis", "maxSize", literal("50D"))
        prop(products, "categoryAxis", "wordWrap", literal("true"))
        prop(products, "categoryAxis", "innerPadding", literal("10D"))
        query_tooltips(products, True)
        orders = visuals["0d26f07ae3e59165a455"]
        position(orders, 952, 508, 374, 316)
        title(orders, "Sale invoices by month", "Monthly net value / invoice in tooltip")
        prop(orders, "valueAxis", "showAxisTitle", literal("true"))
        prop(orders, "valueAxis", "titleText", string("Sale invoices"))
        prop(orders, "labels", "show", literal("false"))
        orders["visual"]["query"]["queryState"]["Tooltips"] = {"projections": [projection("Average Order Value", "Net value / sale invoice (£)"), projection("Net Sales", "Net merchandise (£)")]}
        hint = new_text(visuals["eb470f7e84ed9703a8d8"], "retail_sales_definition", ["Net = eligible gross − merchandise cancellations / reversals. Administrative adjustments are separate."], 208, 188, 1110, 24, 10)
        visuals[hint["name"]] = hint
        # A compact reconciliation row is useful under Line Type = Adjustment/Gift Voucher too.
        bridge = {"$schema": net["$schema"], "name": "retail_financial_bridge", "position": {"x": 200, "y": 834, "z": 25000, "width": 1126, "height": 70, "tabOrder": 25000}, "visual": {"visualType": "tableEx", "query": {"queryState": {"Values": {"projections": [projection("Main Sales", "Gross merchandise (£)"), projection("Returns Amount", "Reversals (£)"), projection("Administrative Adjustments", "Administrative (£)"), projection("Other Movements", "Other movements (£)"), projection("Total Sales", "All movements (£)")]}}}, "objects": {"grid": [{"properties": {"textSize": literal("10D"), "rowPadding": literal("3D")}}], "total": [{"properties": {"totals": literal("false")}}]}, "visualContainerObjects": {"title": [{"properties": {"show": literal("false")}}]}, "drillFilterOtherVisuals": True}}
        visuals[bridge["name"]] = bridge
        template = visuals["eb470f7e84ed9703a8d8"]
    else:
        position(visuals["5d94eeb50cdd08a9dc2d"], 215, 10, 1095, 35)
        position(visuals["00c6198092a372ab0910"], 215, 50, 1095, 26)
        text(visuals["5d94eeb50cdd08a9dc2d"], ["Product & Customer Insights"], 20, "#FFFFFF")
        text(visuals["00c6198092a372ab0910"], ["Known customers and merchandise cancellations / reversals. December 2011 ends on the 9th."], 10, "#FFFFFF")
        customers = visuals["8659739282b008532eee"]
        position(customers, 200, 172, 552, 312)
        title(customers, "Top 10 known customers by net sales (£)")
        query_tooltips(customers)
        country = visuals["fc81c2d8bc82287d528b"]
        position(country, 768, 172, 558, 312)
        title(country, "Top 10 countries by reversal value (£)")
        country["filterConfig"] = {"filters": [top_filter("Online Retail", "Country", "Returns Amount", 10)]}
        query_tooltips(country)
        products = visuals["326efa6cd15edb5615ca"]
        position(products, 200, 504, 736, 320)
        title(products, "Top 10 products by reversal value (£)")
        products["visual"]["query"]["queryState"]["Category"]["projections"] = [projection("Product_Label", "Stock code and product", "DimProduct", "Column")]
        products["filterConfig"] = {"filters": [top_filter("DimProduct", "Product_Label", "Returns Amount", 10)]}
        prop(products, "categoryAxis", "maxSize", literal("50D"))
        prop(products, "categoryAxis", "wordWrap", literal("true"))
        prop(products, "categoryAxis", "innerPadding", literal("10D"))
        query_tooltips(products, True)
        for target in (country, products):
            prop(target, "dataPoint", "defaultColor", color("#B4533F"))
        scatter = visuals["bfd4fc73192936bc42c7"]
        position(scatter, 952, 504, 374, 320)
        title(scatter, "Gross sales vs reversals (£)", "Top 30 by gross sales. Bubble = sale invoices")
        state = scatter["visual"]["query"]["queryState"]
        state["Category"]["projections"] = [projection("Product_Label", "Product", "DimProduct", "Column")]
        state["X"]["projections"] = [projection("Main Sales", "Gross merchandise (£)")]
        state["Y"]["projections"] = [projection("Returns Amount", "Reversals (£)")]
        scatter["filterConfig"] = {"filters": [top_filter("DimProduct", "Product_Label", "Main Sales", 30)]}
        prop(scatter, "categoryLabels", "show", literal("false"))
        prop(scatter, "labels", "show", literal("false"))
        for axis, label in [("categoryAxis", "Gross (£)"), ("valueAxis", "Reversals (£)")]:
            prop(scatter, axis, "showAxisTitle", literal("true"))
            prop(scatter, axis, "titleText", string(label))
            prop(scatter, axis, "labelDisplayUnits", literal("1000D"))
            prop(scatter, axis, "labelPrecision", literal("0L"))
        prop(scatter, "zoom", "show", literal("false"))
        query_tooltips(scatter, True)
        # Reuse the native card configuration already present in the source project.
        original_card = json.loads((SALES / "visuals/b7f03dd49cd6692b1d55/visual.json").read_text(encoding="utf-8"))
        for identity, metric, label, x, width, units in [("retail_unknown_net", "Unidentified Net Sales", "Net sales without customer ID", 200, 552, 1000000), ("retail_identified_share", "Identified Sales Share", "Gross sales with customer ID", 768, 558, 0)]:
            card = copy.deepcopy(original_card)
            card["name"] = identity
            position(card, x, 96, width, 64)
            card["visual"]["query"] = {"queryState": {"Data": {"projections": [projection(metric, label)]}}}
            card["visual"]["objects"] = {"value": [{"properties": {"fontSize": literal("22D"), "labelDisplayUnits": literal(str(units) + "D"), "decimalPlaces": literal("2L"), "fontColor": color("#1F3A5F")}}], "label": [{"properties": {"fontSize": literal("10D")}}]}
            visuals[identity] = card
        footer = new_text(visuals["00c6198092a372ab0910"], "retail_insights_limitations", ["Customer rankings exclude unknown IDs; their sales remain in commercial totals. Coverage cards use the current selection.", "Negative movements show cancellations / reversion postings. The source cannot establish physical returns, delivery or customer dissatisfaction."], 208, 834, 1110, 68, 10)
        visuals[footer["name"]] = footer
        template = visuals["00c6198092a372ab0910"]
    sidebar = new_text(template, "retail_filter_scope", ["Selectors sync across", "both pages.", "", "Clear selectors resets", "Year, Country and", "Line Type.", "", "Charts filter this page.", "Click a selected mark", "again to clear it.", "", "Commercial KPIs are", "blank for Adjustment", "and Gift Voucher."], 32, 490, 144, 350, 9, "#FFFFFF")
    visuals[sidebar["name"]] = sidebar
    quantitative = [j for j in visuals.values() if j["visual"]["visualType"] in {"cardVisual", "tableEx", "clusteredBarChart", "clusteredColumnChart", "lineChart", "scatterChart"}]
    charts = [j for j in quantitative if j["visual"]["visualType"] not in {"cardVisual", "tableEx"}]
    slicers = [j for j in visuals.values() if j["visual"]["visualType"] == "slicer"]
    interactions = [{"source": source["name"], "target": target["name"], "type": "DataFilter"} for source in charts + slicers for target in quantitative if source["name"] != target["name"]]
    interactions += [{"source": source["name"], "target": target["name"], "type": "NoFilter"} for source in charts for target in slicers]
    p["visualInteractions"] = interactions
    for i, j in enumerate(sorted(visuals.values(), key=lambda v: (v["position"]["y"], v["position"]["x"], v["position"]["z"]))):
        # Keep query metadata consistent with the model instead of retaining old
        # numeric-only formats that can override currency in tooltips/labels.
        formats = json.loads((REPO / "evidence/financial/measure_definitions.json").read_text(encoding="utf-8"))
        for obj in walk(j):
            field = obj.get("field", {}).get("Measure", {})
            if field.get("Property") in formats and "format" in obj:
                obj["format"] = formats[field["Property"]]["format"]
        j["position"]["tabOrder"] = i * 100
        if j["visual"]["visualType"] not in {"shape", "textbox"}:
            label = j["visual"].get("visualType", "Visual")
            titles = j["visual"].get("visualContainerObjects", {}).get("title", [])
            if titles and "text" in titles[0].get("properties", {}):
                label = titles[0]["properties"]["text"]["expr"]["Literal"]["Value"].strip("'")
            prop(j, "general", "altText", string(label), True)
        save(page, j)
    pagefile.write_text(json.dumps(p, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    changes.append({"page": p["displayName"], "visuals": len(visuals), "height": p["height"], "chart_selections": "DataFilter to metrics; NoFilter to slicers", "slicer_groups": [v["visual"]["syncGroup"] for v in slicers]})
(REPO / "evidence/validation/phase3-authoring.json").write_text(json.dumps({"native_rendered": False, "pages": changes, "original_visuals_retained": 31, "new_visuals": 7, "removed_visuals": 0, "reason_for_canvas_height": "Fit ten ranking rows, coverage and financial reconciliation without hiding source context"}, indent=2) + "\n", encoding="utf-8")
print("Phase 3 PBIR edits applied to both pages. Native visual/interaction acceptance pending.")
