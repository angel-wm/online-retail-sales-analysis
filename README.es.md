[English](README.md) | Español

# Análisis de ventas de retail online del Reino Unido

Proyecto de Power BI de dos páginas para explorar ventas de mercancía, cobertura de clientes y valor de cancelaciones/reversos del dataset Online Retail de UCI. Incluye el Excel original, las definiciones editables del reporte y del modelo, y comprobaciones financieras reproducibles.

**Empieza por la [guía de apertura](docs/SETUP.md).** Para desarrollar y mantener el proyecto, abre el [PBIP](uk-online-retail-sales-analysis.pbip) de la raíz. Si prefieres abrir un solo archivo en Power BI Desktop, utiliza el [PBIX exportado](exports/uk-online-retail-sales-analysis.pbix). El PBIP con TMDL/PBIR sigue siendo la fuente principal del proyecto. Las referencias detalladas están en inglés.

Los importes están en **GBP (£)**, la moneda de la fuente. Los datos abarcan del **1 de diciembre de 2010 al 9 de diciembre de 2011**: 2010 sólo contiene diciembre y diciembre de 2011 está incompleto. Las transacciones negativas identifican reversos registrados; no acreditan devoluciones físicas ni insatisfacción de clientes.

## Abrir y explorar

Para **consultar el dashboard**, descarga y abre el [PBIX exportado](exports/uk-online-retail-sales-analysis.pbix) en Power BI Desktop. Puedes explorar los datos incluidos; para actualizarlos en otro equipo, debes configurar la ruta del Excel dentro de Desktop.

Para **desarrollar el proyecto PBIP**:

1. Clona o descarga el repositorio completo, incluidas `powerbi/` y `data/raw/`.
2. Ejecuta `python scripts/configure_source.py` para configurar la ubicación local del Excel y abre el PBIP de la raíz en Power BI Desktop.
3. Actualiza y explora **Sales Overview** y **Product & Customer Insights**. Los filtros Year, Country y Line Type están sincronizados. Antes de crear un commit, ejecuta `python scripts/configure_source.py --reset` para no publicar tu ruta local. Consulta [Configuración](docs/SETUP.md).

El reporte interactivo requiere Power BI Desktop en Windows. Python y .NET sólo se necesitan para el [procedimiento opcional de validación](docs/VALIDATION.md#run-source-and-static-checks).

## Vista previa del dashboard

Las dos imágenes se capturaron del reporte actual en Power BI Desktop el 10 de octubre de 2026, con ambos años incluidos, Country y Line Type en All, y sin marcas seleccionadas en los gráficos.

### Sales Overview

![Sales Overview: KPIs comerciales, ventas netas mensuales, principales países y productos, y facturas de venta por mes](screenshots/sales-overview.png)

La primera página reúne ventas netas de mercancía, facturas de venta, clientes conocidos, valor neto por factura y reversos como proporción del bruto. El gráfico mensual identifica diciembre de 2011 como mes parcial.

### Product & Customer Insights

![Product and Customer Insights: cobertura de clientes, rankings de clientes y reversos, y dispersión con eje de reversos logarítmico](screenshots/product-customer-insights.png)

La segunda página muestra cobertura de clientes y rankings por ventas netas o valor de reversos. La dispersión compara ventas brutas y reversos de los 30 productos principales por bruto. Su eje vertical es logarítmico y el tamaño de las burbujas representa facturas de venta.

Estas imágenes muestran las páginas renderizadas. El alcance de las comprobaciones numéricas y de interacción se explica en [Validación](docs/VALIDATION.md).

## Documentación

| Para… | Consulta |
| --- | --- |
| Abrir, configurar o resolver problemas del reporte | [Configuración](docs/SETUP.md) |
| Interpretar ventas, reversos y cobertura de clientes | [Métricas](docs/METRICS.md) |
| Entender tablas, relaciones e identidad de producto | [Modelo](docs/MODEL.md) |
| Consultar campos y reglas de clasificación | [Diccionario de datos](data/data-dictionary.md) |
| Entender la preparación y los límites de la fuente | [Notas de limpieza](docs/cleaning-notes.md) |
| Repetir comprobaciones y conocer su alcance | [Validación](docs/VALIDATION.md) |
| Localizar archivos y distinguir los generados en local | [Estructura del proyecto](docs/PROJECT_STRUCTURE.md) |

## Fuente y licencia

La fuente versionada es [Online Retail.xlsx](data/raw/Online%20Retail.xlsx), con 541,909 líneas de transacción. Se conserva sin editar. El modelo mantiene 540,455 líneas después de la exclusión documentada de descripciones nulas y conserva las líneas repetidas.

**Cita del dataset:** Chen, D. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository. [DOI: 10.24432/C5BW33](https://doi.org/10.24432/C5BW33).

El dataset conserva su licencia **CC BY 4.0**; consulta [atribución y licencia de los datos](DATA_LICENSE.md). Los materiales propios del repositorio usan la [licencia MIT](LICENSE).

Creado por [Angel W. Miller](https://github.com/angel-wm).
