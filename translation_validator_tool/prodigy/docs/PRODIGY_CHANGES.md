Resumen de cambios aplicados al módulo `prodigy`

Objetivo
-------
Documentar los cambios aplicados al sistema Prodigy en este repositorio para soportar:
- Asignación de validadores por servicio (POS / Features / Relations)
- Monitor de batches que detecta completitud por validador y avanza automáticamente
- Mejor integración entre `prodigy_manager.py`, `batch_monitor.py` y los scripts de arranque

Cambios por archivo
-------------------
- `.env` (ruta: `prodigy/.env`)
  - Añadidas variables de validadores por servicio:
    - `VALIDATORS_POS` (ej. `"alice,bob"`)
    - `VALIDATORS_FEATURES` (ej. `"carlos,elena"`)
    - `VALIDATORS_RELATIONS` (ej. `"marcos,nicolas"`)
  - Se amplió `PRODIGY_ALLOWED_SESSIONS` con todos los nombres.

- `.env.example` (ruta: `prodigy/.env.example`)
  - Documentadas las nuevas variables `VALIDATORS_POS`, `VALIDATORS_FEATURES`, `VALIDATORS_RELATIONS`.

- `prodigy_manager.py`
  - Añadida función `parse_validators_list` para leer listas desde `.env`.
  - Nueva estructura `SERVICE_VALIDATORS` que contiene los validadores permitidos por servicio.
  - `ALL_ALLOWED_SESSIONS` / `PRODIGY_ALLOWED_SESSIONS` construida a partir de `SERVICE_VALIDATORS`.
  - Al iniciar un servicio Prodigy (`start_prodigy_process_for_service`) se configura la variable de entorno `PRODIGY_ALLOWED_SESSIONS` para el proceso con la lista concreta de validadores de ese servicio (de modo que la UI de Prodigy y las recetas reciban la lista correcta).
  - Nuevo endpoint API `GET /api/validators` que retorna `validators_by_service` y `all_validators` — útil para la UI o debugging.

- `batch_monitor.py`
  - Cambio en la carga de `.env` para usar `find_dotenv()` y fallback local.
  - Añadida función `parse_validators_list` y `SERVICE_VALIDATORS` reutilizada.
  - `check_batch_completion` ahora mapea los `_session_id` devueltos por Prodigy a nombres de usuario asignados. Ejemplos de matching soportado:
    - `guarani_features_batch_003-carlos` -> `carlos`
    - `guarani_features_batch_003_elena` -> `elena`
    - También intenta buscar el `user` dentro del `session_id` como fallback.
  - `check_batch_completion` devuelve un `progress_display` con claves del tipo `guarani_<tipo>_batch_<NNN>-<usuario>` y sólo cuenta completitud para los validadores asignados al servicio.
  - `print_status` actualizado para mostrar la lista de `Validadores:` por servicio y marcar con `(!)` sesiones no asignadas (diagnóstico).
  - Mantiene compatibilidad con token interno `internal-monitor` para llamadas al manager.

- `start_batch_auto.ps1`
  - Cambiado el mecanismo de arranque del `batch_monitor` para ejecutarlo en primer plano (no en Job/Background) y así mostrar siempre la salida en la consola.
  - Mensaje de resumen actualizado para imprimir las listas de validadores por servicio (lee variables de entorno cargadas).

Motivación técnica
------------------
- Prodigy registra `_session_id` en los registros; muchas instalaciones usan prefijos/dataset info en el `session_id` (p.ej. `guarani_features_batch_003-carlos`). Antes hacíamos una comparación simple que no coincidía con estos IDs, por eso no se detectaba completitud.
- Al mapear correctamente los `session_id` a nombres de validadores y limitar el conteo a los validadores asignados por servicio, el monitor puede determinar si se alcanzaron las `SENTENCES_PER_BATCH` por validador y avanzar automáticamente.

Consideraciones y recomendaciones
----------------------------------
- Asegurar que los usuarios (`alice`, `carlos`, etc.) se logueen o pasen `?session=<user>` en la URL de Prodigy para que `_session_id` incluya el nombre esperado.
- Si la convención de `session_id` cambia (prefijos distintos), ajustar la heurística de `check_batch_completion` para evitar falsos positivos.
- Si deseas reglas más estrictas, podemos (1) forzar que Prodigy use `_session_id` exacto (pasando `--session`), o (2) crear en `prodigy_manager` una variable env `PRODIGY_SESSION_PREFIX` para homogeneizar.

Pruebas realizadas
------------------
- Verificación manual local de `batch_monitor.py --check-once` con datasets `guarani_features_batch_003` simulados
- Validación de que `start_batch_auto.ps1` ahora muestra siempre la salida del monitor en la consola

Siguientes pasos opcionales
--------------------------
- Generar pruebas unitarias o un pequeño script de integración que alimente la DB de Prodigy con anotaciones de ejemplo y verifique la transición automática de batches.
- Añadir una ruta en el UI para editar `SERVICE_VALIDATORS` dinámicamente y persistir en `data/prodigy_config.json`.

---
Fecha: 2025-12-31
Autora: Cambios aplicados por el equipo (implementado por la herramienta automática)