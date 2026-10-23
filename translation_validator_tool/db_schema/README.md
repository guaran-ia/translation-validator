# Database schema and initialization

Tools and documentation for managing the project's PostgreSQL database,
including initialization, reset operations, and migrations.

## Overview

- Migrations: `db_schema/alembic/` (Alembic).
- Initialization helper: `init_database.py`, backed by `init_db.py`.
- Configuration: `translation_validator_tool/api/.env` contains `DATABASE_URL` and other settings.

Migrations and `add_column.py` read `DATABASE_URL` from the environment or
`api/.env`, without a fallback connection containing fixed credentials.
Exported environment variables take precedence. Configure this variable before
running the scripts. Migrations also load backend settings, including `SECRET_KEY`,
as shown in `api/.env.example`.

## Directory layout

```text
db_schema/
├── alembic/                # Alembic migrations (versions/, env.py)
├── alembic.ini             # Alembic configuration
├── init_db.py              # Reusable initialization/reset functions
├── init_database.py        # Initialization/reset/connection-test command
└── README.md               # This guide
```

## Script commands

- `init_database.py init` — Creates the database if needed, applies migrations,
  and adds a default administrator when no users exist.
- `init_database.py reset` — Drops and recreates tables for development.
- `init_database.py drop` — Drops all tables and deletes their data.
- `init_database.py test` — Tests the database connection.

The scripts import backend modules (`app.*`). Run them with the API virtual
environment's Python interpreter or activate that environment first.

## Initialization

The following examples start at the repository root.

**Windows — PowerShell:**

```powershell
cd translation_validator_tool/db_schema
..\api\venv\Scripts\python.exe init_database.py init
```

**Linux/macOS — Bash:**

```bash
cd translation_validator_tool/db_schema
../api/venv/bin/python init_database.py init
```

## Alembic migrations

Run Alembic from `db_schema` so that it can locate `alembic.ini`.
The following examples start at the repository root.

**Windows — PowerShell:**

```powershell
cd translation_validator_tool/db_schema
..\api\venv\Scripts\python.exe -m alembic upgrade head
```

**Linux/macOS — Bash:**

```bash
cd translation_validator_tool/db_schema
../api/venv/bin/python -m alembic upgrade head
```

## Notes

- There are no `init.sql`, `seed.sql`, `migrate.bat`, or `migrate.sh` files.
  Initialization is handled by `init_database.py` and Alembic.
- If you get `No module named 'app'`, run the command from `db_schema` with the
  backend environment's Python interpreter.
- If you prefer to create the database manually, use `psql` or `createdb`, then
  apply the Alembic migrations.

## Backup and restore

Generic examples; replace the connection details with your own:

```bash
pg_dump -h localhost -p 5432 -U postgres -d translation_validator -f backup.sql
psql -h localhost -p 5432 -U postgres -d translation_validator -f backup.sql
```

## Troubleshooting

- `CREATE DATABASE` inside a transaction: use `init_database.py init` or create
  the database manually with `psql`.
- Environment variables: check `translation_validator_tool/api/.env`.
- CSV encoding: save input files as UTF-8.

## References

- Scripts and utilities: `translation_validator_tool/api/app/scripts/`.
- Migrations: `translation_validator_tool/db_schema/alembic/`.
