<!-- ...existing code... -->

# Prodigy — Anotación Morfológica y POS para Guaraní (Guía práctica)

Breve, práctica y orientada a ejecutar los scripts seguros de SPANS y entender qué hace el proxy.

---

## Resumen rápido (qué hay de nuevo)
- Proxy seguro que valida JWT antes de permitir acceso a Prodigy.
- Recipes por "capas" y recipe `guarani-char-spans` para anotación por spans (overlapping) con tokenización por caracteres.
- Mapeo automático a Universal Dependencies (UD) al exportar.
- UI integrada con el proxy (no abrir Prodigy interno directamente).

---

## Requisitos previos
1. Backend API corriendo y validando JWT (por defecto: `http://localhost:8000`).
2. Variables en `prodigy/.env` (no subir credenciales):
   - `PRODIGY_PORT` (ej. 8080) — puerto interno donde arranca Prodigy.
   - `PRODIGY_PROXY_PORT` (ej. 8082) — puerto público del proxy.
   - Asegúrate de comentar/eliminar `PRODIGY_ALLOWED_SESSIONS` (no usar como control de acceso).
3. Frontend corriendo para obtener token vía UI (ej. `http://localhost:5173`).

---

## Cómo iniciar (secure spans) — paso a paso

1) Abrir una terminal PowerShell en:
```
C:\Users\infor\Desktop\manu\LACUNA\guarani-corpus-lacuna-uni\translation_validator_tool\prodigy
```

2) Iniciar backend (si no está en marcha):
```powershell
# ir a la carpeta api y lanzar el backend (ejemplo)
cd ..\api
uvicorn app.main:app --reload --port 8000
```

3) Iniciar Prodigy + proxy seguro (PowerShell helper):
```powershell
# PowerShell (recomendado)
estar en la carpeta de /prodigy
.\start_prodigy_spans_secure.ps1 -Recipe guarani-char-spans -Dataset test -Source ".\data\export\original_translations.jsonl" -Port 8082
```

o con Python directo:
```powershell
python start_prodigy_spans_secure.py guarani-char-spans test ./data/export/original_translations.jsonl
```

4) Acceder SOLO vía proxy:
- Abrir en navegador (usar token JWT válido):
```
http://localhost:8082/?token=<TU_JWT_VÁLIDO>
```
- No usar `http://localhost:8080` ni `?session=alice` para acceder a la UI de anotación.

---

## Qué hace exactamente el proxy (resumen técnico)
- Exige un query param `?token=<JWT>` con formato JWT (header.payload.signature).
- Valida el token contra el backend (endpoint de validación).
- Si el JWT es válido:
  - Crea una cookie de sesión para permitir la carga de recursos estáticos (JS/CSS/API).
  - Reenvía (proxy) las peticiones del cliente al Prodigy interno (en `PRODIGY_PORT`) y devuelve respuestas.
- Si el JWT no es válido o ausente:
  - Responde con página de "Acceso Restringido" / 401.
- Nota: el proxy SOLO acepta tokens; `?session=` no otorga acceso.

---

## Recipes principales y flujo recomendado (capas)
- `guarani-char-spans` — spans_manual, tokenización por caracteres (overlapping).
- Capas (recomendado para no mostrar muchas etiquetas a la vez):
/* aun no implementado las capas del "/*" hasta el "*/"
  - `guarani-capa1-morfemas` → Raíz, Prefijo, Sufijo
  - `guarani-capa2-persona` → Persona, Número, Clusividad
  - `guarani-capa3-categoria` → VERB, NOUN, PRON, ...
  - `guarani-capa4-caso` → Casos y relacionales
  - `guarani-capa5-tam` → Aspecto / Modo / Gerundio
  - `guarani-completo` → revisión experta (todas)
- Ejecutar una capa:
```powershell
python start_prodigy_spans_secure.py guarani-capa1-morfemas capa1 ./data/export/original_translations.jsonl
```
*/

---

## Exportar y mapear a Universal Dependencies (UD)
- Exportar anotaciones + conversión a UD:
```powershell
python scripts/export_to_json_with_iaa.py pos_character --output resultados/export_completo.json
```
- Exportar conflictos:
```powershell
python scripts/export_conflicts.py pos_character --output conflictos/para_revisar.jsonl --threshold 0.5
```
- El mapper UD está en `prodigy/scripts/pos_tag_mapper.py` y se aplica en el pipeline de export.

---

## Buenas prácticas de seguridad y pruebas
- NO uses `PRODIGY_ALLOWED_SESSIONS` como control de acceso; comentalo en `.env`.
- Si ves acceso con `?session=usuario`:
  1. Borrar cookies del dominio `localhost:8082` o abrir ventana incógnita.
  2. Reiniciar proxy seguro.
- Recomiendo fijar `PRODIGY_PORT` a `127.0.0.1` en producción (o usar firewall) para no exponer Prodigy interno.
- Reducir expiración del JWT (1–4 horas) para minimizar riesgos.

---

## Troubleshooting rápido
- "Token inválido": verificar formato `header.payload.signature` y backend corriendo.
- "Ingreso con ?session=..." sin token: borrar cookies e iniciar proxy seguro.
- Recursos JS/CSS no cargan tras login: el proxy establece cookie tras validación; si falla, revisar logs del proxy.
- Cambias `.env` → reiniciar scripts para aplicar cambios.

---

## Comandos útiles
- Listar datasets Prodigy:
```powershell
python -m prodigy stats -ls
```
- Volcar dataset a JSONL:
```powershell
python -m prodigy db-out <DATASET> > data/annotations/export.jsonl
```

---

## Dónde mirar (archivos clave)
- Scripts arranque seguro: `prodigy/start_prodigy_spans_secure.py`, `prodigy/start_prodigy_spans_secure.ps1`
- Recipes spans y capas: `prodigy/recipes/guarani_spans.py`
- Seguridad / proxy: `prodigy/security/*` (`jwt_auth_middleware.py`, `prodigy_auth_middleware.py`, `login_portal.py`)
- Mapper UD: `prodigy/scripts/pos_tag_mapper.py`
- Data fuente: `prodigy/data/export/original_translations.jsonl`
- UI: `ui/src/pages/ProdigyPage.jsx` (obtiene URL del proxy desde env)

---

Si querés, aplico el cambio en el archivo README.md directamente (ya listo arriba). ¿Querés que además:
- 1) comente `PRODIGY_ALLOWED_SESSIONS` en `prodigy/.env`, o
- 2) añada un checklist con capturas para anotadores?  
Elijo la opción 1 si no indicás otra cosa.<!-- filepath: c:\Users\infor\Desktop\manu\LACUNA\guarani-corpus-lacuna-uni\translation_validator_tool\prodigy\README.md -->
<!-- ...existing code... -->

# Prodigy — Anotación Morfológica y POS para Guaraní (Guía práctica)

Breve, práctica y orientada a ejecutar los scripts seguros de SPANS y entender qué hace el proxy.

---

## Resumen rápido (qué hay de nuevo)
- Proxy seguro que valida JWT antes de permitir acceso a Prodigy.
- Recipes por "capas" y recipe `guarani-char-spans` para anotación por spans (overlapping) con tokenización por caracteres.
- Mapeo automático a Universal Dependencies (UD) al exportar.
- UI integrada con el proxy (no abrir Prodigy interno directamente).

---

## Requisitos previos
1. Backend API corriendo y validando JWT (por defecto: `http://localhost:8000`).
2. Variables en `prodigy/.env` (no subir credenciales):
   - `PRODIGY_PORT` (ej. 8080) — puerto interno donde arranca Prodigy.
   - `PRODIGY_PROXY_PORT` (ej. 8082) — puerto público del proxy.
   - Asegúrate de comentar/eliminar `PRODIGY_ALLOWED_SESSIONS` (no usar como control de acceso).
3. Frontend (opcional) corriendo para obtener token vía UI (ej. `http://localhost:5173`).

---

## Cómo iniciar (secure spans) — paso a paso

1) Abrir una terminal PowerShell en:
```
C:\Users\infor\Desktop\manu\LACUNA\guarani-corpus-lacuna-uni\translation_validator_tool\prodigy
```

2) Iniciar backend (si no está en marcha):
```powershell
# ir a la carpeta api y lanzar el backend (ejemplo)
cd ..\api
uvicorn app.main:app --reload --port 8000
```

3) Iniciar Prodigy + proxy seguro (PowerShell helper):
```powershell
# PowerShell (recomendado)
.\start_prodigy_spans_secure.ps1 -Recipe guarani-char-spans -Dataset test -Source ".\data\export\original_translations.jsonl" -Port 8082
```

o con Python directo:
```powershell
python start_prodigy_spans_secure.py guarani-char-spans test ./data/export/original_translations.jsonl
```

4) Acceder SOLO vía proxy:
- Abrir en navegador (usar token JWT válido):
```
http://localhost:8082/?token=<TU_JWT_VÁLIDO>
```
- No usar `http://localhost:8080` ni `?session=alice` para acceder a la UI de anotación.

---

## Qué hace exactamente el proxy (resumen técnico)
- Exige un query param `?token=<JWT>` con formato JWT (header.payload.signature).
- Valida el token contra el backend (endpoint de validación).
- Si el JWT es válido:
  - Crea una cookie de sesión para permitir la carga de recursos estáticos (JS/CSS/API).
  - Reenvía (proxy) las peticiones del cliente al Prodigy interno (en `PRODIGY_PORT`) y devuelve respuestas.
- Si el JWT no es válido o ausente:
  - Responde con página de "Acceso Restringido" / 401.
- Nota: el proxy SOLO acepta tokens; `?session=` no otorga acceso.

---

## Recipes principales y flujo recomendado (capas)
- `guarani-char-spans` — spans_manual, tokenización por caracteres (overlapping).
- Capas (recomendado para no mostrar muchas etiquetas a la vez):
  - `guarani-capa1-morfemas` → Raíz, Prefijo, Sufijo
  - `guarani-capa2-persona` → Persona, Número, Clusividad
  - `guarani-capa3-categoria` → VERB, NOUN, PRON, ...
  - `guarani-capa4-caso` → Casos y relacionales
  - `guarani-capa5-tam` → Aspecto / Modo / Gerundio
  - `guarani-completo` → revisión experta (todas)
- Ejecutar una capa:
```powershell
python start_prodigy_spans_secure.py guarani-capa1-morfemas capa1 ./data/export/original_translations.jsonl
```

---

## Exportar y mapear a Universal Dependencies (UD)
- Exportar anotaciones + conversión a UD:
```powershell
python scripts/export_to_json_with_iaa.py pos_character --output resultados/export_completo.json
```
- Exportar conflictos:
```powershell
python scripts/export_conflicts.py pos_character --output conflictos/para_revisar.jsonl --threshold 0.5
```
- El mapper UD está en `prodigy/scripts/pos_tag_mapper.py` y se aplica en el pipeline de export.

---

## Buenas prácticas de seguridad y pruebas
- NO uses `PRODIGY_ALLOWED_SESSIONS` como control de acceso; comentalo en `.env`.
- Si ves acceso con `?session=usuario`:
  1. Borrar cookies del dominio `localhost:8082` o abrir ventana incógnita.
  2. Reiniciar proxy seguro.
- Recomiendo fijar `PRODIGY_PORT` a `127.0.0.1` en producción (o usar firewall) para no exponer Prodigy interno.
- Reducir expiración del JWT (1–4 horas) para minimizar riesgos.

---

## Troubleshooting rápido
- "Token inválido": verificar formato `header.payload.signature` y backend corriendo.
- "Ingreso con ?session=..." sin token: borrar cookies e iniciar proxy seguro.
- Recursos JS/CSS no cargan tras login: el proxy establece cookie tras validación; si falla, revisar logs del proxy.
- Cambias `.env` → reiniciar scripts para aplicar cambios.

---

## Comandos útiles
- Listar datasets Prodigy:
```powershell
python -m prodigy stats -ls
```
- Volcar dataset a JSONL:
```powershell
python -m prodigy db-out <DATASET> > data/annotations/export.jsonl
```

---

## Dónde