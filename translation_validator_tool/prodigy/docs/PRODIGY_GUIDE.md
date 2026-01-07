Prodigy — Guía completa (secciones 2.1–2.10)

2.1 Introducción a Prodigy
--------------------------
Prodigy es una herramienta ligera y flexible para la anotación de datos supervisados. Fue diseñada para ser extensible vía "recipes" en Python y para integrarse bien en pipelines de NLP. En este proyecto usamos Prodigy para un flujo en tres etapas: POS → Features → Relations.

Por qué Prodigy aquí:
- Interfaces de anotación simples y directas.
- Sistema de sesiones que permite multi-anotador.
- Soporte para export/import vía CLI (`prodigy db-out`, `prodigy db-in`).

2.2 Requisitos y Configuración Inicial
--------------------------------------
Requisitos del Sistema
----------------------
| Componente | Requisito |
|---|---|
| Python | 3.10 o superior |
| Prodigy | Licencia válida instalada (prodigy disponible en el entorno) |
| PostgreSQL | Servicio en ejecución con los datos del corpus (opcional si se exporta a JSONL) |
| OpenAI API Key | Solo necesario para los modos OpenAI (opcional) |

Estructura de archivos (resumen relevante)
-----------------------------------------
```
translation_validator_tool/prodigy/
├── .env                              # Variables de entorno (NO commitear)
├── .env.example                      # Plantilla de variables
│
├── start_prodigy_spans_secure.ps1    # 🚀 Lanzador SPANS (recomendado)
├── start_prodigy_openai_secure.ps1   # 🚀 Lanzador OpenAI
├── start_prodigy_spans_secure.py     # Script Python SPANS
├── start_prodigy_openai_secure.py    # Script Python OpenAI
│
├── data/
│   ├── export/                       # Archivos JSONL para anotar
│   │   └── original_translations.jsonl
│   ├── examples/                     # Datos de ejemplo
│   └── openai_cache/                 # Cache de respuestas OpenAI
│
├── recipes/
│   ├── guarani_spans.py              # Recipes de anotación SPANS
│   └── guarani_openai.py             # Recipe con OpenAI
│
├── scripts/
│   ├── ud_guarani_mapper.py          # Mapeo etiquetas ↔ UD
│   ├── export_to_prodigy.py          # Exportar desde PostgreSQL
│   ├── export_to_json_with_iaa.py    # Exportar con métricas IAA
│   ├── calculate_iaa.py              # Calcular Cohen's Kappa
│   └── sync_prodigy_to_db.py         # Sincronizar con PostgreSQL
│
├── logs/                             # Logs de ejecución
└── resultados/                       # Exportaciones
```

Configuración del archivo `.env`
--------------------------------
1. Copiar `prodigy/.env.example` → `prodigy/.env` y completar las variables.

Variables relevantes (ejemplos):

```
# Puertos
PRODIGY_PORT=8080
PRODIGY_PROXY_PORT=8085

# Backend para autenticación
BACKEND_URL=http://localhost:8000

# OpenAI (solo para modo OpenAI)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Sesiones y validadores
PRODIGY_ALLOWED_SESSIONS="alice,bob,carlos,diana,elena,marcos,nicolas"
VALIDATORS_POS="alice,bob"
VALIDATORS_FEATURES="carlos,elena"
VALIDATORS_RELATIONS="marcos,nicolas"

# Batch monitor
BATCH_MONITOR_INTERVAL=60
REQUIRED_VALIDATORS=2
SENTENCES_PER_BATCH=50
TOTAL_BATCHES=60
```

Notas sobre `VALIDATORS_*`:
- Estas variables definen qué usuarios están permitidos para cada servicio (POS/Features/Relations).
- `prodigy_manager.py` lee estas listas y exporta `PRODIGY_ALLOWED_SESSIONS` al proceso Prodigy correspondiente para limitar sesiones.
- `batch_monitor.py` usa las mismas listas para contar sólo los validadores asignados a cada servicio.

Preparación de datos
--------------------
1. Exportar traducciones desde PostgreSQL (si corresponde) hacia JSONL:

```
cd translation_validator_tool/prodigy
python scripts/export_to_prodigy.py \
  --output data/export/original_translations.jsonl \
  --only-original \
  --limit 100
```

2. Verificar el archivo generado (PowerShell):

``powershell
Get-Content data/export/original_translations.jsonl -Head 3
```

Formato esperado (JSONL):

```json
{"text": "Che ahayhu nde", "meta": {"spanish_text": "Yo te amo", "id": 1}}
{"text": "Ha'e oguata", "meta": {"spanish_text": "Él camina", "id": 2}}
```

Generación de lotes
-------------------
Recomendado generar batches con `generate_batches.py`:

```
# Modo secuencial (mantiene orden original) - RECOMENDADO para preservar contexto
python scripts/generate_batches.py --total 3000 --batch-size 50
```

Instalación y dependencias
---------------------------
1. Crear y activar un entorno Python (3.10+):

```
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1   # PowerShell
```

2. Instalar dependencias:

```
pip install -r requirements.txt
pip install -r prodigy/requirements.txt  # si existe
```

3. Verificar que `prodigy` esté disponible:

```
python -m prodigy --help
```

Arranque recomendado
--------------------
- Para iniciar la plataforma completa (manager + servicios + monitor):

``powershell
.\\start_batch_auto.ps1
```

- Nota: `start_batch_auto.ps1` ahora ejecuta el `batch_monitor` en primer plano para garantizar que siempre veas su salida en la consola.

Diagnóstico rápido
------------------
- Si el monitor no avanza: revisar `data/batch_monitor_state.json` y los logs `prodigy/logs/prodigy_<service>.log`.
- Asegúrate que los usuarios accedan pasando `?session=<user>` en la URL del proxy para que `_session_id` sea mapeable (p.ej. `guarani_features_batch_003-carlos`).


2.3 Modos de Inicio
-------------------
Resumen de modos

| Modo | Script | Descripción | Cuándo usar |
|---|---:|---|---|
| SPANS Seguro | `start_prodigy_spans_secure.ps1` | Anotación manual completa con JWT | Anotación desde cero |
| OpenAI Seguro | `start_prodigy_openai_secure.ps1` | Pre-anotación automática con IA + corrección manual | Acelerar anotación morfológica |
| Relations Seguro | `start_prodigy_relations_secure.ps1` | Anotación de dependencias sintácticas | Análisis sintáctico UD |


Modo SPANS Seguro
------------------
El usuario anota desde cero, seleccionando texto y eligiendo etiquetas.

Iniciar con PowerShell:

```powershell
cd translation_validator_tool/prodigy
# Básico (todas las etiquetas, por caracter)
.\start_prodigy_spans_secure.ps1
# Con grupo específico
.\start_prodigy_spans_secure.ps1 -Group "pos-tags"
.\start_prodigy_spans_secure.ps1 -Group "morfemas"
.\start_prodigy_spans_secure.ps1 -Group "features-tam"
# Con dataset personalizado
.\start_prodigy_spans_secure.ps1 -Group "pos-tags" -Dataset "mi_dataset"
# Con archivo de datos específico
.\start_prodigy_spans_secure.ps1 -Group "morfemas" -Source "data/export/original_translations.jsonl"
# Tokenizar por PALABRA (en vez de caracter)
.\start_prodigy_spans_secure.ps1 -Group "pos-tags" -WordLevel
# Con límite de oraciones
.\start_prodigy_spans_secure.ps1 -Group "features" -Limit 50
# Ver grupos disponibles
.\start_prodigy_spans_secure.ps1 -ListGroups
```

Parámetros disponibles (SPANS)

| Parámetro | Descripción | Default |
|---|---|---:|
| `-Recipe` | Recipe a utilizar | `guarani-char-spans` |
| `-Dataset` | Nombre del dataset | `morfologia_guarani` |
| `-Source` | Archivo JSONL de entrada | `data/export/original_translations.jsonl` |
| `-Group` | Grupo de etiquetas | `Todas` |
| `-CharLevel` | Anotación por caracteres (false = word level posible) | `false` |
| `-Port` | Puerto del proxy | `8082` |


Modo OpenAI Seguro (Pre-anotación Automática)
--------------------------------------------
OpenAI analiza cada oración y genera spans automáticamente. El usuario corrige lo que esté mal.

Iniciar con PowerShell:

```powershell
cd translation_validator_tool/prodigy
# Básico (usa translations.csv automáticamente)
.\start_prodigy_openai_secure.ps1
# Con modelo específico
.\start_prodigy_openai_secure.ps1 -Model "gpt-4o"
# Con límite de oraciones
.\start_prodigy_openai_secure.ps1 -Limit 50
# Con grupo específico de etiquetas
.\start_prodigy_openai_secure.ps1 -Group "pos-tags"
.\start_prodigy_openai_secure.ps1 -Group "features"
.\start_prodigy_openai_secure.ps1 -Group "morfemas"
# Con sub-grupos específicos 
.\start_prodigy_openai_secure.ps1 -Group "features-persona-numero"
# Combinado
.\start_prodigy_openai_secure.ps1 -Model "gpt-4o-mini" -Limit 100 -Group "categorias"
```

Parámetros disponibles (OpenAI)

| Parámetro | Descripción | Default |
|---|---|---:|
| `-Dataset` | Nombre del dataset | `guarani_openai_secure` |
| `-Source` | Archivo JSONL (o usa translations.csv) | `Auto` |
| `-Model` | Modelo OpenAI | `gpt-4o-mini` |
| `-Port` | Puerto del proxy | `8082` |
| `-Limit` | Límite de oraciones | `100` |
| `-NoCache` | Desactivar cache de OpenAI | `false` |
| `-Group` | Grupo de etiquetas específico | `Todas` |


Modo Relations Seguro (Dependencias UD)
--------------------------------------

Iniciar con PowerShell:

```powershell
cd translation_validator_tool/prodigy
.\start_prodigy_relations_secure.ps1
.\start_prodigy_relations_secure.ps1 -Group "relations"
.\start_prodigy_relations_secure.ps1 -Limit 50
.\start_prodigy_relations_secure.ps1 -Group "relations" -Limit 100
```

Parámetros (Relations)

| Parámetro | Descripción | Default |
|---|---|---:|
| `-Dataset` | Nombre del dataset | `guarani_relations_secure` |
| `-Source` | Archivo JSONL | `Auto` |
| `-Port` | Proxy | `8082` |
| `-Limit` | Límite | `100` |
| `-Group` | Grupo UD | `relations` |

Controles de Relations

| Acción | Cómo hacerlo |
|---|---|
| Crear arco | Click palabra origen → click palabra destino |
| Eliminar arco | Click en el arco |
| Ver contexto | `Ctrl+Shift+C` o botón “Ver Contexto” |


Grupos de etiquetas disponibles
-----------------------------

| Grupo | Descripción | Color | Etiquetas |
|---|---|---:|---|
| `pos-tags` | POS Tags (UPOS) | 🔴 Rojo | 11 etiquetas |
| `features` | Rasgos morfológicos | 🟣 Violeta | 37 etiquetas |
| `relations` | Relaciones sintácticas | 🟢 Verde | 20 etiquetas |
| `morfemas` | Segmentación morfológica | 🔵 Azul | 3 etiquetas |

Subgrupos de Features (para anotación más específica)
- `--group features-persona-numero` — Persona, Número, Clusividad
- `--group features-caso` — Casos (Ablativo, Locativo, etc.)
- `--group features-tam` — Tiempo, Aspecto, Modo
- `--group features-relacional` — Prefijos relacionales
- `--group features-nominalizadores` — Nominalizadores
- `--group features-otros` — Otros features

POS Tags (ejemplos)

| Etiqueta | UD |
|---|---:|
| Posposición | ADP |
| Adverbio | ADV |
| Determinante | DET |
| Interjección | INTJ |
| Sustantivo | NOUN |
| Numeral | NUM |
| Partícula | PART |
| Pronombre | PRON |
| Nombre Propio | PROPN |
| Puntuación | PUNCT |
| Verbo | VERB |

Relations (ejemplos)

| Etiqueta | Código | Descripción |
|---|---:|---|
| RAÍZ | `root` | Núcleo |
| Sujeto | `nsubj` | Sujeto |
| Objeto | `obj` | Objeto directo |
| iobj | `iobj` | Objeto indirecto |
| obl | `obl` | Oblicuo |
| advmod | `advmod` | Modificador adverbial |
| nmod | `nmod` | Modificador nominal |
| det | `det` | Determinante |
| case | `case` | Marcador de caso |
| compound | `compound` | Compuesto |
| appos | `appos` | Aposición |

Morfemas (ejemplos)

| Etiqueta | Código |
|---|---:|
| Raíz | `Root` |
| Prefijo | `Prefix` |
| Sufijo | `Suffix` |

Features (ejemplos de subgrupos)

Persona y Número

| Etiqueta | UD |
|---|---:|
| 1º Persona | `Person=1` |
| 2º Persona | `Person=2` |
| 3º Persona | `Person=3` |
| Singular | `Number=Sing` |
| Plural | `Number=Plur` |
| Inclusivo | `Clusivity=In` |
| Exclusivo | `Clusivity=Ex` |

Caso (ejemplos)

| Etiqueta | UD |
|---|---:|
| Ablativo | `Case=Abl` |
| Alativo | `Case=All` |
| Dativo | `Case=Dat` |
| Locativo | `Case=Loc` |
| Referencial | `Case=Ref` |

TAM (ejemplos)

| Etiqueta | UD |
|---|---:|
| Pasado | `Tense=Past` |
| Futuro | `Tense=Fut` |
| Imperativo | `Mood=Imp` |
| Gerundio | `VerbForm=Ger` |

Por defecto: Anotación a nivel de CARÁCTER
Con `-WordLevel`: Tokenización por PALABRA
Ej: `.\\start_prodigy_spans_secure.ps1 -Group "pos-tags" -WordLevel`

2.4 Acceso a la Interfaz
------------------------
- UI principal (React): `http://localhost:5173`
- Prodigy Manager (proxy): `http://localhost:8085` — puerta de autenticación y proxy a instancias de Prodigy.
- Instancias directas de Prodigy:
  - POS: `http://localhost:8080`
  - Features: `http://localhost:8081`
  - Relations: `http://localhost:8082`

Sesión de usuario:
- Se pasa la sesión en la URL: `http://localhost:8085/?session=alice`.
- Es importante que la sesión incluya el nombre del validador usado en `VALIDATORS_*` para que el monitor lo identifique correctamente.

2.5 Prodigy con Login
---------------------
- El `prodigy_manager` valida tokens JWT contra el backend (`BACKEND_URL`) si el request incluye un token.
- También existe el token interno `internal-monitor` usado por el `batch_monitor` para llamadas internas.
- Recomendación: usar la UI del proyecto para login y obtener un token válido.

2.6 Etiquetas y Universal Dependencies
--------------------------------------
Este proyecto sigue esquema UD para POS, features y relaciones sintácticas. Las recipes definidas en `recipes/` generan las tareas con la estructura siguiente:
- POS: tokens y etiquetas POS
- Features: análisis morfológico por token
- Relations: dependencias entre tokens

Archivos importantes:
- `recipes/guarani_batch.py` — implementación del stream, manejo de exclusiones por sesión y políticas de IAA.

2.7 Sistema Multi-Anotador e IAA
--------------------------------
Diseño:
- Cada tarea puede ser vista por N anotadores (`ANNOTATIONS_PER_TASK` en `.env`).
- `SERVICE_VALIDATORS` controla qué usuarios pueden anotar en cada servicio.
- `batch_monitor` cuenta por `session_id` y decide completitud cuando al menos `REQUIRED_VALIDATORS` de los validadores asignados alcanzan `SENTENCES_PER_BATCH`.

Detalles de implementación:
- `prodigy_manager.py` pasa `PRODIGY_ALLOWED_SESSIONS` al proceso Prodigy para limitar sesiones visibles/permitidas.
- `batch_monitor.py` mapea `_session_id` a `user` para detectar completitud aunque el `session_id` incluya prefijos (p.ej. `guarani_features_batch_003-carlos`).

Recomendaciones para IAA:
- Mantener `ANNOTATIONS_PER_TASK >= 2` para obtener comparaciones entre anotadores.
- Recolectar export completo (`prodigy db-out dataset`) y usar `scripts/calculate_iaa.py` para métricas.

2.8 Exportación de Anotaciones
-----------------------------
Comandos útiles:
- Exportar un dataset: `python -m prodigy db-out <dataset>` (se usa en `batch_monitor` y `prodigy_manager`).
- Exportar todo: `prodigy db-out --all` (según versión de prodigy).
- Scripts de export en `scripts/` (p. ej. `export_to_prodigy.py`, `export_to_json_with_iaa.py`).

Formato: JSONL con campos `_session_id`, `_input_hash`, `answer`, etc.

2.9 Comandos Útiles de Prodigy
-----------------------------
- `python -m prodigy <recipe> <dataset> [SOURCE] -F recipe.py` — iniciar una sesión de anotación.
- `prodigy db-in <dataset> data.jsonl` — importar.
- `prodigy db-out <dataset> > output.jsonl` — exportar.
- `prodigy stats <dataset>` — estadísticas simples (según versión).

2.10 Flujo de Trabajo Completo
-----------------------------
1. Preparar datasets con `scripts/generate_batches.py` → `data/batches/batch_XXX.jsonl`.
2. Configurar `.env` con validadores y parámetros (batch interval, sentences per batch).
3. Iniciar sistema completo: `.












Uso: copiar/pegar en Confluence o en la carpeta `prodigy/docs/` para consulta interna.Generado: 2025-12-31---- Si el monitor no avanza: comprobar `data/batch_monitor_state.json` y los logs en `prodigy/logs/prodigy_<service>.log`.- Si un servicio aparece `[OFF]` en el monitor: verificar que `prodigy_manager` esté corriendo y que la instancia de Prodigy para ese puerto esté activa.----------------------------Apéndice - Diagnóstico rápido6. Exportar resultados y calcular IAA con `scripts/calculate_iaa.py`.5. El `batch_monitor` verifica progreso periódicamente y avanza automáticamente cuando los validadores asignados a un servicio cumplen `SENTENCES_PER_BATCH`.4. Los anotadores se conectan a través del proxy y pasan `?session=<user>`.un start_batch_auto.ps1` o `start_batch_auto.ps1`.