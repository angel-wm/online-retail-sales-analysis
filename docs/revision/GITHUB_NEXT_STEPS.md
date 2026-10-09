# Recomendaciones para GitHub después de revisión y aprobación

Estado actual: rama local, sin push ni merge. Los README públicos, diccionario, limpieza, capturas antiguas y placeholder se conservan. Estas son recomendaciones y no autorización ni acciones publicadas.

1. Completar [DESKTOP_ACCEPTANCE.md](DESKTOP_ACCEPTANCE.md), resolver cualquier error y registrar capturas/PDF y resultados nativos. Revisar personalmente definiciones, neto principal, agrupación de productos, AOV por factura del periodo, restricciones Top N y filtros sincronizados. El proyecto todavía no puede presentarse como funcionalidad nativa completamente certificada.

2. Actualizar README inglés/español con ubicación del PBIP, versión Desktop verificada, pasos de configuración/refresh, GBP, definiciones de los KPI, resultados nuevos y límites temporales/clientes/reversos. Sustituir afirmaciones sobre devoluciones físicas, compradores anónimos contados o años completos. Enlazar informes y conciliación; conservar procedencia y licencia del dataset UCI.

3. Actualizar diccionario y documentación de limpieza: AMAZONFEE administrativo; reglas de Movement_Type y flags; DimProduct y descripción representativa; diferencia Main Sales / Net Sales / Total Sales; conservación de duplicados y exclusión previa de descripciones nulas; redondeo por línea y precisión completa de cocientes. No tratar decisiones documentales como nuevas reglas comerciales.

4. Exportar un **PBIX nuevo desde Desktop actualizado y aceptado**. Verificar que abre, refresca, tiene ambas páginas y coincide con las consultas. Sólo tras autorización, sustituir el archivo de dos bytes `powerbi/online-retail-sales-analysis .pbix`. Resolver explícitamente si se conserva ese nombre o se elimina el espacio antes de la extensión, actualizando enlaces. No renombrar ni sustituir el PBIX recuperado original como parte de este trabajo.

5. Actualizar las capturas y el PDF con la versión aceptada y selección documentada. Las imágenes existentes prueban el estado anterior. Revisar tamaño del PBIX y estrategia normal de almacenamiento del repositorio; decidir LFS/Release asset sólo si el tamaño lo exige, sin reescribir el historial ni publicar automáticamente.

6. Preparar una PR revisable desde la rama autorizada, con problema, comportamiento final, cifras antes/después, evidencia y pendientes. Antes del push, eliminar de la configuración publicada rutas personales de SourceFilePath y sustituirlas por un valor de ejemplo documentado; ejecutar configure_source.py en cada checkout local. Inspeccionar datos, artefactos, paths de evidencia y archivos temporales; publicar exclusivamente lo aprobado. Mantener `.pbi`, `.cache`, `.tools`, bin/obj y respaldos locales fuera del repositorio. No borrar la copia original para hacer esta limpieza.

7. Tras aprobación explícita para integración/publicación, comprobar main remoto, actualizar la rama sin force/rewrite, revisar el diff, volver a validar si hubo cambios, realizar push normal y crear la PR. La autorización actual no incluye este paso ni Power BI Service. El README principal no debe anunciar disponibilidad de un PBIX válido mientras siga siendo un placeholder.
