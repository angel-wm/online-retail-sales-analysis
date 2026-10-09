[English](README.md) | Español

# Análisis de Ventas de Retail Online del Reino Unido

## Resumen

Este proyecto analiza ventas, productos, cobertura de clientes y cancelaciones/reversiones de mercancía del dataset UK Online Retail mediante un reporte de Power BI de dos páginas.

El proyecto de trabajo es [uk-online-retail-sales-analysis.pbip](uk-online-retail-sales-analysis.pbip), directamente en la raíz. Sus componentes de reporte y modelo están en `powerbi/`. Las correcciones realizadas en el checkout separado `review` se consolidaron en este proyecto original; existe un único acceso PBIP activo. [La estructura del proyecto](docs/PROJECT_STRUCTURE.md) explica las carpetas y respaldos actuales.

Es una rama local en revisión. El estado de las verificaciones nativas y los pendientes visuales/de interacción se documentan en [Aceptación en Desktop](docs/revision/DESKTOP_ACCEPTANCE.md). Las capturas siguientes muestran el reporte anterior.

## Cómo Usarlo

1. Abrir [uk-online-retail-sales-analysis.pbip](uk-online-retail-sales-analysis.pbip) en Power BI Desktop. El PBIX placeholder archivado no es un reporte válido.
2. Si el proyecto cambió de ubicación, cerrar Desktop y ejecutar `python scripts/configure_source.py` desde la nueva raíz. Configura `SourceFilePath` para el archivo local `data/raw/Online Retail.xlsx`. Volver a abrir el mismo PBIP de la raíz y actualizar.
3. Explorar **Sales Overview** y **Product & Customer Insights**. Los segmentadores Year, Country y Line Type están sincronizados entre ambas páginas.
4. Revisar [cambios financieros](docs/revision/PHASE_1.md), [cambios del modelo](docs/revision/PHASE_2.md), [reproducción](docs/revision/REPRODUCE.md) y [pendientes en Desktop](docs/revision/DESKTOP_ACCEPTANCE.md).

El PBIX real recuperado se conserva en `backups` como instantánea histórica. Editar el PBIP no actualiza ese binario; un PBIX actualizado debe guardarse desde Desktop tras la aceptación del proyecto.

## Vista Previa del Dashboard

Estas capturas muestran el diseño del reporte original de dos páginas. Sus métricas no están publicadas aquí como
resultados numéricos verificados de forma independiente.

### Sales Overview

![Página Sales Overview de Power BI con KPIs comerciales y tendencias de ventas](screenshots/sales-overview.png)

La página ejecutiva reúne ventas, pedidos, clientes únicos, valor promedio por pedido, tasa de devolución, ventas
netas en el tiempo, desempeño por país, los diez productos principales por ventas netas y volumen mensual de
pedidos.

### Product & Customer Insights

![Página Product and Customer Insights de Power BI con comparaciones de clientes y devoluciones](screenshots/product-customer-insights.png)

La segunda página compara los diez clientes principales por ventas netas, valor devuelto por país, productos con
mayor valor de devoluciones y ventas frente a devoluciones por producto.

El reporte documenta los filtros **Year**, **Country** y **Line Type**. El PBIP actual permite interactuar con ellos; estas capturas históricas son estáticas.

## Preguntas de Negocio

El análisis se diseñó para explorar:

- ¿Cómo cambian las ventas y el volumen de pedidos con el tiempo?
- ¿Qué productos y clientes aportan más ventas netas?
- ¿Qué países concentran pedidos y valor devuelto?
- ¿Cómo varían las devoluciones entre productos y países?
- ¿Cómo evoluciona el valor promedio por pedido?

Estas son preguntas que el dashboard busca investigar, **no hallazgos verificados de forma independiente**. No
deben confundirse posibles patrones de concentración o devoluciones con resultados medidos sin disponer del
reporte o analizar los datos de origen.

## Herramientas Utilizadas

- **Excel:** inspección inicial de los datos.
- **Power Query:** preparación, clasificación y transformación documentadas.
- **Power BI / DAX:** modelo de datos, medidas y visualizaciones documentados.

## Dataset

La fuente versionada es [`data/raw/Online Retail.xlsx`](data/raw/Online%20Retail.xlsx). Sus campos de transacción
incluyen identificadores y fechas de factura, códigos y descripciones de productos, cantidades, precios unitarios,
identificadores de clientes y países.

La fuente es el dataset **Online Retail** publicado por UCI Machine Learning Repository y creado por Daqing Chen.
UCI lo identifica como 541,909 transacciones entre el 1 de diciembre de 2010 y el 9 de diciembre de 2011 de una
empresa de retail online registrada en el Reino Unido y sin tienda física.

**Cita del dataset:** Chen, D. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository.
https://doi.org/10.24432/C5BW33

El dataset está licenciado bajo **Creative Commons Attribution 4.0 International (CC BY 4.0)**. La copia incluida
en este repositorio conserva esa licencia; consultar [Licencia y atribución del dataset](DATA_LICENSE.md).

Las cancelaciones, cantidades negativas, IDs de cliente vacíos y códigos especiales requieren tratamiento distinto
según la métrica. Las [notas de limpieza](docs/cleaning-notes.md) explican las decisiones; el
[diccionario de datos](data/data-dictionary.md) recoge los campos y reglas documentados.

## Limpieza y Preparación de Datos

La fuente Excel se conserva byte a byte. El modelo excluye las 1,454 filas con descripción nula según la regla de calidad recuperada, dejando 540,455 filas en la tabla de hechos. Las líneas de transacción repetidas se conservan.

Las ventas brutas de mercancía requieren líneas Product normales, cantidad y precio positivos y factura no cancelada. Los reversos de mercancía requieren cantidad negativa y precio positivo en líneas Product normales. El neto comercial resta estos reversos del bruto; los ajustes administrativos y otros movimientos permanecen separados. `AMAZONFEE` se clasifica como administrativo. Los importes usan GBP (£) y los cocientes conservan la precisión completa del cálculo.

Consultar [Fase 1](docs/revision/PHASE_1.md), [Fase 2](docs/revision/PHASE_2.md) y [conciliación antes/después](evidence/financial/before_after.csv) para las definiciones actuales. Las [notas de limpieza originales](docs/cleaning-notes.md) documentan la implementación histórica y pueden diferir del modelo revisado.

## Modelo de Datos

El modelo actual contiene la tabla de hechos **Online Retail**, **Calendar** y **DimProduct**, además de las dos tablas automáticas de fecha ocultas conservadas. Hay 17 medidas y tres relaciones. La identidad de producto usa código y descripción representativa determinista; las variantes originales de descripción permanecen consultables.

La implementación autoritativa es el TMDL en `powerbi/uk-online-retail-sales-analysis.SemanticModel/definition/`. [La Fase 2](docs/revision/PHASE_2.md) explica relaciones, descripciones y parámetro de origen. El [diccionario original](data/data-dictionary.md) se mantiene como referencia histórica.

## Mapa de Documentación

| Para… | Consulta |
| --- | --- |
| Abrir el proyecto actual | [PBIP de la raíz](uk-online-retail-sales-analysis.pbip) |
| Entender carpetas y respaldos | [Estructura del proyecto](docs/PROJECT_STRUCTURE.md) |
| Examinar la fuente original | [Online Retail.xlsx](data/raw/Online%20Retail.xlsx) |
| Revisar las medidas corregidas | [Fase 1](docs/revision/PHASE_1.md), [antes/después](evidence/financial/before_after.csv) |
| Revisar el modelo e identidad de producto | [Fase 2](docs/revision/PHASE_2.md) |
| Repetir validaciones | [Guía de reproducción](docs/revision/REPRODUCE.md) |
| Revisar pendientes nativos | [Aceptación en Desktop](docs/revision/DESKTOP_ACCEPTANCE.md) |
| Verificar procedencia y licencia | [Licencia del dataset](DATA_LICENSE.md) |

```text
uk-online-retail-sales-analysis.pbip
powerbi/          # reporte PBIR y modelo semántico TMDL
data/raw/        # fuente Excel original
docs/revision/   # decisions, phase changes and acceptance
docs/archive/    # recovered historical PDF, measures and theme
screenshots/     # capturas del reporte original
scripts/         # source configuration and validation
evidence/        # baseline, reconciliation and validation receipts
backups/         # respaldos locales; ignorados por Git
```

## Estado del Proyecto

Las correcciones están implementadas localmente en `codex/retail-dashboard-corrections`. No se hizo push, merge ni publicación en Power BI Service. La conciliación de fuente, parseo TMDL, cobertura de esquemas JSON, referencias y respaldos tienen evidencia reproducible en `evidence/validation`.

La actualización nativa se registra en `desktop-native-refresh.json` y el contraste final de medidas en `desktop-native-check.json`; no demuestran la representación visual ni las interacciones del reporte. Completar [Aceptación en Desktop](docs/revision/DESKTOP_ACCEPTANCE.md) antes de integrar. Las capturas son históricas; no se afirma haber exportado un PBIX ni capturas nuevas.

## Licencia

Los materiales originales del proyecto incluidos en este repositorio se publican bajo la [Licencia MIT](LICENSE).

El dataset de origen **no se relicencia bajo MIT**. `data/raw/Online Retail.xlsx` corresponde al dataset
**Online Retail** de UCI, creado por Daqing Chen, y conserva su licencia **CC BY 4.0**. La atribución y las
condiciones de reutilización se documentan en [DATA_LICENSE.md](DATA_LICENSE.md).

## Autor

**Angel W. Miller** — Junior Data Analyst enfocado en business intelligence, analytics y desarrollo de dashboards.

## Contacto

- GitHub: [angel-wm](https://github.com/angel-wm)
- LinkedIn: [Angel W. Miller](https://www.linkedin.com/in/angel-w-miller/)
