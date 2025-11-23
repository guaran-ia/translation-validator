# Prodigy - Anotación Gramatical (POS Tagging) para Textos Guaraní

## 📋 Resumen

Prodigy es una herramienta de anotación profesional desarrollada por Explosion AI (creadores de spaCy) que usamos para anotar categorías gramaticales (POS Tagging) en oraciones Guaraní. Esto permite identificar sujetos, verbos, objetos y otras categorías gramaticales para crear datos de entrenamiento de alta calidad.

**Ahora con soporte multi-anotador** para garantizar calidad mediante Inter-Annotator Agreement (IAA) y resolución de conflictos.

## 🎯 Uso Principal

Anotar categorías gramaticales en textos Guaraní para análisis lingüístico:
- **SUJETO** - Quien realiza la acción
- **VERBO** - Acción o estado
- **OBJETO** - Sobre qué/quién recae la acción
- **SUSTANTIVO, ADJETIVO, ADVERBIO**, etc.

## 🚀 Inicio Rápido

### Anotación Individual (Simple)

### 1. Navegar al directorio

```powershell
cd C:\Users\infor\Desktop\manu\LACUNA\guarani-corpus-lacuna-uni\translation_validator_tool\prodigy
```

### 2. Exportar traducciones (si es necesario)

```powershell
cd ..\api
python ..\prodigy\scripts\export_to_prodigy.py --output ..\prodigy\data\export\original_translations.jsonl --only-original --limit 100
cd ..\prodigy
```

### 3. Iniciar servidor de anotación POS

```powershell
$env:PRODIGY_PORT=8081
python -m prodigy guarani-pos pos_guarani_new data/export/original_translations.jsonl -F recipes/guarani_pos_tagging.py
```

### 4. Abrir navegador

Ve a: **http://localhost:8081**

---

## 👥 Anotación Multi-Anotador (Calidad)

**Para proyectos que requieren alta calidad y validación entre anotadores.**

### 1. Definir anotadores

```powershell
$env:PRODIGY_ALLOWED_SESSIONS="alice,bob,carlos"
```

### 2. Iniciar servidor con recipe v2

```powershell
python -m prodigy guarani-pos-v2 pos_v2 data/export/original_translations.jsonl -F recipes/guarani_pos_v2.py --port 8081
```

### 3. Cada anotador accede con su sesión

- Alice: `http://localhost:8081/?session=alice`
- Bob: `http://localhost:8081/?session=bob`
- Carlos: `http://localhost:8081/?session=carlos`

### 4. Validación automática

El sistema requiere obligatoriamente:
- ✅ Al menos 1 **SUJETO**
- ✅ Al menos 1 **VERBO**

Si intentas aceptar sin cumplir esto, verás un mensaje de error.

### 5. Calcular Inter-Annotator Agreement

```powershell
python scripts/calculate_iaa.py pos_v2 --output reports/iaa_report.md
```

### 6. Identificar y resolver conflictos

```powershell
python scripts/export_conflicts.py pos_v2 --output data/export/conflicts.jsonl --threshold 0.3
```

**Ver workflow completo:** [QUALITY_ASSURANCE.md](QUALITY_ASSURANCE.md)

### 5. Anotar

1. **Haz clic en palabras** del texto en Guaraní
2. **Selecciona la etiqueta** (SUJETO, VERBO, OBJETO, etc.)
3. **Presiona ✓ (Accept)** para guardar
4. La siguiente oración aparece automáticamente

### 6. Exportar resultados

```powershell
python -m prodigy db-out pos_guarani_new > data/annotations/pos_export_$(Get-Date -Format 'yyyyMMdd_HHmmss').jsonl
```

### 7. Visualizar anotaciones en HTML

```powershell
# Exportar con encoding correcto
python -m prodigy db-out pos_guarani_new | Out-File -Encoding UTF8 data/annotations/export.jsonl

# Generar visualización HTML
python scripts/visualize_annotations.py data/annotations/export.jsonl data/annotations/visualization.html

# Abrir en navegador
start data/annotations/visualization.html
```

## 🏷️ Categorías Gramaticales

| Etiqueta | Descripción | Ejemplo (Guaraní) | Ejemplo (Español) |
|----------|-------------|-------------------|-------------------|
| **SUJETO** | Quien realiza la acción | `Itaugua` | En Itaguá |
| **VERBO** | Acción o estado | `omokyre'ÿ` | promueven |
| **OBJETO** | Sobre qué/quién recae | `Congreso` | el Congreso |
| **SUSTANTIVO** | Persona, lugar, cosa | `tapicha` | personas |
| **ADJETIVO** | Califica sustantivo | `político` | político |
| **ADVERBIO** | Modifica verbo | `hikuái` | también |
| **PRONOMBRE** | Reemplaza sustantivo | `ko'ã` | estos |
| **PREPOSICIÓN** | Relación espacial/temporal | `-pe` | en |
| **ARTÍCULO** | Determina sustantivo | - | el, la |
| **CONJUNCIÓN** | Une palabras/frases | `ha` | y |

## 📝 Atajos de Teclado

- `1-9` - Seleccionar etiquetas
- `Enter` - Aceptar anotación
- `D` - Eliminar anotación seleccionada
- `Ctrl+C` - Detener servidor (en terminal)

## 💾 Comandos Útiles

### Ver estadísticas

```powershell
python -m prodigy stats pos_guarani_new
python -m prodigy stats -ls  # Listar todos los datasets
```

### Exportar anotaciones

```powershell
# JSONL con timestamp
python -m prodigy db-out pos_guarani_new > data/annotations/pos_export_$(Get-Date -Format 'yyyyMMdd_HHmmss').jsonl

# CSV
python -m prodigy db-out pos_guarani_new --csv > data/annotations/pos_export.csv
```

### Gestionar datasets

```powershell
python -m prodigy drop NOMBRE_DATASET  # Eliminar
python -m prodigy db-merge dataset1,dataset2 dataset_final  # Fusionar
```

### Sincronizar con PostgreSQL (opcional)

```powershell
cd ..\api
python ..\prodigy\scripts\sync_prodigy_to_db.py sync-validations pos_guarani_new --user-id 1 --dry-run
python ..\prodigy\scripts\sync_prodigy_to_db.py sync-validations pos_guarani_new --user-id 1
cd ..\prodigy
```

## 🗄️ Estructura de Archivos

```
translation_validator_tool/prodigy/
├── README.md                       # Esta guía
├── POS_ANNOTATION_GUIDE.md        # Guía detallada de anotación
├── QUALITY_ASSURANCE.md           # Workflow multi-anotador completo ⭐
├── requirements.txt                # Dependencias Python
├── scripts/
│   ├── export_to_prodigy.py       # PostgreSQL → JSONL
│   ├── sync_prodigy_to_db.py      # Prodigy → PostgreSQL
│   ├── calculate_iaa.py           # Calcular Inter-Annotator Agreement ⭐
│   ├── export_conflicts.py        # Exportar desacuerdos ⭐
│   └── visualize_annotations.py   # Generar HTML de visualización
├── recipes/
│   ├── guarani_pos_tagging.py     # Recipe POS v1 (básico)
│   ├── guarani_pos_v2.py          # Recipe POS v2 con validación y task routing ⭐
│   └── translation_demo.py        # Recipe validación traducciones
├── data/
│   ├── export/                    # Datos exportados de PostgreSQL
│   │   ├── original_translations.jsonl
│   │   └── conflicts.jsonl        # Conflictos identificados
│   └── annotations/               # Anotaciones exportadas
│       ├── pos_guarani_new_export.jsonl
│       └── visualization.html
├── reports/                       # Reportes de calidad ⭐
│   └── iaa_report.md
└── models/                        # Modelos entrenados (futuro)
```

⭐ = **Nuevo en versión multi-anotador**

## 🐛 Solución de Problemas

### Las anotaciones no se guardan
- **Causa:** No presionaste el botón ✓ (Accept)
- **Solución:** SIEMPRE presiona ✓ o ✗ después de anotar cada oración

### El texto no es seleccionable
- **Causa:** Falta tokenización en el recipe
- **Solución:** El recipe debe incluir `set_hashes(example)` y generar tokens

### Puerto 8081 ocupado
```powershell
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
$env:PRODIGY_PORT=8082  # Usar otro puerto
```

### Caracteres especiales (ã, ẽ, ĩ) no se ven
- **Solución:** Asegúrate de usar UTF-8:
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

## 📊 Métricas de Calidad

### Interpretación de Cohen's Kappa (IAA)

| Valor | Interpretación |
|-------|----------------|
| < 0.20 | Acuerdo pobre |
| 0.21 - 0.40 | Acuerdo bajo |
| 0.41 - 0.60 | Acuerdo moderado |
| 0.61 - 0.80 | Acuerdo sustancial ⭐ |
| 0.81 - 1.00 | Acuerdo casi perfecto |

**Meta recomendada:** Kappa > 0.70

## 📚 Recursos

- **Documentación oficial**: https://prodi.gy/docs
- **Demo interactiva**: https://demo.prodi.gy/
- **Forum de soporte**: https://support.prodi.gy/
- **Recipes de ejemplo**: https://github.com/explosion/prodigy-recipes
- **spaCy integration**: https://spacy.io/universe/project/prodigy
- **Task routing guide**: https://prodi.gy/docs/task-routing

---

**Estado**: 🟢 **PRODUCCIÓN** - Sistema multi-anotador con quality assurance  
**Última actualización**: Noviembre 2025  
**Base de datos**: C:\Users\infor\.prodigy\prodigy.db  
**Datasets activos**: 
- `pos_guarani_new` (anotación simple)
- `pos_v2` (multi-anotador con IAA)
