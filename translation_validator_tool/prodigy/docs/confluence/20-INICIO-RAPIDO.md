# 🚀 Inicio Rápido

Esta guía te permite iniciar el sistema de anotación Prodigy en **5 minutos**.

---

## Prerrequisitos

✅ Python 3.9+ instalado  
✅ Licencia de Prodigy válida  
✅ Acceso al repositorio del proyecto  

---

## Paso 1: Clonar y Navegar

```powershell
# Clonar repositorio (si no lo tienes)
git clone <url-repositorio>

# Navegar al directorio de Prodigy
cd guarani-corpus-lacuna-uni/translation_validator_tool/prodigy
```

---

## Paso 2: Crear Entorno Virtual

```powershell
# Crear entorno
python -m venv venv

# Activar entorno (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Verificar que está activo
(venv) PS> python --version
```

---

## Paso 3: Instalar Dependencias

```powershell
# Actualizar pip
python -m pip install --upgrade pip

# Instalar Prodigy (usa tu clave de licencia)
pip install prodigy -f https://XXXX-XXXX-XXXX-XXXX@download.prodi.gy

# Instalar otras dependencias
pip install -r requirements.txt

# Descargar modelo spaCy
python -m spacy download es_core_news_sm
```

---

## Paso 4: Configurar Variables de Entorno

```powershell
# Copiar plantilla
Copy-Item .env.example .env

# Editar configuración
notepad .env
```

**Configuración mínima en `.env`:**

```bash
BACKEND_URL=http://localhost:8000
VALIDATORS_POS=alice,bob,carlos
VALIDATORS_FEATURES=diana,elena
VALIDATORS_RELATIONS=gabriel,helena
CURRENT_BATCH_POS=1
CURRENT_BATCH_FEATURES=1
CURRENT_BATCH_RELATIONS=1
```

---

## Paso 5: Verificar Lotes

```powershell
# Verificar que existen los lotes
Get-ChildItem data/batches/ | Select-Object -First 5

# Debe mostrar:
# batch_001.jsonl
# batch_002.jsonl
# ...
```

Si no existen, generarlos:

```powershell
python scripts/generate_batches.py --total 3000 --batch-size 50
```

---

## Paso 6: Iniciar el Sistema

### Opción A: Todo en uno (recomendado)

```powershell
.\start_batch_all.ps1
```

Este script inicia:
- JWT Proxy en puerto **8085**
- Prodigy POS en puerto **8080**
- Prodigy Features en puerto **8081**
- Prodigy Relations en puerto **8082**
- Batch Monitor (auto-advance)

### Opción B: Manual (para desarrollo)

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

## Paso 7: Acceder al Sistema

### URLs

| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:5173 |
| JWT Proxy (principal) | http://localhost:8085 |
| API Status | http://localhost:8085/api/status |

### Acceder a Prodigy

1. Obtén un JWT token iniciando sesión en el frontend (http://localhost:5173)
2. Accede a Prodigy via proxy: `http://localhost:8085/?token=<JWT_TOKEN>&service=pos`

O configura el token en una cookie y accede directamente.

---

## Paso 8: Verificar Funcionamiento

```powershell
# Verificar estado de servicios
curl http://localhost:8085/api/status

# Respuesta esperada:
# {
#   "services": {
#     "pos": {"running": true, "port": 8080},
#     "features": {"running": true, "port": 8081},
#     "relations": {"running": true, "port": 8082}
#   }
# }
```

---

## Comandos Útiles

### Ver logs

```powershell
# Logs del proxy
Get-Content logs/prodigy_manager_*.log -Tail 20

# Logs de recipes
Get-Content logs/relations_recipe_*.log -Tail 20
```

### Ver progreso

```powershell
# Estadísticas de un dataset
prodigy stats guarani_pos_batch_01
```

### Detener servicios

```powershell
# Detener todos los procesos Python/Prodigy
Get-Process python | Stop-Process -Force
```

---

## Problemas Comunes

### Puerto en uso

```powershell
# Ver qué usa el puerto 8085
netstat -ano | findstr :8085

# Matar el proceso
taskkill /PID <PID> /F
```

### Prodigy no inicia

```powershell
# Verificar licencia
prodigy stats

# Si hay error de licencia, verificar PRODIGY_KEY
echo $env:PRODIGY_KEY
```

### Lotes no encontrados

```powershell
# Verificar ruta
Test-Path data/batches/batch_001.jsonl

# Regenerar si es necesario
python scripts/generate_batches.py --total 3000 --batch-size 50
```

---

## Siguiente Paso

Consulta [21-GUIA-ANOTADOR.md](21-GUIA-ANOTADOR.md) para instrucciones de anotación.
