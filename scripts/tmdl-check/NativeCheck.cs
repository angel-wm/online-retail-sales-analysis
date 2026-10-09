using Microsoft.AnalysisServices.Tabular;
using Microsoft.AnalysisServices.AdomdClient;
using System.Text.Json;

internal static class NativeCheck {
    public static int RunMonthly(string[] args) {
        var output = Path.GetFullPath(args[2]);
        var receipt = new Dictionary<string, object?> {
            ["startedUtc"] = DateTime.UtcNow,
            ["connectionScope"] = "Power BI Desktop local engine only",
            ["population"] = "All loaded dates, countries and line types, without additional report selections",
            ["nativeRefreshRequested"] = false,
            ["modelModified"] = false,
            ["reportRenderingOrInteractionsTested"] = false
        };
        try {
            if (args.Length != 3)
                throw new ArgumentException("Usage: TmdlCheck --monthly <local port> <output json>");
            var port = ushort.Parse(args[1]);
            if (port == 0) throw new ArgumentException("Invalid local port");
            using var server = new Server();
            server.Connect($"Data Source=localhost:{port};Timeout=300");
            var db = server.Databases.Cast<Database>().Single(d => d.Model?.Tables.Contains("Online Retail") == true && d.Model.Tables.Contains("DimProduct"));
            receipt["sourceFilePath"] = db.Model.Expressions["SourceFilePath"].Expression;
            receipt["categorySortByColumn"] = db.Model.Tables["Calendar"].Columns["YearMonth_Label"].SortByColumn?.Name;
            using var connection = new AdomdConnection($"Data Source=localhost:{port};Initial Catalog={db.ID}");
            connection.Open();
            const string query = """
                EVALUATE
                SUMMARIZECOLUMNS(
                    'Calendar'[YearMonthSort],
                    'Calendar'[YearMonth_Label],
                    "GrossGBP", [Main Sales],
                    "ReversalsGBP", [Returns Amount],
                    "NetGBP", [Net Sales],
                    "Orders", [Orders],
                    "FactRows", COUNTROWS('Online Retail'),
                    "FirstInvoice", MIN('Online Retail'[Invoice_Date]),
                    "LastInvoice", MAX('Online Retail'[Invoice_Date]),
                    "CalendarDays", COUNTROWS('Calendar'),
                    "TransactionDays", DISTINCTCOUNT('Online Retail'[Invoice_Day])
                )
                ORDER BY 'Calendar'[YearMonthSort]
                """;
            using var command = connection.CreateCommand();
            command.CommandTimeout = 120;
            command.CommandText = query;
            using var reader = command.ExecuteReader();
            var monthly = new List<Dictionary<string, object?>>();
            while (reader.Read())
                monthly.Add(Enumerable.Range(0, reader.FieldCount).ToDictionary(i => reader.GetName(i), i => reader.IsDBNull(i) ? null : reader.GetValue(i)));
            if (monthly.Count != 13) throw new InvalidOperationException($"Expected 13 source months; obtained {monthly.Count}");
            receipt["query"] = query;
            receipt["monthly"] = monthly;
            receipt["nativeDaxExecuted"] = true;
            receipt["status"] = "PASS_NATIVE_MONTHLY_QUERY";
        } catch (Exception exception) {
            receipt["status"] = "FAIL_OR_INCOMPLETE_NATIVE_MONTHLY_QUERY";
            receipt["error"] = exception.ToString();
        }
        receipt["finishedUtc"] = DateTime.UtcNow;
        Directory.CreateDirectory(Path.GetDirectoryName(output)!);
        File.WriteAllText(output, System.Text.Json.JsonSerializer.Serialize(receipt, new JsonSerializerOptions { WriteIndented = true }) + "\n");
        Console.WriteLine($"Native monthly check: {receipt["status"]}. Receipt: {output}");
        if (receipt.TryGetValue("error", out var error)) Console.WriteLine(error);
        return receipt["status"]!.ToString()!.StartsWith("PASS") ? 0 : 1;
    }

    public static int Run(string[] args) {
        var output = Path.GetFullPath(args[2]);
        var receipt = new Dictionary<string, object?> {
            ["startedUtc"] = DateTime.UtcNow,
            ["connectionScope"] = "Power BI Desktop local engine only",
            ["reportRenderingOrInteractionsTested"] = false,
            ["pbixExported"] = false
        };
        try {
            if (args.Length != 3 && !(args.Length == 4 && args[3] == "--refresh"))
                throw new ArgumentException("Usage: TmdlCheck --desktop <local port> <output json> [--refresh]");
            var port = ushort.Parse(args[1]);
            if (port == 0) throw new ArgumentException("Invalid local port");
            using var server = new Server();
            server.Connect($"Data Source=localhost:{port};Timeout=300");
            var db = server.Databases.Cast<Database>().Single(d => d.Model?.Tables.Contains("Online Retail") == true && d.Model.Tables.Contains("DimProduct"));
            receipt["nativeModelLoaded"] = true;
            receipt["tables"] = db.Model.Tables.Select(t => new { name = t.Name, partitions = t.Partitions.Select(p => new { name = p.Name, state = p.State.ToString() }).ToArray(), columns = t.Columns.Count, measures = t.Measures.Count }).ToArray();
            receipt["sourceFilePath"] = db.Model.Expressions["SourceFilePath"].Expression;
            receipt["measureDataTypes"] = db.Model.Tables["Online Retail"].Measures.ToDictionary(m => m.Name, m => m.DataType.ToString());
            receipt["comparisonPolicy"] = "Currency measures are compared at the native fixed-decimal scale of four digits; other numeric measures retain source precision. BLANK is distinct from zero.";
            receipt["nativeRefreshRequested"] = args.Contains("--refresh");
            if (args.Contains("--refresh")) {
                db.Model.RequestRefresh(RefreshType.Full);
                db.Model.SaveChanges();
                receipt["nativeMRefreshCompleted"] = true;
            }
            using var connection = new AdomdConnection($"Data Source=localhost:{port};Initial Catalog={db.ID}");
            connection.Open();
            Dictionary<string, object?> Query(string dax) {
                using var command = connection.CreateCommand();
                command.CommandTimeout = 120;
                command.CommandText = dax;
                using var reader = command.ExecuteReader();
                if (!reader.Read()) throw new InvalidOperationException("Query returned no rows");
                return Enumerable.Range(0, reader.FieldCount).ToDictionary(i => reader.GetName(i).Trim('[', ']'), i => reader.IsDBNull(i) ? null : reader.GetValue(i));
            }
            var counts = Query("EVALUATE ROW(\"fact\", COUNTROWS('Online Retail'), \"product\", COUNTROWS('DimProduct'), \"calendar\", COUNTROWS('Calendar'))");
            receipt["rowCounts"] = counts;
            if (Convert.ToInt64(counts["fact"]) != 540455 || Convert.ToInt64(counts["product"]) != 3848 || Convert.ToInt64(counts["calendar"]) != 374)
                throw new InvalidOperationException("Native table counts differ from the Excel reconciliation");
            var filters = new Dictionary<string, string> {
                ["All"] = "",
                ["Year 2010"] = "'Calendar'[Year] = 2010",
                ["Year 2011"] = "'Calendar'[Year] = 2011",
                ["Netherlands"] = "'Online Retail'[Country] = \"Netherlands\"",
                ["Germany"] = "'Online Retail'[Country] = \"Germany\"",
                ["United Kingdom"] = "'Online Retail'[Country] = \"United Kingdom\"",
                ["Adjustment"] = "'Online Retail'[Line_Type] = \"Adjustment\"",
                ["Gift Voucher"] = "'Online Retail'[Line_Type] = \"Gift Voucher\"",
                ["Product"] = "'Online Retail'[Line_Type] = \"Product\"",
                ["Customer 12347"] = "'Online Retail'[Customer_ID] = \"12347\"",
                ["Unknown customer"] = "'Online Retail'[Customer_ID] = BLANK()",
                ["Reversal invoice C581484"] = "'Online Retail'[Invoice_ID] = \"C581484\"",
                ["Stock 23843"] = "'DimProduct'[Stock_Code] = \"23843\"",
                ["Stock 85123A"] = "'DimProduct'[Stock_Code] = \"85123A\"",
                ["Empty"] = "FILTER('Online Retail', FALSE())"
            };
            var measures = db.Model.Tables["Online Retail"].Measures.Select(m => m.Name).ToArray();
            var row = "ROW(" + string.Join(", ", measures.Select(m => $"\"{m}\", [{m}]")) + ")";
            using var expected = JsonDocument.Parse(File.ReadAllText("evidence/validation/model-checks.json"));
            var scenarios = new List<object>();
            var differences = new List<object>();
            foreach (var context in expected.RootElement.GetProperty("scenarios").EnumerateArray()) {
                var name = context.GetProperty("context").GetString()!;
                var filter = filters[name];
                var query = "EVALUATE " + (filter.Length == 0 ? row : $"CALCULATETABLE({row}, {filter})");
                var actual = Query(query);
                foreach (var measure in context.GetProperty("expected_from_source").EnumerateObject()) {
                    var value = actual[measure.Name];
                    var expectedBlank = measure.Value.ValueKind == JsonValueKind.Null;
                    var expectedValue = expectedBlank ? 0 : measure.Value.GetDouble();
                    if (!expectedBlank && db.Model.Tables["Online Retail"].Measures[measure.Name].DataType == DataType.Decimal)
                        expectedValue = (double)decimal.Round((decimal)expectedValue, 4, MidpointRounding.ToEven);
                    var agrees = expectedBlank ? value is null : value is not null && Math.Abs(Convert.ToDouble(value) - expectedValue) <= Math.Max(1e-8, Math.Abs(expectedValue) * 1e-12);
                    if (!agrees) differences.Add(new { context = name, measure = measure.Name, expected = measure.Value.Clone(), actual = value });
                }
                scenarios.Add(new { context = name, query, nativeValues = actual });
            }
            receipt["nativeDaxExecuted"] = true;
            receipt["scenarios"] = scenarios;
            receipt["differences"] = differences;
            if (differences.Count > 0) throw new InvalidOperationException($"{differences.Count} native/source discrepancies");
            receipt["desktopCacheSavedByThisTool"] = false;
            receipt["status"] = args.Contains("--refresh") ? "PASS_NATIVE_REFRESH_AND_DAX" : "PASS_NATIVE_DAX_ON_LOADED_MODEL";
        } catch (Exception exception) {
            receipt["status"] = "FAIL_OR_INCOMPLETE_NATIVE_CHECK";
            receipt["error"] = exception.ToString();
        }
        receipt["finishedUtc"] = DateTime.UtcNow;
        Directory.CreateDirectory(Path.GetDirectoryName(output)!);
        File.WriteAllText(output, System.Text.Json.JsonSerializer.Serialize(receipt, new JsonSerializerOptions { WriteIndented = true }) + "\n");
        Console.WriteLine($"Native check: {receipt["status"]}. Receipt: {output}");
        if (receipt.TryGetValue("error", out var error)) Console.WriteLine(error);
        return receipt["status"]!.ToString()!.StartsWith("PASS") ? 0 : 1;
    }
}
