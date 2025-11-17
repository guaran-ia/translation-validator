# Guía de Anotación POS para Textos Guaraní

Esta guía explica cómo usar Prodigy para anotar categorías gramaticales (POS Tagging) en oraciones Guaraní.

---

## 📋 Requisitos Previos

- Python 3.13+
- Prodigy instalado (v1.18.3)
- spaCy instalado
- Base de datos: PostgreSQL (para traducciones) + SQLite (para Prodigy)

---

## 🚀 Inicio Rápido

### 1. Navegar al directorio de Prodigy

```powershell
cd C:\Users\infor\Desktop\manu\LACUNA\guarani-corpus-lacuna-uni\translation_validator_tool\prodigy
```

### 2. Exportar traducciones desde PostgreSQL (si es necesario)

```powershell
cd ..\api
python ..\prodigy\scripts\export_to_prodigy.py --output ..\prodigy\data\export\original_translations.jsonl --only-original --limit 100
cd ..\prodigy
```

### 3. Iniciar servidor de anotación

```powershell
$env:PRODIGY_PORT=8081
python -m prodigy guarani-pos pos_guarani_new data/export/original_translations.jsonl -F recipes/guarani_pos_tagging.py
```

**Salida esperada:**
```
Added dataset pos_guarani_new to database SQLite.
✨  Starting the web server at http://localhost:8081 ...
Open the app in your browser and start annotating!
```

### 4. Abrir navegador

Ir a: **http://localhost:8081**

---

## 🏷️ Categorías Gramaticales

### Etiquetas Principales

| Etiqueta | Descripción | Ejemplo (Guaraní) | Ejemplo (Español) |
|----------|-------------|-------------------|-------------------|
| **SUJETO** | Quien realiza la acción | `Itaugua` | En Itaguá |
| **VERBO** | Acción o estado | `omokyre'ÿ` | promueven |
| **OBJETO** | Sobre qué/quién recae la acción | `Congreso` | el Congreso |
| **SUSTANTIVO** | Persona, lugar o cosa | `tapicha` | personas |
| **ADJETIVO** | Califica al sustantivo | `político` | político |
| **ADVERBIO** | Modifica verbo/adjetivo | `hikuái` | también |
| **PRONOMBRE** | Reemplaza sustantivo | `ko'ã` | estos |
| **PREPOSICIÓN** | Relación espacial/temporal | `-pe` | en |
| **ARTÍCULO** | Determina sustantivo | - | el, la, un |
| **CONJUNCIÓN** | Une palabras/frases | `ha` | y |

---

## 📝 Workflow de Anotación

### Paso 1: Leer la oración

1. **Texto en Guaraní** aparece abajo (seleccionable)
2. **Traducción al español** aparece arriba (referencia)

### Paso 2: Seleccionar palabras

1. **Haz clic en una palabra** del texto en Guaraní
2. La palabra se resalta en color
3. **Selecciona la etiqueta** apropiada (SUJETO, VERBO, etc.)
4. La palabra queda marcada con la etiqueta

**Atajos de teclado:**
- `1` - Primera etiqueta (SUJETO)
- `2` - Segunda etiqueta (VERBO)
- `3` - Tercera etiqueta (OBJETO)
- `4-9` - Siguientes etiquetas
- `D` - Eliminar anotación seleccionada

### Paso 3: Guardar anotación

Cuando termines de anotar la oración:

- **Presiona el botón verde ✓ (Accept)** o tecla `Enter`
- O presiona el botón rojo ✗ (Reject) si la oración tiene problemas

**⚠️ IMPORTANTE:** La anotación NO se guarda hasta que presiones ✓ o ✗

### Paso 4: Continuar

- Automáticamente aparece la siguiente oración
- Repite el proceso
- El progreso se muestra en el sidebar izquierdo

---

## 💾 Guardar y Exportar

### Detener el servidor

Cuando termines de anotar:

```powershell
# Presiona Ctrl+C en la terminal
```

**Las anotaciones ya están guardadas en la base de datos de Prodigy.**

### Ver estadísticas

```powershell
python -m prodigy stats pos_guarani_new
```

**Salida:**
```
Dataset       pos_guarani_new
Annotations   50
Accept        48
Reject        2
```

### Exportar a archivo JSONL

```powershell
python -m prodigy db-out pos_guarani_new > data/annotations/pos_guarani_export_$(Get-Date -Format 'yyyyMMdd_HHmmss').jsonl
```

Esto crea un archivo con timestamp: `pos_guarani_export_20251117_120000.jsonl`

### Exportar a CSV (opcional)

```powershell
python -m prodigy db-out pos_guarani_new --csv > data/annotations/pos_guarani_export.csv
```

---

## 🔄 Sincronizar con PostgreSQL (Opcional)

Si quieres guardar las anotaciones en tu base de datos principal:

```powershell
cd ..\api
python ..\prodigy\scripts\sync_prodigy_to_db.py sync-validations pos_guarani_new --user-id 1 --dry-run
# Si todo está bien, ejecuta sin --dry-run:
python ..\prodigy\scripts\sync_prodigy_to_db.py sync-validations pos_guarani_new --user-id 1
cd ..\prodigy
```

---

## 🎯 Mejores Prácticas

### 1. Sesiones cortas
- Anota 10-20 oraciones por sesión
- Toma descansos para mantener la concentración
- La calidad es más importante que la cantidad

### 2. Consistencia
- Usa siempre las mismas etiquetas para los mismos casos
- Consulta la tabla de categorías cuando tengas dudas
- Si no estás seguro, usa Reject y agrega un comentario

### 3. Organización
- Usa nombres descriptivos para los datasets: `pos_guarani_fecha` o `pos_guarani_tema`
- Exporta regularmente (cada 50-100 anotaciones)
- Mantén backups de los archivos exportados

### 4. Verificación
- Revisa el sidebar izquierdo para ver el progreso
- Verifica que el contador de "accept" aumente después de cada anotación
- Exporta y revisa el archivo JSONL periódicamente

---

## 🐛 Solución de Problemas

### El texto no aparece para anotar
**Causa:** Falta tokenización o error en el recipe
**Solución:** Verifica que el recipe incluya `set_hashes(example)`

### Las anotaciones no se guardan
**Causa:** No presionaste el botón ✓
**Solución:** SIEMPRE presiona ✓ o ✗ después de anotar

### Error de puerto 8081
**Causa:** Puerto ocupado por otro proceso
**Solución:**
```powershell
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
$env:PRODIGY_PORT=8082
# Vuelve a iniciar el servidor
```

### Caracteres especiales no se ven
**Causa:** Problema de encoding
**Solución:** Asegúrate de que el terminal use UTF-8:
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

---

## 📊 Estructura de Datos

### Formato de anotación guardada (JSONL)

```json
{
  "text": "Itaugua omokyre'ÿ \"omopotî\" Congreso",
  "tokens": [
    {"text": "Itaugua", "start": 0, "end": 7, "id": 0},
    {"text": "omokyre'ÿ", "start": 8, "end": 17, "id": 1},
    {"text": "Congreso", "start": 28, "end": 36, "id": 5}
  ],
  "spans": [
    {"start": 0, "end": 7, "token_start": 0, "token_end": 0, "label": "SUJETO"},
    {"start": 8, "end": 17, "token_start": 1, "token_end": 1, "label": "VERBO"},
    {"start": 19, "end": 26, "token_start": 3, "token_end": 3, "label": "OBJETO"}
  ],
  "answer": "accept",
  "meta": {
    "translation_id": 1,
    "spanish_text": "En Itaguá promueven \"limpiar\" el Congreso"
  }
}
```

---

## 🔧 Comandos Útiles

### Listar todos los datasets

```powershell
python -m prodigy stats -ls
```

### Ver detalle de un dataset

```powershell
python -m prodigy stats NOMBRE_DATASET
```

### Eliminar un dataset

```powershell
python -m prodigy drop NOMBRE_DATASET
```

### Fusionar datasets

```powershell
python -m prodigy db-merge dataset1,dataset2,dataset3 dataset_final
```

### Ver progreso en tiempo real

Mientras anotas, abre otra terminal:
```powershell
python -m prodigy progress NOMBRE_DATASET
```

---

## 📚 Referencias

- **Documentación Prodigy:** https://prodi.gy/docs
- **Recipes personalizadas:** `recipes/guarani_pos_tagging.py`
- **Script de exportación:** `scripts/export_to_prodigy.py`
- **Script de sincronización:** `scripts/sync_prodigy_to_db.py`

---

## 👥 Flujo de Trabajo en Equipo

### Para múltiples anotadores:

1. **Cada persona usa su propio dataset:**
   ```powershell
   python -m prodigy guarani-pos pos_maria data/export/original_translations.jsonl -F recipes/guarani_pos_tagging.py
   python -m prodigy guarani-pos pos_juan data/export/original_translations.jsonl -F recipes/guarani_pos_tagging.py
   ```

2. **Al finalizar, fusionar:**
   ```powershell
   python -m prodigy db-merge pos_maria,pos_juan pos_final
   ```

3. **Resolver conflictos (opcional):**
   ```powershell
   python -m prodigy review pos_final pos_maria,pos_juan
   ```

---

## ✅ Checklist de Sesión de Anotación

Antes de empezar:
- [ ] PostgreSQL está corriendo
- [ ] Navegué al directorio `prodigy/`
- [ ] Exporté las traducciones (si es necesario)
- [ ] Puerto 8081 está libre

Durante la anotación:
- [ ] Servidor está corriendo en http://localhost:8081
- [ ] Veo el texto en Guaraní y la traducción al español
- [ ] Presiono ✓ después de cada anotación
- [ ] El contador de "accept" aumenta en el sidebar

Al terminar:
- [ ] Presioné Ctrl+C en la terminal
- [ ] Verifiqué las estadísticas: `python -m prodigy stats DATASET`
- [ ] Exporté a JSONL: `python -m prodigy db-out DATASET > archivo.jsonl`
- [ ] Guardé el archivo de exportación en `data/annotations/`

---

## 🎓 Ejemplos de Anotación

### Ejemplo 1: Oración simple

**Guaraní:** `Mitã oguata escuelape`
**Español:** El niño camina a la escuela

**Anotaciones:**
- `Mitã` → **SUJETO** (el niño)
- `oguata` → **VERBO** (camina)
- `escuelape` → **OBJETO** (a la escuela)

### Ejemplo 2: Oración compleja

**Guaraní:** `Ko'ã itaugüeño he'íva ombotovévo pokaríame`
**Español:** Estos itaugüeños expresan su repudio a los corruptos

**Anotaciones:**
- `Ko'ã` → **PRONOMBRE** (estos)
- `itaugüeño` → **SUJETO** (itaugüeños)
- `he'íva` → **VERBO** (expresan)
- `ombotovévo` → **VERBO** (repudio)
- `pokaríame` → **OBJETO** (a los corruptos)

---

## 📞 Soporte

Si tienes problemas o dudas:
1. Consulta la sección "Solución de Problemas"
2. Revisa los logs en la terminal donde corre el servidor
3. Verifica el archivo exportado para confirmar que las anotaciones están correctas
4. Contacta al administrador del sistema

---

**Última actualización:** 17 de noviembre de 2025
**Versión de Prodigy:** 1.18.3
