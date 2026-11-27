[Read in English](METRICS.md) · [Inicio en español](../README.es.md)

# Métricas e interpretación

Los importes se expresan en GBP (£), la moneda original. El reporte separa la actividad de mercancía elegible de los ajustes administrativos y otros movimientos. Consulta las [expresiones DAX](../powerbi/uk-online-retail-sales-analysis.SemanticModel/definition/tables/Online%20Retail.tmdl) y el [diccionario](../data/data-dictionary.es.md).

## Importes de mercancía y conciliación

| Medida | Definición en la selección actual |
| --- | --- |
| `Main Sales` | Importe bruto de las líneas de mercancía positivas elegibles. |
| `Returns Amount` | Magnitud positiva del importe de las líneas negativas elegibles, contadas una vez. |
| `Return Value` | Alias de `Returns Amount`. |
| `Net Sales` | Ventas brutas de mercancía menos reversos. |
| `Administrative Adjustments` | Importe con signo de líneas administrativas y códigos especiales. |
| `Other Movements` | Importe con signo de vales regalo y demás movimientos excluidos. |
| `Total Sales` | Importe con signo de todas las líneas cargadas. |

```text
Net Sales + Administrative Adjustments + Other Movements = Total Sales
```

El prefijo de cancelación y la cantidad negativa pueden describir la misma línea. La fuente registra reversos, con alcance insuficiente para determinar una devolución física, su causa o la factura de venta original. Los ajustes administrativos son movimientos del archivo.

## Conteos y proporciones

| Medida | Definición |
| --- | --- |
| `Orders` | Facturas únicas con al menos una línea de venta elegible. |
| `Unique Customers` | Identificadores de cliente distintos y no vacíos en ventas elegibles. |
| `Units Sold` | Unidades de las líneas positivas elegibles. |
| `Units Reversed` | Magnitud de las unidades de las líneas negativas elegibles. |
| `Cancelled Orders` | Facturas únicas con líneas negativas elegibles. Todas tienen prefijo `C` en esta fuente. |
| `Average Order Value` | `Net Sales / Orders`, importe neto por factura de venta en el período de registro. |
| `Return rate` | `Returns Amount / Main Sales`, importe de reversos sobre ventas brutas del período. |
| `Zero Price Records` | Líneas cargadas con precio unitario cero, de cualquier tipo. |
| `Unidentified Net Sales` | Valor neto de mercancía con ID de cliente vacío. |
| `Identified Sales Share` | Ventas brutas elegibles con ID conocido como proporción de las ventas brutas elegibles. |

Los conteos distintos pueden duplicar facturas o clientes si se suman entre productos o países. Los reversos se registran en su propio período, por lo que la proporción de importes puede superar el 100 % en una selección estrecha. Las ventas anónimas se incluyen en los totales comerciales y se excluyen de los conteos y rankings de clientes identificados. Las tarjetas de cobertura usan bases distintas, una neta y la otra bruta.

## Precisión

Se multiplica la cantidad por el precio original, incluso si contiene valores como `0.001`. El importe de cada línea se redondea a dos decimales al par y se almacena como `Currency`. El cociente neto por factura es £495,25067668… en la reconstrucción y £495,2507 en el tipo nativo, que se muestra como £495,25. Los porcentajes conservan precisión `Double` antes de mostrarse a dos decimales.

## Filtros y valores en blanco

`KEEPFILTERS` combina las reglas de elegibilidad con los filtros activos. Si faltan filas elegibles o el denominador, la medida puede devolver `BLANK`. Una selección con solo reversos puede mostrar ventas netas negativas y ratios en blanco. Una selección exclusivamente anónima deja en blanco el conteo de clientes identificados. El eje logarítmico de la dispersión requiere reversos positivos, así que una selección puede mostrar menos de 30 puntos.

El encabezado usa los extremos del calendario seleccionado y avisa cuando las ventas brutas y los reversos están en blanco. Las notas de Reino Unido y de los dos productos principales se calculan sobre toda la selección, aunque los gráficos contiguos tengan un Top 10. Los empates del ranking de reversos se resuelven por código.

## Valores de referencia

| Métrica | Total con filtros despejados |
| --- | ---: |
| Ventas brutas elegibles | £10.271.315,81 |
| Reversos de mercancía | £478.724,18 |
| Ventas netas de mercancía | £9.792.591,63 |
| Ajustes administrativos | −£45.646,76 |
| Otros movimientos | £803,06 |
| Total de movimientos con signo | £9.747.747,93 |
| Facturas de venta | 19.773 |
| Clientes identificados | 4.334 |
| Valor neto por factura de venta | £495,25 |
| Importe de reversos sobre ventas brutas | 4,66 % |
| Ventas netas sin cliente identificado | £1.505.928,31 |
| Ventas brutas con cliente identificado | 85,30 % |

Estos valores se contrastaron con el Excel y DAX nativo. [Validación](VALIDATION.es.md) · [Conciliación financiera](../evidence/financial/RECONCILIATION.es.md)

## Cobertura del período

La fuente abarca 374 días consecutivos en 13 meses, desde el 1 de diciembre de 2010 a las 08:26 hasta el 9 de diciembre de 2011 a las 12:50. Ambos gráficos mensuales señalan diciembre de 2011 como incompleto.

Noviembre de 2011 registró £1.432.734,99 netas en 30 días. Diciembre registró £441.366,51 hasta el día 9, lo que produce una caída aparente del 69,19 % al comparar períodos desiguales. Si se toman los primeros nueve días de cada mes, noviembre registra £435.185,39 y diciembre £441.366,51, una diferencia descriptiva del 1,42 %. Diciembre termina a mitad del noveno día y la comparación carece de ajuste estacional o extrapolación. [Comprobación mensual](../evidence/validation/monthly-chart-check.json)
