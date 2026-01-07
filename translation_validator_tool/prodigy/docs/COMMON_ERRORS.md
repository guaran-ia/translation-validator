# 🔥 Guía de Errores Comunes en Prodigy - Qué Puede Salir Mal

> **Propósito:** Catálogo exhaustivo de todo lo que puede fallar en Prodigy y cómo diagnosticarlo

---

## 🎯 Categorías de Problemas

1. [Errores de Inicio](#1-errores-de-inicio)
2. [Errores de Autenticación](#2-errores-de-autenticación)
3. [Errores de Interfaz](#3-errores-de-interfaz)
4. [Errores de Datos](#4-errores-de-datos)
5. [Errores de Persistencia](#5-errores-de-persistencia)
6. [Errores de Red](#6-errores-de-red)
7. [Errores de Configuración](#7-errores-de-configuración)
8. [Errores de Concurrencia](#8-errores-de-concurrencia)
9. [Errores Silenciosos](#9-errores-silenciosos)
10. [Errores de Integración](#10-errores-de-integración)

---

## 1. 🚀 Errores de Inicio

### 1.1 "Port already in use"

```
ERROR: [Errno 10048] Only one usage of each socket address is normally permitted
```

**Causa:** Otro proceso ya usa el puerto (8080, 8085, etc.)

**Diagnóstico:**
```powershell
# Ver qué usa el puerto
netstat -ano | findstr :8080
# Matar proceso por PID
taskkill /F /PID <PID>
```

**Solución:**
- Cambiar puerto en .env
- Matar proceso anterior
- Esperar a que se libere (puede tardar 30-60 segundos)

---

### 1.2 "Module not found: prodigy"

```
ModuleNotFoundError: No module named 'prodigy'
```

**Causa:** Prodigy no está instalado o env incorrecto

**Diagnóstico:**
```powershell
pip list | findstr prodigy
python -c "import prodigy; print(prodigy.__version__)"
```

**Solución:**
```powershell
pip install prodigy -f https://XXXX-XXXX-XXXX@download.prodi.gy
```

---

### 1.3 "Recipe not found"

```
KeyError: 'guarani-batch'
```

**Causa:** Recipe no cargado con -F

**Solución:**
```powershell
prodigy guarani-batch pos 1 -F recipes/guarani_batch.py
```

---

### 1.4 "Database locked"

```
sqlite3.OperationalError: database is locked
```

**Causa:** Otro proceso tiene la DB abierta

**Solución:**
- Cerrar otras instancias de Prodigy
- Cerrar DB Browser u otras herramientas
- Reiniciar máquina si persiste

---

### 1.5 "No such file or directory" (datos)

```
FileNotFoundError: [Errno 2] No such file or directory: './data/batches/batch_001.jsonl'
```

**Causa:** Archivo de entrada no existe

**Diagnóstico:**
```powershell
Test-Path ./data/batches/batch_001.jsonl
ls ./data/batches/
```

**Solución:**
- Verificar ruta correcta
- Generar batches si no existen:
```powershell
python scripts/generate_batches.py
```

---

## 2. 🔐 Errores de Autenticación

### 2.1 "Token inválido" / 401 Unauthorized

**Pantalla:** Página de "Acceso Restringido"

**Causas posibles:**
1. Token expirado (default: 8 horas)
2. Token mal formado
3. Backend API caído
4. Token de otro ambiente (dev vs prod)

**Diagnóstico:**
```powershell
# Verificar formato JWT (3 partes separadas por punto)
$token = "eyJhbGciOiJI..."
$token.Split('.').Count  # Debe ser 3

# Verificar backend
curl http://localhost:8000/api/health
```

**Solución:**
1. Obtener nuevo token desde UI (login)
2. Verificar que backend esté corriendo
3. Limpiar cookies del navegador

---

### 2.2 Acceso con ?session= sin token

**Síntoma:** Usuario entra sin autenticarse

**Causa:** Cookie residual de sesión anterior

**Solución:**
1. Borrar cookies de localhost:8085
2. Usar ventana incógnito
3. Reiniciar proxy

---

### 2.3 "CORS error" en consola

```
Access to fetch at 'http://localhost:8000' has been blocked by CORS policy
```

**Causa:** Backend no permite origen del proxy

**Solución en backend (main.py):**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O especificar orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 3. 🖥️ Errores de Interfaz

### 3.1 UI en blanco / no carga

**Síntomas:**
- Página blanca
- Spinner infinito
- "Loading..." permanente

**Causas:**
1. JavaScript error en consola
2. Recursos estáticos no cargan
3. Proxy no reenvía correctamente

**Diagnóstico:**
- Abrir DevTools (F12) → Console
- Buscar errores rojos
- Tab Network → ver requests fallidos

**Soluciones:**
- Limpiar caché: Ctrl+Shift+R
- Verificar proxy corriendo
- Revisar logs del proxy

---

### 3.2 Etiquetas no aparecen

**Síntoma:** Panel de etiquetas vacío o incompleto

**Causas:**
1. Recipe no define labels
2. Error en carga de config

**Diagnóstico:**
```python
# En el recipe, verificar que retorne labels
return {
    "labels": ["NOUN", "VERB", ...],  # Debe existir
    ...
}
```

---

### 3.3 Texto se ve mal / caracteres raros

**Síntomas:**
- "ã" se ve como "Ã£"
- Caracteres □ o ?

**Causa:** Encoding incorrecto

**Solución:**
1. Archivo JSONL debe ser UTF-8
2. Navegador en UTF-8
3. Terminal en UTF-8:
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

---

### 3.4 Selección de texto no funciona

**Síntomas:**
- No se puede seleccionar texto
- Selección desaparece inmediatamente

**Causas:**
1. JavaScript error
2. CSS interfiere
3. Modo de touch en dispositivo

**Solución:**
- Revisar consola de errores
- Probar en otro navegador
- Desactivar extensiones

---

### 3.5 Colores de etiquetas incorrectos

**Síntoma:** Todas las etiquetas del mismo color

**Causa:** No se definen colores en recipe

**Solución:**
```python
# En recipe, agregar colors al return
"colors": {
    "NOUN": "#2563eb",
    "VERB": "#dc2626",
    ...
}
```

---

## 4. 📊 Errores de Datos

### 4.1 "No examples to annotate"

**Síntoma:** Prodigy dice que no hay datos

**Causas:**
1. Archivo vacío
2. Ya se anotó todo
3. Filtro excluye todo

**Diagnóstico:**
```powershell
# Contar líneas del archivo
(Get-Content ./data/batches/batch_001.jsonl).Count

# Ver dataset stats
python -m prodigy stats -ls
```

**Solución:**
- Verificar que archivo tenga datos
- Usar nuevo dataset
- Regenerar batches

---

### 4.2 JSON inválido en archivo de entrada

```
json.decoder.JSONDecodeError: Expecting value: line 15 column 1
```

**Causa:** Línea mal formada en JSONL

**Diagnóstico:**
```python
# Script para encontrar línea mala
import json
with open('archivo.jsonl') as f:
    for i, line in enumerate(f, 1):
        try:
            json.loads(line)
        except:
            print(f"Error en línea {i}: {line[:50]}...")
```

**Solución:**
- Corregir línea problemática
- Regenerar archivo

---

### 4.3 Campo "text" faltante

```
KeyError: 'text'
```

**Causa:** Datos no tienen el campo esperado

**Solución:**
Cada línea JSONL debe tener:
```json
{"text": "Tu texto aquí", ...}
```

---

### 4.4 Datos duplicados

**Síntoma:** Misma frase aparece múltiples veces

**Causas:**
1. Hash duplicado
2. Archivo con duplicados
3. Re-carga de datos

**Solución:**
```python
# Deduplicar por hash
from prodigy.util import set_hashes
examples = [set_hashes(eg) for eg in examples]
seen = set()
unique = []
for eg in examples:
    if eg["_task_hash"] not in seen:
        seen.add(eg["_task_hash"])
        unique.append(eg)
```

---

## 5. 💾 Errores de Persistencia

### 5.1 Anotaciones no se guardan

**Síntomas:**
- Accept pero no aparece en export
- Progreso no aumenta

**Causas:**
1. Error silencioso de DB
2. Transacción no committed
3. Dataset incorrecto

**Diagnóstico:**
```powershell
# Verificar contenido del dataset
python -m prodigy db-out guarani_pos_batch_001 | head
```

**Solución:**
- Verificar logs de errores
- Usar AUTO_SAVE_EVERY=1
- Revisar permisos de archivo DB

---

### 5.2 Pérdida de datos tras crash

**Causa:** Prodigy guarda en batches

**Prevención:**
```python
# En recipe, forzar guardado frecuente
"config": {
    "batch_size": 1,
    "instant_submit": True
}
```

---

### 5.3 Dataset corrupto

**Síntoma:** Error al leer dataset

**Solución:**
```powershell
# Backup
cp ~/.prodigy/prodigy.db ~/.prodigy/prodigy.db.bak

# Exportar lo que se pueda
python -m prodigy db-out dataset_name > backup.jsonl

# Eliminar dataset corrupto
python -m prodigy drop dataset_name
```

---

## 6. 🌐 Errores de Red

### 6.1 Connection refused

```
ConnectionRefusedError: [WinError 10061]
```

**Causa:** Servicio no está corriendo

**Diagnóstico:**
```powershell
# Verificar qué puertos están abiertos
netstat -an | findstr LISTEN

# Verificar servicios específicos
Test-NetConnection -ComputerName localhost -Port 8000
Test-NetConnection -ComputerName localhost -Port 8085
```

---

### 6.2 Timeout

**Síntomas:**
- Spinner infinito
- "Request timeout"

**Causas:**
1. Servidor sobrecargado
2. Red muy lenta
3. Firewall bloquea

**Solución:**
- Aumentar timeout en cliente
- Verificar firewall
- Reiniciar servicios

---

### 6.3 502 Bad Gateway

**Causa:** Proxy no puede conectar con Prodigy interno

**Diagnóstico:**
1. ¿Prodigy interno está corriendo?
2. ¿Puerto correcto en config?
3. ¿Proceso no crasheó?

```powershell
# Ver procesos Python
Get-Process python
```

---

## 7. ⚙️ Errores de Configuración

### 7.1 .env no se carga

**Síntoma:** Usa valores default incorrectos

**Causa:** dotenv no encuentra archivo

**Solución:**
```python
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
print(f"Buscando .env en: {env_path}")
print(f"Existe: {env_path.exists()}")
load_dotenv(env_path)
```

---

### 7.2 Variable de entorno incorrecta

```
PRODIGY_PORT=8080abc  # Error: no es número
```

**Síntoma:** Error de conversión o comportamiento extraño

**Solución:**
```python
# Validar en código
port = int(os.getenv("PRODIGY_PORT", "8080"))
```

---

### 7.3 Config de Prodigy conflictiva

**Síntoma:** Comportamiento inesperado

**Diagnóstico:**
```powershell
# Ver config actual
python -c "import prodigy; print(prodigy.get_config())"
```

---

## 8. 👥 Errores de Concurrencia

### 8.1 Race condition en DB

**Síntoma:** Datos inconsistentes con múltiples usuarios

**Causa:** SQLite no maneja bien alta concurrencia

**Solución:**
- Usar PostgreSQL para producción
- Reducir batch_size
- Separar datasets por usuario

---

### 8.2 Misma frase asignada a múltiples usuarios

**Síntoma:** 2 usuarios ven la misma frase

**Causa:** Task router no funciona correctamente

**Solución:**
```python
# Habilitar exclusion por sesión
"exclude_by": "session"
```

---

### 8.3 Deadlock de DB

**Síntoma:** Sistema colgado

**Causa:** Múltiples procesos esperando lock

**Solución:**
- Reiniciar todos los procesos
- Solo una instancia de Prodigy por DB

---

## 9. 🤫 Errores Silenciosos (Los Más Peligrosos)

### 9.1 Anotaciones vacías aceptadas

**Síntoma:** Usuario hace Accept sin anotar nada

**Impacto:** Datos de baja calidad en dataset

**Detección:**
```python
# Script para detectar anotaciones vacías
import json
for line in open('export.jsonl'):
    eg = json.loads(line)
    if eg.get('answer') == 'accept' and not eg.get('spans'):
        print(f"VACÍO: {eg['text'][:50]}...")
```

**Prevención:**
- Validación en recipe que requiera al menos 1 span
- Revisión de calidad post-anotación

---

### 9.2 Session ID incorrecto

**Síntoma:** Anotaciones de Alice aparecen como Bob

**Causa:** Cookie/parámetro incorrecto

**Impacto:** IAA calculado incorrectamente

**Detección:**
```python
# Verificar distribución de sessions
from collections import Counter
sessions = []
for line in open('export.jsonl'):
    eg = json.loads(line)
    sessions.append(eg.get('_session_id', 'unknown'))
print(Counter(sessions))
```

---

### 9.3 Token expirado pero cookie activa

**Síntoma:** Usuario sigue trabajando con token expirado

**Impacto:** Posible problema de seguridad

**Prevención:**
- Validar token en cada request importante
- Expiración de cookie = expiración de JWT

---

### 9.4 Datos no sincronizados con API principal

**Síntoma:** Prodigy tiene datos que API no tiene

**Causa:** sync_prodigy_to_db no se ejecutó

**Solución:**
```powershell
python scripts/sync_prodigy_to_db.py
```

---

## 10. 🔗 Errores de Integración

### 10.1 UI principal no conecta con Prodigy

**Síntoma:** Botón "Abrir Prodigy" no funciona

**Causas:**
1. URL incorrecta en config
2. Proxy no corriendo
3. CORS bloqueando

**Solución:**
- Verificar VITE_PRODIGY_URL en ui/.env
- Verificar proxy activo

---

### 10.2 Batch Monitor no detecta progreso

**Síntoma:** Auto-avance no funciona

**Causas:**
1. Dataset name incorrecto
2. Prodigy Manager no responde
3. Permisos de API

**Diagnóstico:**
```powershell
# Verificar que dataset existe
python -m prodigy stats -ls | findstr guarani_pos

# Verificar API del manager
curl http://localhost:8085/api/status
```

---

### 10.3 Export con formato incorrecto

**Síntoma:** Datos exportados no sirven para entrenamiento

**Causa:** Campos faltantes o formato incorrecto

**Validación:**
```python
# Verificar estructura de export
import json
with open('export.jsonl') as f:
    eg = json.loads(f.readline())
    required = ['text', 'spans', 'answer', '_session_id']
    missing = [k for k in required if k not in eg]
    if missing:
        print(f"Faltan campos: {missing}")
```

---

## 📋 Checklist de Diagnóstico Rápido

Cuando algo falla, verificar en orden:

1. **¿Los servicios están corriendo?**
   ```powershell
   netstat -an | findstr "8000 8080 8085"
   ```

2. **¿Hay errores en consola del navegador?**
   - F12 → Console → buscar rojo

3. **¿Hay errores en logs del servidor?**
   - Revisar terminal donde corre uvicorn/prodigy

4. **¿El token es válido?**
   ```powershell
   curl -H "Authorization: Bearer <token>" http://localhost:8000/api/auth/me
   ```

5. **¿La DB es accesible?**
   ```powershell
   python -m prodigy stats -ls
   ```

6. **¿Los archivos de datos existen?**
   ```powershell
   ls ./data/batches/
   ```

7. **¿Las variables de entorno están cargadas?**
   ```powershell
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('PRODIGY_PORT'))"
   ```

---

## 🛠️ Herramientas de Diagnóstico

### Script de Health Check

```python
#!/usr/bin/env python
"""health_check.py - Verifica estado del sistema"""

import os
import sys
import json
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def check_all():
    results = {}
    
    # 1. Backend API
    try:
        r = httpx.get("http://localhost:8000/api/health", timeout=5)
        results["backend_api"] = "✅" if r.status_code == 200 else "❌"
    except:
        results["backend_api"] = "❌ No conecta"
    
    # 2. Prodigy Manager
    try:
        r = httpx.get("http://localhost:8085/api/status", timeout=5)
        results["prodigy_manager"] = "✅" if r.status_code in [200, 401] else "❌"
    except:
        results["prodigy_manager"] = "❌ No conecta"
    
    # 3. Prodigy DB
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "prodigy", "stats", "-ls"],
            capture_output=True, timeout=10
        )
        results["prodigy_db"] = "✅" if result.returncode == 0 else "❌"
    except:
        results["prodigy_db"] = "❌ Error"
    
    # 4. Archivos de datos
    batches_dir = Path("./data/batches")
    batch_count = len(list(batches_dir.glob("*.jsonl"))) if batches_dir.exists() else 0
    results["batch_files"] = f"✅ {batch_count} batches" if batch_count > 0 else "❌ Sin batches"
    
    # 5. Variables de entorno
    required_vars = ["PRODIGY_PORT", "PRODIGY_PROXY_PORT", "BACKEND_URL"]
    missing = [v for v in required_vars if not os.getenv(v)]
    results["env_vars"] = "✅" if not missing else f"❌ Faltan: {missing}"
    
    print("\n🔍 HEALTH CHECK RESULTS")
    print("=" * 40)
    for key, value in results.items():
        print(f"  {key}: {value}")
    print("=" * 40)

if __name__ == "__main__":
    check_all()
```

### Uso:
```powershell
python health_check.py
```

---

## 📞 Cómo Reportar un Bug

Incluir:

1. **Descripción del problema**
2. **Pasos para reproducir**
3. **Resultado esperado vs actual**
4. **Logs relevantes** (terminal, consola del navegador)
5. **Capturas de pantalla**
6. **Información del sistema:**
   - OS y versión
   - Navegador y versión
   - Versión de Python
   - Versión de Prodigy

---

## 🔄 Actualizaciones de este Documento

| Fecha | Cambio |
|-------|--------|
| 2025-12-29 | Creación inicial |
| | |
