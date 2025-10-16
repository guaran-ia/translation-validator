# Translation Validator Tool — Guía rápida (README principal)

Resumen
- Proyecto: herramienta para validar/parar y sugerir traducciones Guaraní ↔ Español.
- Estructura:
  - api/       → Backend (FastAPI)
  - ui/        → Frontend (React + Vite)
  - db_schema/ → Migraciones y scripts de inicialización

Prioridad de lectura
1. Este README (root) — entrada principal y comandos esenciales.
2. `api/README.md` — instrucciones detalladas del backend.
3. `ui/README.md` — instrucciones detalladas del frontend.
4. `db_schema/README.md` — migraciones y scripts SQL.

Quick start (Windows PowerShell)
1) Clonar
```powershell
git clone https://github.com/aalvarez-fiuni/guarani-corpus-lacuna-uni.git
git checkout translation-validator
cd translation-validator-tool
```

2) Backend (api)
```powershell
cd api
python -m venv venv
# PowerShell:
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env     # editar .env -> DATABASE_URL, SECRET_KEY, CORS_ORIGINS
```

Migraciones / inicialización (usar db_schema)
```powershell
cd ..\db_schema
# con el venv activado desde api:
python -m alembic upgrade head
# o:
python init_database.py init
```

3) Frontend (ui)
```powershell
cd ..\ui
npm install
copy .env.example .env     # editar VITE_API_URL si es necesario (ej: http://localhost:8000/api)
npm run dev
```

4) Levantar backend
```powershell
# desde api con venv activo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Puntos importantes
- Usa `db_schema/` para gestionar migraciones (alembic) y scripts de inicialización.
- No commitees archivos `.env` ni `venv/`. Revisa `.gitignore`.
- Si alguien clona: primero crear venv en `api/`, luego aplicar migraciones en `db_schema/`, luego levantar backend y frontend.
- Para producción: aplicar migraciones con Alembic y usar un DB gestionado (Postgres). No uses los scripts de init en producción salvo para entornos controlados.

Archivos de referencia
- `api/README.md` — setup backend, comandos scripts.
- `ui/README.md` — setup frontend.
- `db_schema/README.md` — init/reset/migrate DB.

---

# Importar CSV de traducciones

Coloca tu archivo CSV en:
```
data/translations.csv
```

Formato esperado (encabezado):
```
split,source,gn,es,tokens_gn,tokens_es
```

Método recomendado — usar el script del backend
1. Abrir PowerShell en la raíz del proyecto.
2. Activar entorno y entrar al backend:
```powershell
cd api
.\venv\Scripts\Activate.ps1           # si no existe, crear venv: python -m venv venv
pip install -r requirements.txt
```
3. Asegurarse de aplicar migraciones (desde db_schema con el venv activado):
```powershell
cd ..\db_schema
python -m alembic upgrade head
cd ..\api
```
4. Ejecutar el script de carga (usa el script incluido app.scripts.load_corpus):
```powershell
# ruta relativa al CSV: ../../data/translations.csv
python -m app.scripts.load_corpus --csv ../../data/translations.csv
# o, si solo quieres una muestra:
python -m app.scripts.load_corpus --sample
```
El script leerá el CSV y creará las filas en la tabla `translations`. Revisa la salida para ver conteo y errores.

Método alternativo — usar psql COPY (directo a Postgres)
1. Exporta tu DATABASE_URL en PowerShell (o edita para psql):
```powershell
# Si tienes .env en api/, toma DATABASE_URL de allí:
(Get-Content .env) -match 'DATABASE_URL' | Out-Null
$DATABASE_URL = (($Matches[0]).Split('=')[1]).Trim()
```
2. Ejecuta COPY (PowerShell; ajusta nombres de columnas según tu tabla):
```powershell
# ruta absoluta o relativa al CSV
$csv = Resolve-Path ..\data\translations.csv

psql $DATABASE_URL -c "\copy translations(split, source, guarani_text, spanish_text, tokens_gn, tokens_es) FROM '$csv' CSV HEADER DELIMITER ','"
```
Notas:
- Asegúrate de que los nombres de columnas en el comando COPY coincidan con los de tu tabla (`guarani_text`/`spanish_text` ó `gn`/`es`).
- Si la tabla ya existe y tiene constraints, es posible que necesites cargar en una tabla temporal y luego insertar filtrando/normalizando.
- Para grandes CSV, habilita transacciones y/o carga por lotes para evitar timeouts.

Problemas comunes
- Error de encoding: abre el CSV en UTF-8.
- Columnas con comillas/commas: usa CSV con HEADER y configuraciones de QUOTE/ESCAPE adecuadas.
- Permisos DB: asegúrate que el usuario en DATABASE_URL puede INSERT.

Si quieres, añado un script PowerShell `scripts/import_csv.ps1` que automatice los pasos (activar venv, migraciones, ejecutar el script). ¿Lo genero ahora?