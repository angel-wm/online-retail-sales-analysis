# Fase 1 — Lógica financiera y KPI

Estado: implementación aplicada; recálculo de fuente y comprobación independiente a céntimos. La ejecución de DAX/M en Power BI Desktop queda pendiente y no se sustituye por estas pruebas.

## Definición comercial adoptada

Se aplica la propuesta del usuario: **ventas netas de mercancía** como KPI principal. El bruto incluye líneas `Product`, `Normal`, con cantidad y precio positivos, sin prefijo de factura C. Se descuenta una sola vez el importe de líneas `Product`, `Normal`, con cantidad negativa y precio positivo. Los ajustes administrativos y otros movimientos quedan fuera del KPI comercial y se conservan en medidas de conciliación.

`Is_Cancelled` sigue indicando prefijo C; `Is_Merchandise_Reversal` determina la elegibilidad económica de la reversión. No se resta una vez por cantidad negativa y otra vez por prefijo C. Todos los negativos de mercancía con importe elegible de esta fuente tienen C. Los negativos sin C son movimientos de valor cero. No hay ventas positivas de mercancía en facturas C que requieran otra política.

La terminología del reporte es **cancelaciones / reversiones**. La fuente no identifica devoluciones físicas, motivos, entregas ni un enlace formal con la factura original. Se conservan los dos pares grandes que se revierten en minutos y todos los demás registros.

## Clasificación revisada

Se inspeccionaron **todos los 26 códigos que no siguen el patrón numérico habitual**, no sólo AMAZONFEE. `special_codes.json` registra sus nombres, recuentos, importes y clasificaciones efectivas.

- `AMAZONFEE` y la variante documentada `AMAZON FEE`: Adjustment. Los 34 registros incluyen £13,761.09 positivos y £235,281.59 negativos. Se mantiene la variante con espacio para futuras fuentes.
- M, S, POST, BANK CHARGES, D, DOT, C2, B y CRUK: se conserva la clasificación administrativa existente. Incluye portes, descuentos, comisiones, muestras, ajustes manuales y deuda incobrable. La medida no se denomina beneficio ni gasto operativo.
- Prefijo GIFT_ o descripción GIFT VOUCHER: Gift Voucher. Sus £769.14 firmados se mantienen en otros movimientos.
- Los códigos DCGS con descripción de mercancía, DCGSSBOY, DCGSSGIRL y PADS siguen siendo productos. Un código alfabético no demuestra que sea administrativo. PADS tiene precio 0.001; se conserva y no se redondea el precio antes de multiplicar.
- Se conserva la regla de descripción EBAY como Adjustment. Dos códigos DCGS tienen tanto nombres de mercancía como EBAY; esas filas se clasifican individualmente. Las filas EBAY son de importe cero. No se asigna una única categoría al código en la dimensión de producto.
- Se conservan los flags Normal, Manual / Review y Operational / Non-Product. No se inventa una nueva regla a partir de una descripción ambigua.

`Movement_Type` particiona las filas cargadas en venta de mercancía, reversión de mercancía, ajuste administrativo, vale y otro movimiento excluido. No es un nuevo filtro financiero oculto; documenta la clasificación usada por las medidas.

## Medidas

Las 12 medidas originales conservan nombre y lineageTag para proteger referencias. `Return Value` pasa a ser un alias de `Returns Amount`, con idéntico ámbito. Todas las restricciones de elegibilidad se intersectan con los filtros externos mediante KEEPFILTERS. Se eliminan MROUND y el redondeo del cociente porcentual. `DISTINCTCOUNTNOBLANK` cuenta IDs sin ampliar una selección de cliente.

`Total Sales` mantiene su significado de total firmado global dentro del contexto seleccionado. `Main Sales` es bruto elegible de mercancía. `Net Sales` es el KPI comercial. Los títulos visibles se corrigen en la fase 3. Se conserva BLANK cuando no existe población; el neto de un producto con únicamente reversiones es negativo. AOV y tasa quedan en BLANK cuando falta el denominador, sin errores ni valores artificiales.

El AOV mantiene la fórmula neto / pedidos de venta del periodo, ahora con precisión completa. No representa el tamaño de una cesta física: las reversiones se imputan a su fecha de registro, y no se emparejan con pedidos de otro periodo. La tasa es un cociente de valor del periodo, puede superar 100% y no se limita artificialmente.

Se añaden cinco medidas con uso concreto: Administrative Adjustments y Other Movements para el puente financiero; Units Reversed para corregir tooltips; Unidentified Net Sales e Identified Sales Share para comunicar cobertura de clientes. No se añade una tasa de devolución física ni una proporción de pedidos cancelados con una cohorte que el Excel no acredita.

## Puente financiero

| Concepto | GBP |
| --- | ---: |
| Bruto elegible de mercancía | £10,271,315.81 |
| Cancelaciones / reversiones de mercancía | -£478,724.18 |
| Neto de mercancía | £9,792,591.63 |
| Ajustes administrativos firmados | -£45,646.76 |
| Otros movimientos (vales £769.14 y residuales £33.92) | £803.06 |
| Total firmado global | £9,747,747.93 |

El total global no cambia. El neto comercial aumenta £404,327.22: se quitan £13,761.09 de comisiones del bruto y se dejan de descontar £418,088.31 de negativos administrativos. Estos últimos son £235,281.59 de AMAZONFEE más £182,806.72 de otros ajustes.

Ver [conciliación completa](../../evidence/financial/RECONCILIATION.md), [resultados JSON](../../evidence/financial/before_after.json) y [serie mensual](../../evidence/financial/monthly.csv). Los importes conservan la política existente de redondeo por línea a dos decimales, empate al par. La precisión de ratios y AOV se mantiene en el cálculo; el formato controla su presentación. La moneda es GBP sin conversión, coherente con [la fuente UCI](https://archive.ics.uci.edu/dataset/352/online%2Bretail).

## Validación y alcance

La reconstrucción original coincide con los 12 KPI de la auditoría. El nuevo puente concilia a céntimos. Un segundo lector del XML del XLSX, con lógica escalar y Decimal, contrasta importes, pedidos, clientes, unidades, facturas de reversión y diagnósticos sin usar el helper de pandas. El parser oficial de Microsoft valida los objetos TMDL y sus relaciones; no evalúa las expresiones DAX/M.

Los totales de pedidos y clientes son distintos por contexto, no sumables a través de productos o países. Los £1,505,928.31 de neto de cliente desconocido permanecen en el KPI comercial y fuera del ranking de clientes identificados. No hay decisión de negocio material sin resolver que impida pasar a la fase 2.
