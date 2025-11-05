# Backend — Translation Validator (instrucciones claras)

Este README explica cómo configurar y ejecutar el backend (FastAPI).

Nota: la carpeta que contiene este README es `translation_validator_tool/api`.

1) Preparar entorno (Windows / Linux)

Windows (PowerShell):
```powershell
cd translation_validator_tool/api
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edita api/.env y configura DATABASE_URL, SECRET_KEY, CORS_ORIGINS
```

Linux / macOS (bash):
```bash
cd translation_validator_tool/api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edita api/.env y configura DATABASE_URL, SECRET_KEY, CORS_ORIGINS
```

2) Crear la base de datos y aplicar migraciones

Recomendado: usa el helper `init_database.py` desde `translation_validator_tool/db_schema` (ejecutar con el Python del venv del backend).

Windows (PowerShell):
```powershell
cd translation_validator_tool/db_schema
..\api\venv\Scripts\python.exe init_database.py init
```

Linux / macOS (bash):
```bash
cd translation_validator_tool/db_schema
../api/venv/bin/python init_database.py init
```

Alternativa: aplicar migraciones con Alembic (ejecutar desde `db_schema`):

Windows (PowerShell):
```powershell
cd translation_validator_tool/db_schema
..\api\venv\Scripts\python.exe -m alembic upgrade head
```

Linux / macOS (bash):
```bash
cd translation_validator_tool/db_schema
../api/venv/bin/python -m alembic upgrade head
```

3) Ejecutar el servidor local (desarrollo)

Windows (PowerShell):
```powershell
cd translation_validator_tool/api
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Linux / macOS (bash):
```bash
cd translation_validator_tool/api
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints útiles:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

4) Scripts útiles (ubicados en `app/scripts`)

Crear admin (ejemplo):

Windows (PowerShell):
```powershell
cd translation_validator_tool/api
.\venv\Scripts\Activate.ps1
python -m app.scripts.create_admin --username admin --email admin@example.com --password admin123
```

Linux / macOS (bash):
```bash
cd translation_validator_tool/api
source venv/bin/activate
python -m app.scripts.create_admin --username admin --email admin@example.com --password admin123
```

Cargar corpus desde CSV (ejemplo):

Windows (PowerShell):
```powershell
cd translation_validator_tool/api
.\venv\Scripts\Activate.ps1
python -m app.scripts.load_corpus --file ..\..\data\translations.csv
```

Linux / macOS (bash):
```bash
cd translation_validator_tool/api
source venv/bin/activate
python -m app.scripts.load_corpus --file ../../data/translations.csv
```

Opciones del script:
- `--file PATH` — ruta al CSV
- `--sample` — cargar datos de ejemplo

Formato mínimo esperado en CSV:
```
guarani,spanish,source
```

5) Desarrollo y migraciones (resumen)

Crear una nueva migración (desde `db_schema` con venv activo):

Windows (PowerShell):
```powershell
cd translation_validator_tool/db_schema
..\api\venv\Scripts\python.exe -m alembic revision --autogenerate -m "Describe changes"
```

Linux / macOS (bash):
```bash
cd translation_validator_tool/db_schema
../api/venv/bin/python -m alembic revision --autogenerate -m "Describe changes"
```

Aplicar migraciones:

Windows (PowerShell):
```powershell
cd translation_validator_tool/db_schema
..\api\venv\Scripts\python.exe -m alembic upgrade head
```

Linux / macOS (bash):
```bash
cd translation_validator_tool/db_schema
../api/venv/bin/python -m alembic upgrade head
```

Revertir la última migración:

Windows (PowerShell):
```powershell
cd translation_validator_tool/db_schema
..\api\venv\Scripts\python.exe -m alembic downgrade -1
```

Linux / macOS (bash):
```bash
cd translation_validator_tool/db_schema
../api/venv/bin/python -m alembic downgrade -1
```

6) Troubleshooting rápido

- `No module named 'psycopg2'`: instala la dependencia en el venv:

	Windows:
	```powershell
	.\venv\Scripts\python.exe -m pip install psycopg2-binary
	```

	Linux:
	```bash
	source venv/bin/activate
	python -m pip install psycopg2-binary
	```

- `CREATE DATABASE cannot be executed inside a transaction`: usa el helper `init_database.py` o crea la BD manualmente con `psql`/`createdb`.
- Problemas de encoding al cargar CSV: asegúrate que el archivo está en UTF-8.

7) Organización recomendada

- Scripts que usan modelos y `SessionLocal`: `api/app/scripts`.
- Migraciones e inicialización de BD: `db_schema`.

---
---