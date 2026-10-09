# Reproducir la revisión

El acceso editable es `uk-online-retail-sales-analysis.pbip` en la raíz; sus componentes están en `powerbi`. Su fuente es el Excel versionado en `data/raw`; el Excel no se edita. Los scripts de validación sólo escriben resultados en evidence y cachés locales ignoradas. La revisión se realizó con Python 3.12.14 y .NET SDK 8.0.425; [requirements-analysis.txt](../../requirements-analysis.txt) fija las versiones Python utilizadas. El parser oficial se fija en el proyecto C# a Microsoft.AnalysisServices 19.114.12.

Desde la raíz de un checkout, con Python 3.12, .NET 8 y acceso de red para dependencias/esquemas:

```powershell
python -m pip install -r requirements-analysis.txt
$env:NUGET_PACKAGES = (Join-Path (Get-Location) '.tools/nuget')
$env:DOTNET_CLI_HOME = (Join-Path (Get-Location) '.tools/dotnet')
dotnet restore scripts/tmdl-check/TmdlCheck.csproj
python scripts/configure_source.py
python scripts/run_validation.py --fresh
```

`dotnet restore` y el runner deben compartir la caché NuGet. Las variables del bloque fijan los mismos directorios locales aislados que usa el runner.

Para la aceptación nativa seguir [DESKTOP_ACCEPTANCE.md](DESKTOP_ACCEPTANCE.md). Configurar el parámetro con Desktop cerrado antes de abrir el PBIP; la utilidad modifica exclusivamente expressions.tmdl. No se afirma que Power Query detecte la ubicación del checkout por sí mismo.

El recálculo compara los 12 KPI originales con la auditoría, calcula los corregidos con céntimos enteros y conserva duplicados. `crosscheck_xml.py` usa otro lector y lógica independiente sobre el XML del XLSX. TOM deserializa TMDL y comprueba referencias del modelo; `validate_model.py` reconstruye dimensión, join, calendario, valores y 15 contextos; `validate_report.py` inspecciona PBIR y dependencias; `validate_json.py` usa esquemas oficiales con cobertura parcial documentada.

`run_validation.py` añade una comprobación de preservación del original local y respaldo. Esta última es específica del directorio recuperado: requiere los respaldos locales en `backups` dentro de la raíz. Comprueba el archivo original dentro del ZIP, la instantánea PBIX, el checkout archivado, la fuente y que sólo exista un PBIP activo; el proyecto principal se edita por autorización del usuario. En otro equipo, ejecutar las comprobaciones portables individualmente, sin fingir que existe ese respaldo:

```powershell
python scripts/reconcile.py --fresh
python scripts/crosscheck_xml.py
dotnet run --no-restore --project scripts/tmdl-check/TmdlCheck.csproj -- powerbi/uk-online-retail-sales-analysis.SemanticModel/definition evidence/validation/final-tom.json
python scripts/validate_model.py
python scripts/validate_report.py
python scripts/validate_json.py --output evidence/validation/final-json-schema.json
```

El recálculo sin `--fresh` verifica el SHA-256 del XLSX antes de reutilizar una caché de datos local; la comprobación XML vuelve a leer el archivo siempre. Las dependencias y esquemas se guardan en `.tools`, los datos derivados grandes en `.cache`. Ambos directorios están ignorados. No hacen falta el PBIX original ni `.pbi` para reproducir las comprobaciones fuente; abrir y actualizar Desktop es una prueba separada.

Los archivos `bootstrap_recovery.py`, `implement_phase1.py`, `implement_phase2.py` e `implement_phase3.py` conservados en `scripts/archive` documentan la operación de autoría inicial. **No son comandos de reproducción y no deben volver a ejecutarse sobre el proyecto editado**, porque pueden reescribir cambios posteriores. Para comprobar la entrega se usan los validadores, no esos scripts de autoría.

## Comprobación nativa local

Con el PBIP principal abierto, localizar el puerto del proceso msmdsrv correspondiente a ese proyecto. `dotnet run --no-restore --project scripts/tmdl-check/TmdlCheck.csproj -- --desktop PUERTO evidence/validation/desktop-native-check.json` consulta únicamente el modelo local. No ejecuta refresh por defecto ni comprueba la interfaz. `--refresh` solicita actualización completa desde la fuente configurada y requiere que se espere hasta su terminación; nunca publica en un servicio. La comprobación usa las expectativas de `model-checks.json` y los tipos nativos, incluyendo Currency de cuatro decimales y BLANK.

Las evidencias actuales separan actualización M completada (`desktop-native-refresh.json`) y contraste DAX final (`desktop-native-check.json`). El guardado de caché y la exportación PBIX deben hacerse en Desktop; el motor Diskless no soporta Backup/Restore por TOM.

Si una ejecución integral falla después de leer el Excel por una dependencia o acceso a esquemas, `python scripts/run_validation.py --resume-from tmdl` conserva los dos pasos de fuente exitosos del recibo anterior, verifica el SHA-256 del Excel y repite las comprobaciones restantes. No reutilizar esa opción si cambió la fuente; ejecutar `--fresh`.
