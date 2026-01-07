Instrucciones para copiar a Confluence

Resumen
------
Este archivo contiene pasos y recomendaciones para pegar el contenido de `PRODIGY_GUIDE.md` en Confluence y cómo organizar las páginas.

Sugerencia de estructura en Confluence
-------------------------------------
- Espacio: "Annotators" o el espacio de proyecto actual
- Página padre: "Prodigy"
  - Página hija: "2.1 Introducción a Prodigy"
  - Página hija: "2.2 Requisitos y Configuración Inicial"
  - ...
  - Página hija: "2.10 Flujo de Trabajo Completo"
  - Página hija: "Cambios realizados (PRODIGY_CHANGES)"

Cómo pegar (paso a paso)
------------------------
1. Abrir `PRODIGY_GUIDE.md` en el editor.
2. Seleccionar una sección (por ejemplo 2.1) y copiar.
3. En Confluence, crear una nueva página con el título exacto.
4. Pegar como "Texto enriquecido". Confluence soporta Markdown básico; si el formato no se conserva, usar el editor visual y pegar solo texto.
5. Añadir etiquetas (labels) en Confluence: `prodigy`, `annotation`, `batch-monitor`, `IAA`.
6. Repetir para cada sección.

Mejoras automáticas (opcional)
------------------------------
- Si necesitas, puedo generar HTML o export XML (Confluence storage format) listo para import.
- Para subir directamente a Confluence mediante API necesitaré:
  - URL de Confluence
  - Usuario y API token con permisos de edición
  - Nombre del espacio y path donde crear páginas

Notas finales
-------------
- Recomendación: crear una página índice que enlace a las 10 secciones numeradas para facilitar navegación.
- Añade capturas de pantalla (logs, UI) donde sea útil: p.ej. la salida del `batch_monitor` mostrando barras de progreso.

---
Si quieres, genero ahora las páginas en formato HTML listo para importar o preparo un ZIP con las MD convertidas a HTML.