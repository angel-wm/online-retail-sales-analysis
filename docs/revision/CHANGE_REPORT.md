# Online Retail — Informe integral de cambios

La revisión está implementada en `uk-online-retail-sales-analysis.pbip`, directamente en la raíz, con los componentes en `powerbi`. Se verificaron apertura del modelo en Desktop 2.158.1304.0, actualización M completa y 17 medidas DAX en 15 contextos. El usuario confirmó años apilados y ausencia de scroll en el ranking de países de Sales Overview. El agente verificó después en la interfaz ambas páginas, los dos rankings de países sin scroll, encabezados y tarjetas completos, y los cuatro desplegables legibles sin hover. Se guardó, cerró y reabrió el PBIP con los gráficos cargados. **La aceptación de todas las interacciones y la exportación siguen pendientes**; las comprobaciones visuales concretas están separadas de los resultados de consultas.

La rama sigue siendo `codex/retail-dashboard-corrections`, a partir de main `83d0e32e56e1ae539151ab383099565c3571ef2c`. El checkout `review` se consolidó en el proyecto original por instrucción del usuario y su historial Git se trasladó a la raíz. Los 63 archivos originales se conservan dentro de su ZIP verificado; el checkout anterior y el placeholder se conservan en un segundo ZIP local. No se hizo push, merge ni publicación. [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md) documenta las rutas y el ensanchamiento de rankings realizado durante la consolidación.

## Cambios por fase

| Fase | Implementación | Evidencia y límite |
| --- | --- | --- |
| 1 — Finanzas | AMAZONFEE administrativo; bruto y reversos con el mismo ámbito de mercancía; neto principal; ajustes/otros separados; KEEPFILTERS; precisión AOV/tasas; GBP. | Excel reconstruido, baseline de 12 KPI, contraste XML independiente y 17 medidas DAX comprobadas en 15 contextos. |
| 2 — Modelo/origen | SourceFilePath configurable; M simplificado y tipado; DimProduct por código; calendario y relaciones preservados/explícitos; duplicados conservados. | Join sin inflación/huérfanos, 3,848 códigos, 374 fechas, 17 medidas con contrato preservado, TOM oficial y actualización M nativa completada. |
| 3 — Reporte y corrección de presentación | Dos páginas; rankings por código; cobertura; filtros sincronizados; títulos sin sufijos de moneda; años apilados; más espacio para encabezados, tarjetas, países y dispersograma. Se retiraron la tabla de conciliación y cuatro cuadros explicativos solicitados por el usuario. | 31 visuales originales retenidos y 2 tarjetas de cobertura; referencias y geometría verificadas. Render a ajuste de página, desplegables y guardado/reapertura comprobados; aceptación completa de interacciones pendiente. |

El detalle y la motivación están en [PHASE_1.md](PHASE_1.md), [PHASE_2.md](PHASE_2.md), [PHASE_3.md](PHASE_3.md) y [DECISIONS.md](DECISIONS.md). No hay una definición de negocio material pendiente para la implementación realizada; falta la aceptación visual/de interacción y la revisión del usuario.

## Resultados financieros conciliados

| KPI | Original reconstruido | Corregido desde Excel |
| --- | ---: | ---: |
| Bruto elegible | £10,285,076.90 | £10,271,315.81 |
| Reversos que restaba el neto | £896,812.49 | £478,724.18 |
| Neto comercial | £9,388,264.41 | £9,792,591.63 |
| Pedidos de venta | 19,775 | 19,773 |
| Clientes conocidos | 4,334 | 4,334 |
| AOV implementado | £474.00 | £495.25 mostrado; £495.2506766803 calculado |
| Tasa implementada | 9.00% | 4.66% mostrado; 4.6607872726% calculado |
| Total firmado de todos los movimientos | £9,747,747.93 | £9,747,747.93 |

Los **£404,327.22** de aumento del neto se explican por excluir £13,761.09 de comisiones del bruto y dejar de descontar £418,088.31 de negativos administrativos. El total global no cambia. Neto £9,792,591.63 + ajustes -£45,646.76 + otros £803.06 = £9,747,747.93.

[RECONCILIATION.md](../../evidence/financial/RECONCILIATION.md) contiene 12 KPI con definición, antes/después, diferencias absoluta/relativa y explicación; [before_after.csv](../../evidence/financial/before_after.csv) y [before_after.json](../../evidence/financial/before_after.json) son datos inspectables. Se revisan los 26 códigos especiales. No se interpretan negativos como prueba de devolución física ni se asignan reversiones a pedidos originales sin vínculo fuente.

## Validación ejecutada

Los resultados concretos se conservan en [validation-run.json](../../evidence/validation/validation-run.json), con comandos, salidas, tiempos y exit codes. El runner recalcula el Excel y contrasta su XML, deserializa el modelo con el parser oficial de Microsoft, comprueba dimensión/calendario/contrato, valida referencias y disposición del reporte, revisa JSON/esquemas y prueba la conservación de originales y respaldo. La lectura fresca final está registrada en [fresh-source-run.json](../../evidence/validation/fresh-source-run.json): fuente, XML, TOM, modelo y reporte pasaron; esa primera ejecución se detuvo después por una restricción DNS al obtener esquemas. Se repitió con acceso de red permitido y caché de fuente contrastada por SHA-256, manteniendo la cobertura de esquema explícitamente parcial. [REPRODUCE.md](REPRODUCE.md) explica herramientas, versiones, comandos y el alcance portable.

- [independent_xml.json](../../evidence/validation/independent_xml.json): lector independiente, cifras a céntimos y puente financiero.
- [final-tom.json](../../evidence/validation/final-tom.json): cinco tablas, tres relaciones y 17 medidas deserializadas; sin ejecución de expresiones.
- [model-checks.json](../../evidence/validation/model-checks.json): 540,455 filas preservadas, claves únicas, sin huérfanos, calendario y 15 selecciones esperadas desde Excel.
- [report-checks.json](../../evidence/validation/report-checks.json): referencias, recursos, dependencias, 33 contenedores, Top N, reset, grupos e interacciones declaradas.
- [presentation-json-schema.json](../../evidence/validation/presentation-json-schema.json): 49 JSON legibles; 12 esquemas exactos, 33 de compatibilidad, un esquema privado de ajustes locales no publicado y tres archivos sin esquema declarado. Sin errores detectados; cobertura **parcial** porque el esquema visual 2.13 no está disponible públicamente. `final-json-schema.json` conserva la comprobación de la fase inicial.
- [presentation-revision.json](../../evidence/validation/presentation-revision.json): objetos eliminados, dimensiones, corrección de años/scroll y respaldo del estado guardado por Desktop. [presentation-format-checks.json](../../evidence/validation/presentation-format-checks.json) registra las propiedades contrastadas con Microsoft y enlaza el alcance de la revisión nativa posterior.
- [desktop-presentation-model-check.json](../../evidence/validation/desktop-presentation-model-check.json): reapertura con caché existente, 17 medidas en 15 contextos y cero discrepancias; no prueba el render ni los controles.
- [monthly-chart-check.json](../../evidence/validation/monthly-chart-check.json): Excel leído de nuevo, consulta DAX de los trece meses y comprobación de medida/orden del gráfico; cero discrepancias. [monthly-source-check.json](../../evidence/validation/monthly-source-check.json) y [desktop-monthly-check.json](../../evidence/validation/desktop-monthly-check.json) conservan los resultados fuente y nativos.
- [report-load-repair.json](../../evidence/validation/report-load-repair.json): recuperación del archivo visual sobrescrito con un resultado de validación; prueba nativa de ambas páginas, desplegables y rankings; guardado y reapertura correctos. El validador rechaza ahora ese tipo de contenido y registra las huellas de todos los visuales. El modelo conserva su significado tras el guardado nativo.
- [original-integrity.json](../../evidence/validation/original-integrity.json): 63 miembros del respaldo original verificados; Excel e instantánea PBIX idénticos, main conservado, placeholder archivado y un único PBIP activo.

No se declara una mejora de rendimiento sin medición. La cobertura incluye 135,080 filas sin CustomerID y 5,268 repeticiones excedentes exactas preservadas. El periodo va de 1 de diciembre de 2010 a 9 de diciembre de 2011: 2010 y diciembre de 2011 son coberturas incompletas. La dimensión estabiliza identidad de código; su nombre es representativo, no un catálogo comercial aprobado.

La consulta mensual confirma £1,432,734.99 netos en noviembre de 2011 y £441,366.51 en diciembre, que contiene sólo los días 1–9. Desde Excel, el neto de los días 1–9 de noviembre es £435,185.39: diciembre queda 1.42% por encima en ese intervalo descriptivo. El archivo finaliza a las 12:50 del día 9 y no contiene el resto de diciembre. También se verificó la venta 581483 y el reverso C581484 del producto 23843, ambos de £168,469.60 el día 9: su efecto neto combinado es cero. Se conserva el total mensual real, sin extrapolar ni rellenar fechas con ventas cero.

## Revisión antes de integración

Seguir la lista corta de [DESKTOP_ACCEPTANCE.md](DESKTOP_ACCEPTANCE.md): abrir/refresh, comparar medidas y casos límite, filtros/sincronización/reset, rankings/tooltips, legibilidad y evidencia nueva. Incluye [consultas DAX preparadas](../../evidence/validation/desktop-queries.dax) para comparar el motor con los valores esperados. Cualquier diferencia real requiere corregir y volver a validar.

[GITHUB_NEXT_STEPS.md](GITHUB_NEXT_STEPS.md) recoge los pasos pendientes de documentación histórica, capturas, exportación PBIX e integración. Los README y las rutas se actualizaron localmente al consolidar el proyecto; las publicaciones y exportaciones finales siguen pendientes de aceptación.
