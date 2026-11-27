[Read in English](VALIDATION.md) · [Inicio en español](../README.es.md)

# Validación y alcance de las comprobaciones

El proyecto comprueba por separado la reconstrucción desde Excel, las definiciones estáticas, las consultas DAX nativas y el reporte renderizado. Los resultados de cada comprobación tienen un alcance específico. [Métricas](METRICS.es.md) · [Configuración](SETUP.es.md)

## Ejecutar las comprobaciones

Desde la raíz, usa Python 3.12 y .NET SDK 8. La primera descarga de dependencias y esquemas requiere conexión. El proceso genera evidencias y registros locales a partir del Excel y las definiciones del proyecto.

```powershell
python -m pip install -r requirements-analysis.txt
$env:NUGET_PACKAGES = (Join-Path (Get-Location) '.tools/nuget')
$env:DOTNET_CLI_HOME = (Join-Path (Get-Location) '.tools/dotnet')
dotnet restore scripts/tmdl-check/TmdlCheck.csproj
python scripts/run_validation.py --fresh
```

Consulta `evidence/validation/validation-run.json` para ver el resultado de tu ejecución. Los detalles están en `.cache/validation/`. Sin `--fresh`, el lector puede usar una caché vinculada al SHA-256 del Excel. Tras un fallo posterior, `--resume-from tmdl` reutiliza los pasos iniciales solo si coinciden el archivo y la implementación comprobada.

| Comprobación | Qué verifica |
| --- | --- |
| [Conciliación](../evidence/financial/before_after.json) y [lectura XML](../evidence/validation/independent_xml.json) | Reconstrucción en peniques y comprobación independiente de totales del XLSX. |
| [Analizador TMDL](../evidence/validation/final-tom.json) y [modelo](../evidence/validation/model-checks.json) | Cinco tablas, tres relaciones, 21 medidas, claves, uniones y 15 contextos reconstruidos. |
| [Reporte PBIR](../evidence/validation/report-checks.json) | Identidad, posiciones, dependencias, filtros e interacciones de los 35 contenedores. |
| [Esquemas](../evidence/validation/final-json-schema.json) | 48 JSON legibles, 41 con esquema exacto, cuatro visuales con esquema compatible 2.13 y tres archivos sin esquema declarado. |
| [Integridad](../evidence/validation/project-integrity.json) | Huella y ZIP del Excel, rutas, licencias, capturas y estructura ZIP del PBIX. |

La ejecución documentada devuelve `PASS_SOURCE_AND_STATIC_CHECKS_WITH_PARTIAL_SCHEMA_COVERAGE`. [Registro versionado](../evidence/validation/validation-run.json)

## GitHub Actions

CI ejecuta el flujo de validación en los pull requests hacia `main`, los pushes a `main` y las ejecuciones manuales. Verifica el marcador portátil de `SourceFilePath` y que coincida el registro versionado de integridad. Los artefactos de cada ejecución duran siete días. CI comprueba el paquete PBIX. La apertura en Desktop, el refresco M, el renderizado y las selecciones interactivas se verifican aparte. [Ejecuciones del flujo](https://github.com/angel-wm/online-retail-sales-analysis/actions/workflows/source-static-validation.yml)

## Comprobaciones en Power BI Desktop

- **Octubre de 2026.** Desktop 2.158.1304.0 ejecutó un refresco de M con los recuentos esperados. La comparación de esa ejecución discrepó en once casos de precisión de `Currency` y tratamiento de `BLANK`. Después de corregir la política de comparación, DAX validó las 17 medidas financieras y de diagnóstico en 15 contextos. [Refresco](../evidence/validation/desktop-native-refresh.json) · [Consultas DAX](../evidence/validation/desktop-native-check.json)
- **Gráficos.** Se contrastaron trece meses y 90 valores de 30 productos de la dispersión. También se observaron ambas páginas y casos seleccionados de filtros. [Meses](../evidence/validation/monthly-chart-check.json) · [Dispersión](../evidence/validation/desktop-scatter-check.json) · [Observación en Desktop](../evidence/validation/scatter-scale-revision.json)
- **27 de noviembre de 2026.** Se renderizaron y capturaron ambas páginas revisadas. El PBIX abre en Sales Overview y las definiciones de páginas y visuales coinciden con el PBIP. El DAX nativo comprobó el conjunto completo, Year 2010, Adjustment y mercados fuera del Reino Unido. Con todos los filtros despejados hay 19.773 facturas y 4.334 clientes identificados. Reino Unido aporta el 84,77 % de ventas netas y dos productos concentran el 51,38 % de los reversos. La vista de 2010 cubre solo diciembre y la vista Adjustment devuelve indicadores en blanco con un mensaje. [Consultas y valores](../evidence/validation/desktop-dashboard-review.json) · [Capturas](../README.es.md#vista-previa-del-dashboard)

## Consultas y pruebas adicionales

Después de ejecutar la validación estática y refrescar el PBIP, identifica el puerto local de Analysis Services de ese proyecto:

```powershell
$retailDesktopPort = Read-Host 'Puerto local de Analysis Services para este PBIP'
dotnet run --no-restore --project scripts/tmdl-check/TmdlCheck.csproj -- --desktop $retailDesktopPort evidence/validation/desktop-native-check.json
```

También puedes usar `--monthly` o `--scatter` con sus respectivos archivos de salida. Solo `--desktop --refresh` solicita un refresco completo de M. [Ejemplos DAX](../evidence/validation/desktop-queries.dax)

Quedan fuera de la cobertura completa las combinaciones de selectores y selecciones múltiples, la matriz de interacciones, los empates de Top N, el diseño al 100 %, la accesibilidad, el rendimiento, la vista móvil y Power BI Service. Al distribuir una nueva exportación, repite la apertura y compara sus dos páginas y valores con el PBIP. [Actualizar la exportación](SETUP.es.md#actualizar-el-pbix-exportado)

La verificación opcional de recuperación usa `python scripts/validate_integrity.py --local-recovery` y requiere los archivos originales y el manifiesto local en `backups/`. Las comprobaciones normales funcionan desde una copia completa del repositorio.
