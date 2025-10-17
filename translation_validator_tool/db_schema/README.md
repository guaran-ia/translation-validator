# 🗄️ Database schema and initialization

Este directorio contiene las herramientas y la documentación para gestionar la base de datos PostgreSQL del proyecto.

**Resumen rápido:**
- Las migraciones de esquema están en `db_schema/alembic/`.
- El helper principal para creación/inicialización es `init_database.py` (usa `init_db.py`).
- La configuración de la aplicación (incluyendo `DATABASE_URL`) está en `api/.env`.

## Estructura importante

```
db_schema/
├── alembic/                # Migraciones con Alembic (versions/, env.py)
├── alembic.ini             # Configuración de Alembic
├── init_db.py              # Funciones reutilizables para init/reset
├── init_database.py        # Script ejecutable para init/reset/test
└── README.md               # Esta documentación
```

## Objetivo de los scripts

- `init_database.py init` — crea la base de datos (si no existe), crea tablas y agrega un admin por defecto.
- `init_database.py reset` — elimina tablas y las vuelve a crear (útil en dev).
- `init_database.py drop` — elimina todas las tablas (cuidado: borra datos).
- `init_database.py test` — prueba la conexión a la base de datos.

> Nota: estos scripts importan módulos del backend (`app.*`), por lo que deben ejecutarse usando el Python del venv del `api` o con el venv activado. Ver sección 'Uso' abajo.

## Uso (resumen)

- Asegúrate de tener el entorno virtual del backend (`api/venv`) con las dependencias instaladas.
- El archivo `.env` que contiene `DATABASE_URL` y `SECRET_KEY` está en `translation_validator_tool/api/.env`.
- Recomendamos usar el helper `init_database.py init` para crear la BD + tablas + admin en desarrollo.

## Migraciones (Alembic)

- Las migraciones se gestionan con Alembic y están en `db_schema/alembic/`.
- Ejecuta Alembic desde `db_schema` (para que `alembic.ini` se resuelva correctamente). En entornos Windows, es conveniente invocar el python del venv del backend.

Ejemplo (usar python del venv del backend):

```
cd translation_validator_tool/db_schema
..\api\venv\Scripts\python.exe -m alembic upgrade head
```

## Recomendaciones y notas

- No existen en este repo archivos `init.sql`, `seed.sql`, `migrate.bat` o `migrate.sh`. Si ves referencias a ellos en documentación antigua, ignóralas: la funcionalidad relevante está en `init_database.py` y Alembic.
- Si recibes `No module named 'app'`, asegúrate de ejecutar desde `db_schema` y de usar el Python del venv del `api` (o activar el venv antes).
- El helper `init_database.py` utiliza la URL en `api/.env` para crear la BD. Si la DB debe crearse manualmente (por ejemplo en entornos controlados), puedes usar `psql`/`createdb` y luego aplicar migraciones con Alembic.

## Backup & restore (comandos genéricos)

Puedes usar `pg_dump` y `psql` para backup y restore (ajusta host/puerto/usuario):

```
pg_dump -h localhost -p 5432 -U postgres -d translation_validator -f backup.sql
psql -h localhost -p 5432 -U postgres -d translation_validator -f backup.sql
```

## Solución de problemas rápidos

- Error al crear la base de datos (CREATE DATABASE dentro de transacción): usa `init_database.py init` (ya maneja autocommit) o crea la BD manualmente con `psql`.
- Error de variables de entorno: comprueba `translation_validator_tool/api/.env` y que `DATABASE_URL` y `SECRET_KEY` estén presentes.
- Problemas con codificación al importar CSV: asegúrate de que el CSV esté en UTF-8.

## Referencias

- Scripts de carga y utilidades del backend: `translation_validator_tool/api/app/scripts/`
- Migraciones y env para Alembic: `translation_validator_tool/db_schema/alembic/`

Si quieres, puedo limpiar más el README (por ejemplo, añadir ejemplos de uso con `init_database.py` usando el python del venv, o añadir un pequeño script `scripts/init_all.ps1` para Windows). Dime si lo deseas.