[Read in English](data-dictionary.md) · [Inicio en español](../README.es.md)

# Diccionario de datos

La hoja **Online Retail** se conserva en el [Excel original](raw/Online%20Retail.xlsx). Los nombres y categorías de esta guía coinciden con los identificadores que se ven en Power BI. [Modelo](../docs/MODEL.es.md) · [Métricas](../docs/METRICS.es.md)

## Tabla Online Retail

| Campo del Excel | Campo del modelo | Tipo y significado |
| --- | --- | --- |
| `InvoiceNo` | `Invoice_ID` | Texto, identificador de factura, compartido por varias líneas. |
| `StockCode` | `Stock_Code` | Texto, código recortado y en mayúsculas que vincula con `DimProduct`. |
| `Description` | `Product_Name` | Texto, descripción original de la línea. |
| `Quantity` | `Quantity` | Entero, cantidad con signo. |
| `InvoiceDate` | `Invoice_Date` | Fecha y hora originales de la transacción. |
| `UnitPrice` | `Unit_Price` | `Double`, precio unitario original en GBP. |
| `CustomerID` | `Customer_ID` | Texto, identificador de cliente que puede estar vacío. |
| `Country` | `Country` | Texto, país registrado. |

| Campo derivado | Tipo y significado |
| --- | --- |
| `Invoice_Day` | Fecha en un campo DateTime. Clave de calendario. |
| `Sales_Amount` | `Currency`. Cantidad por precio original, redondeada al par a dos decimales. |
| `Line_Type` | Texto, Product, Gift Voucher o Adjustment. |
| `Record_Flag` | Texto, Normal, Manual / Review u Operational / Non-Product. |
| `Is_Cancelled` | Booleano. El identificador normalizado comienza con `C`. |
| `Is_Negative_Qty` | Booleano. Cantidad no nula inferior a cero. |
| `Is_Zero_Price` | Booleano. Precio unitario no nulo igual a cero. |
| `Include_In_Main_Analysis` | Booleano. Venta positiva elegible. |
| `Is_Merchandise_Reversal` | Booleano. Movimiento negativo de mercancía elegible. |
| `Movement_Type` | Texto. Categoría económica exclusiva para conciliación. |

## Reglas de clasificación

**Tipo de línea.** Se aplica en este orden a códigos y descripciones recortados y convertidos a mayúsculas:

1. **Gift Voucher** si el código empieza por `GIFT_` o la descripción contiene `GIFT VOUCHER`.
2. **Adjustment** si la descripción es `EBAY` o el código pertenece a `M, S, POST, AMAZONFEE, AMAZON FEE, BANK CHARGES, D, DOT, C2, B, CRUK`.
3. **Product** para el resto.

**Indicador de registro.** Si falta el ID de cliente y la descripción empieza con `*`, se asigna **Manual / Review**. Si falta el ID, el precio es cero o nulo y la descripción contiene `?`, `MISSING`, `LOST`, `DAMAGE`, `DISPLAY` o `SOLD AS SETS`, se asigna **Operational / Non-Product**. Las demás líneas quedan como **Normal**.

**Elegibilidad.** Una venta requiere Product, Normal, factura sin cancelar, cantidad positiva y precio positivo. Un reverso requiere Product, Normal, cantidad negativa y precio positivo. El prefijo `C` sirve de diagnóstico y el importe negativo se cuenta una vez.

**Tipo de movimiento.** Se toma la primera categoría aplicable entre venta elegible, reverso elegible, ajuste administrativo, movimiento de vale regalo y otro movimiento excluido. [Códigos especiales](../evidence/financial/special_codes.json)

## Tabla Calendar

| Campo | Función |
| --- | --- |
| `Date`, `Year`, `Day` | Clave diaria, año y día del mes. |
| `Trimester` | Trimestre `T1` a `T4`. |
| `Month#`, `Month`, `Month_short` | Número, nombre y abreviatura del mes. Los nombres se ordenan por número. |
| `Year_Month`, `YearMonth_Label` | Etiquetas de mes ordenadas por `YearMonthSort`. La segunda marca el mes final incompleto con `*`. |
| `YearMonthSort` | Entero `Year * 100 + Month#`. |
| `Weekday#`, `Weekday` | Número y nombre del día de la semana. El lunes es 1. |

## Tabla DimProduct

| Campo | Función |
| --- | --- |
| `Stock_Code` | Texto y clave única de la dimensión. |
| `Product_Name` | Descripción representativa normalizada. |
| `Product_Label` | Código y descripción separados por una raya. |
| `Description_Variants` | Número entero de descripciones normalizadas distintas del código. |

Los campos originales del código y descripción de la tabla de hechos están ocultos en la lista del reporte. El modelo conserva los campos para diagnóstico. Consulta la [identidad de producto](../docs/MODEL.es.md#identidad-de-producto) y el [contrato de medidas](../evidence/financial/measure_definitions.json).
