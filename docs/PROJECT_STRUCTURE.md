# Project structure

Open [uk-online-retail-sales-analysis.pbip](../uk-online-retail-sales-analysis.pbip) in the root. It points to the report in `powerbi/`; the report points to the semantic model beside it. Keep these items together when cloning, moving or downloading the project.

## Versioned project

```text
online-retail-sales-analysis/
├── uk-online-retail-sales-analysis.pbip
├── README.md
├── README.es.md
├── LICENSE
├── DATA_LICENSE.md
├── .gitignore
├── .gitattributes
├── requirements-analysis.txt
├── exports/
│   └── uk-online-retail-sales-analysis.pbix
├── powerbi/
│   ├── uk-online-retail-sales-analysis.Report/
│   └── uk-online-retail-sales-analysis.SemanticModel/
├── data/
│   ├── data-dictionary.md
│   └── raw/Online Retail.xlsx
├── docs/
│   ├── SETUP.md
│   ├── METRICS.md
│   ├── MODEL.md
│   ├── VALIDATION.md
│   ├── cleaning-notes.md
│   └── PROJECT_STRUCTURE.md
├── screenshots/
│   ├── sales-overview.png
│   └── product-customer-insights.png
├── scripts/
│   ├── configure_source.py
│   ├── reconcile.py
│   ├── crosscheck_xml.py
│   ├── validate_model.py
│   ├── validate_report.py
│   ├── validate_json.py
│   ├── validate_integrity.py
│   ├── run_validation.py
│   └── tmdl-check/
└── evidence/
    ├── baseline/
    ├── financial/
    └── validation/
```

| Folder | Purpose |
| --- | --- |
| `powerbi/` | Active PBIR report definitions, resources and TMDL semantic model. |
| `exports/` | Optional single-file Power BI Desktop snapshot; PBIP remains the maintained source. |
| `data/` | Unchanged source workbook and current field reference. |
| `docs/` | User procedures, explanations, references and validation scope. |
| `screenshots/` | The two current report images linked from both README files. |
| `scripts/` | Source configuration and supported validation utilities. |
| `evidence/` | Inspectable baseline, financial reconciliation and recorded check results. |

Screenshots remain in their existing folder and keep their filenames. They are presentation assets referenced by the documentation; moving them into `docs/` would add no useful distinction for this project.

## Why evidence is retained

`baseline/` retains the original file manifest, original source profile and original calculation records. The manifest identifies original visuals and the unchanged workbook; the reconciliation supplies original KPI expectations. These are inputs and provenance, not an alternative report.

`financial/` contains the current source reconciliation, before/after values, monthly and country totals, special-code review, product identity and the measure-expression contract. Its CSV and JSON files support the metric definitions without placing large data tables in the README.

`validation/` contains current source/static results and dated native Desktop checks. [Validation](VALIDATION.md) distinguishes their scope and explains the retained refresh attempt and the schema snapshot associated with a native visual test. Superseded phases and authoring attempts are not part of the maintained documentation.

## Local generated content

| Local location | Purpose |
| --- | --- |
| `backups/` | Recovery ZIP files, the original PBIX snapshot and local backup verification. |
| `.cache/` | Source-data cache and detailed validation logs. |
| `.tools/` | Python dependencies, NuGet packages, .NET state and cached JSON schemas. |
| `**/.pbi/` | Desktop settings and loaded-model cache. |
| `**/bin/`, `**/obj/`, `**/__pycache__/` | Rebuildable compilation and Python output. |

These locations remain available locally and are excluded by [.gitignore](../.gitignore). Local virtual environments, editor settings and operating-system temporary files are excluded as well. A fresh clone obtains dependencies and refreshes the model; it does not require another person's caches or recovery copies.

The supported checks write concise results to `evidence/validation/` and full diagnostics to `.cache/validation/`. Optional recovery verification writes only under `backups/`.

## Documentation organization

The README is an entry point; detailed procedures, metric meanings, model relationships and validation scope each have a dedicated page. Field-level rules have their home in the data dictionary. This follows the reader-intent and progressive-detail guidance in [Repository Documentation Readability, guide 0.2](https://github.com/angel-wm/repository-documentation-readability/blob/65c2f82c9e76b4340320618e42a7e3a59332ffe7/GUIDE.md), without imposing its examples as a mandatory folder template.
