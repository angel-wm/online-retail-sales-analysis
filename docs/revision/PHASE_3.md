# Fase 3 — Dashboard y experiencia visual

Estado: cambios reales aplicados a PBIR y comprobación estática satisfactoria. La aceptación visual e interactiva en Power BI Desktop está pendiente. No se ha producido ni presentado una captura nueva como si fuera un render nativo.

## Alcance y disposición

Se conservan las dos páginas, identidad azul/gris, tipos de gráfico que responden a preguntas útiles, seis segmentadores, botones y los 31 identificadores originales. Se añaden siete contenedores: explicación del neto, puente financiero, dos tarjetas de cobertura, una nota de limitaciones y dos notas de alcance de filtros. No se añaden páginas. El lienzo cambia de 1336 × 768 a 1336 × 920 para dar espacio a diez filas de ranking y al contexto necesario; el ajuste a página en pantallas pequeñas debe revisarse personalmente.

Se alinean encabezados, tarjetas y bloques, se separan títulos y subtítulos y se declara el periodo incompleto en ambas páginas. Los contenedores de contenido no se solapan ni salen del lienzo; las formas de fondo sí se superponen intencionadamente. Se conservan tonos azules para ventas y se usa un acento cobre para reversiones, con títulos y ejes que también expresan su significado. Se añaden texto alternativo y orden de tabulación único, sin afirmar una prueba de lector de pantalla.

Tras las capturas aportadas por el usuario, se corrige el contraste de Country y Line Type en ambas páginas. Sales Overview conservaba texto casi blanco (`#F0F2F5` o blanco de tema) sobre el desplegable blanco; Insights utilizaba un color de tema demasiado claro. Los cuatro desplegables pasan a texto gris azulado `#52667B` y fondo blanco explícito en Values, que según [Microsoft](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-slicer-visual#format-slicers) se aplica a la caja y al panel desplegado. El contraste calculado de esa pareja es 5.923:1; no es una medición de un render nativo. Los seis encabezados usan blanco explícito sobre el panel azul, los años conservan blanco sobre azul y se normaliza Segoe UI a 10 pt. Se alinean los dos títulos Filters con más separación respecto a las acciones de Year y se desactiva el título vacío de Line Type. [slicer-contrast.json](../../evidence/validation/slicer-contrast.json) registra los valores antes/después y confirma que consultas, selecciones, sincronización y los 13 archivos del modelo semántico permanecen iguales al commit previo.

## Sales Overview

La tarjeta comercial principal utiliza **Net Sales** y se etiqueta **Net merchandise sales**. Pedidos se refiere a facturas con venta elegible; clientes a IDs conocidos; AOV a neto por factura de venta; la tasa a valor de reversos / bruto. El formato monetario del modelo y los overrides de consulta se alinean con GBP. Los dos cocientes conservan toda su precisión y se presentan con dos decimales.

La evolución mensual utiliza neto, línea sin área y sin etiquetas para todos los puntos. El eje monetario declara GBP y unidades de millones con un decimal, evitando que distintos niveles se muestren todos como £1M. La serie de pedidos conserva su pregunta propia; el AOV mensual se ofrece en tooltip, sin añadir otro gráfico. Los tooltips incluyen bruto, reversos y neto para explicar el resultado.

Países y productos muestran Top 10 por neto, indicado en el título. Los productos se agrupan por `DimProduct.Product_Label` (código y nombre representativo), con más anchura para la categoría, texto ajustable y altura para diez filas. El tooltip muestra código, nombre completo y variantes. Esto resuelve la referencia y asigna espacio; el recorte real y la ausencia de scroll necesitan comprobarse en Desktop.

La tabla inferior muestra bruto, reversos, ajustes administrativos, otros movimientos y total firmado, junto al neto de la tarjeta. Mantiene utilidad si Line Type selecciona Adjustment o Gift Voucher, donde las métricas comerciales carecen de población. No se mezcla el total global con ventas netas de mercancía.

## Product & Customer Insights

Se conservan las ventas sin ID en las métricas comerciales y se hace explícita su exclusión del ranking de clientes conocidos. Dos tarjetas muestran neto sin CustomerID y participación del bruto con CustomerID conocido, bajo la selección vigente. Esta última describe cobertura financiera, no proporción de compradores.

Los rankings de países y productos utilizan el mismo reverso de mercancía que el resto del reporte. Se elimina el umbral oculto de £1,000 en países. Las exclusiones manuales de descripciones del ranking de productos se sustituyen por las reglas financieras trazables de la Fase 1 y la identidad por código de la Fase 2.

El dispersograma conserva bruto en X y reversos en Y, ambos con ejes GBP y unidades de miles; el tamaño utiliza Orders. Su subtítulo declara **Top 30 by gross sales. Bubble = sale invoices**. Se cambia Top 30 de neto a bruto para no ocultar un producto grande cuyo neto cae al revertirse. Se ocultan las etiquetas de todos los puntos y se deja el detalle completo en tooltip. No representa una relación causal ni satisfacción del cliente.

## Filtros e interacciones declaradas

Year, Country y Line Type se sincronizan entre las dos páginas mediante tres grupos explícitos, con cambios de campo y filtro compartidos. La acción nativa ClearAllSlicers se conserva y la etiqueta pasa a **Clear selectors**. La nota lateral describe su alcance: limpia los tres segmentadores; una selección de gráfico se limpia pulsando de nuevo la marca. Top N permanece como restricción de cada visual y no se promete un reset universal.

Las selecciones de gráfico filtran los visuales cuantitativos de su página, en lugar de depender de resaltados parciales. No filtran las listas de segmentadores. Los segmentadores filtran todos los visuales cuantitativos. Las 128 parejas de interacción tienen origen y destino válidos, sin duplicados. El comportamiento efectivo, la navegación y la sincronización requieren la aceptación nativa.

## Evidencia

[report-checks.json](../../evidence/validation/report-checks.json) comprueba los 38 contenedores, los 31 originales preservados, 45 referencias a columnas, 90 referencias a medidas, entidades, metadatos de consulta, dependencia de medidas sin ciclos, rutas PBIP/PBIR, recursos, Top N, reset, grupos de segmentadores e interacciones. No elimina medidas, columnas, relaciones ni visuales originales.

[final-json-schema.json](../../evidence/validation/final-json-schema.json) registra 51 archivos JSON legibles, 10 validaciones con esquema exacto y 38 validaciones de compatibilidad. Los tres JSON sin esquema declarado sólo se comprueban como JSON. El esquema visual 2.13.0 declarado por el original devuelve HTTP 404 en las fuentes públicas de Microsoft; se usa 2.9.0 como comprobación parcial, sin cambiar la versión del proyecto. No se confunde esta compatibilidad con aceptación completa, validación de cada propiedad del visual o funcionamiento en Desktop.

Las medidas y relaciones no cambian en esta fase. La validación final vuelve a contrastar el modelo y los KPI con el Excel. [DESKTOP_ACCEPTANCE.md](DESKTOP_ACCEPTANCE.md) define la aceptación pendiente.
