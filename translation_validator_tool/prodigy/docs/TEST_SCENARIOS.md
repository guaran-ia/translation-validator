# 🧪 Guía Completa de Pruebas - Escenarios para Usuario Inexperto

> **Última actualización:** 29 de diciembre, 2025  
> **Versión:** 1.0  
> **Objetivo:** Documentar TODOS los escenarios posibles de fallo y comportamiento esperado en Prodigy

---

## 📋 Índice

1. [Escenarios de Navegador](#1-escenarios-de-navegador)
2. [Escenarios de Conexión](#2-escenarios-de-conexión)
3. [Escenarios de Autenticación](#3-escenarios-de-autenticación)
4. [Escenarios de Sesión](#4-escenarios-de-sesión)
5. [Escenarios de Anotación](#5-escenarios-de-anotación)
6. [Escenarios de Datos](#6-escenarios-de-datos)
7. [Escenarios de Sistema](#7-escenarios-de-sistema)
8. [Escenarios de Batch Monitor](#8-escenarios-de-batch-monitor)
9. [Escenarios de Servicios Backend](#9-escenarios-de-servicios-backend)
10. [Escenarios Multi-Usuario](#10-escenarios-multi-usuario)
11. [Edge Cases y Comportamientos Extraños](#11-edge-cases)
12. [Checklist de Pruebas](#12-checklist)

---

## 1. 🌐 Escenarios de Navegador

### 1.1 Cierre de Navegador

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Cerrar pestaña durante anotación | Cerrar la pestaña mientras se anota | Anotación actual se PIERDE si no se guardó | | ⏳ |
| Cerrar navegador completo | Cerrar todo el navegador | Las anotaciones guardadas persisten en DB | | ⏳ |
| Cerrar pestaña justo después de "Accept" | Cerrar inmediatamente tras clic | Puede perderse si no hubo sync | | ⏳ |
| Cierre accidental (Alt+F4) | Cerrar con atajo de teclado | Mismo efecto que cerrar ventana | | ⏳ |

**QUÉ VERIFICAR:**
- [ ] ¿Las anotaciones guardadas persisten después de cerrar?
- [ ] ¿Se pierde la anotación en progreso (sin guardar)?
- [ ] ¿El progreso se mantiene al reabrir?
- [ ] ¿La sesión del usuario sigue siendo válida?

### 1.2 Recargar Página (F5 / Ctrl+R)

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Recargar durante anotación | F5 mientras se selecciona texto | Se pierde selección actual | | ⏳ |
| Recargar después de Accept | F5 tras guardar | Muestra siguiente frase | | ⏳ |
| Recargar sin token en URL | F5 sin ?token= | Debería pedir re-autenticación | | ⏳ |
| Recargar con token expirado | F5 después de horas | Error 401, redirect a login | | ⏳ |
| Spam de recarga rápida | F5 múltiples veces seguidas | Posible bloqueo temporal | | ⏳ |

**QUÉ VERIFICAR:**
- [ ] ¿Se mantiene el progreso del batch?
- [ ] ¿El contador de anotaciones es correcto?
- [ ] ¿Se carga la frase correcta (no repetida)?
- [ ] ¿El token JWT sigue válido?

### 1.3 Navegación con Botones Atrás/Adelante

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Botón "Atrás" del navegador | Clic en flecha atrás | Puede salir de Prodigy | | ⏳ |
| Botón "Adelante" después de atrás | Clic en flecha adelante | Volver a Prodigy | | ⏳ |
| Atrás durante anotación | Atrás con frase a medio anotar | Anotación actual se pierde | | ⏳ |
| Navegar a otra página y volver | Ir a Google y volver con Atrás | Puede requerir re-login | | ⏳ |

### 1.4 Múltiples Pestañas/Ventanas

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Abrir misma URL en 2 pestañas | Duplicar pestaña | ⚠️ Conflictos de sesión | | ⏳ |
| Anotar misma frase en 2 pestañas | Submit en ambas | Duplicación de datos | | ⏳ |
| Diferentes usuarios, mismo navegador | Login como alice, luego bob | Cookies pueden mezclarse | | ⏳ |
| Ventana incógnito + normal | Abrir en modo incógnito | Sesiones separadas (correcto) | | ⏳ |

---

## 2. 📡 Escenarios de Conexión

### 2.1 Pérdida de Internet

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Desconectar WiFi durante anotación | Apagar WiFi mientras se anota | Error de red al guardar | | ⏳ |
| Reconectar después de pérdida | Volver a conectar WiFi | ¿Reintenta automático? | | ⏳ |
| Anotación offline | Anotar sin internet | Falla silenciosa o ruidosa | | ⏳ |
| Internet intermitente | Conexión que se corta y vuelve | Posibles datos inconsistentes | | ⏳ |
| VPN desconectado | VPN cae mientras se trabaja | Depende de configuración | | ⏳ |

**QUÉ VERIFICAR:**
- [ ] ¿Hay mensaje de error claro?
- [ ] ¿Se guarda localmente como backup?
- [ ] ¿Se reintenta automáticamente?
- [ ] ¿El usuario sabe qué hacer?

### 2.2 Conexión Lenta

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Latencia alta (>5 segundos) | Anotar con internet lento | UI debe mostrar "Guardando..." | | ⏳ |
| Timeout de request | Petición tarda >30s | Error de timeout | | ⏳ |
| Doble clic por impaciencia | Clic múltiples veces en Accept | ¿Duplica la anotación? | | ⏳ |
| Carga lenta de página | Internet lento al cargar | Mostrar indicador de carga | | ⏳ |

### 2.3 Servidor Caído

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Backend API caído | Apagar uvicorn | Error 502/503, mensaje claro | | ⏳ |
| Prodigy interno caído | Matar proceso de Prodigy | Error 502, mensaje de mantenimiento | | ⏳ |
| Proxy caído (puerto 8085) | Matar prodigy_manager | No carga nada | | ⏳ |
| Base de datos caída | SQLite bloqueado/corrupto | Error interno 500 | | ⏳ |

---

## 3. 🔐 Escenarios de Autenticación

### 3.1 Token JWT

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Sin token en URL | Acceder sin ?token= | Página "Acceso Restringido" | | ⏳ |
| Token inválido | ?token=abc123 | Error 401, redirect a login | | ⏳ |
| Token expirado | Token de hace 8+ horas | Error 401, debe re-loguearse | | ⏳ |
| Token de otro usuario | Usar token de Alice siendo Bob | Debería fallar validación | | ⏳ |
| Token malformado | ?token=not.valid.jwt | Error de formato | | ⏳ |
| Token con caracteres especiales | Token con / o + en URL | Encoding issues | | ⏳ |
| Token muy largo | Token extremadamente largo | Posible truncamiento | | ⏳ |

### 3.2 Sesión y Cookies

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Cookie borrada manualmente | Borrar cookies del navegador | Debe re-autenticarse | | ⏳ |
| Cookie de sesión antigua | Cookie de sesión anterior | Debe validar token de nuevo | | ⏳ |
| Navegador bloquea cookies | Configuración anti-tracking | ⚠️ No funciona correctamente | | ⏳ |
| Cambiar de navegador | De Chrome a Firefox | Nueva sesión requerida | | ⏳ |

### 3.3 Intentos de Bypass

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Acceso directo a Prodigy interno | http://localhost:8080 | ⚠️ Debe estar bloqueado | | ⏳ |
| Usar ?session=alice sin token | Parámetro legacy | No debe dar acceso | | ⏳ |
| Manipular cookie manualmente | Editar cookie en DevTools | Debe fallar validación | | ⏳ |
| Inyección en token | Token con SQL/XSS | Debe sanitizarse | | ⏳ |

---

## 4. 👤 Escenarios de Sesión

### 4.1 Gestión de Usuarios

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Usuario sin permisos de anotador | Login con cuenta sin rol | Error o acceso de solo lectura | | ⏳ |
| Usuario deshabilitado | Cuenta desactivada | Error 403 | | ⏳ |
| Usuario eliminado después de login | Admin borra cuenta mientras trabaja | Siguiente acción falla | | ⏳ |
| Cambio de contraseña | Admin cambia contraseña | Token debería invalidarse | | ⏳ |
| Sesión duplicada | Mismo usuario en 2 dispositivos | Ambos deberían funcionar | | ⏳ |

### 4.2 Sesiones de Prodigy

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Session ID correcto | alice, bob, carlos, etc. | Progreso separado por sesión | | ⏳ |
| Session ID inventado | ?session=hacker123 | Debería rechazarse | | ⏳ |
| Sin session ID | No enviar session | Usar default o username | | ⏳ |
| Session ID con caracteres especiales | ?session=user<script> | Debe sanitizarse | | ⏳ |

---

## 5. ✏️ Escenarios de Anotación

### 5.1 Selección de Texto

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Selección vacía | Clic sin seleccionar texto | Mostrar advertencia | | ⏳ |
| Selección de un solo carácter | Seleccionar "a" | Permitir (útil en guaraní) | | ⏳ |
| Selección de toda la frase | Ctrl+A | Crear span de todo | | ⏳ |
| Selección inversa (derecha a izquierda) | Arrastrar al revés | Debe funcionar igual | | ⏳ |
| Doble clic en palabra | Doble clic | Seleccionar palabra completa | | ⏳ |
| Triple clic | Triple clic | Seleccionar línea/párrafo | | ⏳ |
| Selección con Shift+Click | Shift + clic | Extender selección | | ⏳ |

### 5.2 Etiquetado

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Sin seleccionar etiqueta | Accept sin elegir label | Advertencia o bloqueo | | ⏳ |
| Múltiples etiquetas en mismo span | Superponer etiquetas | Permitido (overlapping) | | ⏳ |
| Etiqueta incorrecta aplicada | Error del anotador | Debe poder deshacer | | ⏳ |
| Cambiar etiqueta después de aplicar | Querer corregir | Debe poder modificar | | ⏳ |
| Borrar etiqueta | Quitar span aplicado | Clic en X del span | | ⏳ |

### 5.3 Botones de Acción

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Accept sin anotaciones | Accept con 0 spans | ¿Guardar vacío o advertir? | | ⏳ |
| Reject | Marcar como malo | Guardar con answer=reject | | ⏳ |
| Ignore | Saltar frase | Guardar con answer=ignore | | ⏳ |
| Undo después de Accept | Querer volver atrás | Funciona si hay historial | | ⏳ |
| Doble clic en Accept | Clic rápido 2 veces | No debe duplicar | | ⏳ |
| Spam de clicks | Muchos clicks seguidos | Rate limiting | | ⏳ |

### 5.4 Atajos de Teclado

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Enter para Accept | Presionar Enter | Guardar y siguiente | | ⏳ |
| Esc para limpiar | Presionar Escape | Limpiar selección | | ⏳ |
| Ctrl+Z para deshacer | Ctrl+Z | Deshacer último span | | ⏳ |
| Números para etiquetas | 1, 2, 3... | Seleccionar etiqueta N | | ⏳ |
| Ctrl+Shift+C para contexto | Atajo de contexto | Abrir diálogo de contexto | | ⏳ |
| Tab para navegar | Tab entre elementos | Navegación accesible | | ⏳ |

### 5.5 Texto Problemático

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Texto con emojis | 😀 en el texto | Manejar correctamente | | ⏳ |
| Texto con caracteres guaraní | ã, ẽ, ỹ, g̃ | ✅ Debe funcionar | | ⏳ |
| Texto muy largo | Frase de 1000+ caracteres | Scroll o wrap correcto | | ⏳ |
| Texto vacío | Frase vacía "" | Saltar o advertir | | ⏳ |
| Solo espacios | "   " | Saltar o advertir | | ⏳ |
| Caracteres especiales | <>&"' etc. | Escapar HTML correctamente | | ⏳ |
| Unicode inusual | Caracteres raros | No romper UI | | ⏳ |
| RTL (derecha a izquierda) | Texto árabe/hebreo | Renderizado correcto | | ⏳ |

---

## 6. 📁 Escenarios de Datos

### 6.1 Archivos de Entrada

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Archivo JSONL no existe | Ruta incorrecta | Error claro al iniciar | | ⏳ |
| Archivo JSONL vacío | 0 líneas | Mensaje "sin datos" | | ⏳ |
| Archivo JSONL corrupto | JSON malformado | Error de parsing | | ⏳ |
| Archivo muy grande | 1M+ líneas | Carga lenta pero funciona | | ⏳ |
| Archivo sin permisos | Sin acceso de lectura | Error de permisos | | ⏳ |
| Archivo en uso por otro proceso | Bloqueado | Error de acceso | | ⏳ |
| Encoding incorrecto | UTF-16 en vez de UTF-8 | Caracteres rotos | | ⏳ |

### 6.2 Base de Datos Prodigy

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| DB no existe | Primera ejecución | Crear automáticamente | | ⏳ |
| DB corrupta | prodigy.db dañado | Error al iniciar | | ⏳ |
| DB bloqueada | Otro proceso usa DB | Error de lock | | ⏳ |
| Disco lleno | Sin espacio | Error al guardar | | ⏳ |
| Permisos incorrectos | Sin write access | Error de escritura | | ⏳ |
| Dataset duplicado | Mismo nombre ya existe | Agregar a existente | | ⏳ |

### 6.3 Exportación

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Exportar dataset vacío | db-out de dataset sin datos | Archivo vacío o error | | ⏳ |
| Exportar dataset inexistente | db-out de nombre malo | Error "dataset not found" | | ⏳ |
| Conflicto de escritura | Exportar a archivo en uso | Error de acceso | | ⏳ |
| Exportar durante anotación | Mientras alguien anota | Datos parciales | | ⏳ |

---

## 7. 💻 Escenarios de Sistema

### 7.1 Recursos del Sistema

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| RAM insuficiente | Sistema con poca memoria | Lentitud o crash | | ⏳ |
| CPU al 100% | Proceso pesado en background | Lentitud de respuesta | | ⏳ |
| Disco lleno | Sin espacio libre | Error al guardar | | ⏳ |
| Muchos procesos abiertos | Sistema sobrecargado | Timeouts | | ⏳ |

### 7.2 Puertos

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Puerto 8080 ocupado | Otro servicio en 8080 | Error "port in use" | | ⏳ |
| Puerto 8085 ocupado | Proxy no puede iniciar | Error claro | | ⏳ |
| Puerto 8000 ocupado | Backend no puede iniciar | Error en API | | ⏳ |
| Firewall bloquea puerto | Reglas de firewall | Conexión rechazada | | ⏳ |
| Puerto < 1024 (privilegiado) | Intentar usar puerto 80 | Error de permisos | | ⏳ |

### 7.3 Procesos

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Matar proceso Prodigy | kill del proceso | Proxy detecta y notifica | | ⏳ |
| Reiniciar máquina | Reboot inesperado | Estado persistente en DB | | ⏳ |
| Suspender computadora | Laptop en sleep | ¿Reconecta al despertar? | | ⏳ |
| Crash de Python | Error no manejado | Logs en archivo | | ⏳ |

### 7.4 Variables de Entorno

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| .env no existe | Sin archivo .env | Usar defaults | | ⏳ |
| Variable malformada | PRODIGY_PORT=abc | Error o default | | ⏳ |
| Variable vacía | PRODIGY_PORT= | Error o default | | ⏳ |
| Variable con espacios | PRODIGY_PORT= 8080 | Trim o error | | ⏳ |

---

## 8. 🔄 Escenarios de Batch Monitor

### 8.1 Progreso de Batches

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| 0 anotadores activos | Nadie trabaja | Monitor espera | | ⏳ |
| 1 de 3 anotadores completa | Solo alice termina | Espera a otros 2 | | ⏳ |
| Todos completan batch | 3 de 3 terminan | Auto-avanza a siguiente | | ⏳ |
| Anotador se salta frases (ignore) | Muchos ignore | ¿Cuenta como completo? | | ⏳ |
| Más de 50 anotaciones | Anotador hace 60 | OK, solo necesita 50 | | ⏳ |
| Menos de 50 anotaciones | Solo 30 de 50 | No avanza hasta 50 | | ⏳ |

### 8.2 Estado Persistente

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Reiniciar monitor | Parar y volver a iniciar | Carga estado de JSON | | ⏳ |
| Estado corrupto | JSON malformado | Reset a defaults | | ⏳ |
| Estado desactualizado | Manual edit del JSON | Inconsistencias | | ⏳ |
| Archivo de estado borrado | Eliminar batch_monitor_state.json | Empezar desde batch 1 | | ⏳ |

### 8.3 Auto-Avance

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Auto-avance en último batch | Batch 60 completo | No hay siguiente, fin | | ⏳ |
| Auto-avance falla | Prodigy no reinicia | Retry o notificación | | ⏳ |
| Prodigy manager caído | No puede reiniciar | Error en logs | | ⏳ |
| Intervalo de chequeo muy corto | 1 segundo | Sobrecarga de DB | | ⏳ |

---

## 9. 🖥️ Escenarios de Servicios Backend

### 9.1 API FastAPI

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| API caída | Apagar uvicorn | Error de conexión | | ⏳ |
| API reiniciando | Durante restart | Errores temporales 503 | | ⏳ |
| API muy lenta | Sobrecarga | Timeouts en validación | | ⏳ |
| Endpoint /auth/me falla | Error en validación | Bloquea todo acceso | | ⏳ |

### 9.2 Base de Datos PostgreSQL/SQLite

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| DB de traducciones caída | PostgreSQL apagado | Error al cargar datos | | ⏳ |
| DB de Prodigy caída | SQLite bloqueado | No guarda anotaciones | | ⏳ |
| Migración de DB pendiente | Schema desactualizado | Errores de campo | | ⏳ |

---

## 10. 👥 Escenarios Multi-Usuario

### 10.1 Concurrencia

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| 2 usuarios misma frase | Alice y Bob anotan igual | Ambas se guardan | | ⏳ |
| 10 usuarios simultáneos | Alta carga | Performance aceptable | | ⏳ |
| Usuario lento bloquea | Alice tarda 1 hora | No bloquea a Bob | | ⏳ |
| Escritura simultánea a DB | Muchos writes a la vez | No hay race condition | | ⏳ |

### 10.2 Asignación de Tareas

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Usuario asignado a batch incorrecto | Error de config | Advertencia o bloqueo | | ⏳ |
| Usuario sin batch asignado | Nuevo usuario | ¿Qué batch ve? | | ⏳ |
| Reasignación de batch | Cambiar a otro batch | Nuevo contenido carga | | ⏳ |

---

## 11. 🎭 Edge Cases y Comportamientos Extraños

### 11.1 Usuario Inexperto Típico

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| No entiende las etiquetas | Aplica etiquetas random | ⚠️ Datos de baja calidad | | ⏳ |
| Acepta todo sin anotar | Accept sin spans | Datos vacíos | | ⏳ |
| Rechaza todo | Reject en todo | Muchos reject en IAA | | ⏳ |
| Ignora todo | Skip en todo | No contribuye | | ⏳ |
| Anota MUY rápido | 1 segundo por frase | Sospechoso, revisar | | ⏳ |
| Anota MUY lento | 30 min por frase | OK pero ineficiente | | ⏳ |

### 11.2 Errores de Usuario

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| URL pegada incorrectamente | Falta parte del token | Error de auth | | ⏳ |
| Copiar token con espacios | " eyJhbG..." | Falla validación | | ⏳ |
| Bookmark de URL con token | Guardar en favoritos | Token expira | | ⏳ |
| Compartir URL con token | Enviar a otro usuario | ⚠️ Riesgo de seguridad | | ⏳ |
| Usar URL de producción en dev | Ambiente incorrecto | Datos mezclados | | ⏳ |

### 11.3 Comportamientos del Navegador

| Escenario | Acción | Resultado Esperado | Resultado Real | Estado |
|-----------|--------|-------------------|----------------|--------|
| Autocompletado de formulario | Navegador llena campos | Puede romper UI | | ⏳ |
| Extensiones de navegador | AdBlocker activo | Puede bloquear requests | | ⏳ |
| Modo oscuro forzado | Extension dark mode | UI puede verse mal | | ⏳ |
| Zoom del navegador | Ctrl + / - | UI debe ser responsive | | ⏳ |
| Print (Ctrl+P) | Intentar imprimir | ¿Se ve bien impreso? | | ⏳ |

---

## 12. ✅ Checklist de Pruebas

### Pre-Pruebas
- [ ] Backend API corriendo en puerto 8000
- [ ] Prodigy Manager corriendo en puerto 8085
- [ ] Base de datos accesible
- [ ] Archivo .env configurado
- [ ] Token JWT válido disponible

### Pruebas Básicas
- [ ] Login exitoso con token válido
- [ ] Visualización correcta de texto guaraní
- [ ] Selección de texto funciona
- [ ] Aplicar etiqueta funciona
- [ ] Accept guarda correctamente
- [ ] Reject guarda correctamente
- [ ] Ignore salta correctamente
- [ ] Undo funciona
- [ ] Siguiente frase carga

### Pruebas de Resiliencia
- [ ] Recarga de página mantiene progreso
- [ ] Cierre y reapertura funciona
- [ ] Pérdida de conexión muestra error
- [ ] Token expirado redirige a login
- [ ] Servidor caído muestra mensaje claro

### Pruebas de Seguridad
- [ ] Sin token = acceso denegado
- [ ] Token inválido = acceso denegado
- [ ] Puerto interno bloqueado
- [ ] ?session= no da acceso

### Pruebas de Multi-Usuario
- [ ] 2+ usuarios simultáneos funciona
- [ ] Sesiones separadas correctamente
- [ ] Progreso independiente por usuario

### Pruebas de Batch Monitor
- [ ] Progreso se actualiza
- [ ] Auto-avance funciona
- [ ] Estado persiste tras reinicio

---

## 📝 Cómo Documentar Resultados

Para cada prueba, actualizar la tabla con:

| Campo | Descripción |
|-------|-------------|
| Resultado Real | Qué pasó exactamente |
| Estado | ✅ Pasa / ❌ Falla / ⚠️ Parcial / ⏳ Pendiente |
| Notas | Observaciones adicionales |
| Bug ID | Si se crea issue, número |
| Fecha | Cuándo se probó |
| Probador | Quién lo probó |

### Ejemplo de Documentación:

```markdown
| Escenario | Acción | Esperado | Real | Estado |
|-----------|--------|----------|------|--------|
| Cerrar pestaña | Cerrar tab | Pierde actual | Se perdió anotación en progreso, las guardadas OK | ✅ |
```

---

## 🚨 Bugs Conocidos

_(Actualizar esta sección conforme se descubren)_

1. **BUG-001**: [Descripción] - Estado: Abierto/Cerrado
2. **BUG-002**: [Descripción] - Estado: Abierto/Cerrado

---

## 📞 Contacto para Reportar Issues

- Crear issue en el repositorio
- Incluir: pasos para reproducir, resultado esperado vs real, capturas de pantalla
- Etiquetar con: `bug`, `prodigy`, `test-failure`
