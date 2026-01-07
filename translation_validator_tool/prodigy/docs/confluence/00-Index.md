# 📚 Documentación del Sistema de Anotación Guaraní - Prodigy

**Versión:** 1.0  
**Última actualización:** Enero 2025  
**Proyecto:** Guaraní Corpus Lacuna - Herramienta de Validación de Traducciones

---

## 📖 Índice de Documentación

Esta documentación cubre todos los aspectos del sistema de anotación Prodigy para el corpus Guaraní.

### 🏗️ Arquitectura y Configuración

| # | Documento | Descripción |
|---|-----------|-------------|
| 01 | [Introducción y Arquitectura](01-INTRODUCCION-ARQUITECTURA.md) | Visión general del sistema, componentes y flujo de datos |
| 02 | [Instalación y Setup](02-INSTALACION-SETUP.md) | Requisitos, instalación de dependencias y configuración inicial |
| 03 | [Variables de Entorno](03-VARIABLES-ENTORNO.md) | Configuración del archivo `.env` y parámetros del sistema |

### 🔐 Autenticación y Proxy

| # | Documento | Descripción |
|---|-----------|-------------|
| 04 | [JWT Proxy (Puerto 8085)](04-JWT-PROXY.md) | Servidor proxy con autenticación JWT, endpoints API |
| 05 | [Flujo de Autenticación](05-FLUJO-AUTENTICACION.md) | Cómo funciona la autenticación desde el frontend hasta Prodigy |

### 🍳 Recipes de Prodigy

| # | Documento | Descripción |
|---|-----------|-------------|
| 06 | [guarani-batch (POS/Features/Relations)](06-RECIPE-BATCH.md) | Recipe principal para anotación por lotes |
| 07 | [guarani-spans (Manual)](07-RECIPE-SPANS.md) | Anotación manual de spans con overlapping |
| 08 | [guarani-relations (Sintaxis)](08-RECIPE-RELATIONS.md) | Anotación de relaciones sintácticas |
| 09 | [guarani-openai (IA Asistida)](09-RECIPE-OPENAI.md) | Pre-anotación automática con OpenAI |

### 📦 Sistema de Lotes

| # | Documento | Descripción |
|---|-----------|-------------|
| 10 | [Sistema de Batches](10-SISTEMA-BATCHES.md) | Generación, estructura y gestión de lotes |
| 11 | [Auto-Advance (batch_monitor)](11-AUTO-ADVANCE.md) | Sistema automático de avance de lotes |
| 12 | [Prodigy Manager](12-PRODIGY-MANAGER.md) | Gestión unificada de servicios Prodigy |

### 🏷️ Etiquetas y Mapeo

| # | Documento | Descripción |
|---|-----------|-------------|
| 13 | [Universal Dependencies Mapper](13-UD-MAPPER.md) | Mapeo entre etiquetas amigables y códigos UD |
| 14 | [Etiquetas POS](14-ETIQUETAS-POS.md) | Categorías gramaticales (NOUN, VERB, etc.) |
| 15 | [Etiquetas Features](15-ETIQUETAS-FEATURES.md) | Características morfológicas |
| 16 | [Etiquetas Relations](16-ETIQUETAS-RELATIONS.md) | Relaciones sintácticas |

### 🛠️ Scripts de Utilidad

| # | Documento | Descripción |
|---|-----------|-------------|
| 17 | [Scripts de Generación](17-SCRIPTS-GENERACION.md) | generate_batches.py, export scripts |
| 18 | [Scripts de Exportación](18-SCRIPTS-EXPORTACION.md) | Exportar anotaciones con IAA |
| 19 | [Cálculo de IAA](19-CALCULO-IAA.md) | Inter-Annotator Agreement |

### 🚀 Guías de Uso

| # | Documento | Descripción |
|---|-----------|-------------|
| 20 | [Inicio Rápido](20-INICIO-RAPIDO.md) | Pasos para iniciar el sistema en minutos |
| 21 | [Guía del Anotador](21-GUIA-ANOTADOR.md) | Instrucciones para anotadores |
| 22 | [Troubleshooting](22-TROUBLESHOOTING.md) | Solución de problemas comunes |

---

## 🗺️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FLUJO DE DATOS COMPLETO                             │
└─────────────────────────────────────────────────────────────────────────────┘

        ┌─────────────────┐
        │  PostgreSQL DB  │  ← Corpus original de traducciones
        │  (Backend API)  │
        └────────┬────────┘
                 │ export_to_prodigy.py
                 ▼
        ┌─────────────────┐
        │   JSONL Files   │  ← data/export/original_translations.jsonl
        └────────┬────────┘
                 │ generate_batches.py
                 ▼
        ┌─────────────────┐
        │  Batch Files    │  ← data/batches/batch_001.jsonl ... batch_060.jsonl
        │  (60 × 50 = 3000)│
        └────────┬────────┘
                 │
┌────────────────┴────────────────────────────────────────────────────────────┐
│                         FRONTEND UI (Puerto 5173)                           │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  React + Vite │ Login → Dashboard → Selección de Anotación          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└────────────────┬────────────────────────────────────────────────────────────┘
                 │ Autenticación
                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      BACKEND API (Puerto 8000)                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  FastAPI │ /api/auth/login → JWT Token │ /api/users │ PostgreSQL    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└────────────────┬────────────────────────────────────────────────────────────┘
                 │ Token JWT
                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PROXY JWT (Puerto 8085)                                │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  prodigy_manager.py                                                 │    │
│  │  - Valida token JWT contra Backend API (/api/auth/me)               │    │
│  │  - Gestiona cookies de sesión                                       │    │
│  │  - Reenvía requests a Prodigy interno                               │    │
│  │  - API: /api/status, /api/types, /api/start-prodigy                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└────────────────┬────────────────────────────────────────────────────────────┘
                 │
     ┌───────────┼───────────┬───────────────────┐
     │           │           │                   │
     ▼           ▼           ▼                   ▼
┌─────────┐ ┌─────────┐ ┌─────────┐      ┌─────────────┐
│ PRODIGY │ │ PRODIGY │ │ PRODIGY │      │   BATCH     │
│   POS   │ │FEATURES │ │RELATIONS│      │  MONITOR    │
│  8080   │ │  8081   │ │  8082   │      │ Auto-advance│
└────┬────┘ └────┬────┘ └────┬────┘      └─────────────┘
     │           │           │
     │    ┌──────┴──────┐    │
     └────┤   RECIPES   ├────┘
          └──────┬──────┘
                 │
┌────────────────┴────────────────────────────────────────────────────────────┐
│                    RECIPES DE ANOTACIÓN                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │ guarani-batch    │  │ guarani-spans    │  │ guarani-openai   │          │
│  │ (POS/Features)   │  │ (Manual spans)   │  │ (IA asistida)    │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │ guarani-relations│  │ Validaciones en  │  │ Task Router      │          │
│  │ (Sintaxis)       │  │ tiempo real      │  │ (Multi-anotador) │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
└────────────────┬────────────────────────────────────────────────────────────┘
                 │
    ┌────────────┼────────────┬────────────┐
    ▼            ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
│ alice  │  │  bob   │  │ carlos │  │ elena  │
│Session │  │Session │  │Session │  │Session │
└────────┘  └────────┘  └────────┘  └────────┘
    │            │            │            │
    └────────────┴────────────┴────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Prodigy SQLite DB                                        │
│         (~/.prodigy/prodigy.db o ubicación configurada)                     │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────────────────┐              │
│  │ Anotaciones  │ │   Sessions   │ │  Hashes (dedup)        │              │
│  │ (spans,rels) │ │ (por usuario)│ │  (evita duplicados)    │              │
│  └──────────────┘ └──────────────┘ └────────────────────────┘              │
└────────────────┬────────────────────────────────────────────────────────────┘
                 │ prodigy db-out / export scripts
                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EXPORTACIÓN Y ANÁLISIS                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │ export_to_json   │  │ calculate_iaa.py │  │ convert_pos_     │          │
│  │ _with_iaa.py     │  │ (Cohen's Kappa)  │  │ tags.py (→UD)    │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
└────────────────┬────────────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RESULTADOS FINALES                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │ Gold Standard    │  │ Reportes IAA     │  │ Dataset UD       │          │
│  │ Dataset          │  │ (Markdown)       │  │ (CoNLL-U)        │          │
│  │ (Consenso)       │  │ reports/*.md     │  │ (Training NLP)   │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔌 Componentes Principales

| Componente | Puerto | Descripción |
|------------|--------|-------------|
| **Frontend UI** | 5173 | Aplicación React (Vite) - Login y Dashboard |
| **Backend API** | 8000 | FastAPI - Autenticación JWT, PostgreSQL |
| **JWT Proxy** | 8085 | prodigy_manager.py - Valida tokens y gestiona servicios |
| **Prodigy POS** | 8080 | Anotación de categorías gramaticales |
| **Prodigy Features** | 8081 | Anotación de características morfológicas |
| **Prodigy Relations** | 8082 | Anotación de relaciones sintácticas |
| **Batch Monitor** | - | Auto-avance de lotes cuando se completan |

---

## 📊 Flujo de Datos Resumido

```
PostgreSQL → JSONL → Batches → Prodigy → SQLite → Export → Gold Standard
     ↓          ↓        ↓         ↓         ↓        ↓          ↓
  Corpus    Formato   60×50    Anotación  Almacén  IAA+UD    Dataset
  Original  Prodigy   Lotes    Multi-user  Local   Métricas  Final
```

---

## 🚀 Inicio Rápido

```powershell
# 1. Navegar al directorio
cd translation_validator_tool/prodigy

# 2. Activar entorno virtual
.\venv\Scripts\Activate.ps1

# 3. Copiar y configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# 4. Iniciar el sistema completo
.\start_batch_all.ps1

# 5. Acceder a la UI
# Frontend: http://localhost:5173
# Prodigy (via proxy): http://localhost:8085
```

---

## 📝 Convenciones de Documentación

- **Código:** Se muestran ejemplos reales del proyecto
- **Puertos:** Siempre se especifica el puerto de cada servicio
- **Etiquetas:** Se usa el formato `Etiqueta Amigable` → `codigo_ud`
- **Rutas:** Relativas al directorio `prodigy/`

---

## 🔗 Enlaces Útiles

- [Universal Dependencies - Old Guaraní](https://universaldependencies.org/treebanks/gn_oldtudet/index.html)
- [Prodigy Documentation](https://prodi.gy/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

---

*Documentación generada para el proyecto Guaraní Corpus Lacuna*
