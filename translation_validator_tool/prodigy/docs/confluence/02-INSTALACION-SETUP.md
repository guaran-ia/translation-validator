# 🔧 Instalación y Setup

Esta guía detalla los pasos para instalar y configurar el sistema de anotación Prodigy desde cero.

---

## 1. Requisitos del Sistema

### 1.1 Software Requerido

| Software | Versión Mínima | Verificar |
|----------|----------------|-----------|
| Python | 3.9+ | `python --version` |
| Node.js | 18+ | `node --version` |
| PostgreSQL | 14+ | `psql --version` |
| Git | 2.x | `git --version` |

### 1.2 Licencia de Prodigy

Prodigy requiere una licencia válida. Asegúrate de tener:
- Archivo `prodigy.json` con tu clave de licencia
- O variable de entorno `PRODIGY_KEY`

---

## 2. Clonar el Repositorio

```powershell
git clone <url-repositorio>
cd guarani-corpus-lacuna-uni/translation_validator_tool/prodigy
```

---

## 3. Crear Entorno Virtual

### Windows (PowerShell)

```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno
.\venv\Scripts\Activate.ps1

# Verificar activación
(venv) PS> python --version
```

### Linux/Mac

```bash
python -m venv venv
source venv/bin/activate
```

---

## 4. Instalar Dependencias

### 4.1 Dependencias de Python

```powershell
# Actualizar pip
python -m pip install --upgrade pip

# Instalar Prodigy (requiere licencia)
pip install prodigy -f https://XXXX-XXXX-XXXX-XXXX@download.prodi.gy

# Instalar dependencias del proyecto
pip install -r requirements.txt
```

### 4.2 Archivo `requirements.txt`

```
# requirements.txt
fastapi>=0.100.0
uvicorn>=0.23.0
httpx>=0.24.0
python-dotenv>=1.0.0
python-jose[cryptography]>=3.3.0
spacy>=3.5.0
prodigy>=1.11.0
```

### 4.3 Modelo de spaCy

```powershell
# Descargar modelo español (usado para tokenización)
python -m spacy download es_core_news_sm
```

---

## 5. Configurar Variables de Entorno

### 5.1 Crear archivo `.env`

```powershell
# Copiar plantilla
Copy-Item .env.example .env

# Editar con tu editor preferido
notepad .env
# o
code .env
```

### 5.2 Contenido de `.env`

```bash
# =============================================================================
# CONFIGURACIÓN DEL SISTEMA DE ANOTACIÓN PRODIGY
# =============================================================================

# --- Backend API ---
BACKEND_URL=http://localhost:8000

# --- Validadores por tipo de anotación ---
VALIDATORS_POS=alice,bob,carlos
VALIDATORS_FEATURES=diana,elena,felipe
VALIDATORS_RELATIONS=gabriel,helena,ivan

# --- Configuración de tareas ---
ANNOTATIONS_PER_TASK=3
ENABLE_TASK_ROUTING=true

# --- Lotes ---
CURRENT_BATCH_POS=1
CURRENT_BATCH_FEATURES=1
CURRENT_BATCH_RELATIONS=1

# --- Puertos ---
PORT_POS=8080
PORT_FEATURES=8081
PORT_RELATIONS=8082
PORT_PROXY=8085

# --- OpenAI (opcional, para guarani_openai) ---
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
```

Consulta [03-VARIABLES-ENTORNO.md](03-VARIABLES-ENTORNO.md) para detalles de cada variable.

---

## 6. Inicializar Base de Datos Prodigy

Prodigy crea automáticamente su base de datos SQLite en:
- **Windows:** `%USERPROFILE%\.prodigy\prodigy.db`
- **Linux/Mac:** `~/.prodigy/prodigy.db`

### Verificar instalación

```powershell
# Verificar que Prodigy está instalado
prodigy stats

# Debe mostrar información de datasets y conexión
```

---

## 7. Generar Lotes de Datos

### 7.1 Preparar datos de entrada

Coloca tu archivo JSONL de oraciones en:
```
data/export/original_translations.jsonl
```

Formato esperado:
```json
{"text": "Oración en guaraní", "meta": {"spanish_text": "Traducción al español", "source": "..."}}
```

### 7.2 Ejecutar generador de lotes

```powershell
# Generar 60 lotes de 50 oraciones (3000 total)
python scripts/generate_batches.py --total 3000 --batch-size 50

# Con orden aleatorio (reproducible)
python scripts/generate_batches.py --total 3000 --batch-size 50 --shuffle --seed 42
```

### 7.3 Verificar lotes generados

```powershell
# Listar lotes
Get-ChildItem data/batches/

# Salida esperada:
# batch_001.jsonl
# batch_002.jsonl
# ...
# batch_060.jsonl
# batches_index.json
```

---

## 8. Configurar Backend (Puerto 8000)

El backend maneja autenticación de usuarios.

### 8.1 Navegar al directorio

```powershell
cd ../api
```

### 8.2 Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 8.3 Configurar PostgreSQL

```sql
-- Crear base de datos
CREATE DATABASE guarani_corpus;

-- Crear usuario (opcional)
CREATE USER guarani_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE guarani_corpus TO guarani_user;
```

### 8.4 Ejecutar migraciones

```powershell
cd ../db_schema
alembic upgrade head
```

### 8.5 Crear usuarios iniciales

```powershell
python init_db.py
```

---

## 9. Configurar Frontend (Puerto 5173)

### 9.1 Navegar al directorio

```powershell
cd ../ui
```

### 9.2 Instalar dependencias

```powershell
npm install
```

### 9.3 Iniciar en desarrollo

```powershell
npm run dev
```

---

## 10. Verificar Instalación Completa

### 10.1 Checklist

- [ ] Python 3.9+ instalado
- [ ] Entorno virtual activado
- [ ] Prodigy instalado y licenciado
- [ ] Archivo `.env` configurado
- [ ] Lotes generados en `data/batches/`
- [ ] PostgreSQL configurado
- [ ] Backend funcionando en puerto 8000
- [ ] Frontend funcionando en puerto 5173

### 10.2 Test rápido

```powershell
# Desde el directorio prodigy/

# 1. Verificar Prodigy
prodigy stats

# 2. Verificar mapper
python -c "from scripts.ud_guarani_mapper import FRIENDLY_TO_UD; print('OK')"

# 3. Verificar recipe
prodigy guarani-batch pos 1 --help -F recipes/guarani_batch.py
```

---

## 11. Iniciar el Sistema

### 11.1 Inicio rápido (todo en uno)

```powershell
# Desde prodigy/
.\start_batch_all.ps1
```

Este script:
1. Inicia el JWT Proxy (8085)
2. Inicia Prodigy POS (8080)
3. Inicia Prodigy Features (8081)
4. Inicia Prodigy Relations (8082)
5. Inicia el Batch Monitor

### 11.2 Inicio manual (paso a paso)

```powershell
# Terminal 1: JWT Proxy
python prodigy_manager.py

# Terminal 2: Prodigy POS
prodigy guarani-batch pos 1 -F recipes/guarani_batch.py --port 8080

# Terminal 3: Prodigy Features
prodigy guarani-batch features 1 -F recipes/guarani_batch.py --port 8081

# Terminal 4: Prodigy Relations
prodigy guarani-batch relations 1 -F recipes/guarani_batch.py --port 8082
```

---

## 12. Acceder al Sistema

| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/docs |
| JWT Proxy | http://localhost:8085 |
| Prodigy (via proxy) | http://localhost:8085/?token=JWT_TOKEN |

---

## 13. Siguiente Paso

Continúa con [03-VARIABLES-ENTORNO.md](03-VARIABLES-ENTORNO.md) para entender cada variable de configuración.
