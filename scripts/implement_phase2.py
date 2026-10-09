"""One-time maintainability migration; preserves Phase 1 financial predicates."""
from pathlib import Path
import json
import re
import uuid

REPO = Path(__file__).resolve().parents[1]
MODEL_ROOT = REPO / "powerbi/project/uk-online-retail-sales-analysis.SemanticModel"
MODEL = MODEL_ROOT / "definition"
fact = MODEL / "tables/Online Retail.tmdl"
s = fact.read_text(encoding="utf-8")
source = '''let
    Source = Excel.Workbook(File.Contents(SourceFilePath), null, true),
    Sheet = Source{[Item="Online Retail", Kind="Sheet"]}[Data],
    Headers = Table.PromoteHeaders(Sheet, [PromoteAllScalars=true]),
    Renamed = Table.RenameColumns(Headers, {{"InvoiceNo", "Invoice_ID"}, {"StockCode", "Stock_Code"}, {"Description", "Product_Name"}, {"InvoiceDate", "Invoice_Date"}, {"UnitPrice", "Unit_Price"}, {"CustomerID", "Customer_ID"}}),
    Typed = Table.TransformColumnTypes(Renamed, {{"Invoice_ID", type text}, {"Stock_Code", type text}, {"Product_Name", type text}, {"Quantity", Int64.Type}, {"Invoice_Date", type datetime}, {"Unit_Price", type number}, {"Customer_ID", type text}, {"Country", type text}}, "en-GB"),
    // Preserve the original quality rule: 1,454 null descriptions, total amount GBP 0.
    Described = Table.SelectRows(Typed, each [Product_Name] <> null),
    Codes = Table.TransformColumns(Described, {{"Stock_Code", each Text.Upper(Text.Trim(_)), type text}}),
    LineType = Table.AddColumn(Codes, "Line_Type", each
        let code = [Stock_Code], name = Text.Upper(Text.Trim([Product_Name]))
        in if Text.StartsWith(code, "GIFT_") or Text.Contains(name, "GIFT VOUCHER") then "Gift Voucher"
        else if List.Contains({"M", "S", "POST", "AMAZONFEE", "AMAZON FEE", "BANK CHARGES", "D", "DOT", "C2", "B", "CRUK"}, code) or name = "EBAY" then "Adjustment"
        else "Product", type text),
    Day = Table.AddColumn(LineType, "Invoice_Day", each Date.From([Invoice_Date]), type date),
    Quality = Table.AddColumn(Day, "Record_Flag", each
        let name = Text.Upper(Text.Trim([Product_Name])),
            hasCustomer = [Customer_ID] <> null and Text.Trim([Customer_ID]) <> "",
            manual = Text.StartsWith(name, "*") and not hasCustomer,
            operational = not hasCustomer and List.AnyTrue(List.Transform({"?", "MISSING", "LOST", "DAMAGE", "DISPLAY", "SOLD AS SETS"}, (word) => Text.Contains(name, word))) and ([Unit_Price] = null or [Unit_Price] = 0)
        in if manual then "Manual / Review" else if operational then "Operational / Non-Product" else "Normal", type text),
    Cancelled = Table.AddColumn(Quality, "Is_Cancelled", each [Invoice_ID] <> null and Text.StartsWith(Text.Upper(Text.Trim([Invoice_ID])), "C"), type logical),
    Negative = Table.AddColumn(Cancelled, "Is_Negative_Qty", each [Quantity] <> null and [Quantity] < 0, type logical),
    ZeroPrice = Table.AddColumn(Negative, "Is_Zero_Price", each [Unit_Price] <> null and [Unit_Price] = 0, type logical),
    // Keep original rounding after quantity x full-precision price, with explicit half-even policy.
    Amount = Table.AddColumn(ZeroPrice, "Sales_Amount", each if [Quantity] = null or [Unit_Price] = null then null else Number.Round([Quantity] * [Unit_Price], 2, RoundingMode.ToEven), Currency.Type),
    GrossEligible = Table.AddColumn(Amount, "Include_In_Main_Analysis", each [Line_Type] = "Product" and [Record_Flag] = "Normal" and not [Is_Cancelled] and [Quantity] > 0 and [Unit_Price] > 0, type logical),
    ReversalEligible = Table.AddColumn(GrossEligible, "Is_Merchandise_Reversal", each [Line_Type] = "Product" and [Record_Flag] = "Normal" and [Quantity] < 0 and [Unit_Price] > 0, type logical),
    Movement = Table.AddColumn(ReversalEligible, "Movement_Type", each if [Include_In_Main_Analysis] then "Merchandise sale" else if [Is_Merchandise_Reversal] then "Merchandise cancellation / reversal" else if [Line_Type] = "Adjustment" then "Administrative adjustment" else if [Line_Type] = "Gift Voucher" then "Gift voucher movement" else "Other / excluded movement", type text)
in
    Movement'''
ix = s.index("\tpartition 'Online Retail' = m")
s = s[:ix] + "\tpartition 'Online Retail' = m\n\t\tmode: import\n\t\tsource =\n" + "\n".join("\t\t\t\t" + line for line in source.splitlines()) + "\n\n\tannotation PBI_NavigationStepName = Navigation\n\n\tannotation PBI_ResultType = Table\n"
column_blocks = list(re.finditer(r"(?m)^\tcolumn ([^\n]+).*?(?=^\t(?:column|partition) |\Z)", s, re.S))
for block in reversed(column_blocks):
    name = block.group(1).strip()
    content = block.group(0)
    if name == "Sales_Amount":
        content = content.replace("dataType: double", "dataType: decimal")
        content = content.replace("\t\tlineageTag:", "\t\tformatString: £#,0.00;(£#,0.00);£0.00\n\t\tlineageTag:", 1)
        content = re.sub(r"\n\t\tannotation PBI_FormatHint = .*", "", content)
    if name == "Unit_Price":
        content = content.replace("summarizeBy: sum", "summarizeBy: none")
        content = content.replace("\t\tlineageTag:", "\t\tformatString: £0.0000\n\t\tlineageTag:", 1)
    if name in {"Product_Name", "Stock_Code", "Record_Flag", "Is_Cancelled", "Is_Negative_Qty", "Is_Zero_Price", "Sales_Amount", "Include_In_Main_Analysis", "Is_Merchandise_Reversal", "Movement_Type"}:
        content = content.replace("\n\t\tdataType:", "\n\t\tisHidden\n\t\tdataType:", 1)
    s = s[:block.start()] + content + s[block.end():]
fact.write_text(s, encoding="utf-8")

expressions = f'''/// Full path to the unchanged source workbook. Set in Manage parameters or with scripts/configure_source.py.
expression SourceFilePath = "{REPO / 'data/raw/Online Retail.xlsx'}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
\tlineageTag: {uuid.uuid5(uuid.NAMESPACE_URL, 'retail/expression/SourceFilePath')}
\tannotation PBI_ResultType = Text
'''
(MODEL / "expressions.tmdl").write_text(expressions, encoding="utf-8")

product_source = '''let
    Source = #"Online Retail",
    Columns = Table.SelectColumns(Source, {"Stock_Code", "Product_Name", "Include_In_Main_Analysis"}),
    Normalized = Table.TransformColumns(Columns, {{"Product_Name", each Text.Upper(Text.Trim(_)), type text}}),
    Products = Table.Group(Normalized, {"Stock_Code"}, {
        {"Product_Name", each
            let Sales = Table.SelectRows(_, each [Include_In_Main_Analysis]),
                Candidates = if Table.IsEmpty(Sales) then _ else Sales,
                Frequency = Table.Group(Candidates, {"Product_Name"}, {{"Count", each Table.RowCount(_), Int64.Type}}),
                MaxCount = List.Max(Frequency[Count]),
                Tied = Table.SelectRows(Frequency, each [Count] = MaxCount)[Product_Name]
            in List.First(List.Sort(Tied, Comparer.Ordinal)), type text},
        {"Description_Variants", each List.Count(List.Distinct([Product_Name])), Int64.Type}
    }),
    Labels = Table.AddColumn(Products, "Product_Label", each [Stock_Code] & " — " & [Product_Name], type text)
in
    Labels'''
lineage = str(uuid.uuid5(uuid.NAMESPACE_URL, "retail/table/DimProduct"))
dim = f"/// One row per stock code. Representative source description; not an authoritative product master.\ntable DimProduct\n\tlineageTag: {lineage}\n\n"
for name, dtype in [("Stock_Code", "string"), ("Product_Name", "string"), ("Product_Label", "string"), ("Description_Variants", "int64")]:
    dim += f"\tcolumn {name}\n\t\tdataType: {dtype}\n"
    if name == "Stock_Code":
        dim += "\t\tisKey\n"
    dim += f"\t\tlineageTag: {uuid.uuid5(uuid.NAMESPACE_URL, 'retail/dimproduct/' + name)}\n\t\tsummarizeBy: none\n\t\tsourceColumn: {name}\n\n"
dim += "\tpartition DimProduct = m\n\t\tmode: import\n\t\tsource =\n" + "\n".join("\t\t\t\t" + line for line in product_source.splitlines()) + "\n\n\tannotation PBI_ResultType = Table\n"
(MODEL / "tables/DimProduct.tmdl").write_text(dim, encoding="utf-8")

model_path = MODEL / "model.tmdl"
model = model_path.read_text(encoding="utf-8")
model = model.replace('annotation PBI_QueryOrder = ["Online Retail"]', 'annotation PBI_QueryOrder = ["SourceFilePath","Online Retail","DimProduct"]')
model = model.replace("ref table Calendar", "ref table Calendar\nref table DimProduct\n\nref expression SourceFilePath")
model_path.write_text(model.rstrip() + "\n", encoding="utf-8")
rel_path = MODEL / "relationships.tmdl"
rels = rel_path.read_text(encoding="utf-8")
rels = rels.replace("relationship 817c63ef-72e8-d19b-b5ac-8549b2c395b9\n", "relationship 817c63ef-72e8-d19b-b5ac-8549b2c395b9\n\tfromCardinality: many\n\ttoCardinality: one\n\tcrossFilteringBehavior: oneDirection\n\tisActive: true\n")
rels = rels.rstrip() + f"\n\nrelationship {uuid.uuid5(uuid.NAMESPACE_URL, 'retail/relationship/product')}\n\tfromCardinality: many\n\ttoCardinality: one\n\tcrossFilteringBehavior: oneDirection\n\tisActive: true\n\tfromColumn: 'Online Retail'.Stock_Code\n\ttoColumn: DimProduct.Stock_Code\n"
rel_path.write_text(rels, encoding="utf-8")
cal_path = MODEL / "tables/Calendar.tmdl"
cal = cal_path.read_text(encoding="utf-8").replace("summarizeBy: sum", "summarizeBy: none").replace("[invoice_day]", "[Invoice_Day]")
cal_path.write_text(cal.rstrip() + "\n", encoding="utf-8")
diagram_path = MODEL_ROOT / "diagramLayout.json"
diagram = json.loads(diagram_path.read_text(encoding="utf-8"))
diagram["diagrams"][0]["nodes"].append({"location": {"x": 270, "y": 0}, "nodeIndex": "DimProduct", "nodeLineageTag": lineage, "size": {"height": 240, "width": 220}, "zIndex": 3})
diagram_path.write_text(json.dumps(diagram, indent=2) + "\n", encoding="utf-8")
print("Phase 2: configurable source, typed M, one-to-many product dimension, preserved calendar and compatibility date tables.")
