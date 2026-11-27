# Open the Power BI project

Open the [PBIX snapshot](../exports/uk-online-retail-sales-analysis.pbix) in Power BI Desktop to explore the report with the included data. It opens on **Sales Overview**. For edits and source refreshes, use [uk-online-retail-sales-analysis.pbip](../uk-online-retail-sales-analysis.pbip) from a complete checkout and follow the procedure below.

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

   The helper sets `SourceFilePath` to this checkout's `data/raw/Online Retail.xlsx`. It changes only the parameter in `expressions.tmdl`; it does not edit the workbook. The stored path is machine-specific, so repeat this step after moving or cloning the project.

3. Open `uk-online-retail-sales-analysis.pbip` from the repository root.
4. Select **Refresh** in Desktop and wait for it to finish. Loaded data and Desktop state in `.pbi/` are local and excluded from Git; a new checkout must refresh from the Excel file.
5. Confirm both pages load: **Sales Overview** and **Product & Customer Insights**. With all selectors cleared, compare the report with the [documented metrics](METRICS.md#reference-values) and [current screenshots](../README.md#dashboard-preview).
6. Save in Desktop before closing if you want to retain the local loaded-data cache.

Alternatively, set **SourceFilePath** through Power Query's **Manage Parameters**, choose the local Excel file, then apply the change and refresh. The helper's default source is the versioned workbook; an alternative workbook may change the results.

## Explore the report

Year, Country and Line Type selectors are synchronized across both pages. To compare markets outside the UK, open **Country**, choose **Select all**, and deselect **United Kingdom**. Select a chart mark to filter the cards and other charts on that page, then select the mark again to clear it. **Clear selectors** resets Year, Country and Line Type. Clear chart marks separately.

The line beneath each page title shows the selected calendar period. It also explains when a selection has no eligible merchandise activity. The asterisk on the monthly charts identifies an incomplete final source month.

The rankings use net merchandise sales or merchandise reversal value, as their titles indicate. Product labels combine stock code with a representative source description. The scatter plot uses gross sales on X, reversal value on a logarithmic Y axis and sale-invoice count for bubble size. Read [metric interpretation](METRICS.md) before comparing periods or treating a reversal as a physical return.

## Troubleshooting

### The Excel source cannot be found

The stored parameter points to another checkout or machine. Close the project, run the configuration helper from the current root, reopen the PBIP and refresh. Confirm `SourceFilePath` names the workbook that actually exists in `data/raw/`.

### Desktop opens but the report does not load

Confirm both `powerbi/` item folders were downloaded and open the root PBIP. Record the full Desktop error if loading still fails. The [source and static checks](VALIDATION.md#run-source-and-static-checks) can identify invalid JSON, misplaced visual definitions and broken references; a successful static check does not establish that Desktop renders the report.

### The charts are empty in a new checkout

Run **Refresh** and wait for completion, then clear Year, Country and Line Type. Confirm the Excel parameter and check for a query error. Administrative or gift-voucher selections can legitimately leave merchandise measures blank; see [filter and blank behavior](METRICS.md#filters-and-blank-values).

### December drops sharply in the monthly charts

The source ends on 9 December 2011. Both monthly charts mark the final month with an asterisk and show the source cutoff when that month is selected. Use the [documented period comparison](METRICS.md#period-coverage) when interpreting it.

## Refresh the PBIX export

After an accepted report change, refresh the model from the versioned Excel source, clear chart selections and selectors, and open **Sales Overview**. Use **File > Save as** in Desktop to update the snapshot in `exports/`. Reopen the PBIX and check its starting page, both report pages and the reference values. Capture the two previews from the same version when the visuals change. See Microsoft's [Desktop conversion workflow](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview#frequently-asked-questions).

For developer checks, continue to [Validation](VALIDATION.md). For folder purposes, see [Project structure](PROJECT_STRUCTURE.md).
