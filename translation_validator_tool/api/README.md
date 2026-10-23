# Backend — Translation Validator

This README explains how to configure and run the FastAPI backend.
It is located in `translation_validator_tool/api`.

Each command block that starts with `cd translation_validator_tool/...` assumes
you are at the repository root. For a sequential installation walkthrough, see
the [main guide](../../README.md#installation).

## 1. Set up the environment

**Windows — PowerShell:**

```powershell
cd translation_validator_tool/api
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edit api/.env and set DATABASE_URL, SECRET_KEY, and CORS_ORIGINS.
```

**Linux/macOS — Bash:**

```bash
cd translation_validator_tool/api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit api/.env and set DATABASE_URL, SECRET_KEY, and CORS_ORIGINS.
```

Copy the template only during initial setup to avoid overwriting your configuration.

## 2. Create the database and apply migrations

Use `init_database.py` from `translation_validator_tool/db_schema`, with the
backend virtual environment's Python interpreter.

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

Alternatively, apply migrations with Alembic from `db_schema`:

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

## 3. Run the development server

**Windows — PowerShell:**

```powershell
cd translation_validator_tool/api
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Linux/macOS — Bash:**

```bash
cd translation_validator_tool/api
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Useful endpoints:

- [Swagger UI](http://127.0.0.1:8000/docs).
- [ReDoc](http://127.0.0.1:8000/redoc).

## 4. Utility scripts

Scripts are located in `app/scripts`.

### Create an administrator

The full name defaults to `Administrador`. To customize it, append
`--nombre-completo "Administrator name"` to the command. The automatic database
initializer also uses `Administrador` as the default full name.

**Windows — PowerShell:**

```powershell
cd translation_validator_tool/api
.\venv\Scripts\Activate.ps1
python -m app.scripts.create_admin --username admin --email admin@example.com --password admin123
```

**Linux/macOS — Bash:**

```bash
cd translation_validator_tool/api
source venv/bin/activate
python -m app.scripts.create_admin --username admin --email admin@example.com --password admin123
```

Replace example credentials with your own values.

### Import a sentence corpus from CSV

Provide your own UTF-8 CSV file; the campaign dataset is not distributed with the repository.

**Windows — PowerShell:**

```powershell
cd translation_validator_tool/api
.\venv\Scripts\Activate.ps1
python -m app.scripts.load_corpus --file ..\..\data\translations.csv
```

**Linux/macOS — Bash:**

```bash
cd translation_validator_tool/api
source venv/bin/activate
python -m app.scripts.load_corpus --file ../../data/translations.csv
```

Options:

- `--file PATH` — Path to the CSV file.
- `--sample` — Load sample data.

Expected CSV columns:

```csv
guarani,spanish,source
```

## 5. Development and migrations

Create a migration from `db_schema` using the backend interpreter:

**Windows — PowerShell:**

```powershell
cd translation_validator_tool/db_schema
..\api\venv\Scripts\python.exe -m alembic revision --autogenerate -m "Describe changes"
```

**Linux/macOS — Bash:**

```bash
cd translation_validator_tool/db_schema
../api/venv/bin/python -m alembic revision --autogenerate -m "Describe changes"
```

Apply migrations:

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

Revert the latest migration:

**Windows — PowerShell:**

```powershell
cd translation_validator_tool/db_schema
..\api\venv\Scripts\python.exe -m alembic downgrade -1
```

**Linux/macOS — Bash:**

```bash
cd translation_validator_tool/db_schema
../api/venv/bin/python -m alembic downgrade -1
```

## 6. Troubleshooting

- `No module named 'psycopg2'`: install the dependency in the backend virtual environment.

  From `api/` on Windows:

  ```powershell
  .\venv\Scripts\python.exe -m pip install psycopg2-binary
  ```

  From `api/` on Linux/macOS:

  ```bash
  source venv/bin/activate
  python -m pip install psycopg2-binary
  ```

- `CREATE DATABASE cannot be executed inside a transaction`: use `init_database.py`
  or create the database manually with `psql` or `createdb`.
- CSV encoding errors: save the input file as UTF-8.

## 7. Code organization

- Scripts using models and `SessionLocal`: `api/app/scripts`.
- Database migrations and initialization: `db_schema`.
