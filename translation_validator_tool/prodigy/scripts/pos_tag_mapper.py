"""
Mapeo de etiquetas POS internas (español) a Universal Dependencies (UPOS)

Este módulo proporciona conversión bidireccional entre las etiquetas POS
internas en español utilizadas en el proyecto y las etiquetas Universal 
Dependencies estándar para Guaraní.

Referencias:
- Universal Dependencies: https://universaldependencies.org/
- UD Guaraní: https://universaldependencies.org/gn/index.html
- UPOS tags: https://universaldependencies.org/u/pos/index.html
"""

# Mapeo de etiquetas internas (español) a Universal Dependencies
INTERNAL_TO_UPOS = {
    # Etiquetas de función sintáctica
    "SUJETO": "NOUN",        # Sujeto → Sustantivo (función sintáctica → categoría léxica)
    "VERBO": "VERB",         # Verbo → Verbo
    "OBJETO": "NOUN",        # Objeto → Sustantivo (función sintáctica → categoría léxica)
    
    # Etiquetas de categoría léxica
    "ADJETIVO": "ADJ",       # Adjetivo → Adjective (nota: en guaraní clásico no hay ADJ)
    "ADVERBIO": "ADV",       # Adverbio → Adverb
    "PRONOMBRE": "PRON",     # Pronombre → Pronoun
    "PREPOSICION": "ADP",    # Preposición → Adposition (en guaraní son posposiciones)
    "PREPOSICIÓN": "ADP",    # Alias con tilde
    "ARTICULO": "DET",       # Artículo → Determiner
    "ARTÍCULO": "DET",       # Alias con tilde
    "CONJUNCION": "CCONJ",   # Conjunción → Coordinating Conjunction
    "CONJUNCIÓN": "CCONJ",   # Alias con tilde
    
    # Etiquetas morfológicas
    "RAIZ": "X",             # Raíz morfológica (se mantiene como X en UPOS)
    "PREFIJO": "X",          # Prefijo morfológico
    "SUFIJO": "X",           # Sufijo morfológico
    "INFIJO": "X",           # Infijo morfológico
    
    # Etiquetas adicionales
    "VERBO_AUX": "AUX",      # Verbo auxiliar
    "NOMBRE_PROPIO": "PROPN",# Nombre propio
    "NUMERAL": "NUM",        # Numeral
    "PARTICULA": "PART",     # Partícula
    "PARTÍCULA": "PART",     # Alias con tilde
    "INTERJECCION": "INTJ",  # Interjección
    "INTERJECCIÓN": "INTJ",  # Alias con tilde
    "CONJUNCION_SUB": "SCONJ", # Conjunción subordinante
    "CONJUNCIÓN_SUB": "SCONJ", # Alias con tilde
    "PUNTUACION": "PUNCT",   # Puntuación
    "PUNTUACIÓN": "PUNCT",   # Alias con tilde
    "SIMBOLO": "SYM",        # Símbolo
    "SÍMBOLO": "SYM",        # Alias con tilde
    "OTRO": "X",             # Otro (no clasificable)
}

# Mapeo inverso: UPOS a etiquetas internas (español)
UPOS_TO_INTERNAL = {
    "NOUN": "SUSTANTIVO",    # Por defecto mapea a SUSTANTIVO
    "VERB": "VERBO",
    "ADJ": "ADJETIVO",
    "ADV": "ADVERBIO",
    "PRON": "PRONOMBRE",
    "ADP": "PREPOSICION",
    "DET": "ARTICULO",
    "CCONJ": "CONJUNCION",
    "AUX": "VERBO_AUX",
    "PROPN": "NOMBRE_PROPIO",
    "NUM": "NUMERAL",
    "PART": "PARTÍCULA",
    "INTJ": "INTERJECCIÓN",
    "SCONJ": "CONJUNCIÓN_SUB",
    "PUNCT": "PUNTUACIÓN",
    "SYM": "SÍMBOLO",
    "X": "OTRO",
}

# Descripción de cada etiqueta UPOS con ejemplos en Guaraní
UPOS_DESCRIPTIONS = {
    "NOUN": {
        "nombre": "Sustantivo",
        "descripcion": "Palabras que nombran personas, lugares, cosas o conceptos",
        "ejemplos_guarani": ["kuña (mujer)", "oga (casa)", "tembi'u (comida)", "tendota (guerra)"],
        "notas": "En Guaraní, los sustantivos pueden llevar posposiciones (-pe, -gui, -rehe) y prefijos posesivos (che-, nde-, i-)"
    },
    "VERB": {
        "nombre": "Verbo",
        "descripcion": "Palabras que expresan acciones, estados o procesos",
        "ejemplos_guarani": ["ajuka (yo mato)", "oho (él/ella va)", "aikotevẽ (yo necesito)", "omombe'u (él/ella cuenta)"],
        "notas": "Los verbos guaraníes tienen prefijos de persona (a-, o-, ja-, ro-) y pueden llevar sufijos de modo y aspecto"
    },
    "ADJ": {
        "nombre": "Adjetivo",
        "descripcion": "Palabras que modifican sustantivos",
        "ejemplos_guarani": ["porã (bueno/a)", "guasu (grande)", "michĩ (pequeño/a)", "pyahu (nuevo/a)"],
        "notas": "IMPORTANTE: En Guaraní clásico no existe una categoría separada de adjetivos. Los 'adjetivos' son verbos estativos o sustantivos que funcionan como modificadores"
    },
    "ADV": {
        "nombre": "Adverbio",
        "descripcion": "Palabras que modifican verbos, adjetivos u otros adverbios",
        "ejemplos_guarani": ["ko'áĝa (ahora)", "upe jave (entonces)", "porãiterei (muy bien)", "tape rupi (por el camino)"],
        "notas": "Muchos adverbios en Guaraní se forman con posposiciones o son frases adverbiales"
    },
    "PRON": {
        "nombre": "Pronombre",
        "descripcion": "Palabras que reemplazan a sustantivos",
        "ejemplos_guarani": ["che (yo)", "nde (tú)", "ha'e (él/ella)", "ore (nosotros exclusivo)", "ñande (nosotros inclusivo)"],
        "notas": "El Guaraní distingue entre nosotros inclusivo (ñande) y exclusivo (ore). Los pronombres también funcionan como prefijos verbales"
    },
    "ADP": {
        "nombre": "Adposición",
        "descripcion": "Posposiciones que indican relaciones espaciales, temporales o lógicas",
        "ejemplos_guarani": ["-pe (en, a)", "-gui (de, desde)", "-rehe (sobre)", "-ndi (con)", "-me (en)"],
        "notas": "En Guaraní son POSposiciones (van después del sustantivo), no PREposiciones"
    },
    "DET": {
        "nombre": "Determinante",
        "descripcion": "Palabras que determinan o cuantifican sustantivos",
        "ejemplos_guarani": ["ko (este/a)", "upe (ese/a)", "ambuae (otro/a)", "opaite (todo/a)"],
        "notas": "Los demostrativos en Guaraní también pueden funcionar como pronombres"
    },
    "CCONJ": {
        "nombre": "Conjunción coordinante",
        "descripcion": "Palabras que conectan elementos del mismo nivel sintáctico",
        "ejemplos_guarani": ["ha (y)", "o (o)", "katu (pero)", "avei (también)"],
        "notas": "Conectan palabras, frases u oraciones de igual jerarquía"
    },
    "AUX": {
        "nombre": "Verbo auxiliar",
        "descripcion": "Verbos que acompañan al verbo principal para expresar tiempo, modo o aspecto",
        "ejemplos_guarani": ["ikatu (poder)", "ombohasa (hacer)", "oñemohenda (prepararse)"],
        "notas": "Los verbos auxiliares son menos comunes en Guaraní que en español"
    },
    "PROPN": {
        "nombre": "Nombre propio",
        "descripcion": "Nombres específicos de personas, lugares u organizaciones",
        "ejemplos_guarani": ["Asunción", "Paraguay", "Guaraní", "Juan"],
        "notas": "Incluye nombres de lugares, personas y entidades"
    },
    "NUM": {
        "nombre": "Numeral",
        "descripcion": "Palabras que expresan cantidad o número",
        "ejemplos_guarani": ["peteĩ (uno)", "mokõi (dos)", "mbohapy (tres)", "irundy (cuatro)", "po (cinco)"],
        "notas": "El sistema numeral guaraní tradicional es quinario (base 5)"
    },
    "PART": {
        "nombre": "Partícula",
        "descripcion": "Palabras funcionales que no encajan en otras categorías",
        "ejemplos_guarani": ["pa (interrogativo)", "ko (demostrativo)", "raka'e (reportativo)", "ndaje (dubitativo)"],
        "notas": "Incluye partículas interrogativas, modales y evidenciales"
    },
    "INTJ": {
        "nombre": "Interjección",
        "descripcion": "Palabras que expresan emociones o reacciones",
        "ejemplos_guarani": ["epa (¡vaya!)", "tɨre (expresión de sorpresa)", "aĝã (expresión de afirmación)"],
        "notas": "Expresiones exclamativas o emotivas independientes"
    },
    "SCONJ": {
        "nombre": "Conjunción subordinante",
        "descripcion": "Palabras que introducen oraciones subordinadas",
        "ejemplos_guarani": ["ramo (si, cuando)", "rupi (porque)", "rehe (sobre, acerca de)", "ague (para que)"],
        "notas": "Conectan oraciones de diferente jerarquía sintáctica"
    },
    "PUNCT": {
        "nombre": "Puntuación",
        "descripcion": "Signos de puntuación",
        "ejemplos_guarani": [".", ",", ":", ";", "¿", "?", "¡", "!"],
        "notas": "Incluye todos los signos ortográficos de puntuación"
    },
    "SYM": {
        "nombre": "Símbolo",
        "descripcion": "Símbolos especiales que no son puntuación",
        "ejemplos_guarani": ["$", "%", "@", "#", "&"],
        "notas": "Símbolos matemáticos, monetarios, técnicos, etc."
    },
    "X": {
        "nombre": "Otro",
        "descripcion": "Palabras que no pueden clasificarse en ninguna categoría",
        "ejemplos_guarani": ["palabras extranjeras sin adaptar", "errores tipográficos", "fragmentos incompletos"],
        "notas": "Usado cuando la categoría es indeterminable o no aplica"
    }
}

# Etiquetas actuales del proyecto (español)
INTERNAL_LABELS = list(INTERNAL_TO_UPOS.keys())

# Lista completa de etiquetas UPOS
UPOS_LABELS = [
    "ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", 
    "NOUN", "NUM", "PART", "PRON", "PROPN", "PUNCT", 
    "SCONJ", "SYM", "VERB", "X"
]


def convert_to_upos(internal_label: str) -> str:
    """
    Convierte una etiqueta interna (español) a UPOS.
    
    Args:
        internal_label: Etiqueta en español (ej: "VERBO", "SUSTANTIVO")
        
    Returns:
        Etiqueta UPOS correspondiente (ej: "VERB", "NOUN")
        
    Raises:
        ValueError: Si la etiqueta interna no existe en el mapeo
    """
    if internal_label not in INTERNAL_TO_UPOS:
        raise ValueError(
            f"Etiqueta interna '{internal_label}' no reconocida. "
            f"Etiquetas válidas: {', '.join(INTERNAL_LABELS)}"
        )
    return INTERNAL_TO_UPOS[internal_label]


def convert_to_internal(upos_label: str) -> str:
    """
    Convierte una etiqueta UPOS a etiqueta interna (español).
    
    Args:
        upos_label: Etiqueta UPOS (ej: "VERB", "NOUN")
        
    Returns:
        Etiqueta interna en español correspondiente
        
    Raises:
        ValueError: Si la etiqueta UPOS no existe en el mapeo
    """
    if upos_label not in UPOS_TO_INTERNAL:
        raise ValueError(
            f"Etiqueta UPOS '{upos_label}' no reconocida. "
            f"Etiquetas válidas: {', '.join(UPOS_LABELS)}"
        )
    return UPOS_TO_INTERNAL[upos_label]


def convert_spans_to_upos(spans: list) -> list:
    """
    Convierte una lista de spans con etiquetas internas a UPOS.
    
    Args:
        spans: Lista de dicts con keys 'start', 'end', 'label', 'text'
        
    Returns:
        Nueva lista de spans con etiquetas UPOS
        
    Example:
        >>> spans = [{"start": 0, "end": 5, "label": "VERBO", "text": "ahasa"}]
        >>> convert_spans_to_upos(spans)
        [{"start": 0, "end": 5, "label": "VERB", "text": "ahasa", "upos": "VERB", "original_label": "VERBO"}]
    """
    converted = []
    for span in spans:
        new_span = span.copy()
        internal_label = span.get("label", "")
        
        try:
            upos_label = convert_to_upos(internal_label)
            new_span["upos"] = upos_label
            new_span["original_label"] = internal_label
            new_span["label"] = upos_label  # Reemplazar label con UPOS
        except ValueError as e:
            # Si la etiqueta no existe, mantener original y marcar como desconocida
            new_span["upos"] = "X"
            new_span["original_label"] = internal_label
            new_span["label"] = "X"
            new_span["conversion_error"] = str(e)
        
        converted.append(new_span)
    
    return converted


def convert_spans_to_internal(spans: list) -> list:
    """
    Convierte una lista de spans con etiquetas UPOS a internas (español).
    
    Args:
        spans: Lista de dicts con keys 'start', 'end', 'label', 'text'
        
    Returns:
        Nueva lista de spans con etiquetas internas
    """
    converted = []
    for span in spans:
        new_span = span.copy()
        upos_label = span.get("label", "")
        
        try:
            internal_label = convert_to_internal(upos_label)
            new_span["internal_label"] = internal_label
            new_span["upos"] = upos_label
            new_span["label"] = internal_label  # Reemplazar label con interno
        except ValueError as e:
            # Si la etiqueta no existe, mantener original y marcar como desconocida
            new_span["internal_label"] = "OTRO"
            new_span["upos"] = upos_label
            new_span["label"] = "OTRO"
            new_span["conversion_error"] = str(e)
        
        converted.append(new_span)
    
    return converted


def get_upos_description(upos_label: str) -> dict:
    """
    Obtiene la descripción detallada de una etiqueta UPOS.
    
    Args:
        upos_label: Etiqueta UPOS
        
    Returns:
        Dict con nombre, descripción, ejemplos y notas
    """
    return UPOS_DESCRIPTIONS.get(upos_label, {
        "nombre": upos_label,
        "descripcion": "Sin descripción disponible",
        "ejemplos_guarani": [],
        "notas": ""
    })


def print_mapping_table():
    """Imprime una tabla con el mapeo completo de etiquetas."""
    print("\n" + "="*80)
    print("MAPEO DE ETIQUETAS: INTERNO (ESPAÑOL) → UNIVERSAL DEPENDENCIES (UPOS)")
    print("="*80)
    print(f"{'ETIQUETA INTERNA':<20} {'UPOS':<10} {'DESCRIPCIÓN':<50}")
    print("-"*80)
    
    for internal, upos in sorted(INTERNAL_TO_UPOS.items()):
        desc = UPOS_DESCRIPTIONS.get(upos, {}).get("nombre", "")
        print(f"{internal:<20} {upos:<10} {desc:<50}")
    
    print("="*80)


def print_upos_guide():
    """Imprime una guía completa de etiquetas UPOS con ejemplos en Guaraní."""
    print("\n" + "="*80)
    print("GUÍA DE ETIQUETAS UNIVERSAL DEPENDENCIES PARA GUARANÍ")
    print("="*80)
    
    for upos in sorted(UPOS_LABELS):
        info = get_upos_description(upos)
        print(f"\n{upos} - {info['nombre']}")
        print("-" * 80)
        print(f"Descripción: {info['descripcion']}")
        
        if info['ejemplos_guarani']:
            print(f"Ejemplos en Guaraní:")
            for ejemplo in info['ejemplos_guarani']:
                print(f"  • {ejemplo}")
        
        if info['notas']:
            print(f"Notas: {info['notas']}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Mapeo de etiquetas POS internas a Universal Dependencies"
    )
    parser.add_argument(
        "--table", "-t",
        action="store_true",
        help="Mostrar tabla de mapeo"
    )
    parser.add_argument(
        "--guide", "-g",
        action="store_true",
        help="Mostrar guía completa de UPOS"
    )
    parser.add_argument(
        "--convert", "-c",
        type=str,
        help="Convertir una etiqueta (ej: VERBO → VERB)"
    )
    
    args = parser.parse_args()
    
    if args.table:
        print_mapping_table()
    
    if args.guide:
        print_upos_guide()
    
    if args.convert:
        try:
            # Intentar conversión interna → UPOS
            upos = convert_to_upos(args.convert)
            print(f"\n{args.convert} → {upos}")
            info = get_upos_description(upos)
            print(f"Descripción: {info['nombre']} - {info['descripcion']}")
        except ValueError:
            try:
                # Intentar conversión UPOS → interna
                internal = convert_to_internal(args.convert)
                print(f"\n{args.convert} → {internal}")
            except ValueError as e:
                print(f"\nError: {e}")
    
    if not any([args.table, args.guide, args.convert]):
        parser.print_help()
