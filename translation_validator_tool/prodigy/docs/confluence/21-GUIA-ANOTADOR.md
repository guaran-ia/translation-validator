# 👤 Guía del Anotador

Esta guía explica cómo usar el sistema de anotación Prodigy para el corpus Guaraní.

---

## 1. Acceso al Sistema

### 1.1 Iniciar Sesión

1. Abre tu navegador y ve a **http://localhost:5173**
2. Ingresa tu usuario y contraseña
3. Selecciona el tipo de anotación (POS, Features, Relations)
4. El sistema te redirigirá a Prodigy

### 1.2 URL Directa (si tienes token)

```
http://localhost:8085/?token=<TU_TOKEN>&service=pos
```

Reemplaza `pos` por `features` o `relations` según corresponda.

---

## 2. Interfaz de Prodigy

### 2.1 Componentes de la Pantalla

```
┌─────────────────────────────────────────────────────────────────────┐
│ 🏷️ POS Tags (UD) - Universal Dependencies UPOS                     │
│                                    Lote 5 | Paso 1/3 | #25/50      │
├─────────────────────────────────────────────────────────────────────┤
│ [📖 Ver Contexto]                                   Ctrl+Shift+C   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   "Che roipota   nde   rape"                                       │
│    ─────────────────────────                                       │
│        (área de texto para seleccionar)                            │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│ ETIQUETAS:                                                          │
│ [Sustantivo] [Verbo] [Pronombre] [Posposición] [Adverbio]          │
│ [Numeral] [Partícula] [Interjección] [Nombre Propio] [Puntuación]  │
├─────────────────────────────────────────────────────────────────────┤
│     [✓ Aceptar]      [✗ Rechazar]      [? Ignorar]                 │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Barra de Información

- **Tipo de anotación**: POS Tags, Features, o Relations
- **Lote actual**: Número de lote (1-60)
- **Paso**: 1/3 (POS), 2/3 (Features), 3/3 (Relations)
- **Progreso**: #25/50 = oración 25 de 50 en el lote actual

---

## 3. Cómo Anotar

### 3.1 POS Tags (Etiquetas gramaticales)

1. **Lee la oración** en guaraní
2. **Selecciona una palabra** haciendo clic y arrastrando
3. **Elige la etiqueta** correspondiente del panel
4. **Repite** para cada palabra
5. **Haz clic en [✓ Aceptar]** cuando termines

**Ejemplo:**
```
"Che roipota nde rape"
 ───  ──────  ─── ────
 [Pronombre] [Verbo] [Determinante] [Sustantivo]
```

### 3.2 Features (Características morfológicas)

1. **Selecciona el morfema** (puede ser parte de una palabra)
2. **Elige la característica** del panel
3. Los spans **pueden superponerse**

**Ejemplo:**
```
"roipota"
 │└─ "ipo" → [Verbo/Raíz]
 └── "ro-" → [1ra Persona], [Plural]
     "-ta" → [Futuro]
```

### 3.3 Relations (Relaciones sintácticas)

1. **Haz clic en la palabra origen** (dependiente)
2. **Haz clic en la palabra destino** (head)
3. **Selecciona el tipo de relación**

**Ejemplo:**
```
"Che roipota nde rape"
      ───────→ (SUJETO)
      │        nde
      │        ───→ (DETERMINANTE)
      │        rape
      └────────→ (OBJETO DIRECTO)
```

---

## 4. Atajos de Teclado

| Tecla | Acción |
|-------|--------|
| `A` | Aceptar ejemplo |
| `X` | Rechazar ejemplo |
| `Space` | Ignorar ejemplo |
| `Ctrl+Z` | Deshacer última selección |
| `Ctrl+Shift+C` | Abrir/cerrar contexto |
| `←` / `→` | Navegar entre ejemplos |

---

## 5. Botón de Contexto

### Ver oraciones adyacentes

Haz clic en **[📖 Ver Contexto]** o presiona **Ctrl+Shift+C** para ver:
- Las 2 oraciones anteriores
- La oración actual (resaltada)
- Las 2 oraciones siguientes

Esto ayuda a entender el contexto del texto.

```
┌─────────────────────────────────────────────────────────────────┐
│ 📖 Contexto - Oración #25/50                               [X] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ...oración 23. Oración 24. [ORACIÓN 25 ACTUAL EN AMARILLO]    │
│  Oración 26. Oración 27...                                      │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  La oración actual está resaltada en amarillo                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Etiquetas Disponibles

### 6.1 POS Tags (11 etiquetas)

| Etiqueta | Descripción | Ejemplo |
|----------|-------------|---------|
| Sustantivo | Nombres comunes | oga (casa) |
| Verbo | Acciones, estados | oguata (camina) |
| Pronombre | Pronombres | che (yo) |
| Nombre Propio | Nombres propios | Paraguái |
| Determinante | Artículos, demostrativos | ko (este) |
| Posposición | Posposiciones | -pe (en) |
| Adverbio | Modificadores | ko'ápe (aquí) |
| Numeral | Números | mokõi (dos) |
| Partícula | Partículas | katu, ko |
| Interjección | Exclamaciones | añaménte |
| Puntuación | Signos | . , ; |

### 6.2 Features más comunes

| Categoría | Etiquetas |
|-----------|-----------|
| Persona | 1ra Persona, 2da Persona, 3ra Persona |
| Número | Singular, Plural |
| Clusividad | Inclusivo, Exclusivo |
| Tiempo | Pasado, Futuro, Futuro-Pasado |
| Modo | Imperativo, Permisivo |
| Voz | Causativo, Comitativo |

### 6.3 Relaciones más comunes

| Relación | Descripción |
|----------|-------------|
| SUJETO | Quién realiza la acción |
| OBJETO DIRECTO | Qué recibe la acción |
| OBJETO INDIRECTO | Beneficiario de la acción |
| MODIFICADOR ADVERBIAL | Cómo, cuándo, dónde |
| MODIFICADOR NOMINAL | Modifica un sustantivo |
| RAÍZ | Verbo principal de la oración |

---

## 7. Cuándo Rechazar

Usa **[✗ Rechazar]** cuando:
- El texto está corrupto o ilegible
- No es guaraní (es español u otro idioma)
- No tiene sentido gramatical
- Es demasiado fragmentado para anotar

---

## 8. Cuándo Ignorar

Usa **[? Ignorar]** cuando:
- No estás seguro de la anotación
- Necesitas consultar con otro anotador
- El texto es ambiguo

---

## 9. Guardar Progreso

### Guardado automático

El sistema guarda automáticamente cada 3 anotaciones (configurable).

### Verificar guardado

- Observa el contador de progreso (#25/50)
- Si avanza, la anotación se guardó

### Cerrar sesión

Puedes cerrar el navegador en cualquier momento. Tu progreso se mantiene.

---

## 10. Consejos

### Para POS Tags
- Cada palabra debe tener exactamente una etiqueta POS
- La puntuación también se etiqueta (PUNCT)
- En caso de duda entre NOUN y VERB, considera el contexto

### Para Features
- Un morfema puede tener múltiples features
- Los spans pueden superponerse
- Anota desde los morfemas más externos hacia los internos

### Para Relations
- Toda palabra debe conectarse a otra (excepto la RAÍZ)
- La RAÍZ es típicamente el verbo principal
- El sujeto se conecta al verbo principal

---

## 11. Problemas Comunes

### "No puedo seleccionar texto"
- Verifica que estás en el área de texto correcta
- Intenta hacer clic y arrastrar más lentamente

### "Perdí mi progreso"
- El sistema guarda automáticamente
- Verifica que no perdiste conexión a internet
- Contacta al administrador si el problema persiste

### "No veo todas las etiquetas"
- Desplázate en el panel de etiquetas
- Algunas etiquetas pueden estar colapsadas en grupos

---

## 12. Contacto

Si tienes dudas o encuentras problemas:
1. Consulta con otros anotadores
2. Revisa la documentación
3. Contacta al administrador del proyecto
