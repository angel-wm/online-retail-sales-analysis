[Read in English](SETUP.md) · [Inicio en español](../README.es.md)

# Abrir el proyecto de Power BI

Para explorar los datos incluidos, descarga el [PBIX](../exports/uk-online-retail-sales-analysis.pbix) y ábrelo en Power BI Desktop. La página inicial es **Sales Overview**. Para editar el reporte o el modelo, trabaja con el [PBIP](../uk-online-retail-sales-analysis.pbip) desde una copia completa del repositorio.

## Configurar y abrir

Necesitas Windows, Power BI Desktop con soporte para PBIP y las carpetas completas `powerbi/` y `data/raw/`. El proyecto se verificó con Desktop 2.158.1304.0. El asistente de configuración requiere Python 3.12 y solo usa su biblioteca estándar.

1. Cierra el proyecto en Desktop.
2. Desde la raíz del repositorio, ejecuta:

   ```powershell
   python scripts/configure_source.py
   ```

   El asistente sustituye el marcador `SET_LOCAL_ONLINE_RETAIL_XLSX_PATH` por la ruta local de [Online Retail.xlsx](../data/raw/Online%20Retail.xlsx) en `expressions.tmdl`. Repítelo si mueves o clonas el proyecto.
3. Abre el PBIP de la raíz, pulsa **Refresh** y espera a que termine. La caché `.pbi/` es local.
4. Comprueba que carguen **Sales Overview** y **Product & Customer Insights**. Con los filtros despejados, compara las tarjetas con los [valores de referencia](METRICS.es.md#valores-de-referencia) y las [capturas](../README.es.md#vista-previa-del-dashboard).
5. Guarda en Desktop si quieres conservar la caché local.

También puedes establecer `SourceFilePath` mediante **Manage Parameters** en Power Query. Si eliges otro Excel, pueden cambiar los resultados.

### Antes de hacer commit o push

Con el PBIP cerrado, restaura y comprueba el marcador portátil:

```powershell
python scripts/configure_source.py --reset
python scripts/configure_source.py --check-repository
git status --short
```

Esto solo cambia el parámetro del PBIP. Para refrescar otra vez, vuelve a configurar la ruta local.

## Explorar el reporte

Los filtros **Year**, **Country** y **Line Type** se sincronizan entre páginas. Para comparar mercados fuera del Reino Unido, usa **Select all** en Country y desmarca **United Kingdom**. Seleccionar una marca afecta a las tarjetas y otros gráficos de su página. Pulsa la misma marca para despejarla. **Clear selectors** restablece los tres selectores.

El encabezado indica el período seleccionado y avisa si no hay actividad de mercancía elegible. El asterisco marca el mes final incompleto. En el diagrama de dispersión, X muestra ventas brutas, Y muestra reversos en escala logarítmica y el tamaño representa facturas de venta. [Interpretación de las métricas](METRICS.es.md)

## Solución de problemas

- **No encuentra el Excel.** Cierra el PBIP, ejecuta el asistente desde la raíz y comprueba que la ruta apunte al Excel que existe en `data/raw/`.
- **Desktop abre pero el reporte no carga.** Comprueba que descargaste ambas carpetas bajo `powerbi/` y abriste el PBIP de la raíz. Conserva el mensaje completo si persiste el problema. [Comprobaciones estáticas](VALIDATION.es.md#ejecutar-las-comprobaciones)
- **Los gráficos están vacíos.** Actualiza y despeja los selectores. Adjustment y Gift Voucher pueden dejar en blanco las medidas comerciales. [Filtros y valores en blanco](METRICS.es.md#filtros-y-valores-en-blanco)
- **Diciembre muestra una caída marcada.** La fuente termina el 9 de diciembre de 2011. [Cobertura del período](METRICS.es.md#cobertura-del-período)

## Actualizar el PBIX exportado

Para refrescar el PBIX en otro equipo, configura `SourceFilePath` en **Transform data > Edit parameters**. El asistente de configuración actúa sobre el PBIP.

Después de un cambio aceptado, refresca el modelo desde el Excel versionado, despeja los selectores y las marcas y abre **Sales Overview**. Usa **File > Save as** para actualizar el PBIX en `exports/`. Vuelve a abrirlo, verifica ambas páginas y los valores de referencia, y renueva las capturas si cambiaron los visuales. [Validación](VALIDATION.es.md) · [Estructura del proyecto](PROJECT_STRUCTURE.es.md)
