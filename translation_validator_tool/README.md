# Translation Validator Tool — Guía rápida (README principal)

Resumen
- Herramienta para validar y sugerir traducciones Guaraní ↔ Español. La carpeta
  `translation_validator_tool/` contiene el backend (`api/`), frontend (`ui/`) y las
  migraciones (`db_schema/`).

Estructura recomendada de lectura
1. `translation_validator_tool/README.md` — guía principal del proyecto
2. `translation_validator_tool/api/README.md` — backend (detallado)
3. `translation_validator_tool/ui/README.md` — frontend (detallado)
4. `translation_validator_tool/db_schema/README.md` — migraciones y helpers

Quick start — pasos principales (Windows PowerShell / Linux bash)

1) Clonar el repositorio

Windows (PowerShell):
```powershell
git clone https://github.com/aalvarez-fiuni/guarani-corpus-lacuna-uni.git
cd guarani-corpus-lacuna-uni
git checkout translation-validator
cd translation_validator_tool
```

Linux / macOS (bash):
```bash
git clone https://github.com/aalvarez-fiuni/guarani-corpus-lacuna-uni.git
cd guarani-corpus-lacuna-uni
git checkout translation-validator
cd translation_validator_tool
```

2) Backend — crear y activar venv, instalar dependencias

Windows (PowerShell):
```powershell
cd api
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# editar api/.env -> DATABASE_URL, SECRET_KEY, CORS_ORIGINS
```

Linux / macOS (bash):
```bash
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# editar api/.env -> DATABASE_URL, SECRET_KEY, CORS_ORIGINS
```

3) Migraciones / inicialización (usar `db_schema`)

Recomendado: usar el helper `init_database.py` que automatiza creación de BD (si se
requiere) y aplica las tablas necesarias. Ejecuta el helper usando el Python del venv
del backend.

Windows (PowerShell):
```powershell
cd ..\db_schema
..\api\venv\Scripts\python.exe init_database.py init
```

Linux / macOS (bash):
```bash
cd ../db_schema
../api/venv/bin/python init_database.py init
```

Alternativa: aplicar migraciones con Alembic (ejecutar desde `db_schema`):

Windows (PowerShell):
```powershell
cd db_schema
..\api\venv\Scripts\python.exe -m alembic upgrade head
```

Linux / macOS (bash):
```bash
cd db_schema
../api/venv/bin/python -m alembic upgrade head
```

4) Frontend — instalar dependencias y ejecutar

Windows (PowerShell):
```powershell
cd ../ui
npm install
copy .env.example .env
npm run dev
```

Linux / macOS (bash):
```bash
cd ../ui
npm install
cp .env.example .env
npm run dev
```

5) Levantar backend (uvicorn)

Windows (PowerShell):
```powershell
cd ../api
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Linux / macOS (bash):
```bash
cd ../api
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Importar CSV de traducciones (opcional)

Coloca tu CSV en `data/translations.csv` y usa el script de carga del backend.

Windows (PowerShell):
```powershell
cd api
.\venv\Scripts\Activate.ps1
python -m app.scripts.load_corpus --file ..\..\data\translations.csv
```

Linux / macOS (bash):
```bash
cd api
source venv/bin/activate
python -m app.scripts.load_corpus --file ../../data/translations.csv
```

Notas rápidas
- No comitees `.env` ni `venv/`.
- Usa `db_schema/` para gestionar migraciones y mantener el historial con Alembic.

Archivos de referencia
- `translation_validator_tool/api/README.md` — instrucciones detalladas del backend
- `translation_validator_tool/ui/README.md` — instrucciones detalladas del frontend
- `translation_validator_tool/db_schema/README.md` — migraciones y helpers

---
