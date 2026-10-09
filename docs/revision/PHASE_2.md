# Fase 2 — Power Query, modelo y reproducción

Actualización posterior a la fase inicial: el proyecto está consolidado en el PBIP de la raíz. Se completaron refresh M y contraste de 17 medidas DAX en 15 contextos en Desktop 2.158.1304.0. La comprobación de AOV respeta Currency de cuatro decimales y los recuentos vacíos respetan BLANK; las fórmulas se conservan. [Aceptación y evidencias actuales](DESKTOP_ACCEPTANCE.md). Las referencias a pruebas nativas pendientes del resto de este informe describen el cierre inicial de la fase.

Estado: implementado y contrastado con la fuente; parser oficial TMDL satisfactorio. La actualización de consultas M y la carga real en Desktop quedan pendientes.

## Origen configurable

La consulta utiliza `File.Contents(SourceFilePath)` y el parámetro M `SourceFilePath` es la única configuración de ubicación. En este checkout apunta al Excel versionado en `data/raw`, cuyo SHA-256 coincide con el original recuperado. No depende de la ubicación antigua en Courses.

Al mover o clonar el proyecto, ejecutar desde la raíz:

```powershell
python scripts/configure_source.py
```

También acepta `--excel 'D:\Datos\Online Retail.xlsx'`. Verifica existencia y formato XLSX antes de modificar el parámetro. Alternativamente, abrir **Transformar datos → Administrar parámetros → SourceFilePath** en Desktop. El valor es una ruta absoluta configurable; no se afirma que Power Query resuelva automáticamente rutas relativas al PBIP. Cambiarlo requiere cerrar y volver a abrir el proyecto si se editó externamente.

## Consulta mantenible

Se sustituye la cadena de transformaciones redundantes por pasos con propósito: lectura, encabezados, nombres, tipos, regla de descripción, clasificación, fecha, flags, importe y elegibilidad. Se eliminan conversiones de booleano a texto y vuelta a lógico, cambios de tipo repetidos, el filtro `each true` y la duplicación/renombrado de fecha. Los flags se crean como `type logical`, los IDs como texto y `Invoice_Day` como fecha.

`Unit_Price` conserva precisión de origen y tipo numérico; no se redondea antes de multiplicar. `Sales_Amount` conserva el redondeo original a céntimos con `RoundingMode.ToEven` explícito y se carga como decimal fijo para sumar importes monetarios. Los tipos y el registro de la política permiten contrastar la suma a céntimos; su comportamiento M nativo todavía debe probarse en Desktop.

Se conserva explícitamente la exclusión previa de 1,454 descripciones nulas: £0 de importe total. Permanecen 540,455 líneas. No se añade ninguna exclusión ni deduplicación. Las 5,268 repeticiones excedentes exactas no prueban un error: no existe un identificador de línea. Se preservan los flags de calidad, cancelaciones, clientes desconocidos y movimientos grandes de la Fase 1.

## Identidad de producto

La mejora demostrada es agrupar por `Stock_Code`: 212 códigos con ventas elegibles tienen varias descripciones normalizadas. La dimensión tiene **3,848 códigos únicos**, incluye todos los códigos cargados y conserva una relación activa **1 → muchos**, con filtro únicamente desde DimProduct al hecho. La tabla de hechos no depende de una unión con la dimensión para calcular su clasificación.

`Product_Name` en DimProduct es una **descripción representativa del origen**, no un catálogo comercial aprobado. Se selecciona la descripción normalizada más frecuente entre líneas de venta elegibles; si no existen, se usan las descripciones cargadas. Los empates se resuelven por orden ordinal. `Product_Label` combina código y nombre para que dos códigos con el mismo nombre no se fusionen. `Description_Variants` registra cuántos nombres originales normalizados tiene cada código; 642 códigos tienen más de uno entre todas las líneas cargadas.

Los nombres de cada transacción se mantienen en el hecho. [product_identity.csv](../../evidence/financial/product_identity.csv) registra el resultado reconstruido de la regla. En la Fase 3 se migran categorías, filtros Top N y tooltips de productos a la dimensión de manera conjunta. El total monetario no cambia; sí puede cambiar el orden de rankings al consolidar nombres de un mismo código. No se unen productos diferentes porque compartan descripción.

Line_Type se mantiene en el hecho: los códigos DCGS con líneas EBAY de valor cero no tienen una categoría única por código. No se crea DimCustomer ni DimCountry: no hay una ambigüedad de clave ni reutilización que exija más dimensiones para este reporte.

## Calendario, relaciones y metadatos

Calendar conserva la cobertura exacta de **1 de diciembre de 2010 a 9 de diciembre de 2011**, 374 fechas continuas y únicas. Se conserva la clave de fecha, los atributos y las ordenaciones de Month, Weekday y YearMonth_Label. La relación Invoice_Day → Calendar.Date se declara explícitamente muchos-a-uno, activa y unidireccional. Los atributos de fecha numéricos pasan a `summarizeBy: none`.

La plantilla y tabla local de Auto Date/Time permanecen ocultas por compatibilidad con la variación de Invoice_Date y metadatos Q&A. Los visuales temporales usan Calendar. Su tamaño es pequeño y no hay evidencia de un problema de rendimiento que justifique retirar estructuras funcionales. No se añaden años completos ni cálculos de crecimiento interanual sobre periodos incompletos.

Se ocultan los campos técnicos y el nombre transaccional de producto para orientar nuevas ediciones a DimProduct; las referencias existentes conservan sus lineageTags. Unit_Price deja de permitir suma predeterminada. El diagrama incorpora la dimensión. Las medidas mantienen el contrato de la Fase 1 sin modificaciones.

## Calidad y limitaciones

- 135,080 líneas del Excel original carecen de CustomerID; las ventas anónimas se conservan y no permiten estimar compradores únicos.
- 2010 contiene sólo diciembre. Diciembre de 2011 llega al día 9. No comparar esas coberturas como años o meses completos.
- Cancelaciones y reversiones se registran en la fecha de su factura negativa, sin vínculo formal al pedido inicial ni prueba de devolución física.
- Stock_Code estabiliza identidad; una descripción representativa no demuestra que cambios de nombre sean equivalencias comerciales aprobadas.
- Las repeticiones exactas y las reversiones grandes se conservan. No hay pérdida de filas ni ajustes ocultos en esta refactorización.

## Evidencia

[model-checks.json](../../evidence/validation/model-checks.json) reconstruye dimensión, joins, calendario y 15 contextos de filtro desde la fuente. Las 540,455 filas antes y después del join coinciden, sin huérfanos; se conservan importes y las 17 expresiones/formatos de medidas. El parser TOM confirma 5 tablas, 3 relaciones y las propiedades efectivas de las nuevas relaciones. Esto verifica estructura y contratos fuente, no actualización ni propagación interactiva ejecutada por Desktop.

No se afirma una mejora de velocidad: no se han medido refresh, memoria ni consultas. La nueva dimensión responde a un defecto de identidad demostrado y sus costes deben medirse sólo si aparece un problema real.
