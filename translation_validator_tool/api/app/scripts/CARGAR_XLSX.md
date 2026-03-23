# Script de Carga de Anotaciones desde Excel

## Descripción

Script para cargar anotaciones desde un archivo Excel en formato `.xlsx`.

## Formato esperado del Excel

### Hoja requerida
- **Nombre**: `train_mgsm_es_to_gn`

### Columnas esperadas (a partir de la fila 1 con encabezados, datos desde fila 2)

| Columna | Nombre del Campo | Tipo | Obligatorio |
|---------|------------------|------|------------|
| A | ID | (ignorada) | No |
| B | question_es | Text | ✅ Sí |
| D | answer_es | Text | ✅ Sí |
| F | answer_number | Integer | No |
| G | equation_solution | Text | No |


```

## Uso

### Opción 1: Usando módulo Python

```bash
# Desde el directorio api/
python -m app.scripts.load_annotations --file /path/to/file.xlsx
```

### Opción 2: Desde el directorio db_schema (usando venv del api)

**Windows (PowerShell):**
```powershell
cd ..\api
..\api\venv\Scripts\python.exe -m app.scripts.load_annotations --file /path/to/file.xlsx
```

**Linux/macOS (bash):**
```bash
cd ../api
../api/venv/bin/python -m app.scripts.load_annotations --file /path/to/file.xlsx
```

## Salida esperada

```
Loading annotations from /path/to/file.xlsx...
✅ Found sheet 'train_mgsm_es_to_gn'
✓ Row 2: Created annotation ID 1
   Q: Roger tiene 5 pelotas de tenis...
   A: Respuesta paso a paso: Roger comenzó con 5...
   Equation: 5 + 6 = 11
✓ Row 3: Created annotation ID 2
   ...
✓ Reached end of data at row 11

============================================================
✅ Successfully loaded 9 annotations
⚠️  Skipped 0 rows
============================================================
```

## Manejo de errores

- **Archivo no encontrado**: Muestra el path que intentó abrir
- **Hoja no encontrada**: Lista las hojas disponibles
- **Fila inválida**: Salta la fila y continúa, mostrando por qué
- **Dato duplicado**: Salta y muestra que ya existe
- **Error de inserción**: Muestra el error de BD y continúa
