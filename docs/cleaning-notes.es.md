[Read in English](cleaning-notes.md) · [Inicio en español](../README.es.md)

# Preparación y límites de los datos

El [Excel original de UCI](../data/raw/Online%20Retail.xlsx) contiene 541.909 líneas. El modelo excluye 1.454 con descripción nula y carga 540.455. Las líneas excluidas suman cero después del redondeo. Se conservan 5.268 filas repetidas adicionales en los ocho campos de origen porque el archivo carece de un identificador de línea que permita distinguir duplicados accidentales de registros repetidos válidos. [Cobertura](../evidence/financial/coverage.json) · [Perfil bruto](../evidence/baseline/raw_profile.json)

## Transformaciones

1. Leer la hoja **Online Retail**, promover encabezados y renombrar las ocho columnas.
2. Aplicar tipos con cultura `en-GB`. Los identificadores son texto y las cantidades son enteras. La fecha, la hora y el precio mantienen sus tipos correspondientes.
3. Excluir descripciones nulas y normalizar el código de inventario con recorte y mayúsculas. Conservar la descripción de origen.
4. Derivar el tipo de línea, la fecha de factura, los indicadores de calidad, cancelación, cantidad negativa y precio cero.
5. Multiplicar cantidad por precio unitario original y redondear el importe de línea a dos decimales con `RoundingMode.ToEven`. Almacenar el resultado como `Currency`.
6. Calcular por separado la elegibilidad de ventas y reversos y asignar la categoría de conciliación.

`AMAZONFEE` y `AMAZON FEE` son ajustes administrativos según la lista explícita. Otros códigos alfabéticos pueden corresponder a mercancía. El precio de `PADS` de `0.001` se conserva antes de multiplicar. Una línea negativa elegible se contabiliza una sola vez. Los ajustes y vales regalo siguen disponibles para la conciliación. [Reglas de clasificación](../data/data-dictionary.es.md#reglas-de-clasificación) · [Implementación](../powerbi/uk-online-retail-sales-analysis.SemanticModel/definition/tables/Online%20Retail.tmdl)

## Clientes y productos

La fuente tiene 135.080 líneas con ID de cliente ausente. La actividad anónima elegible entra en los importes y queda fuera del conteo de clientes identificados. Las tarjetas describen esa cobertura sin estimar compradores anónimos únicos. El modelo agrupa por código de inventario y conserva una descripción representativa y el recuento de variantes. [Cobertura y métricas](METRICS.es.md) · [Identidad de producto](MODEL.es.md#identidad-de-producto)

## Límites y verificación

La fuente permite estudiar reversos registrados. La entrega del producto, la devolución física, la causa y la factura original quedan fuera de lo que se puede establecer con fiabilidad. El último mes termina el 9 de diciembre de 2011. Sus importes se presentan con la cobertura observada, sin extrapolación ni relleno de fechas posteriores. Se conservaron los valores atípicos.

La conciliación se reconstruyó en peniques enteros. Una lectura independiente del XML del XLSX comprobó totales seleccionados. Las consultas DAX compararon el modelo cargado con los valores reconstruidos, teniendo en cuenta los tipos `Currency` y `BLANK`. [Conciliación](../evidence/financial/RECONCILIATION.es.md) · [Alcance de validación](VALIDATION.es.md)
