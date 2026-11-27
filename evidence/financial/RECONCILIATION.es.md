[Read in English](RECONCILIATION.md) · [Inicio en español](../../README.es.md)

# Conciliación financiera

La reconstrucción compara los cálculos originales y actuales con el mismo Excel, todos los países y todas las fechas. Los importes están en GBP. La validación DAX se registra por separado. [Validación en Desktop](../../docs/VALIDATION.es.md#comprobaciones-en-power-bi-desktop)

| Medida | Original | Actual |
| --- | ---: | ---: |
| Ventas brutas elegibles | £10.285.076,90 | £10.271.315,81 |
| `Returns Amount` | £896.812,49 | £478.724,18 |
| `Return Value` | £714.005,77 | £478.724,18 |
| Ventas netas de mercancía | £9.388.264,41 | £9.792.591,63 |
| Facturas de venta | 19.775 | 19.773 |
| Valor neto por factura | £474,00 | £495,25 |
| Reversos sobre ventas brutas | 9,00 % | 4,66 % |
| Total con signo | £9.747.747,93 | £9.747.747,93 |

Dos comisiones positivas de `AMAZONFEE` se clasificaron como administrativas. Eso redujo las ventas brutas de mercancía en £13.761,09 y eliminó dos facturas de ese conteo. El importe de reversos excluye £418.088,31 en negativos administrativos, incluidos £235.281,59 de `AMAZONFEE` antes tratados como producto.

Aplicar el mismo alcance a ventas y reversos subió el importe neto de mercancía en £404.327,22. El total de movimientos con signo se conserva. El importe neto por factura pasó de un redondeo a múltiplos de dos a un valor nativo de £495,2507, mostrado como £495,25. La proporción de reversos bajó del 9 % implementado originalmente al 4,66078727 % antes del redondeo visual. La diferencia es de 4,33921273 puntos porcentuales.

## Archivos de respaldo

- [Comparación CSV](before_after.csv) y [comparación JSON](before_after.json) con valores y variaciones.
- [Cobertura](coverage.json), [serie mensual](monthly.csv) y [métricas por país](countries.json).
- [Códigos especiales](special_codes.json), [identidad de productos](product_identity.csv) y [definiciones de medidas](measure_definitions.json).

[Valores de referencia](../../docs/METRICS.es.md#valores-de-referencia) · [Preparación de los datos](../../docs/cleaning-notes.es.md)
