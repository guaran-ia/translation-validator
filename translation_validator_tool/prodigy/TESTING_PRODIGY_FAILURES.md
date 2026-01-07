**Pruebas y escenarios de fallo para Prodigy (usuarios inexpertos)**

Resumen: checklist de escenarios que pueden ocurrir en producción o durante pruebas manuales, cómo reproducirlos, qué observar y pasos de mitigación.

- **Contexto / Archivos relevantes**:
  - Estado central: `prodigy/data/batch_monitor_state.json`
  - Script de arranque: `prodigy/start_batch_auto.ps1`
  - Manager API: `http://localhost:8085/api/status`
  - Servicios: `pos`(8080), `features`(8081), `relations`(8082)

1) Manager no responde
  - Reproducir: arrancar `start_batch_auto.ps1` y matar el proceso `prodigy_manager.py`.
  - Observación: `start_batch_auto` reporta "Manager no responde" o el `prodigy_diagnostic.py` muestra fallo en `/api/status`.
  - Remediación: revisar logs, reiniciar `prodigy_manager.py`, verificar puerto 8085, comprobar variables de entorno en `.env`.

2) Un servicio no levanta (puerto cerrado)
  - Reproducir: bloquear puerto o simular fallo en `prodigy` worker.
  - Observación: puerto (8080/8081/8082) cerrado; Manager puede reportar fallo al intentar start.
  - Remediación: revisar logs del manager y del proceso prodigy, reiniciar servicio desde manager web UI.

3) `batch_monitor_state.json` ausente o corrupto
  - Reproducir: eliminar o truncar `data/batch_monitor_state.json`.
  - Observación: `start_batch_auto.ps1` usa fallback `-Batch` y `prodigy_diagnostic.py` denuncia ausencia.
  - Remediación: restaurar desde backup, re-sincronizar con estado real (script de sync), o iniciar manualmente batches correctos.

4) Batches inconsistentes entre servicios
  - Reproducir: editar `current_batch` para que `pos=4` y `features=2` mientras `relations=1`.
  - Observación: usuarios ven distintas tareas; potencial pérdida de continuidad.
  - Remediación: decidir fuente de verdad (batch_monitor_state.json), actualizar servicios para usar valores correctos, ejecutar comprobaciones de consistencia.

5) Pérdida de conexión de un anotador (browser close / network loss)
  - Reproducir: cerrar pestaña del navegador mientras anota.
  - Observación: tarea queda sin completar; si todos hacen lo mismo, monitor piensa que no hay progreso.
  - Remediación: implementar timeouts para sesiones, guardar progreso parcial en DB, advertir en UI.

6) Autenticación/Token fallido para llamadas internas
  - Reproducir: cambiar header `Authorization` esperado por manager.
  - Observación: llamadas desde scripts fallan con 401/403.
  - Remediación: verificar tokens en `.env` y en las llamadas internas (`Bearer internal-monitor`).

7) Port conflict
  - Reproducir: otro servicio usando 8080.
  - Observación: Start falla con error de bind; `start_batch_auto` muestra error al iniciar servicio.
  - Remediación: detectar procesos en puerto, liberar puerto o actualizar puertos en configuración.

8) Lote parcialmente completado (inconsistencia de progreso)
  - Reproducir: manipular `progress` en `batch_monitor_state.json` para simular usuarios parcialmente avanzados.
  - Observación: Monitor puede auto-advanzar incorrectamente.
  - Remediación: validar reglas de avance en `batch_monitor.py`; guardar checksums y snapshots de progreso.

9) Errores en Prodigy (dependencias faltantes)
  - Reproducir: eliminar paquete python `prodigy` o no instalarlo en el entorno.
  - Observación: `start_batch_auto` detecta "Prodigy no instalado" y aborta.
  - Remediación: reinstalar dependencias (ver `prodigy/requirements.txt`) y asegurar `python` correcto.

10) Escritos concurrentes en `batch_monitor_state.json`
  - Reproducir: dos procesos escriben al mismo tiempo.
  - Observación: JSON corrupto o pérdida de datos.
  - Remediación: usar locking o escribir a archivo temp + rename atómico.

Checklist de pruebas (manual)
- Arrancar `start_batch_auto.ps1` con estado válido.
- Forzar manager caído y observar manejo de errores.
- Simular cierre de navegador y comprobar que el monitor no avanza erróneamente.
- Editar `data/batch_monitor_state.json` y volver a lanzar `start_batch_auto.ps1` para validar el fallback.
- Ejecutar `python prodigy/scripts/prodigy_diagnostic.py` y revisar salidas.

Herramientas recomendadas
- `prodigy/scripts/prodigy_diagnostic.py` — comprobación rápida (ya incluida).
- Monitorizar logs en `prodigy/logs/` y usar `tail -f` en Windows con `Get-Content -Wait`.
- Usar backups de `data/batch_monitor_state.json.bak` antes de cualquier cambio manual.
