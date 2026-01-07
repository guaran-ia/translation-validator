# 📋 Informe de Avances - Semanas 4 y 5 (Diciembre 2025)

**Proyecto:** Sistema de Anotación Guaraní-Castellano  
**Período:** 22 de Diciembre 2025 - 31 de Diciembre 2025  
**Desarrollador:** Manuel

---

## 📅 Resumen Ejecutivo

Durante estas dos semanas se completaron las siguientes áreas principales:

1. ✅ **Sistema de Auto-Avance de Batches** - Completado
2. ✅ **Configuración de Buffer desde Admin** - Completado
3. ✅ **Asignación de Usuarios por Tipo de Validación** - Completado
4. ✅ **Documentación Completa del Sistema** - Completado (22 documentos)
5. ✅ **Scripts de Diagnóstico y Health Check** - Completado
6. ✅ **Corrección del Bug del Batch Monitor** - Completado

---

## 📆 Semana 4

### Lunes 22/12/25
**Reunión con Liz para revisión de avances del sistema de anotaciones**

#### Trabajo Realizado:

**Testing y Validación:**
- ✅ Se probaron todos los casos de cierre de navegador (con y sin aceptar)
- ✅ Se validó el comportamiento de guardado automático
- ✅ Se documentaron los edge cases encontrados
- ✅ Comportamiento verificado: el sistema guarda anotaciones cada N envíos (configurable)

**Batches Automáticos - Investigación y Desarrollo:**
- ✅ **Implementación de `batch_monitor.py`** - Script que:
  - Detecta cuando todos los anotadores terminan un batch mediante queries periódicas
  - Consulta la base de datos de Prodigy cada 10 segundos (configurable)
  - Inicia automáticamente el siguiente batch cuando se cumple el umbral
  - Almacena estado persistente en `data/batch_monitor_state.json`

```python
# Configuración del batch monitor (batch_monitor.py líneas 50-56)
BATCH_MONITOR_INTERVAL = int(os.getenv("BATCH_MONITOR_INTERVAL", "10"))
REQUIRED_VALIDATORS = int(os.getenv("REQUIRED_VALIDATORS", "3"))
SENTENCES_PER_BATCH = int(os.getenv("SENTENCES_PER_BATCH", "50"))
TOTAL_BATCHES = int(os.getenv("TOTAL_BATCHES", "60"))
```

**Estructura de Datos:**
- ✅ Se analizó la unificación de anotaciones (POS, Features, Relations)
- ✅ Cada tipo tiene su propio dataset en Prodigy: `guarani_pos_batch_XXX`, `guarani_features_batch_XXX`, `guarani_relations_batch_XXX`
- ✅ Se implementó exportación unificada a JSONL para visualizaciones agregadas

---

### Martes 23/12/25
**Desarrollo de Features Técnicas**

- ✅ Refactorización del sistema de logging para el batch monitor
- ✅ Implementación de colores en terminal para mejor visualización del progreso
- ✅ Creación de scripts PowerShell para automatizar el inicio del sistema

---

### Miércoles 24/12/25
**Preparación de Documentación**

- ✅ Inicio de la estructura de documentación en `/docs/confluence/`
- ✅ Creación del índice principal (00-Index.md)

---

### Jueves 25/12/25
**🎄 Navidad - Día no laborable**

---

### Viernes 26/12/25
**Reunión con Liz**

#### Testing / QA:
- ✅ Validación de todos los casos de prueba
- ✅ Confirmación del comportamiento en escenarios límite:
  - Cierre abrupto del navegador: las anotaciones se guardan cada N envíos
  - Pérdida de conexión: se recupera el estado al reconectar
  - Múltiples anotadores simultáneos: cada sesión es independiente

- ✅ **Verificación del auto-avance de batches:**
  - El sistema detecta correctamente cuando todos los validadores asignados completan 50 frases
  - El cambio de batch se dispara automáticamente

#### Documentación Creada:
- ✅ `docs/TESTING_PRODIGY_FAILURES.md` - Casos de prueba documentados
- ✅ `docs/COMMON_ERRORS.md` - Errores comunes y soluciones

---

## 📆 Semana 5

### Lunes 29/12/25
**Reunión con Liz y Aldo: resumen de avances**

#### Testing y Validación Exhaustiva:
- ✅ Auto-guardado verificado con diferentes configuraciones de buffer
- ✅ Cierre de navegador: sin pérdida de datos con buffer ≤ 3
- ✅ Pérdida de conexión: manejado correctamente
- ✅ Persistencia de sesión: verificada con tokens JWT de 24 horas

#### Buffer de Guardado - Implementado:

**API de Configuración** (prodigy_manager.py líneas 668-730):

```python
# Endpoint GET para obtener configuración actual
@app.get("/api/config/buffer")
async def get_buffer_config(request: Request):
    """Obtiene la configuración actual del buffer de anotaciones."""
    return {
        "config": buffer_config,
        "defaults": DEFAULT_BUFFER_CONFIG,
    }

# Endpoint POST para actualizar configuración
@app.post("/api/config/buffer")
async def set_buffer_config(request: Request):
    """Actualiza la configuración del buffer."""
    # Permite configurar:
    # - instant_submit: True/False (guardado instantáneo)
    # - batch_size: 1-10 (anotaciones antes de guardar)
```

**Configuración por Defecto:**
```python
DEFAULT_BUFFER_CONFIG = {
    "instant_submit": False,
    "batch_size": 3,  # Guarda cada 3 anotaciones
}
```

**Archivo de Configuración Persistente:**
- Ubicación: `data/prodigy_config.json`
- Se carga al iniciar el manager
- Se puede modificar vía API o editando el archivo directamente

#### Batch Monitor - Fix del Bug:
- ✅ **Problema:** El monitor dejaba de correr después de cierto tiempo
- ✅ **Solución:** Se implementó manejo robusto de excepciones y reconexión automática
- ✅ **Mejora:** Ahora el monitor se ejecuta en primer plano en `start_batch_auto.ps1` para ver el output siempre

#### Asignación de Usuarios por Tarea - Implementado:

**Configuración en `.env`:**
```bash
# Usuarios asignados a cada tipo de validación
VALIDATORS_POS=alice,bob,carlos
VALIDATORS_FEATURES=diana,elena
VALIDATORS_RELATIONS=gabriel,helena
```

**Implementación en código** (prodigy_manager.py líneas 76-91):
```python
def parse_validators_list(env_var: str, default: str) -> list:
    """Parsea una lista de validadores desde variable de entorno"""
    value = os.getenv(env_var, default).strip('"').strip("'")
    return [v.strip() for v in value.split(",") if v.strip()]

SERVICE_VALIDATORS = {
    "pos": parse_validators_list("VALIDATORS_POS", "alice,bob"),
    "features": parse_validators_list("VALIDATORS_FEATURES", "carlos,elena"),
    "relations": parse_validators_list("VALIDATORS_RELATIONS", "marcos,nicolas"),
}
```

**Monitoreo por Grupo** (batch_monitor.py líneas 220-270):
- Cada tipo de anotación rastrea solo sus validadores asignados
- El avance de batch es independiente por tipo (POS puede estar en batch 5, Features en batch 3)
- El monitor detecta correctamente el completado por grupo

---

### Martes 30/12/25
**Desarrollo de Scripts y Herramientas**

#### Scripts Creados:

1. **`start_batch_auto.ps1`** - Script principal de inicio
   - Inicia Prodigy Manager (puerto 8085)
   - Inicia los 3 servicios de Prodigy (POS:8080, Features:8081, Relations:8082)
   - Inicia Batch Monitor en primer plano
   - Carga el batch actual desde `data/batch_monitor_state.json`
   - Parámetros: `-Batch`, `-Validators`, `-Interval`, `-NoMonitor`

2. **`stop_batch_auto.ps1`** - Script de parada
   - Detiene todos los servicios vía API
   - Mata procesos de Python relacionados

3. **`health_check.py`** - Diagnóstico completo del sistema
   - Verifica Backend API, Prodigy interno, Proxy, Base de datos
   - Verifica archivos de datos y variables de entorno
   - Verifica recipes y paquetes Python
   - Genera reporte con ✅/❌/⚠️

4. **`scripts/prodigy_diagnostic.py`** - Diagnóstico rápido
   - Verifica manager y puertos
   - Lee estado de batches
   - Genera recomendaciones

---

### Miércoles 31/12/25
**Reunión con Liz y Aldo: Cierre y Nuevo Proyecto**

#### Estado Final del Proyecto Guaraní–Castellano:

| Componente | Estado |
|------------|--------|
| Configuración del buffer desde admin | ✅ Completado |
| Fix del batch monitor | ✅ Completado |
| Asignación de usuarios por tipo | ✅ Completado |
| Documentación completa | ✅ Completado |

---

## 📚 Documentación Creada

Se crearon **22 documentos** en `/docs/confluence/`:

| # | Documento | Descripción |
|---|-----------|-------------|
| 00 | Index.md | Índice principal con arquitectura del sistema |
| 01 | INTRODUCCION-ARQUITECTURA.md | Visión general y componentes |
| 02 | INSTALACION-SETUP.md | Guía de instalación |
| 03 | VARIABLES-ENTORNO.md | Configuración de .env |
| 04 | JWT-PROXY.md | Sistema de autenticación JWT |
| 05 | FLUJO-AUTENTICACION.md | Flujo de login y validación |
| 06 | RECIPE-BATCH.md | Recipe para anotación por lotes |
| 07 | RECIPE-SPANS.md | Recipe para spans morfológicos |
| 08 | RECIPE-RELATIONS.md | Recipe para relaciones sintácticas |
| 09 | RECIPE-OPENAI.md | Recipe con asistencia de OpenAI |
| 10 | SISTEMA-BATCHES.md | Sistema de 60 lotes × 50 oraciones |
| 11 | AUTO-ADVANCE.md | Auto-avance cuando todos completan |
| 12 | PRODIGY-MANAGER.md | Gestión centralizada de servicios |
| 13 | UD-MAPPER.md | Mapeo de etiquetas UD ↔ Amigables |
| 14 | ETIQUETAS-POS.md | Referencia de POS tags |
| 15 | ETIQUETAS-FEATURES.md | Referencia de features morfológicos |
| 16 | ETIQUETAS-RELATIONS.md | Referencia de relaciones sintácticas |
| 17 | SCRIPTS-GENERACION.md | Scripts para generar batches |
| 18 | SCRIPTS-EXPORTACION.md | Scripts para exportar anotaciones |
| 19 | CALCULO-IAA.md | Cálculo de acuerdo inter-anotador |
| 20 | INICIO-RAPIDO.md | Guía de inicio en 5 minutos |
| 21 | GUIA-ANOTADOR.md | Manual para anotadores |
| 22 | TROUBLESHOOTING.md | Solución de problemas comunes |

---

## 🏗️ Arquitectura Final del Sistema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ARQUITECTURA COMPLETA                             │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┐
  │   PostgreSQL    │  ← Corpus original (5234+ oraciones)
  │   (Backend DB)  │
  └────────┬────────┘
           │ GET /api/translations
           ▼
  ┌─────────────────┐
  │  Backend API    │  Puerto 8000
  │   (FastAPI)     │  Autenticación JWT, CRUD traducciones
  └────────┬────────┘
           │
           ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                      PRODIGY MANAGER                        │
  │                       Puerto 8085                           │
  │  ┌──────────────────────────────────────────────────────┐  │
  │  │  • Proxy JWT con validación                          │  │
  │  │  • API para iniciar/detener servicios                │  │
  │  │  • Configuración de buffer (GET/POST /api/config)    │  │
  │  │  • Rutas de progreso y estado                        │  │
  │  └──────────────────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────────────────┘
           │
           │  Inicia y gestiona
           ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │                         SERVICIOS PRODIGY                                 │
  │                                                                           │
  │   ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
  │   │   POS Tagging    │  │    Features      │  │   Relations      │       │
  │   │   Puerto 8080    │  │   Puerto 8081    │  │   Puerto 8082    │       │
  │   │                  │  │                  │  │                  │       │
  │   │ Validadores:     │  │ Validadores:     │  │ Validadores:     │       │
  │   │ VALIDATORS_POS   │  │ VALIDATORS_      │  │ VALIDATORS_      │       │
  │   │                  │  │ FEATURES         │  │ RELATIONS        │       │
  │   └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘       │
  │            │                     │                     │                 │
  └────────────┼─────────────────────┼─────────────────────┼─────────────────┘
               │                     │                     │
               └──────────────┬──────┴──────────────┬──────┘
                              │                     │
                              ▼                     ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │                        BATCH MONITOR                                      │
  │                                                                           │
  │   • Chequea progreso cada 10 segundos                                    │
  │   • Detecta cuando TODOS los validadores asignados completan             │
  │   • Inicia automáticamente el siguiente batch                            │
  │   • Estado persistente en data/batch_monitor_state.json                  │
  │   • Monitoreo independiente por tipo (POS/Features/Relations)            │
  │                                                                           │
  └───────────────────────────────────────────────────────────────────────────┘
               │
               ▼
  ┌─────────────────┐
  │  SQLite         │  ~/.prodigy/prodigy.db
  │ (Prodigy DB)    │  Anotaciones por dataset
  └────────┬────────┘
           │
           │  Scripts de exportación
           ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                      RESULTADOS                             │
  │  • Gold Standard (JSONL con consenso)                       │
  │  • Reportes IAA (Markdown)                                  │
  │  • Dataset UD (CoNLL-U)                                     │
  └─────────────────────────────────────────────────────────────┘
```

---

## 📊 Métricas del Proyecto

| Métrica | Valor |
|---------|-------|
| Archivos Python nuevos/modificados | 8+ |
| Scripts PowerShell creados | 4 |
| Documentos de documentación | 22 |
| Líneas de código agregadas | ~5,000+ |
| Endpoints API nuevos | 6 |
| Servicios gestionados | 4 (Manager + 3 Prodigy) |

---

## ✅ Tareas Completadas

1. [x] Testing y validación de todos los casos
2. [x] Sistema de batches automáticos
3. [x] Buffer de guardado configurable desde admin
4. [x] Fix del bug del batch monitor
5. [x] Asignación de usuarios por tipo de validación
6. [x] Documentación completa
7. [x] Scripts de inicio y parada
8. [x] Health check y diagnóstico

---

## 📎 Archivos Clave Creados/Modificados

### Scripts PowerShell:
- `start_batch_auto.ps1` - Inicio completo del sistema
- `stop_batch_auto.ps1` - Parada del sistema
- `start_batch_all.ps1` - Inicio alternativo

### Scripts Python:
- `batch_monitor.py` - Monitor de auto-avance
- `prodigy_manager.py` - Manager con API de buffer
- `health_check.py` - Diagnóstico del sistema
- `scripts/prodigy_diagnostic.py` - Diagnóstico rápido

### Configuración:
- `.env` - Variables de entorno (VALIDATORS_POS, etc.)
- `data/prodigy_config.json` - Configuración del buffer
- `data/batch_monitor_state.json` - Estado de batches

### Documentación:
- 22 archivos en `/docs/confluence/`

---

## 🚀 Preparación para Explicar a Aldo

El sistema está listo para demostración con los siguientes puntos clave:

1. **Inicio Simple:** `.\start_batch_auto.ps1`
2. **Auto-avance:** Los batches avanzan automáticamente
3. **Usuarios Separados:** Cada tipo de anotación tiene sus propios validadores
4. **Buffer Configurable:** Se puede cambiar desde API o archivo
5. **Documentación:** 22 documentos que cubren todo el sistema
6. **Diagnóstico:** `python health_check.py` para verificar estado

---

*Documento generado el 5 de Enero 2026*
*Período cubierto: 22/12/25 - 31/12/25*
