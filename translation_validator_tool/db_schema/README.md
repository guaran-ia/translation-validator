# 🗄️ Database schema and initialization

Herramientas y documentación para gestionar la base de datos PostgreSQL del
proyecto. Incluye scripts para inicializar, resetear y aplicar migraciones.

Resumen rápido
- Migraciones: `db_schema/alembic/` (Alembic)
- Helper de inicialización: `init_database.py` (usa `init_db.py`)
- Configuración: `translation_validator_tool/api/.env` contiene `DATABASE_URL` y claves

Estructura importante

```
db_schema/
├── alembic/                # Migraciones con Alembic (versions/, env.py)
├── alembic.ini             # Configuración de Alembic
├── init_db.py              # Funciones reutilizables para init/reset
├── init_database.py        # Script ejecutable para init/reset/test
└── README.md               # Esta documentación
```

Objetivo de los scripts

- `init_database.py init` — crea la base de datos (si no existe), crea tablas y
	agrega un admin por defecto (útil en desarrollo).
- `init_database.py reset` — elimina tablas y las vuelve a crear (dev).
- `init_database.py drop` — elimina todas las tablas (peligroso, borra datos).
- `init_database.py test` — prueba la conexión a la base de datos.

Nota: los scripts importan módulos del backend (`app.*`), por lo que deben
ejecutarse usando el Python del venv del `api` o con el venv activado.

Uso (ejemplos Windows / Linux)

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

Migraciones (Alembic)

Ejecuta Alembic desde `db_schema` para que `alembic.ini` se resuelva correctamente.

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

Recomendaciones y notas

- No existen archivos `init.sql`, `seed.sql`, `migrate.bat` ni `migrate.sh`.
	La funcionalidad está en `init_database.py` y Alembic.
- Si ves `No module named 'app'`, ejecuta desde `db_schema` y usa el Python del
	venv del backend.
- Si prefieres crear la BD manualmente (entornos controlados), crea la BD con
	`psql`/`createdb` y luego aplica las migraciones con Alembic.

Backup & restore (ejemplos genéricos)

```bash
pg_dump -h localhost -p 5432 -U postgres -d translation_validator -f backup.sql
psql -h localhost -p 5432 -U postgres -d translation_validator -f backup.sql
```

Solución de problemas rápidos

- `CREATE DATABASE` dentro de transacción: usa `init_database.py init` o crea la
	BD manualmente con `psql`.
- Variables de entorno: revisa `translation_validator_tool/api/.env`.
- Encoding CSV: asegúrate que los CSV estén en UTF-8.

Referencias

- Scripts y utilidades: `translation_validator_tool/api/app/scripts/`
- Migraciones: `translation_validator_tool/db_schema/alembic/`