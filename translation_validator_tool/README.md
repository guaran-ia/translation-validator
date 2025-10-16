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