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

Los dos paneles de filtros terminan en y=488. Los segmentadores y el botón se desplazaron hacia arriba y las instrucciones se resumieron, conservando su descripción completa en el texto alternativo. Esto libera el margen izquierdo debajo de los filtros.

Los rankings de productos de ambas páginas comienzan en x=32 y tienen 904 píxeles de ancho, frente a los 736 de la revisión anterior. Top Return Products conserva el mismo Top 10 por valor de cancelaciones/reversiones y 320 píxeles de alto. Las etiquetas conservan salto de línea y hasta el 50% del ancho del visual. Los nombres completos, códigos y variantes de descripción siguen disponibles en tooltips; se conserva la identidad por producto.

El dispersograma mantiene sus datos, filtros, ejes monetarios y tamaño por facturas de venta. Se desactivaron los controles de zoom y las etiquetas de nombres sobre las burbujas. El nombre completo se consulta al pasar el cursor. Se mantienen el fondo blanco y texto oscuro de las opciones desplegables en ambas páginas.

No se añadieron ni eliminaron visuales en esta consolidación: hay dos páginas y 38 contenedores, incluidos los 31 originales y los elementos de explicación/conciliación incorporados en las fases anteriores.

## Apertura y comprobaciones

Abrir el PBIP de la raíz. Si se mueve el proyecto, cerrar Desktop y ejecutar `python scripts/configure_source.py` desde la nueva raíz antes de volver a abrirlo. El script configura `SourceFilePath` para el Excel local; la ruta relativa PBIP → reporte → modelo se conserva, conforme a la [documentación de proyectos de Microsoft](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview).

La apertura inicial, actualización de datos y evaluación de medidas son comprobaciones distintas de la representación visual y de los filtros. Las pruebas nativas realizadas se registran en `evidence/validation/desktop-native-check.json`; la lista pendiente se mantiene en [DESKTOP_ACCEPTANCE.md](revision/DESKTOP_ACCEPTANCE.md). No inferir una aceptación completa de una validación JSON/TMDL.

El respaldo original y la copia anterior son recuperables, pero no son puntos de entrada de trabajo. El único punto de entrada vigente sigue siendo el PBIP de la raíz.
