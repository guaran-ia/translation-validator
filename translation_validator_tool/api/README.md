# Backend — Translation Validator

Este es el backend (FastAPI) del proyecto Translation Validator. Este README explica cómo configurar el entorno, crear la base de datos, ejecutar migraciones y usar los scripts útiles incluidos en `app/scripts`.

Nota: la carpeta que contiene este README es `translation_validator_tool/api`.

---

## 1 — Preparar entorno (PowerShell)

```powershell
# 1. Crear y activar el entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Copiar .env de ejemplo y editar valores (DATABASE_URL, SECRET_KEY, CORS_ORIGINS)
copy .env.example .env
# Edita api/.env y completa DATABASE_URL, SECRET_KEY, etc.
```

En Linux/macOS usa `source venv/bin/activate` en lugar de `Activate.ps1`.

## 2 — Crear la base de datos (si no existe)

Hay dos opciones (elige una):

- Opción recomendada: usar el helper incluido en `db_schema` que crea la BD (si no existe), tablas y admin por defecto:

```powershell
cd ..\db_schema
..\api\venv\Scripts\python.exe init_database.py init
```

- Opción manual (si prefieres crear la BD tú mismo):

```powershell
# Crear la BD en Postgres (ajusta usuario/host/puerto según tu instalación)
psql -U postgres -c "CREATE DATABASE translation_validator;"
```

Si creas la BD manualmente, luego aplica las migraciones (siguiente sección).

## 3 — Migraciones (Alembic)

Las migraciones están en `db_schema/alembic`. Siempre ejecuta Alembic desde la carpeta `db_schema` (para que `alembic.ini` y `env.py` se encuentren correctamente):

```powershell
cd ..\db_schema
..\api\venv\Scripts\python.exe -m alembic upgrade head
```

Si prefieres la ruta corta y el helper `init_database.py` ya creó la BD y tablas, no necesitas ejecutar Alembic inmediatamente (el helper crea las tablas con SQLAlchemy). En desarrollo recomendamos usar Alembic para mantener historial de migraciones.

## 4 — Ejecutar el servidor

```powershell
cd ..\api
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints útiles:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## 5 — Scripts útiles (ubicados en `app/scripts`)

Los scripts del backend están en `api/app/scripts`. Son scripts que usan los modelos y la configuración del backend, por eso viven dentro del código de la app.

- Crear admin:

```powershell
cd api
.\venv\Scripts\Activate.ps1
python -m app.scripts.create_admin --username admin --email admin@example.com --password admin123
```

- Cargar corpus desde CSV (script optimizado para alias `gn`/`es` y carga por lotes):

Requisitos: el archivo CSV debe tener columnas que representen los textos. El script acepta encabezados `guarani` y `spanish`, y también alias `gn` -> `guarani`, `es` -> `spanish`.

```powershell
cd api
.\venv\Scripts\Activate.ps1
python -m app.scripts.load_corpus --file ..\..\data\translations.csv
```

Opciones del script:
- `--file PATH` — ruta al CSV
- `--sample` — cargar datos de ejemplo (no requiere archivo)

Formato esperado en CSV (mínimo):

```
guarani,spanish,source
... filas ...
```

Si tu CSV usa `gn` y `es` como cabeceras, el script las normalizará automáticamente.

## 6 — Desarrollo y migraciones

- Crear una nueva migración (desde `db_schema` con venv activo):

```powershell
cd ..\db_schema
..\api\venv\Scripts\python.exe -m alembic revision --autogenerate -m "Describe changes"
```

- Aplicar migraciones:

```powershell
cd ..\db_schema
..\api\venv\Scripts\python.exe -m alembic upgrade head
```

- Revertir la última migración:

```powershell
cd ..\db_schema
..\api\venv\Scripts\python.exe -m alembic downgrade -1
```

## 7 — Troubleshooting rápido

- Error `No module named 'psycopg2'`: instala la dependencia en el venv:

```powershell
.\venv\Scripts\python.exe -m pip install psycopg2-binary
```

- Error `CREATE DATABASE cannot be executed inside a transaction`: usa el helper (`init_database.py`) o crea la BD manualmente con `psql`/`createdb`.

- Problemas de encoding al cargar CSV: asegúrate que el archivo está en UTF-8. Puedes re-guardarlo con PowerShell:

```powershell
Get-Content ..\..\data\translations.csv | Out-File ..\..\data\translations_utf8.csv -Encoding utf8
```

## 8 — Recomendaciones de organización

- Los scripts que usan modelos y SessionLocal viven en `api/app/scripts`.
- Los scripts que gestionan la infraestructura (migraciones, creación de BD) están en `db_schema`.
- Si quieres un comando único para inicializar todo en Windows, crea un `scripts/init.ps1` en la raíz que active el venv y llame a `db_schema/init_database.py`.

---

Si quieres, puedo:
- añadir un `scripts/import_csv.ps1` que automatice la carga del CSV (activar venv y ejecutar el script),
- o convertir los scripts en un pequeño CLI (Typer) con opciones `--file`, `--batch-size`, `--dry-run`.

¿Cuál prefieres que haga ahora?