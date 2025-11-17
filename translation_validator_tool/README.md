# Translation Validator Tool — Guía rápida (README principal)

Resumen
- Herramienta para validar y sugerir traducciones Guaraní ↔ Español. La carpeta
  `translation_validator_tool/` contiene el backend (`api/`), frontend (`ui/`) y las
  migraciones (`db_schema/`).

Estructura recomendada de lectura
1. `translation_validator_tool/README.md` — guía principal del proyecto
2. `translation_validator_tool/api/README.md` — backend (detallado)
3. `translation_validator_tool/ui/README.md` — frontend (detallado)
4. `translation_validator_tool/db_schema/README.md` — migraciones y helpers

Quick start — pasos principales (Windows PowerShell / Linux bash)

1) Clonar el repositorio

Windows (PowerShell):
```powershell
git clone https://github.com/aalvarez-fiuni/guarani-corpus-lacuna-uni.git
cd guarani-corpus-lacuna-uni
git checkout translation-validator
cd translation_validator_tool
```

Linux / macOS (bash):
```bash
git clone https://github.com/aalvarez-fiuni/guarani-corpus-lacuna-uni.git
cd guarani-corpus-lacuna-uni
git checkout translation-validator
cd translation_validator_tool
```

2) Backend — crear y activar venv, instalar dependencias

Windows (PowerShell):
```powershell
cd api
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# editar api/.env -> DATABASE_URL, SECRET_KEY, CORS_ORIGINS
```

Linux / macOS (bash):
```bash
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# editar api/.env -> DATABASE_URL, SECRET_KEY, CORS_ORIGINS
```

3) Migraciones / inicialización (usar `db_schema`)

Recomendado: usar el helper `init_database.py` que automatiza creación de BD (si se
requiere) y aplica las tablas necesarias. Ejecuta el helper usando el Python del venv
del backend.

Windows (PowerShell):
```powershell
cd ..\db_schema
..\api\venv\Scripts\python.exe init_database.py init
```

Linux / macOS (bash):
```bash
cd ../db_schema
../api/venv/bin/python init_database.py init
```

Alternativa: aplicar migraciones con Alembic (ejecutar desde `db_schema`):

Windows (PowerShell):
```powershell
cd db_schema
..\api\venv\Scripts\python.exe -m alembic upgrade head
```

Linux / macOS (bash):
```bash
cd db_schema
../api/venv/bin/python -m alembic upgrade head
```

4) Frontend — instalar dependencias y ejecutar

Windows (PowerShell):
```powershell
cd ../ui
npm install
copy .env.example .env
npm run dev
```

Linux / macOS (bash):
```bash
cd ../ui
npm install
cp .env.example .env
npm run dev
```

5) Levantar backend (uvicorn)

Windows (PowerShell):
```powershell
cd ../api
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Linux / macOS (bash):
```bash
cd ../api
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Importar CSV de traducciones (opcional)

Coloca tu CSV en `data/translations.csv` y usa el script de carga del backend.

Windows (PowerShell):
```powershell
cd api
.\venv\Scripts\Activate.ps1
python -m app.scripts.load_corpus --file ..\..\data\translations.csv
```

Linux / macOS (bash):
```bash
cd api
source venv/bin/activate
python -m app.scripts.load_corpus --file ../../data/translations.csv
```

Notas rápidas
- No comitees `.env` ni `venv/`.
- Usa `db_schema/` para gestionar migraciones y mantener el historial con Alembic.
 
Importar corpus desde JSON / JSONL (nuevo)
---------------------------------------

Si tienes un corpus en formato JSON o JSONL con textos en guaraní puedes extraer oraciones y convertirlas a CSV con la herramienta incluida. La extracción respeta estas reglas:

- Se consideran oraciones los fragmentos que terminan en un punto '.' (se ignoran puntos suspensivos '...' y '…').
- Se filtran oraciones con más de N palabras (por defecto 30; palabra = token separado por espacios).
- Por cada item del JSON se extraen hasta M oraciones aleatorias (por defecto M = 50).
- El archivo JSON/JSONL NO debe subirse al repositorio (mantener localmente).

Ubicación y nombre del archivo JSON/JSONL
- **Dónde colocar:** en la carpeta `data/` del repositorio (raíz del proyecto).
- **Nombre recomendado:** cualquier nombre descriptivo con extensión `.json` o `.jsonl` (por ejemplo: `coreguapa_identified_gn.jsonl`, `mi_corpus_guarani.jsonl`).
- **Formato esperado:** cada línea (JSONL) o cada item del array (JSON) debe ser un objeto con al menos el campo `text` que contiene las oraciones en guaraní. Opcionalmente puede incluir metadatos: `corpus`, `corpus_file`, `source`, `url`, `language`.

Script extractor
- Ruta: `translation_validator_tool/scripts/extract_json_to_csv.py`
- Comportamiento por defecto: crea un CSV "append-only" (no modifica `data/translations.csv`) con las filas extraídas. Para incluir las filas originales en la salida usar `--include-original`. Para forzar sobreescritura usar `--force` (no recomendado).

Ejemplos (PowerShell):
```powershell
# Extraer desde un JSONL local y crear un CSV append-only (una sola línea)
python "translation_validator_tool\scripts\extract_json_to_csv.py" --input "data\coreguapa_identified_gn.jsonl" --out "data\coreguapa_appended_only.csv" --max-sentences 50 --max-words 30

# O multi-línea usando backtick ` para continuar:
python "translation_validator_tool\scripts\extract_json_to_csv.py" `
  --input "data\coreguapa_identified_gn.jsonl" `
  --out "data\coreguapa_appended_only.csv" `
  --max-sentences 50 --max-words 30

# Incluir además las filas originales del translations.csv en la salida (opt-in)
python "translation_validator_tool\scripts\extract_json_to_csv.py" --input "data\coreguapa_identified_gn.jsonl" --out "data\trans_with_coreguapa.csv" --include-original --max-sentences 50 --max-words 30
```

Ejemplos (bash):
```bash
# Extraer (JSONL -> CSV append-only)
python3 translation_validator_tool/scripts/extract_json_to_csv.py \
  --input data/coreguapa_identified_gn.jsonl \
  --out data/coreguapa_appended_only.csv \
  --max-sentences 50 --max-words 30
```

Notas del extractor
- Por defecto el script escribe solo las filas extraídas (archivo nuevo). Si quieres combinar con `data/translations.csv` usa `--include-original`.
- No comitees el JSON/JSONL de origen; guarda solo el CSV resultante si lo deseas.

Importar el CSV generado en la base de datos
-----------------------------------------

Una vez generado el CSV puedes importarlo en la base de datos usando el cargador del backend.

PowerShell (desde `translation_validator_tool/api` con el venv activado):
```powershell
cd translation_validator_tool\api
.\venv\Scripts\Activate.ps1
python -m app.scripts.load_corpus --file "..\..\data\coreguapa_appended_only.csv"
```

Bash:
```bash
cd translation_validator_tool/api
source venv/bin/activate
python -m app.scripts.load_corpus --file ../../data/coreguapa_appended_only.csv
```

Comportamiento del loader (resumen importante)
- Si una fila del CSV NO tiene texto en `spanish`, el loader creará UNA SOLA entrada con `direction = 'gn-sp'` (no crea la pareja inversa). Esto evita duplicados cuando importamos oraciones en guaraní sin traducción al español.
- Si la fila tiene ambos textos (`guarani` y `spanish`), el loader mantiene el comportamiento previo: crea/asegura la pareja (original + inversa) y repara registros con campos intercambiados.
- El loader intenta deduplicar antes de insertar; ejecutar repetidamente el mismo CSV no debería crear duplicados pero es buena práctica probar en una BD de staging primero.

Prodigy — Anotación Gramatical (POS Tagging)
-------------------------------------------

El proyecto incluye **Prodigy** (v1.18.3), una herramienta profesional de anotación desarrollada por Explosion AI para identificar categorías gramaticales en textos Guaraní.

**¿Qué hace Prodigy?**
Permite anotar manualmente categorías gramaticales (SUJETO, VERBO, OBJETO, SUSTANTIVO, ADJETIVO, etc.) en oraciones Guaraní. Esto genera datos de entrenamiento de alta calidad para análisis lingüístico y futuros modelos de ML.

**Características principales:**
- ✅ 10 categorías gramaticales predefinidas para Guaraní
- ✅ Interfaz web intuitiva con atajos de teclado
- ✅ Base de datos local (SQLite) - privacidad garantizada
- ✅ Exportación a JSONL/CSV para análisis posterior
- ✅ Integración opcional con PostgreSQL del proyecto

**Inicio rápido (Windows PowerShell):**
```powershell
# 1. Navegar al directorio Prodigy
cd translation_validator_tool\prodigy

# 2. Iniciar servidor de anotación (puerto 8081)
$env:PRODIGY_PORT=8081
python -m prodigy guarani-pos pos_guarani_new data/export/original_translations.jsonl -F recipes/guarani_pos_tagging.py

# 3. Abrir navegador en http://localhost:8081

# 4. Exportar anotaciones
python -m prodigy db-out pos_guarani_new > data/annotations/export_$(Get-Date -Format 'yyyyMMdd_HHmmss').jsonl
```

**Documentación completa:**
- `translation_validator_tool/prodigy/README.md` — guía completa de uso
- `translation_validator_tool/prodigy/POS_ANNOTATION_GUIDE.md` — guía detallada de categorías gramaticales

**Estado actual:** 🟢 Producción - 10 anotaciones completadas exitosamente

---

Archivos de referencia
- `translation_validator_tool/api/README.md` — instrucciones detalladas del backend
- `translation_validator_tool/ui/README.md` — instrucciones detalladas del frontend
- `translation_validator_tool/db_schema/README.md` — migraciones y helpers
- `translation_validator_tool/prodigy/README.md` — anotación gramatical con Prodigy

---
