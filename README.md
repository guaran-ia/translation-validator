# guarani-corpus-lacuna-uni
Corpus y herramienta para Guaraní — Resumen

Proyecto para construir un corpus anotado del guaraní paraguayo y una
herramienta de validación/sugerencias de traducciones (Guaraní ↔ Español).

Estructura principal del repositorio
- `translation_validator_tool/` — Aplicación completa (backend, frontend, migraciones)
	- `api/` — Backend (FastAPI)
	- `ui/` — Frontend (React + Vite)
	- `db_schema/` — Migraciones y scripts para inicializar la base de datos
	- `data/` — CSVs y fuentes de datos (ej.: `translations.csv`)

Quickstart (resumen)
- Windows (PowerShell): activa un venv en `translation_validator_tool/api`, aplica migraciones desde `translation_validator_tool/db_schema`, ejecuta el backend y el frontend.
- Linux / macOS (bash): pasos equivalentes usando `python3 -m venv` y `cp` para copiar `.env`.

Para instrucciones completas y comandos copy-paste, abre los README específicos:
- `translation_validator_tool/README.md` (guía principal del proyecto)
- `translation_validator_tool/api/README.md` (backend)
- `translation_validator_tool/ui/README.md` (frontend)
- `translation_validator_tool/db_schema/README.md` (DB / migraciones)

