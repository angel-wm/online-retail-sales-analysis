# Decisiones de la revisión

| ID | Decisión y motivo | Procedencia |
| --- | --- | --- |
| D01 | Usar neto de mercancía como KPI comercial y separar ajustes administrativos. | Propuesta explícita del usuario, contrastada con el Excel. |
| D02 | Restar cada línea negativa de mercancía elegible una sola vez. Prefijo C es evidencia de cancelación; no prueba devolución física. | Fuente UCI y comprobación de signos y facturas. |
| D03 | Corregir AMAZONFEE y conservar el catálogo de otros códigos probado. No excluir automáticamente todos los códigos alfabéticos. | Perfil de los 26 códigos especiales y descripciones. |
| D04 | Conservar redondeo monetario por línea a céntimos; mantener precisión completa de precios y ratios. | Regla M existente y conciliación independiente. |
| D05 | Mantener el AOV neto por factura elegible del periodo, con etiqueta explícita. No atribuir reversos a una cohorte de pedidos sin vínculo fuente. | Fórmula original y alcance autorizado. |
| D06 | Conservar duplicados, ventas anónimas y outliers. Documentar la exclusión previa de 1,454 descripciones nulas de valor cero. | No hay ID de línea ni evidencia de duplicación accidental. |
| D07 | Usar una rama local basada en main, respaldo ZIP verificado y commits separados. Conservar el PBIX placeholder y los originales hasta aprobación. | Reglas de ejecución del usuario. |
| D08 | Configurar un único parámetro SourceFilePath, con helper que valida el XLSX. La ruta es absoluta y adaptable; no se inventa resolución relativa automática. | Defecto reproducible de la ruta antigua. |
| D09 | Introducir DimProduct por Stock_Code, conservar nombres transaccionales y usar descripción frecuente con desempate ordinal. No crear dimensiones adicionales sin beneficio. | 212 códigos con varias descripciones en mercancía elegible. |
| D10 | Mantener Calendar y tablas locales ocultas con sus dependencias; declarar relaciones activas unidireccionales y atributos sin suma predeterminada. | Inspección del modelo y cobertura de 374 días. |
| D11 | Mantener dos páginas y los 31 visuales originales; ampliar altura para rankings, cobertura y conciliación. | Auditoría de recortes, scroll y contexto insuficiente. |
| D12 | Usar Top 10 por neto en ventas, Top 10 por reversos en Insights y Top 30 por bruto en el dispersograma. Eliminar exclusiones manuales y umbral de países. | Correspondencia entre pregunta, clasificación y selección visible. |
| D13 | Sincronizar tres segmentadores; usar filtro entre gráficos y declarar el alcance del reset de segmentadores. | Evitar selecciones incompatibles y promesas de reset universal. |
| D14 | Tratar validación de esquema visual 2.13 como parcial y dejar apertura, DAX/M, refresh y render/interacciones pendientes. | Esquema público ausente y falta de acceso efectivo a Desktop. |

La implementación autorizada está realizada. La aceptación nativa y revisión personal preceden a cualquier aprobación de integración. No se ha autorizado push, merge ni publicación.
