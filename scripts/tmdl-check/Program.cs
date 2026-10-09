using Microsoft.AnalysisServices.Tabular;
using System.Text.Json;

if (args.Length >= 3 && args[0] == "--desktop") {
    Environment.ExitCode = NativeCheck.Run(args);
    return;
}

if (args.Length != 2) throw new ArgumentException("Usage: TmdlCheck <definition folder> <output json>");
var db = TmdlSerializer.DeserializeDatabaseFromFolder(Path.GetFullPath(args[0]));
var result = new {
    status = "PASS",
    parser = "Microsoft.AnalysisServices.Tabular.TmdlSerializer",
    parserAssembly = typeof(TmdlSerializer).Assembly.FullName,
    engineExecution = false,
    compatibilityLevel = db.CompatibilityLevel,
    tables = db.Model.Tables.Select(t => new {
        name = t.Name,
        columns = t.Columns.Select(c => new { name = c.Name, type = c.DataType.ToString(), summarizeBy = c.SummarizeBy.ToString(), hidden = c.IsHidden }),
        measures = t.Measures.Select(m => new { name = m.Name, expression = m.Expression, format = m.FormatString, description = m.Description }),
        partitions = t.Partitions.Select(p => new { name = p.Name, mode = p.Mode.ToString(), sourceType = p.Source?.GetType().Name })
    }),
    relationships = db.Model.Relationships.OfType<SingleColumnRelationship>().Select(r => new {
        name = r.Name, fromTable = r.FromColumn.Table.Name, fromColumn = r.FromColumn.Name,
        toTable = r.ToColumn.Table.Name, toColumn = r.ToColumn.Name,
        fromCardinality = r.FromCardinality.ToString(), toCardinality = r.ToCardinality.ToString(),
        crossFiltering = r.CrossFilteringBehavior.ToString(), active = r.IsActive
    }),
    expressions = db.Model.Expressions.Select(e => new { name = e.Name, kind = e.Kind.ToString(), expression = e.Expression })
};
Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(args[1]))!);
File.WriteAllText(args[1], System.Text.Json.JsonSerializer.Serialize(result, new JsonSerializerOptions { WriteIndented = true }));
Console.WriteLine($"TMDL PASS: {db.Model.Tables.Count} tables, {db.Model.Relationships.Count} relationships, {db.Model.Tables.Sum(t => t.Measures.Count)} measures. No DAX/M execution.");
