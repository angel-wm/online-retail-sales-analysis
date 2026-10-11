# Validation and acceptance scope

Validation separates calculations reconstructed from the Excel source, checks of the project definitions, native engine queries and observation of the rendered report. A passing source or schema check does not establish that Power BI Desktop refreshed, rendered or applied every interaction correctly.

This page is the status reference. [Metrics](METRICS.md) defines business meaning, and [Setup](SETUP.md) provides the normal opening procedure.

## Run source and static checks

### Prerequisites

Run from the repository root with **Python 3.12**, **.NET SDK 8** and network access for the first dependency and schema download. The recorded environment used Python 3.12.14 and .NET SDK 8.0.425. Python packages are pinned in [requirements-analysis.txt](../requirements-analysis.txt); the [C# project](../scripts/tmdl-check/TmdlCheck.csproj) pins Microsoft Analysis Services libraries to 19.114.12.

These checks do not require an open Desktop session, a loaded-data cache, Git history or local backups. Git's whitespace check runs additionally when the directory is a Git checkout. The runner writes derived financial and validation results, plus ignored local caches; it does not edit the Excel, report or semantic model.

Power BI Desktop adds terminal blank lines when saving TMDL. [.gitattributes](../.gitattributes) permits that native formatting for TMDL while retaining checks for trailing spaces and indentation spacing. The check does not normalize or rewrite the model.

### Procedure

1. Install the pinned Python packages:

   ```powershell
   python -m pip install -r requirements-analysis.txt
   ```

2. Configure and restore the .NET dependencies in the same local directories used by the runner:

   ```powershell
   $env:NUGET_PACKAGES = (Join-Path (Get-Location) '.tools/nuget')
   $env:DOTNET_CLI_HOME = (Join-Path (Get-Location) '.tools/dotnet')
   dotnet restore scripts/tmdl-check/TmdlCheck.csproj
   ```

3. Run all source and definition checks:

   ```powershell
   python scripts/run_validation.py --fresh
   ```

4. Read the generated `evidence/validation/validation-run.json` for the **run you just executed**. The [committed snapshot](../evidence/validation/validation-run.json) records an earlier local run; it is not continuously updated by GitHub Actions. Full diagnostic output remains in `.cache/validation/`, excluded from Git.

The current successful status is `PASS_SOURCE_AND_STATIC_CHECKS_WITH_PARTIAL_SCHEMA_COVERAGE`: 46 JSON files parse, 10 use exact declared schemas, 33 visual containers use the documented compatibility schema, and three files have no declared schema. The report schema has exact coverage in this run. Do not describe this as a complete native or exact-schema certification.

Without `--fresh`, the source reader can reuse its SHA-256-keyed local cache; the independent XML reader still reads the workbook. After a downstream failure, `--resume-from tmdl` reuses successful source prerequisites only if the workbook and source-check implementation fingerprints still match. Do not use it to skip a changed source or calculation implementation.

### What each check establishes

| Check and result | Scope |
| --- | --- |
| [Source reconciliation](../evidence/financial/before_after.json) | Reconstructs original and current rules using integer pennies; confirms preserved original KPI expectations and the signed financial bridge. |
| [Independent XML crosscheck](../evidence/validation/independent_xml.json) | A second XLSX reader and calculation path checks selected totals. |
| [TMDL parser](../evidence/validation/final-tom.json) | Official TOM deserialization: five tables, three relationships, 17 measures. No DAX or M execution. |
| [Model checks](../evidence/validation/model-checks.json) | Reconstructs keys, joins, calendar, financial values and 15 filter contexts; compares measure expressions and formats with the contract. |
| [Report checks](../evidence/validation/report-checks.json) | Visual identities and types, bounds, references, dependencies, resource paths, Top N and interaction configuration; records all 33 visual hashes. |
| [JSON schema checks](../evidence/validation/final-json-schema.json) | Checks versioned project JSON against exact or explicitly identified compatibility schemas. Desktop's ignored `.pbi` files are outside this scope. |
| [Project integrity](../evidence/validation/project-integrity.json) | Source fingerprint and workbook ZIP integrity, one active root PBIP, resolving item paths, license-document presence, current PNG metadata and the committed PBIX export's ZIP entries. This is not a Power BI Desktop open test. |

The baseline [original manifest](../evidence/baseline/original_manifest.json) identifies the recovered source and original visuals. [Original calculation records](../evidence/baseline/data_reconciliation.json) supply the pre-correction expectations. These inputs remain versioned so another checkout can run the checks without recovery archives.

## Automated checks in GitHub Actions

The [source and static validation workflow](../.github/workflows/source-static-validation.yml) runs on every pull request targeting `main`, push to `main`, and manual `workflow_dispatch`. It uses an Ubuntu runner, Python 3.12, .NET 8, the pinned Python requirements, and the pinned TMDL parser dependencies.

Each run executes:

```text
python scripts/run_validation.py --fresh
```

This re-reads the versioned Excel and checks the source reconciliation, independent XLSX XML crosscheck, official TOM/TMDL deserialization, model invariants and filters, report definitions and dependencies, JSON schemas, project integrity, and Git whitespace. No proprietary Desktop cache or local recovery backup is needed. The committed `SourceFilePath` is a machine-local Power Query parameter and **is not used to refresh M in CI**; configure it when opening the project locally.

The workflow fails if a source/static step exits unsuccessfully. It uploads its validation receipts and step logs as a short-lived GitHub Actions artifact (seven days), including when a validation step fails. Some project schema versions use a documented compatibility schema; `PASS_SOURCE_AND_STATIC_CHECKS_WITH_PARTIAL_SCHEMA_COVERAGE` is therefore a successful *partial-coverage* result, not a claim of exact-schema verification.

### Which receipts are current?

- **Latest CI execution:** use the [GitHub Actions workflow runs](https://github.com/angel-wm/online-retail-sales-analysis/actions/workflows/source-static-validation.yml) and download the `source-static-validation-<run-id>` artifact. Its generated `validation-run.json`, detailed logs and project checks belong to that exact commit and run. Artifacts expire after seven days.
- **Versioned evidence:** committed receipts under `evidence/validation/` are reproducible snapshots and may predate the latest workflow run; inspect their embedded timestamps and scopes rather than treating their presence as live execution.
- **PBIX integrity snapshot:** `project-integrity.json` is regenerated by CI. The workflow now fails if the recomputed receipt differs from the versioned copy, keeping its PBIX presence, package structure and screenshot metadata synchronized with the committed files.
- **Portable PBIP parameter:** CI rejects a committed machine-specific `SourceFilePath`. Configure the path locally before a Desktop refresh and [reset it before committing](SETUP.md#before-committing-or-pushing-changes).

A passing receipt validates only what its flags specify. In particular, `pbix_zip_structure_verified: true` does **not** mean `pbix_desktop_open_verified_by_this_check: true`.

**CI does not open Power BI Desktop, execute M refresh or DAX against a newly loaded native model, render visuals, test interactive selections, or export PBIX/PDF.** For those checks, use the dated Desktop evidence and the remaining acceptance tasks below.

## Recorded Desktop checks

The native receipts were recorded in Power BI Desktop **2.158.1304.0**, with engine timestamps in each JSON and visual-test dates as recorded by the observer. They are dated evidence, not a claim that this documentation update reran Desktop tests.

| Result | Evidence and limit |
| --- | --- |
| Full M refresh completed; expected row counts loaded | [desktop-native-refresh.json](../evidence/validation/desktop-native-refresh.json). The overall attempt failed its original comparison assumptions; see the explanation below. |
| All 17 DAX measures checked in 15 contexts, zero discrepancies under native-type policy | [desktop-native-check.json](../evidence/validation/desktop-native-check.json), retaining the later successful query dated 9 October 2026 UTC. It does not test report interactions. |
| Thirteen monthly observations agree with Excel and chart binding | [monthly-chart-check.json](../evidence/validation/monthly-chart-check.json), supported by [source](../evidence/validation/monthly-source-check.json) and [native monthly query](../evidence/validation/desktop-monthly-check.json). |
| Thirty scatter products, 90 values agree with the source | [scatter-source-check.json](../evidence/validation/scatter-source-check.json) and [native scatter query](../evidence/validation/desktop-scatter-check.json). |
| Both pages rendered, complete headers and cards, ten country rows without scroll, dropdown options visible without hover | [Native visual observation on 9 October](../evidence/validation/report-load-repair.json). Save, close and reopen were observed; full interaction acceptance was not. |
| Log scatter axis, tested 2010 and Bahrain views, scatter focus mode and save/reopen | [Native scatter observation on 10 October](../evidence/validation/scatter-scale-revision.json). Tested selectors were restored to All. |
| Current whole-page previews | [Sales Overview](../screenshots/sales-overview.png) and [Product & Customer Insights](../screenshots/product-customer-insights.png), captured on 10 October 2026 at 1245 × 856 pixels. |

The retained refresh attempt has `nativeMRefreshCompleted: true` and expected fact, product and calendar row counts, but its overall status is `FAIL_OR_INCOMPLETE_NATIVE_CHECK`. Its eleven reported differences came from comparing native Currency AOV against an unquantized quotient and treating a blank known-customer count as zero. The comparison policy was corrected; the later successful DAX receipt uses Currency's four-decimal scale and native BLANK semantics. The failed attempt is retained because it is the direct record of M refresh, and is not relabeled as a pass.

The native scatter revision references [presentation-json-schema.json](../evidence/validation/presentation-json-schema.json), the schema snapshot used for that dated test. Current source/static checks use `final-json-schema.json`; the historical snapshot is retained for provenance, not as a replacement for the current check.

## Optional native query checks

First run the source/static workflow to generate current expectations. Open the correct root PBIP and finish refreshing it. Identify the current local Analysis Services port for that Desktop project; do not use a service endpoint or a port belonging to another report.

The following command asks for that port and performs a read-only DAX check of the loaded model:

```powershell
$retailDesktopPort = Read-Host 'Local Analysis Services port for this open PBIP'
dotnet run --no-restore --project scripts/tmdl-check/TmdlCheck.csproj -- --desktop $retailDesktopPort evidence/validation/desktop-native-check.json
```

The same tool supports `--monthly` and `--scatter` in place of `--desktop`, with their corresponding output filenames. These query modes do not refresh, save or render the report. `--desktop` can request a full M refresh only when the additional `--refresh` flag is supplied; wait for its completion and inspect the overall result.

For manual query-view inspection, [desktop-queries.dax](../evidence/validation/desktop-queries.dax) contains equivalent examples. Query-view execution and all chart interactions were not established by the recorded automated query checks.

### Functional testing reported by the maintainer

The maintainer has reported testing the PBIP and exported PBIX in Power BI Desktop. No separate, itemized acceptance record was supplied for that report, so the repository retains the dated native observations below and does not present the CI ZIP integrity check as a Desktop open test. This section distinguishes that report from the full optional interaction checklist rather than negating the maintainer's testing.

## Remaining Desktop acceptance

The report was rendered and saved/reopened, and selected filter cases were exercised. The following broader checks remain outside the recorded scope:

1. Exercise Year, Country and Line Type synchronization in both directions, including multi-selection and clear behavior under chart selections.
2. Check every configured chart-to-chart and chart-to-card interaction, page navigation and what selections persist. Confirm the selector lists stay stable when a chart mark is selected.
3. Check all dynamic Top N populations and tie cases, full product names and tooltip fields under narrow filters, and known-customer exclusion of blanks. Fewer eligible entries can legitimately produce fewer marks.
4. Review the complete report at 100% zoom and any intended display sizes. Scatter focus mode was checked; that does not cover every visual at 100%.
5. Open the [committed PBIX snapshot](../exports/uk-online-retail-sales-analysis.pbix) separately in Desktop; verify its two pages, refresh behavior, metrics and selected interactions against the maintained PBIP. Regenerate it after any subsequent PBIP changes. No PDF is included. Accessibility, mobile layouts, Power BI Service behavior and performance testing have not been established here.

These limits should travel with any claims about the report. They do not prevent inspecting the PBIP, its current screenshots or the supported numerical checks.

## Optional local recovery verification

Recovery copies are local, ignored by Git and unnecessary for normal validation. On the original workspace, verify them separately:

```powershell
python scripts/validate_integrity.py --local-recovery
```

This requires the original recovered ZIP, original PBIX snapshot, archived checkout and `consolidation-backup.json` inside `backups/`. It verifies the recovered manifest and archive hashes, then writes `backups/recovery-check.json`. It does not assert a branch name, a remote commit or publication status.

The maintained public source is the PBIP, its item folders, source, documentation, screenshots and retained evidence; `exports/` contains the optional PBIX snapshot. A Power BI Service deployment is a separate publication action; it is not performed by any validation command.
