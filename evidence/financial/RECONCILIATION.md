# Conciliación financiera antes / después

Población: todas las fechas y países; sin selecciones externas. GBP. Valores reconstruidos desde Excel; no ejecutados por un motor DAX/M.

| KPI | Definición corregida | Original | Corregido | Diferencia absoluta | Diferencia relativa | Explicación |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Main Sales | Gross eligible merchandise sales. Product, Normal, quantity and price positive, invoice not cancelled; GBP. | 10,285,076.90 | 10,271,315.81 | -13,761.09 | -0.133797% | Se reclasifican dos comisiones positivas AMAZONFEE. |
| Total Sales | Signed total of all loaded movements in the current filter context. Reconciliation measure; GBP. | 9,747,747.93 | 9,747,747.93 | 0.00 | 0.000000% | Sin cambio; total firmado de todos los movimientos cargados. |
| Returns Amount | Magnitude of negative eligible merchandise movements, counted once. Cancellation/reversal proxy, not proof of physical returns; GBP. | 896,812.49 | 478,724.18 | -418,088.31 | -46.619367% | Se excluyen todos los negativos administrativos, incluido AMAZONFEE. |
| Return Value | Compatibility alias for Returns Amount. Same merchandise scope in every visual; GBP. | 714,005.77 | 478,724.18 | -235,281.59 | -32.952337% | AMAZONFEE deja de ser mercancía. Mismo ámbito que Returns Amount. |
| Net Sales | Gross eligible merchandise sales less merchandise cancellations/reversals. Administrative adjustments and other movements excluded; GBP. | 9,388,264.41 | 9,792,591.63 | 404,327.22 | 4.306730% | Bruto y reversos comparten ámbito de mercancía. |
| Orders | Distinct invoices with at least one eligible positive merchandise line. Cancellation invoices excluded. Counts are not additive across products/countries. | 19,775 | 19,773 | -2 | -0.010114% | Dos facturas que sólo aportaban AMAZONFEE dejan de ser pedidos comerciales. |
| Unique Customers | Distinct identified customers with eligible merchandise sales in the current context. Anonymous buyers cannot be counted. | 4,334 | 4,334 | 0 | 0.000000% | La población de clientes identificados no cambia. |
| Units Sold | Positive eligible merchandise units. Administrative/gift voucher quantities excluded. | 5,577,101 | 5,577,099 | -2 | -0.000036% | Se excluyen las dos unidades administrativas positivas AMAZONFEE. |
| Cancelled Orders | Distinct invoices containing eligible negative merchandise movements. All such invoices in this source have prefix C; no claim of physical returns or original-order linkage. | 3,836 | 3,422 | -414 | -10.792492% | Sólo facturas con reversos monetarios elegibles de mercancía; se excluyen administrativos y líneas de valor cero. |
| Zero Price Records | Loaded lines with zero unit price. Quality diagnostic across all line types, respecting current filters. | 1,061 | 1,061 | 0 | 0.000000% | Se conserva el diagnóstico con el mismo filtro. |
| Average Order Value | Net merchandise value per eligible sale invoice in the selected period. Reversals are dated at posting, not matched to original orders. Not a physical basket average; GBP. | 474 | 495.25067668 | 21.25067668 | 4.483265% | Neto corregido / 19,773 pedidos; se elimina MROUND a múltiplos de dos. |
| Return rate | Merchandise cancellation/reversal amount divided by gross eligible merchandise sales in the selected period. Posting-period value ratio, not physical return probability; blank if denominator absent. | 9.0% | 4.66078727% | -4.33921273% | -48.213475% | Numerador de mercancía y cociente sin ROUND. Cambio en puntos porcentuales detallado abajo. |

La tasa implementada pasa de 9.000000% a 4.66078727%: -4.33921273 puntos porcentuales. La tasa original antes de ROUND era 8.71955065%. El cambio combina la corrección del ámbito y la eliminación del redondeo prematuro. Las diferencias relativas usan el valor original absoluto como denominador.

El AOV original sin MROUND era £474.75420531; su valor DAX reconstruido era £474. El nuevo cálculo es £495.25067668 y se presenta como £495.25.

Neto de mercancía £9,792,591.63 + ajustes administrativos -£45,646.76 + otros movimientos £803.06 = total global £9,747,747.93.
