# Proyecto principal y organización de archivos

El acceso de trabajo es `uk-online-retail-sales-analysis.pbip`, directamente en la raíz. Sus componentes están en `powerbi/`; la fuente Excel está en `data/raw/`. Se consolidaron aquí las correcciones realizadas previamente en `review`, manteniendo la identidad del reporte, las dos páginas, los 31 visuales originales y las correcciones financieras. No existe otro proyecto PBIP activo.

```text
uk-online-retail-sales-analysis.pbip
powerbi/
  uk-online-retail-sales-analysis.Report/
  uk-online-retail-sales-analysis.SemanticModel/
data/
  raw/Online Retail.xlsx
  data-dictionary.md
docs/
  PROJECT_STRUCTURE.md
  revision/
  archive/
screenshots/
scripts/
  tmdl-check/
  archive/
evidence/
  baseline/
  financial/
  validation/
backups/                          # local, ignorado por Git
```

`powerbi` contiene el reporte PBIR y el modelo TMDL que se editan. `screenshots` conserva las capturas del dashboard original, cuyos valores y distribución son históricos. `docs/archive` conserva el PDF, las medidas y el tema recuperados. `scripts/archive` contiene los scripts de autoría inicial; no deben ejecutarse sobre el proyecto actual. Los validadores y la configuración del origen permanecen en `scripts`.

`evidence/baseline` conserva la línea base; `evidence/financial` contiene la conciliación y las definiciones; `evidence/validation` registra las comprobaciones. `.tools`, `.cache` y `.pbi` son archivos locales de dependencias, cálculos o caché, excluidos de Git.

## Respaldo y eliminación de la duplicación

`review` era un checkout del repositorio usado para crear una rama local. No era una versión publicada ni un segundo proyecto necesario para abrir el dashboard. Su historial Git se trasladó a la raíz y sus cambios se consolidaron en el proyecto principal. La rama sigue siendo `codex/retail-dashboard-corrections`; no se hizo push ni merge.

Los 63 archivos originales están conservados y verificados por SHA-256 en `backups/original-recovered-project.zip`. El checkout anterior, incluyendo fuentes e historial Git y excluyendo cachés reconstruibles, está conservado en `backups/review-before-consolidation.zip`. Los dos archivos Excel y las dos parejas de capturas eran idénticos; quedó una sola copia activa de cada uno.

El PBIX real recuperado se conserva como `backups/uk-online-retail-sales-analysis-original.pbix`. Es una instantánea del estado anterior. El PBIX de dos bytes que producía el error de paquete corrupto quedó dentro del respaldo del checkout anterior; no se ofrece como reporte vigente. Editar el PBIP no actualiza esa instantánea PBIX. Un PBIX de la revisión actual debe guardarse desde Power BI Desktop después de su aceptación.

## Ajustes de presentación de esta revisión

La revisión de presentación sigue trabajando sobre el mismo PBIP de la raíz. Antes de editar se preservó el estado guardado por Desktop, incluyendo su caché local, en `backups/desktop-saved-before-visual-revision.zip`. El modelo semántico no se modificó en esta corrección visual.

Se eliminaron los cinco objetos solicitados: las dos notas del panel de filtros, la tabla de conciliación de Sales Overview, la fórmula explicativa del neto y el pie sobre rankings/cancelaciones de Product & Customer Insights. Hay dos páginas y 33 contenedores: los 31 originales y las dos tarjetas de cobertura de clientes. La eliminación incluye los objetos completos y sus referencias de interacción.

Los encabezados principales tienen 54 píxeles de alto, frente a 35, y márgenes de contenedor explícitos. La segunda línea conserva sólo el período `1 Dec 2010 - 9 Dec 2011`. Las dos tarjetas de cobertura tienen 120 píxeles de alto, frente a 64, y los cinco KPI de Sales Overview tienen 104. Su contenido se configura para ajustarse al espacio disponible y mostrar tanto el valor como la etiqueta. Los años conservan el renderer original Basic/Horizontal, activando explícitamente `responsive=true`: Desktop 2.158 utiliza así una distribución por filas en lugar de una tira con flechas. El contenedor tiene 160 píxeles de alto para alojar 2010 y 2011. Se conserva el contraste corregido de los desplegables.

El gráfico de países de Sales Overview y el dispersograma tienen 558 píxeles de ancho, frente a 374. Tras el feedback del usuario sobre el scroll de países, los KPI de Sales Overview se subieron a y=104 y la fila de tendencia/países a y=224, con 344 píxeles de alto frente a 280. El usuario confirmó que se ven ambos años apilados y que el ranking de países de la primera página ya no tiene scroll. Se aplicó la misma altura de 344 píxeles al ranking de países de Product & Customer Insights y se alineó el ranking de clientes a su lado, en y=240. Las tarjetas conservan sus 120 píxeles de alto y suben a y=104; la fila inferior queda en y=600, con 312 píxeles de alto. Las cinco gráficas de ranking usan un mínimo de categoría de 18 píxeles. Los rankings de productos ocupan 720 píxeles de ancho: 304 de alto en Sales Overview y 312 en Product & Customer Insights. Se reemplazaron las propiedades `maxSize` y `wordWrap`, que Desktop había descartado, por `categoryAxis.maxMarginFactor=55`: ésta es la propiedad nativa para reservar hasta el 55% del ancho a las etiquetas. Se mantienen nombres/códigos completos en los tooltips y la identidad de cada producto. Los títulos conservan su texto salvo el sufijo monetario entre paréntesis; se retiró también de los ejes del dispersograma. La moneda de los importes sigue siendo GBP, como especifica [UCI para UnitPrice](https://archive.ics.uci.edu/dataset/352/online+retail). No se realizó conversión a USD.

Los controles de zoom del dispersograma siguen desactivados. Su mayor ancho conserva los mismos datos, Top 30, filtros y tamaño por facturas de venta. La compatibilidad de las propiedades se contrastó con el [esquema oficial de temas de Microsoft 2.157](https://github.com/microsoft/powerbi-desktop-samples/blob/main/Report%20Theme%20JSON%20Schema/reportThemeSchema-2.157.json) y los recursos de la instalación 2.158. La geometría y las referencias se validan en los archivos; la ausencia de recorte/scroll en la interfaz debe comprobarse con el render de Desktop.

Durante la prueba, el usuario guardó y cerró Desktop antes del último ajuste de años/altura. Ese guardado se conservó en `backups/desktop-test-save-before-final-layout.zip`. Las propiedades nuevas de ancho del eje, márgenes de texto y ajuste de tarjetas sobrevivieron al guardado nativo; los cálculos se contrastaron otra vez con cero discrepancias en [desktop-presentation-model-check.json](../evidence/validation/desktop-presentation-model-check.json). No se atribuye a esa consulta una validación visual.

El siguiente guardado nativo se conserva en `backups/desktop-save-before-second-country-adjustment.zip`. El ajuste de la segunda página modifica sólo seis posiciones/tamaños de contenedor; mantiene sus consultas, filtros y el modelo guardado. La revisión mensual compara el Excel leído de nuevo con los trece meses consultados en el motor de Desktop: [monthly-chart-check.json](../evidence/validation/monthly-chart-check.json) registra cero discrepancias y confirma que diciembre de 2011 termina el día 9. La caída del último punto representa un mes parcial; no se modificaron las cifras del gráfico.

## Apertura y comprobaciones

Abrir el PBIP de la raíz. Si se mueve el proyecto, cerrar Desktop y ejecutar `python scripts/configure_source.py` desde la nueva raíz antes de volver a abrirlo. El script configura `SourceFilePath` para el Excel local; la ruta relativa PBIP → reporte → modelo se conserva, conforme a la [documentación de proyectos de Microsoft](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview).

La apertura inicial, actualización de datos y evaluación de medidas son comprobaciones distintas de la representación visual y de los filtros. Las pruebas nativas realizadas se registran en `evidence/validation/desktop-native-check.json`; la lista pendiente se mantiene en [DESKTOP_ACCEPTANCE.md](revision/DESKTOP_ACCEPTANCE.md). No inferir una aceptación completa de una validación JSON/TMDL.

El respaldo original y la copia anterior son recuperables, pero no son puntos de entrada de trabajo. El único punto de entrada vigente sigue siendo el PBIP de la raíz.
