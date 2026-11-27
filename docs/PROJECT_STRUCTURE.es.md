[Read in English](PROJECT_STRUCTURE.md) · [Inicio en español](../README.es.md)

# Estructura del proyecto

El [PBIP](../uk-online-retail-sales-analysis.pbip) enlaza el reporte y el modelo semántico en `powerbi/`. La [exportación PBIX](../exports/uk-online-retail-sales-analysis.pbix) incluye ambos y permite explorar los datos directamente en Power BI Desktop. [Guía de apertura](SETUP.es.md)

| Ruta | Contenido |
| --- | --- |
| `README.md`, `README.es.md` | Puntos de entrada en inglés y español. |
| `powerbi/` | Definiciones PBIR, recursos del reporte y modelo TMDL editables. |
| `exports/` | PBIX de Power BI Desktop con datos importados. |
| `data/` | Excel original y diccionario del modelo. |
| `docs/` | Guías de apertura, métricas, modelo, limpieza y validación. |
| `screenshots/` | Capturas de ambos reportes, compartidas por las dos versiones del README. |
| `scripts/` | Configuración local, conciliación y validadores de Python y .NET. |
| `evidence/baseline/` | Manifiesto, perfil y resultados del modelo original. |
| `evidence/financial/` | Conciliación actual, histórico mensual y por país, códigos especiales e identidad de producto. |
| `evidence/validation/` | Resultados de las comprobaciones estáticas y observaciones de Desktop. |

Los registros versionados corresponden a ejecuciones concretas. Las ejecuciones nuevas de CI se consultan en los artefactos de GitHub Actions. [Validación y evidencias](VALIDATION.es.md)

## Archivos generados en local

Git excluye `backups/` para copias de recuperación, `.cache/` para datos intermedios y registros, `.tools/` para dependencias y esquemas, `.pbi/` para el estado de Desktop y `bin/`, `obj/` y `__pycache__/` para salidas de compilación. Al clonar, configura tu archivo de origen con `python scripts/configure_source.py`. La versión publicada de TMDL conserva el marcador portátil. Los validadores guardan resultados resumidos en `evidence/validation/` y diagnósticos en `.cache/validation/`.

## Navegación bilingüe

El [README en inglés](../README.md) es la entrada predeterminada de GitHub. La [versión en español](../README.es.md) enlaza las guías traducidas y cada guía permite volver a su equivalente en inglés.
