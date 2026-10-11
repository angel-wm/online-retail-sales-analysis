# Open the Power BI project

Use this procedure to open the editable report from a new checkout or after moving the project. The editable project's entry point is [uk-online-retail-sales-analysis.pbip](../uk-online-retail-sales-analysis.pbip), in the repository root; the separate [PBIX export](../exports/uk-online-retail-sales-analysis.pbix) is available for single-file viewing.

## Prerequisites

- Windows and Power BI Desktop with PBIP support. This project was opened, refreshed, saved and reopened in **September 2026 Desktop, version 2.158.1304.0**. Other versions have not been verified here.
- The complete repository, including both item folders in `powerbi/` and [the Excel source](../data/raw/Online%20Retail.xlsx). Downloading only the PBIP does not include the report or model.
- Python 3.12 if using the configuration helper below. Its dependencies are Python's standard library; analytical packages are unnecessary for opening the report.

Power BI project definitions and the PBIP entry point are described in [Microsoft's PBIP documentation](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview).

## Configure and open

1. Close this project in Power BI Desktop before changing its source parameter externally.
2. Open a terminal in the repository root and run:

   ```powershell
   python scripts/configure_source.py
   ```

   The repository stores the neutral `SET_LOCAL_ONLINE_RETAIL_XLSX_PATH` placeholder instead of a personal Windows path. This helper sets `SourceFilePath` to this checkout's `data/raw/Online Retail.xlsx`; it changes only `expressions.tmdl` and does not edit the workbook. Run it again after moving or cloning the project.

3. Open `uk-online-retail-sales-analysis.pbip` from the repository root.
4. Select **Refresh** in Desktop and wait for it to finish. Loaded data and Desktop state in `.pbi/` are local and excluded from Git; a new checkout must refresh from the Excel file.
5. Confirm both pages load: **Sales Overview** and **Product & Customer Insights**. With all selectors cleared, compare the report with the [documented metrics](METRICS.md#reference-values) and [current screenshots](../README.md#dashboard-preview).
6. Save in Desktop before closing if you want to retain the local loaded-data cache.

Alternatively, set **SourceFilePath** through Power Query's **Manage Parameters**, choose the local Excel file, then apply the change and refresh. The helper's default source is the versioned workbook; an alternative workbook may change the results.

### Before committing or pushing changes

The helper intentionally changes a **tracked** Power Query parameter to a local absolute path so Desktop can refresh. Keep that path on your machine rather than publishing it. Once Desktop is closed and you have saved the project, restore the neutral repository value:

```powershell
python scripts/configure_source.py --reset
python scripts/configure_source.py --check-repository
git status --short
```

`--reset` changes **only** the PBIP source parameter; it does not modify the Excel, PBIX or semantic calculations. A new refresh of the PBIP requires running `python scripts/configure_source.py` again. GitHub Actions checks that the committed parameter uses the neutral placeholder. Do not run `--reset` while the project is open in Desktop.

If you prefer to keep your local path temporarily while working, stage only your intended files; never commit the modified `expressions.tmdl` with your machine-specific path.

## Explore the report

Year, Country and Line Type selectors are synchronized across both pages. Select a chart mark to filter the cards and other charts on that page; select it again to clear that mark. **Clear selectors** resets the three selectors. Chart selections and the charts' Top N rules have their own behavior; the button is not a universal reset.

The rankings use net merchandise sales or merchandise reversal value, as their titles indicate. Product labels combine stock code with a representative source description. The scatter plot uses gross sales on X, reversal value on a logarithmic Y axis and sale-invoice count for bubble size. Read [metric interpretation](METRICS.md) before comparing periods or treating a reversal as a physical return.

## Troubleshooting

### The Excel source cannot be found

The stored parameter points to another checkout or machine. Close the project, run the configuration helper from the current root, reopen the PBIP and refresh. Confirm `SourceFilePath` names the workbook that actually exists in `data/raw/`.

### Desktop opens but the report does not load

Confirm both `powerbi/` item folders were downloaded and open the root PBIP. Record the full Desktop error if loading still fails. The [source and static checks](VALIDATION.md#run-source-and-static-checks) can identify invalid JSON, misplaced visual definitions and broken references; a successful static check does not establish that Desktop renders the report.

### The charts are empty in a new checkout

Run **Refresh** and wait for completion, then clear Year, Country and Line Type. Confirm the Excel parameter and check for a query error. Administrative or gift-voucher selections can legitimately leave merchandise measures blank; see [filter and blank behavior](METRICS.md#filters-and-blank-values).

### December drops sharply in the monthly chart

The source ends on 9 December 2011. The last monthly point contains a shorter period than November. Keep that point and its partial-month annotation; use the [documented period comparison](METRICS.md#period-coverage) when interpreting it.

## Open the single-file PBIX export

The repository also contains [uk-online-retail-sales-analysis.pbix](../exports/uk-online-retail-sales-analysis.pbix), exported from the corrected report for convenient opening in Power BI Desktop. Download the PBIX directly and open it in Desktop; the PBIP and its item folders remain the maintained, versionable source.

The PBIX is a **snapshot**, not a source of truth for subsequent edits. It may contain a machine-specific Excel source path. To refresh it on another computer, open **Transform data > Edit parameters** (or **Manage Parameters** in Power Query), update `SourceFilePath` to the local `Online Retail.xlsx`, apply changes and refresh. Running `scripts/configure_source.py` edits the PBIP's `expressions.tmdl` and **does not update an independently opened PBIX**.

The automated integrity check verifies that the committed PBIX is a readable ZIP package containing model and report entries; it does not prove Desktop can open it or that its rendered visuals match the PBIP. Before distributing or relying on the export, **open the PBIX in Desktop**, verify the two pages, current metrics and filters, and compare it to the source project. If the PBIP changes, regenerate the PBIX with **File > Save as** and repeat that Desktop acceptance check. A local historical PBIX in `backups/` is an earlier snapshot. A PDF export is not included.

For developer checks, continue to [Validation](VALIDATION.md). For folder purposes, see [Project structure](PROJECT_STRUCTURE.md).
