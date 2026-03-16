[English](README.md) | Español

# Análisis de Ventas de Retail Online del Reino Unido

## Resumen
Este proyecto analiza datos transaccionales de una empresa de retail online del Reino Unido para identificar tendencias en el desempeño de ventas, comportamiento de clientes, demanda de productos y devoluciones.

El resultado final es un dashboard interactivo de **Power BI** de dos páginas, construido sobre un dataset limpio y transformado. El proyecto combina limpieza de datos, modelado, medidas DAX y diseño de dashboard para convertir transacciones crudas en insights de negocio.

## Vista Previa del Dashboard

### Sales Overview
![Sales Overview](dashboard/sales-overview.png)

### Product & Customer Insights
![Product & Customer Insights](dashboard/product-customer-insights.png)

## Preguntas de Negocio
Este proyecto está diseñado para responder preguntas como:
- ¿Cómo evolucionan las ventas a lo largo del tiempo?
- ¿Qué productos generan mayores ventas?
- ¿Qué países aportan más pedidos y mayor valor devuelto?
- ¿Cuál es la tasa de devolución por producto o por país?
- ¿Cómo se comportan el volumen de pedidos y el valor promedio por pedido a lo largo del tiempo?
- ¿Qué clientes generan mayores ventas netas?

## Herramientas Utilizadas
- **Excel** – inspección inicial de los datos
- **Power Query** – limpieza y transformación de datos
- **Power BI** – modelado de datos, medidas DAX y desarrollo del dashboard

## Dataset
El dataset contiene datos transaccionales de retail a nivel de detalle, incluyendo:
- Identificadores de factura / pedido
- Códigos y descripciones de producto
- Cantidades vendidas o devueltas
- Precio unitario
- Identificadores de cliente
- País
- Fecha de transacción

> Nota: El dataset incluye cancelaciones, devoluciones, IDs de cliente faltantes y registros que no corresponden a productos o que usan códigos especiales, por lo que una parte importante del proyecto se centró en la limpieza y clasificación de los datos.

## Limpieza y Preparación de Datos
Los pasos principales de preparación incluyeron:
- Estandarización de tipos de datos
- Identificación de facturas canceladas
- Marcado de transacciones devueltas
- Separación de registros válidos de producto frente a códigos especiales o no-producto
- Manejo de valores faltantes
- Creación de banderas de lógica de negocio y calidad de datos
- Construcción de una tabla calendario para análisis temporal
- Creación de campos de tiempo para análisis mensual y anual

## Modelo de Datos
El modelo de Power BI está construido alrededor de una tabla transaccional **Online Retail** conectada a una tabla **Calendar** para soportar análisis mensuales y anuales.

También se crearon columnas calculadas y medidas para evaluar:
- Main Sales
- Net Sales
- Orders
- Unique Customers
- Average Order Value
- Return Value
- Return Rate

## Estructura del Dashboard
El reporte está organizado en dos páginas:

### 1. Sales Overview
Esta página presenta un resumen general del desempeño del negocio mediante KPIs y visualizaciones de tendencia. Incluye:
- KPI de ventas
- Pedidos
- Clientes únicos
- Valor promedio por pedido
- Tasa de devolución
- Ventas netas en el tiempo
- Ventas por país
- Top 10 productos por ventas netas
- Pedidos por mes

### 2. Product & Customer Insights
Esta página se enfoca en el valor de cliente, devoluciones de producto y análisis comparativo. Incluye:
- Top 10 clientes por ventas netas
- Valor devuelto por país
- Top productos devueltos por valor
- Ventas vs devoluciones por producto

## Filtros
El dashboard incluye filtros interactivos para:
- **Year**
- **Country**
- **Line Type**

## Insights Clave
Este dashboard ayuda a identificar patrones como:
- Un grupo pequeño de productos puede concentrar una gran parte de las ventas totales.
- Algunos países pueden generar un volumen fuerte de pedidos, pero también un valor alto de devoluciones.
- El comportamiento de devoluciones puede variar significativamente entre productos.
- Las ventas netas y los pedidos pueden cambiar de forma importante entre meses.
- La contribución de clientes está concentrada en un número relativamente pequeño de compradores.

## Archivos en Este Repositorio
- `README.md` – documentación del proyecto en inglés
- `README.es.md` – documentación del proyecto en español
- `dashboard/` – capturas del dashboard
- `powerbi/` – archivo del proyecto en Power BI
- `docs/` – notas de apoyo, definiciones o documentación del proyecto
- `data/` – archivos opcionales de apoyo, como diccionario de datos

## Estructura Recomendada del Repositorio
```text
online-retail-sales-analysis/
│
├── README.md
├── README.es.md
├── dashboard/
│   ├── sales-overview.png
│   └── product-customer-insights.png
├── docs/
│   └── cleaning-notes.md
├── data/
│   └── data-dictionary.md
└── powerbi/
    └── online-retail-sales-analysis.pbix
```

## Cómo Usarlo
1. Descarga o abre el archivo `.pbix` desde la carpeta `powerbi/`.
2. Abre el archivo en Power BI Desktop.
3. Actualiza la fuente de datos si es necesario.
4. Usa los filtros para explorar el desempeño por año, país y tipo de línea.
5. Revisa ambas páginas del reporte para comparar ventas, pedidos, clientes y devoluciones.

## Estado del Proyecto
Este proyecto está completo y muestra un flujo de trabajo de análisis de ventas de punta a punta, desde la limpieza y preparación de datos hasta el diseño del dashboard y la generación de insights de negocio.

## Autor
**Angel W. Miller**  
Junior Data Analyst enfocado en business intelligence, analytics y desarrollo de dashboards.

## Contacto
- GitHub: [angel-wm](https://github.com/angel-wm)
- LinkedIn: [Angel W. Miller](https://www.linkedin.com/in/angel-w-m-227451276/)
