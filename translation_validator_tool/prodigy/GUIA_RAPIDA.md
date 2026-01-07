# 🚀 Guía Rápida: Prodigy desde Cero

Guía simple para empezar a anotar con Prodigy.

> ✅ Compatible con **Windows** y **Linux/Mac**

---

## 📋 Requisitos Previos

Antes de empezar necesitas:

1. **Python 3.8+** instalado
2. **Prodigy** instalado (licencia requerida)
3. **Backend API** del proyecto (opcional para autenticación)

---

## 🔧 Paso 1: Configurar el Entorno

### 1.1 Ir a la carpeta de Prodigy

```bash
cd translation_validator_tool/prodigy
```

### 1.2 Crear el archivo .env

Copia el archivo de ejemplo:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edita `.env` y configura:

```env
# Backend (si usas autenticación)
BACKEND_URL=http://localhost:8000

# Validadores por tipo de anotación
VALIDATORS_POS="alice,bob"
VALIDATORS_FEATURES="carlos,elena"
VALIDATORS_RELATIONS="marcos,nicolas"
```

### 1.3 Instalar dependencias

```bash
pip install -r requirements.txt
```
pip install prodigy -f https://XXXX-XXXX-XXXX-XXXX@download.prodi.gy

---

## 📦 Paso 2: Preparar los Datos

### 2.1 Exportar oraciones desde la base de datos

Si tienes datos en PostgreSQL:

```bash
python scripts/export_to_prodigy.py --limit 3000 --output data/export/original_translations.jsonl
```

**Opciones:**
- `--limit 3000`: Número de oraciones a exportar
- `--direction gn-sp`: Solo traducciones guaraní → español
- `--only-original`: Solo textos originales

### 2.2 Generar lotes (batches)

Divide las oraciones en lotes de 50:

```bash
python scripts/generate_batches.py --total 3000 --batch-size 50
```

Esto crea 60 archivos en `data/batches/`:
- `batch_001.jsonl`
- `batch_002.jsonl`
- ... 
- `batch_060.jsonl`

**Opciones:**
- `--total 3000`: Total de oraciones
- `--batch-size 50`: Oraciones por lote
- `--shuffle`: Orden aleatorio (opcional)

---

## ▶️ Paso 3: Iniciar Prodigy Manager

### Opción A: Inicio Simple (SIN auto-avance)

```bash
# Windows (PowerShell)
.\start_prodigy_manager.ps1

# Linux/Mac
python prodigy_manager.py
```

Esto inicia el servidor en `http://localhost:8085`

### Opción B: Inicio con Auto-Avance (RECOMENDADO)

```bash
# Windows (PowerShell)
.\start_batch_auto.ps1

# Linux/Mac
python prodigy_manager.py &
python batch_monitor.py --interval 60
```

Esto inicia:
- ✅ Prodigy Manager (puerto 8085)
- ✅ Monitor de batches
- ✅ Servicios POS, Features, Relations

**Opciones del auto-avance:**

```bash
# Empezar desde batch 5
.\start_batch_auto.ps1 -Batch 5          # Windows
python batch_monitor.py --start-batch 5   # Linux/Mac

# Chequear cada 30 segundos
.\start_batch_auto.ps1 -Interval 30       # Windows
python batch_monitor.py --interval 30     # Linux/Mac
```

> 💡 El sistema avanza automáticamente cuando **TODOS** los validadores 
> asignados completan sus 50 frases. Configura los validadores en `.env`.

---

## 🌐 Paso 4: Acceder a Prodigy

### 4.1 Abrir en el navegador

```
http://localhost:8085/?session=alice
```

Reemplaza `alice` por tu nombre de usuario.

### 4.2 Con autenticación JWT (si usas backend)

1. Login en la UI principal: `http://localhost:5173`
2. Ir a **Dashboard → Prodigy**
3. Seleccionar tipo de anotación
4. Click **"Iniciar Servicio"**

---

## 🛑 Paso 5: Detener Prodigy

### Opción 1: Script (Windows)

```powershell
.\stop_batch_auto.ps1
```

### Opción 2: Manual

```bash
# Presionar Ctrl+C en la terminal

# Linux/Mac - Si usaste &, buscar y matar procesos:
pkill -f prodigy_manager
pkill -f batch_monitor
```

---

## 📊 Comandos Útiles

### Ver estadísticas de Prodigy

```bash
python -m prodigy stats -ls
```

### Exportar un dataset

```bash
python -m prodigy db-out mi_dataset > export.jsonl
```

### Ver progreso del batch actual

```bash
curl http://localhost:8085/api/batch-status
```

---

## 🔄 Flujo Completo (Resumen)

```
1. Configurar .env
         ↓
2. Exportar datos (export_to_prodigy.py)
         ↓
3. Generar batches (generate_batches.py)
         ↓
4. Iniciar Prodigy (start_batch_auto.ps1 o python)
         ↓
5. Anotar en el navegador
         ↓
6. El sistema avanza automáticamente
```

---

## ❓ Problemas Comunes

### "No se encontró el archivo batch_001.jsonl"
```bash
# Genera los batches primero
python scripts/generate_batches.py --total 3000 --batch-size 50
```

### "Puerto 8085 en uso"
```bash
# Windows
.\stop_batch_auto.ps1
netstat -ano | findstr :8085
taskkill /PID <numero> /F

# Linux/Mac
lsof -i :8085
kill -9 <PID>
```

### "Token inválido"
- Verifica que el backend esté corriendo en `http://localhost:8000`
- O accede sin token: `http://localhost:8085/?session=alice`

### "No hay oraciones para anotar"
```bash
# Verifica que existan los batches
# Windows
dir data\batches\

# Linux/Mac
ls data/batches/
```

---

## 📁 Estructura de Archivos

```
prodigy/
├── .env                          # Tu configuración
├── start_batch_auto.ps1          # ⭐ Script principal
├── stop_batch_auto.ps1           # Detener todo
├── prodigy_manager.py            # Servidor proxy
├── batch_monitor.py              # Monitor auto-avance
├── data/
│   ├── batches/                  # Lotes generados
│   │   ├── batch_001.jsonl
│   │   ├── batch_002.jsonl
│   │   └── ...
│   └── export/                   # Datos exportados
│       └── original_translations.jsonl
└── scripts/
    ├── export_to_prodigy.py      # Exportar desde DB
    └── generate_batches.py       # Generar lotes
```

---

## 🎯 TL;DR (Versión Ultra Corta)

### Windows (PowerShell)

```powershell
cd translation_validator_tool/prodigy
copy .env.example .env
python scripts/generate_batches.py --total 3000 --batch-size 50
.\start_batch_auto.ps1
# Abrir: http://localhost:8085/?session=tu_nombre
```

### Linux/Mac (Bash)

```bash
cd translation_validator_tool/prodigy
cp .env.example .env
python scripts/generate_batches.py --total 3000 --batch-size 50
python prodigy_manager.py &
python batch_monitor.py --interval 60
# Abrir: http://localhost:8085/?session=tu_nombre
```

¡Listo! 🎉
