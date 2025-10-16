# 🗄️ Database Schema Management

Este directorio contiene todos los scripts y configuraciones para la gestión de la base de datos PostgreSQL del Translation Validator.

## 📁 Estructura

```
db_schema/
├── alembic/                    # Migraciones con Alembic
│   ├── versions/              # Scripts de migración
│   └── env.py                 # Configuración de Alembic
├── alembic.ini               # Configuración de Alembic
├── init_db.py               # Funciones de inicialización de BD
├── init_database.py         # Script principal de gestión
└── README.md                # Esta documentación
```

## 🚀 Scripts de Inicialización

### Script Principal: `init_database.py`

Este script puede **crear la base de datos completa desde cero**, incluyendo:
- ✅ Crear la base de datos PostgreSQL (si no existe)
- ✅ Crear todas las tablas necesarias
- ✅ Añadir usuario administrador por defecto

### Comandos Disponibles

```bash
# Inicializar base de datos completa (comando por defecto)
python init_database.py
python init_database.py init

# Resetear completamente la base de datos (elimina todo y recrea)
python init_database.py reset

# Eliminar todas las tablas
python init_database.py drop

# Probar conexión a la base de datos
python init_database.py test
```

## 📋 Proceso de Inicialización Completa

### 1. Si borras completamente la base de datos:

```bash
cd translation_validator_tool/db_schema
python init_database.py init
```

**Esto hará:**
1. 🏗️ Crear la base de datos `translation_validator` (si no existe)
2. 📊 Verificar conexión a PostgreSQL
3. 🗃️ Crear todas las tablas (users, translations, validations, etc.)
4. 👤 Crear usuario administrador por defecto:
   - **Username:** `admin`
   - **Email:** `admin@translation-validator.com`
   - **Password:** `admin123`

### 2. Arrancar la aplicación:

```bash
cd ../api
uvicorn app.main:app --reload
```

### 3. Probar el sistema:

- 🌐 API: http://127.0.0.1:8000
- 📚 Docs: http://127.0.0.1:8000/docs
- 👤 Login: username=`admin`, password=`admin123`

## ⚠️ Importante

1. **Cambiar contraseña:** El password `admin123` es temporal. Cámbialo inmediatamente después del primer login.

2. **Variables de entorno:** El script usa la configuración del archivo `.env` en el directorio `api/`.

3. **PostgreSQL:** Asegúrate de que PostgreSQL esté ejecutándose en tu sistema.

## 🔄 Migraciones con Alembic

Para cambios en el esquema de la base de datos:

```bash
# Generar nueva migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Ver historial
alembic history

# Volver a versión anterior
alembic downgrade -1
```

## 🛠️ Funciones Disponibles

El módulo `init_db.py` proporciona:

- `create_database_if_not_exists()` - Crear BD si no existe
- `create_tables()` - Crear todas las tablas
- `test_database_connection()` - Probar conexión
- `drop_all_tables()` - Eliminar todas las tablas
- `reset_database()` - Reset completo
- `initialize_database()` - Inicialización completa

## 🔧 Solución de Problemas

### Error de conexión a PostgreSQL:
```bash
# Verificar que PostgreSQL esté ejecutándose
python init_database.py test
```

### Error de variables de entorno:
- Verificar que existe `api/.env`
- Verificar que contiene `DATABASE_URL` y `SECRET_KEY`

### Recrear todo desde cero:
```bash
python init_database.py reset
```

## 🚀 Quick Start

### 1. Database Setup (First Time)

```bash
# 1. Create the database
createdb translation_validator

# 2. Run initialization script (optional)
psql -d translation_validator -f init.sql

# 3. Create initial migration
alembic revision --autogenerate -m "Initial migration"

# 4. Apply migrations
alembic upgrade head

# 5. Insert seed data (optional)
psql -d translation_validator -f seed.sql
```

### 2. Using Helper Scripts

**Windows:**
```cmd
# Create initial migration
migrate.bat init

# Apply migrations
migrate.bat upgrade

# Insert seed data
migrate.bat seed
```

**Linux/Mac:**
```bash
# Make script executable
chmod +x migrate.sh

# Create initial migration
./migrate.sh init

# Apply migrations
./migrate.sh upgrade

# Insert seed data
./migrate.sh seed
```

## 🔧 Common Operations

### Creating New Migrations

When you modify models in the API, create a new migration:

```bash
# Auto-generate migration based on model changes
alembic revision --autogenerate -m "Add user preferences table"

# Apply the new migration
alembic upgrade head
```

### Managing Migrations

```bash
# View migration history
alembic history

# View current migration
alembic current

# Rollback one migration
alembic downgrade -1

# Rollback to specific migration
alembic downgrade <revision_id>
```

### Development Database Reset

⚠️ **WARNING: This deletes all data!**

```bash
# Reset database completely
psql -d translation_validator -f reset_db.sql

# Then reapply migrations
alembic upgrade head

# And insert fresh seed data
psql -d translation_validator -f seed.sql
```

## 📊 Database Schema

### Tables

1. **users** - System users who can validate translations
2. **translations** - Guaraní-Spanish translation pairs
3. **validations** - User ratings/validations for translations
4. **translation_suggestions** - User-suggested improvements

### Key Relationships

- Users can have many validations and suggestions
- Each translation can have many validations and suggestions
- Validations are unique per user-translation pair

## 🔒 Security Notes

- The `seed.sql` contains sample users with the password `password123`
- Change default passwords before production deployment
- Ensure proper database permissions are set

## 📝 Environment Variables

The migration system reads database URL from:
1. `DATABASE_URL` environment variable (highest priority)
2. API settings file (`../api/app/config.py`)
3. Fallback URL in `env.py`

## 🛠 Troubleshooting

### Common Issues

**"No module named 'app'"**
- Ensure you're running from the `db_schema` directory
- Check that the API directory structure is correct

**"Could not locate a Flask application"**
- This is an Alembic/SQLAlchemy project, not Flask
- Make sure you're using the correct commands

**"Permission denied" on scripts**
- On Linux/Mac: `chmod +x migrate.sh`
- On Windows: Run as Administrator if needed

### Manual Migration Creation

If auto-generation doesn't work:

```bash
# Create empty migration
alembic revision -m "Manual migration"

# Edit the generated file in alembic/versions/
# Add your SQL commands in upgrade() and downgrade()
```

## 📈 Performance Tips

- Indexes are created in `seed.sql` for common queries
- Monitor query performance with the statistics in `backup.sql`
- Consider partitioning for large translation datasets

## 🔄 Backup & Restore

### Full Backup
```bash
pg_dump -h localhost -p 5432 -U postgres -d translation_validator -f backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore
```bash
psql -h localhost -p 5432 -U postgres -d translation_validator -f backup_YYYYMMDD_HHMMSS.sql
```

### CSV Export (using backup.sql queries)
```bash
psql -d translation_validator -f backup.sql
```