# Auditoría técnica y visual: Online Retail Sales Analysis

Fecha: 8 de octubre de 2026. Estado: necesita revisión antes de presentarse como entrega funcional validada. Inspección estática y recálculo fuente completos dentro del inventario disponible; validación en Power BI Desktop pendiente. No se modificaron archivos del proyecto, no se hizo commit, push ni publicación.

## Evidencia y alcance

Se inspeccionaron los 63 archivos suministrados: PBIP y sus referencias, definición PBIR, las dos páginas y los 31 contenedores visuales, temas, metadatos, TMDL completo de las cuatro tablas y las dos relaciones, 12 medidas DAX, la consulta M, fórmulas auxiliares, el Excel y la estructura ZIP del PBIX. Los 43 JSON se pudieron parsear. El PBIX tiene Report/Layout y DataModel reales; esto no demuestra apertura satisfactoria ni actualización.

Se revisaron las dos capturas PNG y las dos páginas completas del PDF, renderizadas con Poppler. Son evidencia estática del aspecto del reporte. No se recreó ni rediseñó el dashboard.

El repositorio público se inspeccionó en el commit 83d0e32e56e1ae539151ab383099565c3571ef2c, árbol 8a18aa79def91a583902c29069cc1b7e4b74e36c: 15 archivos, incluidos seis documentos/licencias, dos capturas, cinco .gitkeep, Excel y PBIX. No hay PBIP/TMDL/PBIR publicados. El PBIX remoto mide 2 bytes; el recuperado local, 4.302.979 bytes. El Excel local es idéntico al remoto según hash de blob Git a58636c3714c4cca4e2e1cfe9a1fcb28af30494e. La documentación actual ya reconoce las limitaciones del placeholder; una página web cacheada anterior se descartó como fuente de estado.

Se reconstruyeron las reglas desde el Excel con pandas/openpyxl y se contrastaron independientemente los importes con lectura directa del XML del XLSX, Decimal y sumas de céntimos. Los dos caminos coinciden para ventas principales, importe negativo total, total cargado y devoluciones de producto. Estos son recálculos de la fuente; no constituyen ejecución de DAX/M ni lectura de la caché VertiPaq.

## Resultado cuantitativo de la implementación actual

Población: todos los países, todo Line Type y todas las fechas disponibles. Importes expresados en GBP, moneda del dataset, aunque varios formatos del reporte muestran dólares.

| Concepto | Resultado reconstruido | Interpretación |
| --- | ---: | --- |
| Filas fuente | 541.909 | Grano: línea de factura, no pedido único |
| Fechas | 01/12/2010 08:26 a 09/12/2011 12:50 | Diciembre de 2011 es parcial |
| Filas descartadas por descripción nula | 1.454 | Importe conjunto £0,00 |
| Filas cargadas | 540.455 | Después del primer filtro M |
| Filas del análisis principal | 527.759 | Según flags actuales |
| Total Sales | £9.747.747,93 | Suma firmada de todas las filas cargadas |
| Main Sales | £10.285.076,90 | Sólo líneas elegibles; incluye erróneamente dos comisiones AMAZONFEE |
| Returns Amount | £896.812,49 | Todos los importes de cantidad negativa, en absoluto |
| Return Value | £714.005,77 | Negativos clasificados Product, incluidas comisiones AMAZONFEE |
| Net Sales | £9.388.264,41 | Main Sales menos Returns Amount |
| Orders | 19.775 | Facturas con al menos una línea principal |
| Unique Customers | 4.334 | Clientes identificados con líneas principales |
| Units Sold | 5.577.101 | Cantidad positiva elegible |
| Cancelled Orders | 3.836 | Facturas con prefijo C entre filas cargadas |
| Zero Price Records | 1.061 | Filas cargadas con precio cero |
| AOV sin redondeo | £474,7542053 | Net Sales / Orders |
| AOV con MROUND(...,2) | £474 | Múltiplo de 2 |
| Tasa por valor sin redondeo | 8,719550653 % | Returns Amount / Main Sales |
| Tasa DAX actual | 9,0 % | ROUND(ratio,2), luego formato porcentual |

La serie mensual completa reconstruida coincide a la precisión visible con las capturas: noviembre 2011 £1.410.005,45 / 2.751 pedidos, diciembre 2011 £410.368,60 / 816 pedidos. No se pueden interpretar estos meses como periodos completos comparables.

## Problemas reales, por prioridad

### P1-01. Clasificación de AMAZONFEE como producto

**Encontrado:** Online Retail.tmdl:276 busca el código `AMAZON FEE`, pero el Excel contiene `AMAZONFEE`, con descripción `AMAZON FEE`. Por ello sus 34 filas se clasifican Product. Dos filas positivas (£13.761,09) entran en Main Sales; 32 negativas (£235.281,59) entran en Return Value. Es aproximadamente un tercio del Return Value actual.

**Importancia:** las comisiones administrativas afectan ingresos comerciales y devoluciones de mercancía. El gráfico Top Returned Products aplica una exclusión manual por descripción, mientras Returned Value by Country no la aplica. Reino Unido muestra £681.124,97 de Return Value, incluyendo las comisiones.

**Propuesta:** corregir el código en el mapeo de Line_Type y revisar el catálogo de códigos especiales. Mantener el tratamiento de los ajustes en medidas separadas según la decisión de negocio. Sustituir la exclusión visual manual por reglas compartidas aprobadas.

**Beneficio:** una definición de producto coherente entre países, rankings, KPI y tooltips. Sólo reclasificar AMAZONFEE reduce Main Sales a £10.271.315,81 y Return Value a £478.724,18; Returns Amount amplio permanece £896.812,49. Son efectos de un escenario propuesto, no resultados del dashboard editado.

### P1-02. Universos diferentes para ventas, neto y devoluciones

**Encontrado:** Main Sales exige Product y Normal; Returns Amount filtra únicamente cantidad negativa. £182.806,72 de negativos clasificados Adjustment se restan a ventas que excluyen sus positivos. Return Value limita Product. Online Retail.tmdl:11-33,101-107,336-347.

**Importancia:** Net Sales no equivale al neto de producto ni a la suma neta de todas las transacciones. La tasa KPI y los gráficos de devoluciones usan numeradores distintos. Seleccionar Product cambia el neto a £9.571.071,13 sin cambiar las ventas principales (£10.285.076,90), con las reglas actuales.

**Propuesta:** acordar definiciones separadas de ventas brutas elegibles, reversos de mercancía, ajustes/portes/descuentos y neto global. Elegir la definición ejecutiva y sus denominadores. Si se acepta neto de producto corregido, tras reclasificar AMAZONFEE resulta £9.792.591,63 y su tasa por valor 4,6607873 %. Este escenario todavía incluye reversos/cancelaciones; no equivale a una tasa de devoluciones físicas validada.

**Beneficio:** conciliación explícita de ventas y movimientos negativos. La inconsistencia de ámbitos es demostrable; cuál ámbito conviene es una decisión de negocio pendiente, no motivo para imponer una fórmula nueva automáticamente.

### P1-03. Actualización no reproducible en este equipo

**Encontrado:** Online Retail.tmdl:264 usa File.Contents con la ruta absoluta `C:\Users\angel\Documents\Courses\DA\proyecto_personal\online+retail\Online Retail.xlsx`. La ruta no existe; el Excel disponible está en otra carpeta.

**Importancia:** la caché puede permitir mostrar datos antiguos, pero File.Contents no puede actualizar desde la ubicación definida. No se ejecutó el refresh para provocar el error.

**Propuesta:** parámetro de ubicación de fuente y pasos de configuración local; conservar datos fuente y ruta privada fuera de un supuesto portátil no probado. Validar una actualización completa en Desktop antes de entregar.

**Beneficio:** recuperación funcional verificable y reproducibilidad del PBIP/PBIX.

### P1-04. Precisión de AOV y tasa

**Encontrado:** Online Retail.tmdl:59 usa MROUND(...,2); :64 aplica ROUND(ratio,2). MROUND redondea a múltiplos de 2, no a dos decimales. El AOV actual de £474,7542 pasa a £474, en lugar de £474,75. En un contexto negativo, MROUND con múltiplo positivo puede producir error. La tasa 8,7196 % pasa a 9,0 %; Países Bajos tiene 0,2764 % y se muestra 0,0 % bajo ese cálculo.

**Propuesta:** conservar DIVIDE y controlar precisión con el formato, o usar ROUND(AOV,2) si hay una política explícita de redondeo numérico. Mantener el ratio de tasa sin ROUND a dos decimales del cociente.

**Beneficio:** precisión real, tasas pequeñas visibles y menos errores en contextos negativos. AOV neto por pedido puede ser una definición legítima; la corrección de MROUND es independiente de elegir cesta bruta o ingreso neto por pedido.

### P1-05. Moneda y etiquetas de ventas

**Encontrado:** los formatos del modelo para ventas/AOV usan `$` sin transformación monetaria. Algunos visuales sobrescriben `£`. La tarjeta `dd400a8a673caa8ed6a7` y el gráfico `5f1c21068041053e9103` muestran Total Sales pero vinculan Main Sales. La medida Total Sales real calcula £9.747.747,93, no £10.285.076,90.

**Propuesta:** formatos GBP compartidos para medidas, ejes, etiquetas y tooltips; usar etiquetas que definan ventas principales elegibles y ventas netas. No hacer una conversión de moneda: sólo se corrige la unidad comunicada.

**Beneficio:** lectura financiera coherente y conciliación con el diccionario de medidas.

### P1-06. Reversos/cancelaciones interpretados sin matiz como devoluciones

**Encontrado:** todas las líneas negativas con importe distinto de cero tienen prefijo C en esta fuente. Hay 474 negativos sin C, todos de valor cero. La fuente no incluye razón de devolución, fecha de entrega ni vínculo formal a factura original. Dos pares particularmente grandes coinciden en cliente, producto, cantidad e importe y se revierten en minutos:

- 541431/C541433, producto 23166, 74.215 unidades por £77.183,60, 18/01/2011 10:01 y 10:17.
- 581483/C581484, producto 23843, 80.995 unidades por £168.469,60, 09/12/2011 09:15 y 09:27.

**Importancia:** es verificable la reversión contable; no se conoce si hubo mercancía entregada y devuelta. Los mayores valores no acreditan defectos de producto o insatisfacción.

**Propuesta:** documentar y comunicar el proxy como valor de devoluciones/reversos o cancelaciones según política. Si se desea una tasa de devolución física, haría falta evidencia que el Excel no contiene. Revisar los outliers sin borrarlos automáticamente.

**Beneficio:** conclusiones de negocio proporcionadas a la fuente.

### P1-07. Periodo parcial y subconjuntos de gráficos no comunicados

**Encontrado:** diciembre 2011 termina el día 9. Year 2010 comprende únicamente diciembre. No hay aviso de cobertura junto a las tendencias. Returned Value by Country aplica Top 10 y Return Value >1000 (fc81c2d8bc82287d528b/visual.json:319,402); 19 países tienen valor positivo de devoluciones por debajo del umbral y pueden quedar fuera aunque el usuario los filtre. El dispersograma aplica Top 30 por Net Sales (bfd4fc73192936bc42c7/visual.json:403) sin declarar el subconjunto.

**Propuesta:** mostrar cobertura temporal y mes parcial; explicitar Top N/umbral o retirar el umbral si no cumple una decisión aprobada. Indicar selección Top 30 y tamaño de burbuja por Orders.

**Beneficio:** evita confundir un mes incompleto con caída comercial y un país ocultado con ausencia de devoluciones. El Top 30 por neto deja fuera productos con ventas netas cero y grandes reversos, por lo que no sirve para examinar todos los riesgos de devolución.

### P2-08. Legibilidad analítica de gráficos

**Encontrado:** el dispersograma tiene etiquetas superpuestas, nombres cortados y ambos títulos de ejes ocultos; el eje X hereda dólares y el Y muestra valores sin unidad monetaria. La tendencia configura millones con precisión cero (c1e7baf0796e55151039/visual.json:110-122), y las capturas muestran dos marcas diferentes rotuladas £1M. Los rankings de productos recortan nombres y el Top 10 de Sales Overview sólo presenta nueve barras simultáneas con scroll; en PDF la décima no puede descubrirse interactuando.

**Propuesta:** ejes con unidades y precisión suficiente, menos etiquetas de burbuja y detalle en tooltips, etiquetas seleccionadas o vista de detalle, ajuste de espacio para los diez registros cuando se exporta. Mantener gráficos y estructura cuando estas correcciones basten.

**Beneficio:** identificabilidad y comparación sin cambiar la métrica. No es una preferencia de paleta: afecta información disponible para el lector.

## Mejoras recomendables

| ID | Hallazgo | Cambio propuesto | Beneficio / condición |
| --- | --- | --- | --- |
| R1 | 212 códigos de producto con líneas principales tienen más de una descripción, incluso tras Trim/Upper. Código 85123A aparece como WHITE/CREAM HANGING HEART T-LIGHT HOLDER. 172 descripciones originales se usan para varios códigos. Visuales agrupan Product_Name. | Definir identidad por Stock_Code y una descripción aprobada; evaluar DimProduct y DimCustomer. | Rankings estables; resolver cambios reales de producto y variantes antes de fusionar nombres. No obliga a rehacer todo el modelo. |
| R2 | 5.268 filas exactamente repetidas por encima de la primera (0,972 % de la fuente); las repeticiones elegibles aportan £24.213,74. No hay ID de línea que pruebe duplicación accidental. | Investigar procedencia, factura/código y política de duplicados; conservar diagnóstico y trazabilidad. | Cuantifica riesgo. No aplicar Table.Distinct sin aprobación porque puede borrar líneas legítimas. |
| R3 | 135.080 CustomerID nulos en fuente. 131.419 líneas principales (24,90 %) y £1.524.010,25 (14,82 % de Main Sales) son anónimos. El ranking sí excluye null; el KPI de clientes excluye blanks. | Indicar cobertura de identificación y, si resulta útil, ventas de clientes conocidos frente a anónimos. | Evita interpretar el ranking como reparto de todas las ventas o los 4.334 clientes como todos los compradores. No descartar sus ventas. |
| R4 | M pasa booleanos a texto y otra vez a lógico, repite cambios de tipos y contiene SelectRows(each true). Fórmulas de texto duplican Return Value. | Mantener tipos desde la creación, eliminar pasos vacíos y usar TMDL como referencia de fórmulas. | Menos deuda de mantenimiento. La mejora de velocidad requiere medición, no se presume. |
| R5 | Auto Date/Time coexiste con Calendar; hay plantilla y tabla local ocultas. | Consolidar calendario después de comprobar dependencias. Años completos sólo si se aprueban cálculos temporales que los necesiten. | Un camino de fechas y menos confusión. Las tablas son pequeñas y no prueban un cuello de botella. |
| R6 | Unique Customers aplica NOT(ISBLANK(Customer_ID)) sin KEEPFILTERS; Return Value establece Line_Type=Product sin KEEPFILTERS. | Acordar si deben respetar un filtro directo de cliente/Line_Type e intersectar con KEEPFILTERS o usar DISTINCTCOUNTNOBLANK según definición. | Semántica coherente al ampliar interacción. Sobrescritura de columnas demostrable en DAX; respuesta visible bajo todas las interacciones sigue pendiente. El reporte actual no tiene selector directo de cliente en Sales Overview. |
| R7 | No se encontró sincronización explícita de slicers entre páginas. Botones son ClearAllSlicers, no una eliminación de todos los filtros fijos o selecciones. | Validar navegación/estado y decidir independencia o sincronización. Precisar etiqueta del reset. | Evita comparar páginas con ámbitos diferentes. No declarar que el botón esté roto sin ejecutarlo. |
| R8 | Unit_Price y campos Year/Month#/Day/Weekday# permiten suma por defecto. Columnas técnicas visibles y formatos repetidos por visual. | SummarizeBy none donde corresponde, ocultar claves/flags técnicos según uso y centralizar formatos. | Menos agregaciones accidentales en futuras ediciones. No altera visuales correctos actuales. |
| R9 | Sales_Amount y Unit_Price son double. Number.Round M y ROUND DAX tienen desempates distintos. | Documentar política por línea vs total y evaluar decimal fijo/currency según rango y precisión. | Conciliación financiera explícita; el recálculo actual coincide a céntimos en agregados, no hay diferencia monetaria demostrada que exija cambio inmediato. |
| R10 | No hay serie de AOV ni comparación simultánea de pedidos por país. Valores devueltos absolutos no miden propensión a devolver. Tooltip de devoluciones usa suma Quantity (neto) y Orders principales. | Ajustar promesas de preguntas o aprobar tendencia AOV, comparación de pedidos y tasa por valor compatible. Tooltips con unidades devueltas/reversos y ámbito de facturas. | Responde a preguntas existentes, sin inventar targets o causas. Comparar países sólo por valor favorece al de mayor tamaño. |
| R11 | No se midieron duración de refresh, consultas, memoria ni VertiPaq. Predominan SUM/DISTINCTCOUNT con filtros, con un SUMX acotado a devoluciones. | Performance Analyzer y medición de refresh en Desktop; DAX Studio/VertiPaq si hay cuello de botella real. | Optimización basada en evidencia. No recomendar SUMX→ABS(SUM) hasta probar signos y ámbito. No eliminar medidas de diagnóstico sólo porque hoy no aparezcan. |
| R12 | M descarta 1.454 descripciones nulas (£0), sin registro de rechazos documentado; README no refleja tablas automáticas. | Documentar recuento y razón; fuente/staging y tabla de rechazos si se necesita trazabilidad. Publicar PBIP y instrucciones después de aprobación y validación. | Reproducción y mantenimiento. Los documentos actuales describen honestamente el placeholder y no deben marcarse como falsos por ello. |

## Preferencias estéticas opcionales

- Reducir intensidad de sombras y curvas de tarjetas: aspecto más sobrio y mejor separación visual. Es opcional; el estilo actual es coherente.
- Usar un acento semántico para reversos/devoluciones, conservando buen contraste y etiquetas. Facilita escaneo, pero la paleta monocromática actual no prueba un error.
- Sustituir la curva suavizada por segmentos rectos y reducir relleno de área: enfatiza observaciones mensuales discretas. La curva monotoneX actual no demuestra por sí misma alteración de datos.

Estas preferencias deben decidirse después de las correcciones analíticas; no justifican un rediseño automático.

## Modelo: puntos verificados favorables

La tabla Calendar está marcada como Time y Date como clave. CALENDAR(MIN/MAX) genera 374 días continuos y únicos dentro de cobertura. Month/Month_short y Weekday tienen claves de orden; YearMonth_Label ordena por YearMonthSort. Invoice_Day se convierte a date antes del enlace, evitando desajuste por hora.

Hay dos relaciones: Invoice_Day→Calendar.Date e Invoice_Date→LocalDateTable.Date, esta última con datePartOnly. No se declaran overrides de cardinalidad, actividad ni dirección; la forma serializada corresponde al patrón habitual de *:1 activo, filtro desde fecha hacia hechos. No hay evidencia de muchos-a-muchos ni de filtros bidireccionales declarados. Los valores efectivos deben confirmarse con TOM/Desktop, que no se ejecutaron.

Es una tabla de hechos con atributos de producto/cliente/país incorporados y una dimensión fecha, no una estrella completa. Para una sola fuente de 541.909 líneas eso no acredita por sí solo un error ni rendimiento insuficiente. La necesidad de dimensiones se fundamenta en estabilidad de claves, múltiples nombres y reutilización.

No hay referencia visual rota demostrada: queryRef='Calendar.Return Value' conserva SourceRef.Entity='Online Retail'. El ranking de clientes sí excluye null. Los seis slicers existen; ambos resets declaran ClearAllSlicers. Hay navegación nativa por páginas; no se necesita introducir botones de navegación por preferencia.

## Mapa de componentes

Sales Overview tiene 18 contenedores: cinco tarjetas, cuatro gráficos, tres slicers, un reset, tres textos y dos formas. Product & Customer Insights tiene 13: cuatro gráficos, tres slicers, un reset, tres textos y dos formas. Total: 13 componentes cuantitativos, seis slicers, dos resets y diez contenedores decorativos/texto. Ambas páginas miden 1336×768. Ningún contenedor excede esas dimensiones según sus posiciones declaradas.

| Visual | Campo / métrica | Ámbito relevante |
| --- | --- | --- |
| Sales KPI | Main Sales rotulado Total Sales | Flags de análisis principal |
| Orders | Orders | DISTINCTCOUNT de factura elegible |
| Unique Customers | Unique Customers | Clientes no vacíos; sobrescribe filtro Customer_ID |
| Avg. Order Value | Average Order Value | Neto amplio / pedidos principales |
| Return rate | Return rate | Negativos amplios / Main Sales |
| Net Sales Over Time | Net Sales por YearMonth_Label | Orden cronológico; curva suavizada/área |
| Total Sales by Country | Main Sales por Country | No Top N explícito; scroll |
| Top 10 products by Net Sales | Net Sales por Product_Name | Top 10 por neto; scroll |
| Orders by Month | Orders por YearMonth_Label | Orden cronológico |
| Top 10 Customers by Net Sales | Net Sales por Customer_ID | Top 10; null excluido |
| Returned Value by Country | Return Value por Country | Top 10 y valor >1000 |
| Top Returned Products by Value | Return Value por Product_Name | Top 10 y lista de exclusiones manuales |
| Sales vs Returns by Product | X Net Sales, Y Return Value, tamaño Orders | Product; Top 30 por Net Sales; filtro Include_In_Main_Analysis declarado sin condición activa |

## Límites de verificación y orden de implementación propuesto

No se abrió Power BI Desktop ni se ejecutó refresh, M, DAX o TOM. No se inspeccionó el contenido tabular del DataModel/cache.abf. La reproducción de fuente no demuestra identidad con todos los datos almacenados, aunque coincide con los KPI/serie/rankings visibles de capturas. Los grupos de texto de Python conservan mayúsculas y espacios de origen; el motor Tabular puede aplicar reglas de comparación diferentes. La multiplicidad por código también se confirmó tras normalizar Trim/Upper, por lo que no depende únicamente de esas diferencias.

No se probaron hover, drill, selecciones, highlight, sincronización, reset, exportación interactiva, teclado, lectores de pantalla ni móvil. No hay layout móvil explícito en los archivos inspeccionados; su necesidad depende del destino del reporte. Las capturas/PDF sólo prueban sus estados estáticos. No se midió rendimiento.

Propuesta por lotes: (1) configurar ruta y validar baseline; (2) corregir AMAZONFEE, redondeo, unidades/nombres y aprobar ámbitos de neto/devoluciones; (3) validar diferencias esperadas en total, mes, país, producto y cliente, más contextos vacíos y devoluciones únicamente; (4) corregir legibilidad, periodo/subconjuntos y filtros; (5) aprobar claves/dimensiones y limpieza según evidencia; (6) actualizar documentación y publicación de versión funcional. Los errores corregidos pueden cambiar KPI de forma prevista; la validación debe evitar variaciones involuntarias, no exigir conservar un error anterior.

## Fuentes y evidencia reproducible

- [Repositorio en commit revisado](https://github.com/angel-wm/online-retail-sales-analysis/tree/83d0e32e56e1ae539151ab383099565c3571ef2c)
- [Diccionario revisado](https://github.com/angel-wm/online-retail-sales-analysis/blob/83d0e32e56e1ae539151ab383099565c3571ef2c/data/data-dictionary.md)
- [Notas de limpieza](https://github.com/angel-wm/online-retail-sales-analysis/blob/83d0e32e56e1ae539151ab383099565c3571ef2c/docs/cleaning-notes.md)
- [UCI: fuente, moneda y definiciones](https://archive.ics.uci.edu/dataset/352/online%2Bretail)
- [Microsoft MROUND](https://learn.microsoft.com/en-us/dax/mround-function-dax)
- [Microsoft ROUND](https://learn.microsoft.com/en-us/dax/round-function-dax)
- [Microsoft CALCULATE](https://learn.microsoft.com/en-us/dax/calculate-function-dax)
- read_data.py y data_audit.ipynb: perfil y recálculo principal.
- source_crosscheck.py: lectura independiente XML/céntimos y verificación final de hashes.
- raw_profile.json, data_reconciliation.json, independent_xml_crosscheck.json, monthly_reconciliation.csv: resultados.
- visual_inventory.json y pbix_layout.json: trazabilidad del reporte y bindings.
- initial_manifest.json y final_integrity_check.json: 63 archivos originales, cero cambios y cero archivos añadidos al proyecto.

El notebook reproduce análisis fuente; no ejecuta Power BI. Los artefactos de auditoría se guardan fuera del proyecto y no cambian la entrega original.

## Cobertura de la auditoría

Inventario y observaciones en coverage.json; recuentos generados por el helper summarize-coverage. Cada celda indica componentes/preguntas con defecto observado dividido por el inventario aplicable. Las categorías se solapan y no forman una nota de calidad ni porcentaje de exactitud. Un 0/N no afirma N verificaciones completas. El comportamiento interactivo de los 13 componentes cuantitativos y los ocho controles permanece sin ejecutar en Desktop.

| Calidad del dashboard | Defectos observados | Evaluación |
| --- | --- | --- |
| Utilidad y cobertura | 2 / 5 | Cinco preguntas documentadas. Falta tendencia de AOV; pedidos por país sólo se comparan secuencialmente mediante selector. |
| Claridad analítica | 8 / 13 | Componentes con unidades, ámbitos o cobertura temporal que requieren aclaración. |
| Consistencia visual e interacción | 6 / 21 | Seis componentes presentan defectos visibles; todos los comportamientos Desktop permanecen pendientes. |

| Corrección y robustez analítica | Defectos observados | Evaluación |
| --- | --- | --- |
| Autoridad de fuentes | 0 / 13 | Excel local idéntico al publicado, fuente y definiciones conocidas. Datos de caché tabular sin consultar. |
| Precisión de valores | 6 / 13 | Clasificación, ámbitos y redondeo afectan seis componentes identificados en el registro. Fuente recalculada; motor DAX no ejecutado. |
| Concordancia interna del gráfico | 8 / 13 | Etiquetas/unidades/subconjuntos contrastados con bindings y capturas. |
| Detalle de fuentes | N/A | No existe inspector Data App; se entrega trazabilidad mediante archivos, fórmulas y resultados. |
| Consistencia entre componentes | 2 / 3 | Discrepancias de denominación de ventas y ámbitos de devoluciones. Orden de fechas coherente. |
| Controles de calidad de datos | 6 / 13 | Clasificación errónea documentada. Repeticiones exactas son riesgo investigable, no duplicación accidental demostrada. |
| Soporte de conclusiones | N/A | Docs actuales formulan preguntas y no afirman conclusiones cuantificadas o causales. |
