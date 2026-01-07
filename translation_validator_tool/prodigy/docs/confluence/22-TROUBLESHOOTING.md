# 🐛 Troubleshooting

Solución a problemas comunes del sistema de anotación Prodigy.

---

## 1. Problemas de Conexión

### 1.1 "No autorizado" al acceder a Prodigy

**Síntoma:** Error 401 al intentar acceder a `http://localhost:8085`

**Causas posibles:**
- Token JWT expirado
- Token no incluido en la request
- Backend (8000) no está corriendo

**Soluciones:**

```powershell
# 1. Verificar que el backend está corriendo
curl http://localhost:8000/docs

# 2. Obtener nuevo token
# Ir a http://localhost:5173 y hacer login

# 3. Verificar token en la URL
# http://localhost:8085/?token=<tu_token>&service=pos
```

### 1.2 "Prodigy no responde"

**Síntoma:** Error 503 al acceder al proxy

**Causas posibles:**
- Ningún servicio Prodigy está corriendo
- Servicios Prodigy crashearon

**Soluciones:**

```powershell
# 1. Verificar estado de servicios
curl http://localhost:8085/api/status

# 2. Ver procesos Python corriendo
Get-Process python

# 3. Reiniciar servicios
.\start_batch_all.ps1

# 4. Iniciar manualmente un servicio
prodigy guarani-batch pos 1 -F recipes/guarani_batch.py --port 8080
```

### 1.3 Puerto ya en uso

**Síntoma:** "Address already in use" al iniciar

**Solución:**

```powershell
# Encontrar proceso usando el puerto
netstat -ano | findstr :8085
netstat -ano | findstr :8080

# Matar el proceso (reemplazar <PID>)
taskkill /PID <PID> /F

# O matar todos los procesos Python
Get-Process python | Stop-Process -Force
```

---

## 2. Problemas de Autenticación

### 2.1 Token JWT inválido

**Síntoma:** "Invalid token" o "Token expired"

**Soluciones:**

```powershell
# 1. Verificar expiración del token
# Los tokens expiran después de 24 horas por defecto

# 2. Obtener nuevo token via login
# Frontend: http://localhost:5173

# 3. Verificar formato del token
# Debe ser: eyJhbGciOiJIUzI1NiIs...
```

### 2.2 Usuario no tiene permisos

**Síntoma:** Error 403 "Forbidden"

**Causas:**
- Usuario no está en la lista de validadores
- Usuario no es superuser (para funciones admin)

**Solución:**

```bash
# Verificar en .env que el usuario está en la lista correcta
VALIDATORS_POS=alice,bob,carlos  # ← Agregar usuario aquí
```

---

## 3. Problemas de Datos

### 3.1 Lote no encontrado

**Síntoma:** "No existe el archivo batch_XXX.jsonl"

**Soluciones:**

```powershell
# 1. Verificar que el lote existe
Test-Path data/batches/batch_001.jsonl

# 2. Listar lotes disponibles
Get-ChildItem data/batches/

# 3. Regenerar lotes si es necesario
python scripts/generate_batches.py --total 3000 --batch-size 50
```

### 3.2 Dataset vacío

**Síntoma:** Prodigy no muestra ejemplos

**Causas:**
- Lote está vacío
- Todos los ejemplos ya fueron anotados por el usuario

**Soluciones:**

```powershell
# 1. Verificar contenido del lote
(Get-Content data/batches/batch_001.jsonl).Count

# 2. Verificar anotaciones existentes
prodigy stats guarani_pos_batch_01

# 3. Si el usuario ya anotó todo, asignar nuevo lote
```

### 3.3 Error de encoding UTF-8

**Síntoma:** Caracteres extraños en el texto guaraní

**Solución:**

```powershell
# Verificar encoding del archivo
Get-Content data/batches/batch_001.jsonl -Encoding UTF8 | Select-Object -First 1

# Si hay problemas, regenerar con encoding correcto
python scripts/generate_batches.py --total 3000 --batch-size 50
```

---

## 4. Problemas de Prodigy

### 4.1 Licencia inválida

**Síntoma:** "Invalid license key"

**Soluciones:**

```powershell
# 1. Verificar variable de entorno
echo $env:PRODIGY_KEY

# 2. Verificar archivo prodigy.json
Get-Content ~/.prodigy/prodigy.json

# 3. Reinstalar con clave correcta
pip install prodigy -f https://XXXX-XXXX-XXXX-XXXX@download.prodi.gy
```

### 4.2 Recipe no encontrado

**Síntoma:** "Unknown recipe: guarani-batch"

**Solución:**

```powershell
# Siempre usar -F para cargar el recipe
prodigy guarani-batch pos 1 -F recipes/guarani_batch.py --port 8080
```

### 4.3 Base de datos bloqueada

**Síntoma:** "database is locked"

**Causas:**
- Múltiples procesos accediendo a la DB simultáneamente
- Proceso zombie con lock en la DB

**Soluciones:**

```powershell
# 1. Matar todos los procesos Prodigy
Get-Process python | Where-Object {$_.MainWindowTitle -like "*prodigy*"} | Stop-Process

# 2. Reiniciar servicios uno a uno
prodigy guarani-batch pos 1 -F recipes/guarani_batch.py --port 8080
```

---

## 5. Problemas del Batch Monitor

### 5.1 Auto-advance no funciona

**Síntoma:** El sistema no avanza al siguiente lote automáticamente

**Causas:**
- batch_monitor no está corriendo
- No se alcanzó el número requerido de validadores

**Soluciones:**

```powershell
# 1. Verificar que batch_monitor está corriendo
Get-Process python | Where-Object {$_.CommandLine -like "*batch_monitor*"}

# 2. Verificar logs
Get-Content logs/batch_monitor_*.log -Tail 20

# 3. Verificar progreso
curl http://localhost:8085/api/batch-progress

# 4. Avanzar manualmente
curl -X POST http://localhost:8085/api/advance-batch `
  -H "Authorization: Bearer <TOKEN>" `
  -H "Content-Type: application/json" `
  -d '{"annotation_type": "pos"}'
```

### 5.2 Estado inconsistente

**Síntoma:** El lote actual no coincide con el esperado

**Solución:**

```powershell
# 1. Ver estado actual
Get-Content data/batch_monitor_state.json | ConvertFrom-Json

# 2. Editar manualmente si es necesario
notepad data/batch_monitor_state.json

# 3. Actualizar .env
notepad .env
# CURRENT_BATCH_POS=5
```

---

## 6. Problemas de Interfaz

### 6.1 Botón de contexto no funciona

**Síntoma:** Ctrl+Shift+C no abre el modal de contexto

**Causas:**
- JavaScript no cargó correctamente
- Conflicto con otra extensión del navegador

**Soluciones:**

1. Recargar la página (F5)
2. Abrir en modo incógnito
3. Verificar consola del navegador (F12 → Console)

### 6.2 Etiquetas no aparecen

**Síntoma:** Panel de etiquetas vacío

**Solución:**

```powershell
# Verificar que el mapper está funcionando
python -c "from scripts.ud_guarani_mapper import SPECIALIZED_GROUPS; print(len(SPECIALIZED_GROUPS['pos-tags']['labels']))"
# Debe mostrar: 11
```

### 6.3 Colores incorrectos

**Síntoma:** Todas las etiquetas del mismo color

**Solución:**

```python
# Verificar en el recipe que LABEL_COLORS está siendo usado
# En guarani_batch.py:
from ud_guarani_mapper import LABEL_COLORS
```

---

## 7. Logs y Diagnóstico

### Ubicación de logs

```
prodigy/
└── logs/
    ├── prodigy_manager_YYYYMMDD.log      # JWT Proxy
    ├── batch_monitor_YYYYMMDD.log        # Auto-advance
    ├── relations_recipe_YYYYMMDD.log     # Recipe relations
    └── ...
```

### Ver logs en tiempo real

```powershell
# Seguir logs del proxy
Get-Content logs/prodigy_manager_*.log -Wait -Tail 50

# Seguir logs de batch monitor
Get-Content logs/batch_monitor_*.log -Wait -Tail 50
```

### Habilitar modo debug

```python
# En prodigy_manager.py, cambiar:
logging.basicConfig(level=logging.DEBUG)
```

---

## 8. Comandos de Diagnóstico

### Verificación completa del sistema

```powershell
# 1. Verificar Python
python --version

# 2. Verificar Prodigy
prodigy stats

# 3. Verificar mapper
python -c "from scripts.ud_guarani_mapper import FRIENDLY_TO_UD; print('OK')"

# 4. Verificar lotes
(Get-ChildItem data/batches/*.jsonl).Count

# 5. Verificar servicios
curl http://localhost:8085/api/status

# 6. Verificar backend
curl http://localhost:8000/docs
```

### Reinicio completo

```powershell
# 1. Detener todo
Get-Process python | Stop-Process -Force

# 2. Limpiar logs viejos (opcional)
Remove-Item logs/*.log

# 3. Reiniciar
.\start_batch_all.ps1
```

---

## 9. Soporte

Si el problema persiste:

1. Recopilar logs relevantes
2. Anotar los pasos para reproducir el error
3. Verificar la versión de Prodigy: `prodigy --version`
4. Contactar al equipo de desarrollo con esta información
