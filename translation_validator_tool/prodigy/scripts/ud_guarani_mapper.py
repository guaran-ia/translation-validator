"""
MAPPER CENTRALIZADO: Etiquetas Amigables ↔ Universal Dependencies (Old Guaraní)

Este archivo es la ÚNICA FUENTE DE VERDAD para el mapeo de etiquetas.
Basado en: https://universaldependencies.org/treebanks/gn_oldtudet/index.html

Importar en cualquier script:
    from ud_guarani_mapper import FRIENDLY_TO_UD, UD_TO_FRIENDLY, map_label, LABEL_FAMILIES

Autor: Proyecto Guaraní Corpus Lacuna
Fecha: 2025-12-01
"""

# =============================================================================
# MAPEO PRINCIPAL: Etiqueta Amigable → Universal Dependencies
# =============================================================================
# Basado en: https://universaldependencies.org/treebanks/gn_oldtudet/index.html
#
# UPOS usados en Old Guaraní:
#   ADP, ADV, DET, INTJ, NOUN, NUM, PART, PRON, PROPN, PUNCT, VERB
#   NO SE USAN: ADJ, AUX, SCONJ, CCONJ, SYM, X
#
# Features usados en Old Guaraní:
#   Case, Clusivity, Corf, Dev, Emph, Evident, Int, Intens, Mood, 
#   Nomzr, Number, Number[psor], Number[subj], Person, Person[obj], 
#   Person[psor], Person[subj], Polarity, Poss, Priv, PronType, 
#   Red, Reflex, Rel, Tense, Voice, VerbForm
# =============================================================================

FRIENDLY_TO_UD = {
    # =========================================================================
    # MORFEMAS (Análisis morfológico)
    # =========================================================================
    # Nota: Root, Prefix, Suffix no son etiquetas UD estándar, pero las usamos
    # para análisis morfológico. Se mantienen tal cual para exportación.
    "Raíz": "Root",
    "Prefijo": "Prefix", 
    "Sufijo": "Suffix",
    
    # =========================================================================
    # PERSONA (Person) - UD Feature
    # https://universaldependencies.org/u/feat/Person.html
    # =========================================================================
    "1ra Persona": "Person=1",
    "2da Persona": "Person=2", 
    "3ra Persona": "Person=3",
    
    # =========================================================================
    # NÚMERO (Number) - UD Feature
    # https://universaldependencies.org/u/feat/Number.html
    # =========================================================================
    "Singular": "Number=Sing",
    "Plural": "Number=Plur",
    
    # =========================================================================
    # CLUSIVIDAD (Clusivity) - UD Feature (Específico Guaraní)
    # https://universaldependencies.org/u/feat/Clusivity.html
    # =========================================================================
    "Inclusivo": "Clusivity=In",
    "Exclusivo": "Clusivity=Ex",
    
    # =========================================================================
    # CASO (Case) - UD Feature
    # https://universaldependencies.org/u/feat/Case.html
    # Valores usados en Old Guaraní: Abl, All, Dat, Loc, Ref
    # =========================================================================
    "Ablativo": "Case=Abl",        # Movimiento desde (usado en Old Guaraní)
    "Alativo": "Case=All",         # Movimiento hacia (usado en Old Guaraní)
    "Locativo": "Case=Loc",        # Ubicación
    "Dativo": "Case=Dat",          # Beneficiario/receptor
    "Referencial": "Case=Ref",     # Referencial (usado en Old Guaraní)
    # Los siguientes NO están documentados en Old Guaraní, se mapean a X
    "Perlativo": "Case=Per",       # Por/a través de (no en Old Guaraní docs)
    "Translativo": "Case=Tra",     # Cambio de estado (no en Old Guaraní docs)
    
    # =========================================================================
    # RELACIONAL (Rel) - UD Feature (Específico Tupí-Guaraní)
    # https://universaldependencies.org/aqz/feat/Rel.html
    # Valores usados en Old Guaraní: Abs, Cont, NCont
    # =========================================================================
    "Rel. Absoluto": "Rel=Abs",       # Sin poseedor
    "Rel. Contiguo": "Rel=Cont",      # Poseedor contiguo (r-)
    "Rel. No-Contiguo": "Rel=NCont",  # Poseedor no contiguo (h-/i-)
    # Alias para compatibilidad
    "Rel. Humano": "Rel=NCont",       # Mapea a NCont (aproximación)
    
    # =========================================================================
    # REFLEXIVO (Reflex) - UD Feature
    # https://universaldependencies.org/u/feat/Reflex.html
    # =========================================================================
    "Correferencial": "Reflex=Yes",
    "Reflexivo": "Reflex=Yes",
    
    # =========================================================================
    # ASPECTO (Aspect) - UD Feature
    # https://universaldependencies.org/u/feat/Aspect.html
    # NOTA: Old Guaraní no documenta Aspect explícitamente, pero lo incluimos
    # =========================================================================
    "Completivo": "Aspect=Perf",   # Perfectivo (acción completada)
    "Iterativo": "Aspect=Iter",    # Iterativo
    "Sucesivo": "Aspect=Prosp",    # Prospectivo (aproximación)
    "Habitual": "Aspect=Hab",      # Habitual
    
    # =========================================================================
    # MODO (Mood) - UD Feature  
    # https://universaldependencies.org/u/feat/Mood.html
    # Valores usados en Old Guaraní: Imp, Perm
    # =========================================================================
    "Imperativo": "Mood=Imp",      # Imperativo (documentado)
    "Permisivo": "Mood=Perm",      # Permisivo/optativo (documentado)
    
    # =========================================================================
    # TIEMPO (Tense) - UD Feature
    # https://universaldependencies.org/u/feat/Tense.html
    # Valores usados en Old Guaraní: Fut, FutPast, Past
    # =========================================================================
    "Pasado": "Tense=Past",        # Pasado (documentado)
    "Futuro": "Tense=Fut",         # Futuro (documentado)
    "Futuro-Pasado": "Tense=FutPast",  # Futuro del pasado (documentado)
    
    # =========================================================================
    # FORMA VERBAL (VerbForm) - UD Feature
    # https://universaldependencies.org/u/feat/VerbForm.html
    # Valor usado en Old Guaraní: Ger
    # =========================================================================
    "Gerundio": "VerbForm=Ger",    # Gerundio (documentado)
    
    # =========================================================================
    # VOZ (Voice) - UD Feature
    # https://universaldependencies.org/u/feat/Voice.html
    # Valores usados en Old Guaraní: Cau, Com
    # =========================================================================
    "Causativo": "Voice=Cau",      # Causativo (documentado)
    "Comitativo": "Voice=Com",     # Comitativo (documentado)
    
    # =========================================================================
    # POLARIDAD (Polarity) - UD Feature
    # https://universaldependencies.org/u/feat/Polarity.html
    # Valor usado en Old Guaraní: Neg
    # =========================================================================
    "Negación": "Polarity=Neg",    # Negación (documentado)
    
    # =========================================================================
    # POSESIÓN (Poss) - UD Feature
    # https://universaldependencies.org/u/feat/Poss.html
    # =========================================================================
    "Poseedor": "Poss=Yes",
    "Posesivo": "Poss=Yes",
    
    # =========================================================================
    # NOMINALIZADORES (Nomzr) - UD Feature (Específico Tupí-Guaraní)
    # https://universaldependencies.org/apy/feat/Nomzr.html
    # Valores usados en Old Guaraní: Ag, CCirc, Circ, DevPass, Pas, Rel
    # =========================================================================
    "Agentivo (-sar)": "Nomzr=Ag",           # Agentivo (documentado)
    "Circunstancial (-saβ)": "Nomzr=Circ",   # Circunstancial (documentado)
    "Pasivo (-pɨr)": "Nomzr=Pas",            # Pasivo (documentado)
    "C-Circunstancial": "Nomzr=CCirc",       # C-Circunstancial (documentado)
    "Derivación Pasiva": "Nomzr=DevPass",    # Derivación pasiva (documentado)
    "Relativo (Nomzr)": "Nomzr=Rel",         # Nominalizador relativo (documentado)
    # Alias para compatibilidad con código anterior
    "Habitual (-βor)": "Aspect=Hab",         # Redirigido a Aspect
    
    # =========================================================================
    # EVIDENCIALIDAD (Evident) - UD Feature
    # https://universaldependencies.org/u/feat/Evident.html
    # Valor usado en Old Guaraní: Nfh
    # =========================================================================
    "No-Primera Mano": "Evident=Nfh",  # Evidencia no de primera mano (documentado)
    
    # =========================================================================
    # ÉNFASIS (Emph) - UD Feature (Específico Tupí-Guaraní)
    # =========================================================================
    "Enfático": "Emph=Yes",
    
    # =========================================================================
    # INTENSIFICADOR (Intens) - UD Feature
    # =========================================================================
    "Intensificador": "Intens=Yes",
    
    # =========================================================================
    # PRIVATIVO (Priv) - UD Feature  
    # https://universaldependencies.org/gn/feat/Priv.html
    # =========================================================================
    "Privativo": "Priv=Yes",       # Sin/ausencia de (documentado)
    
    # =========================================================================
    # REDUPLICACIÓN (Red) - UD Feature
    # =========================================================================
    "Reduplicación": "Red=Di",     # Reduplicación distributiva (documentado)
    
    # =========================================================================
    # INTERROGATIVO (Int) - UD Feature
    # =========================================================================
    "Interrogativo": "Int=Yes",
    
    # =========================================================================
    # CORREFERENCIA (Corf) - UD Feature (Específico Tupí-Guaraní)
    # =========================================================================
    "Correferencia": "Corf=Yes",
    
    # =========================================================================
    # CATEGORÍAS GRAMATICALES (UPOS)
    # https://universaldependencies.org/u/pos/
    # Solo los UPOS documentados en Old Guaraní:
    #   ADP, ADV, DET, INTJ, NOUN, NUM, PART, PRON, PROPN, PUNCT, VERB
    # =========================================================================
    # UPOS DOCUMENTADOS EN OLD GUARANÍ:
    "Verbo": "VERB",               # ✓ Documentado
    "Sustantivo": "NOUN",          # ✓ Documentado
    "Pronombre": "PRON",           # ✓ Documentado
    "Adverbio": "ADV",             # ✓ Documentado
    "Posposición": "ADP",          # ✓ Documentado (son posposiciones, no preposiciones)
    "Determinante": "DET",         # ✓ Documentado
    "Numeral": "NUM",              # ✓ Documentado
    "Partícula": "PART",           # ✓ Documentado
    "Interjección": "INTJ",        # ✓ Documentado
    "Nombre Propio": "PROPN",      # ✓ Documentado
    "Puntuación": "PUNCT",         # ✓ Documentado
    
    # UPOS NO USADOS EN OLD GUARANÍ (pero incluidos para completitud):
    "Auxiliar": "AUX",             # ✗ No usado en Old Guaraní
    "Conj. Coordinante": "CCONJ",  # ✗ No usado en Old Guaraní
    "Conj. Subordinante": "SCONJ", # ✗ No usado en Old Guaraní
    "Adjetivo": "ADJ",             # ✗ No existe en Guaraní clásico
    "Símbolo": "SYM",              # ✗ No usado en Old Guaraní
    "Otro": "X",                   # Para etiquetas no clasificables
    
    # =========================================================================
    # RELACIONES SINTÁCTICAS (Deprel) - UD Relations
    # https://universaldependencies.org/u/dep/
    # Basado en Old Guaraní treebank
    # =========================================================================
    "RAÍZ (Verbo Principal)": "root",
    "SUJETO": "nsubj",
    "OBJETO DIRECTO": "obj",
    "OBJETO INDIRECTO": "iobj",
    "COMPLEMENTO OBLICUO": "obl",
    "OBLICUO-OBJETO": "obl:obj",
    "OBLICUO-SUJETO": "obl:subj",
    "MODIFICADOR ADVERBIAL": "advmod",
    "CLÁUSULA ADVERBIAL": "advcl",
    "MODIFICADOR NOMINAL": "nmod",
    "DETERMINANTE (Rel)": "det",
    "MARCADOR DE CASO": "case",
    "PALABRA COMPUESTA": "compound",
    "APOSICIÓN": "appos",
    "COMPLEMENTO VERBAL": "xcomp",
    "ELEMENTO DE DISCURSO": "discourse",
    "PARATAXIS": "parataxis",
    "MODIFICADOR NUMÉRICO": "nummod",
    "PUNTUACIÓN (Rel)": "punct",
    "DEPENDENCIA (General)": "dep",
}

# =============================================================================
# MAPEO INVERSO: Universal Dependencies → Etiqueta Amigable
# =============================================================================
UD_TO_FRIENDLY = {v: k for k, v in FRIENDLY_TO_UD.items()}

# Agregar aliases inversos
UD_TO_FRIENDLY.update({
    # UPOS
    "VERB": "Verbo",
    "NOUN": "Sustantivo", 
    "PRON": "Pronombre",
    "ADV": "Adverbio",
    "ADP": "Posposición",
    "DET": "Determinante",
    "NUM": "Numeral",
    "PART": "Partícula",
    "INTJ": "Interjección",
    "PROPN": "Nombre Propio",
    "PUNCT": "Puntuación",
    "AUX": "Auxiliar",
    "CCONJ": "Conj. Coordinante",
    "SCONJ": "Conj. Subordinante",
    "ADJ": "Adjetivo",
    "SYM": "Símbolo",
    "X": "Otro",
    # Morfemas
    "Root": "Raíz",
    "Prefix": "Prefijo",
    "Suffix": "Sufijo",
})

# =============================================================================
# LISTA DE UPOS VÁLIDOS (para verificación)
# =============================================================================
VALID_UPOS = {
    # Documentados en Old Guaraní
    "ADP", "ADV", "DET", "INTJ", "NOUN", "NUM", "PART", 
    "PRON", "PROPN", "PUNCT", "VERB",
    # No documentados pero posibles
    "ADJ", "AUX", "CCONJ", "SCONJ", "SYM", "X",
}

# =============================================================================
# FEATURES VÁLIDOS DE OLD GUARANÍ (para verificación)
# =============================================================================
VALID_FEATURES = {
    # Nominales
    "Number=Sing", "Number=Plur",
    "Case=Abl", "Case=All", "Case=Dat", "Case=Loc", "Case=Ref",
    "Poss=Yes",
    # Verbales
    "Mood=Imp", "Mood=Perm",
    "Tense=Fut", "Tense=FutPast", "Tense=Past",
    "Voice=Cau", "Voice=Com",
    "VerbForm=Ger",
    "Polarity=Neg",
    # Pronombres/Determinantes
    "PronType=Dem", "PronType=Ind", "PronType=Int", "PronType=Prs", "PronType=Tot",
    "Person=1", "Person=2", "Person=3",
    "Reflex=Yes",
    "NumType=Card",
    # Específicos Tupí-Guaraní
    "Clusivity=In", "Clusivity=Ex",
    "Rel=Abs", "Rel=Cont", "Rel=NCont",
    "Nomzr=Ag", "Nomzr=CCirc", "Nomzr=Circ", "Nomzr=DevPass", "Nomzr=Pas", "Nomzr=Rel",
    "Corf=Yes",
    "Evident=Nfh",
    "Emph=Yes",
    "Intens=Yes",
    "Int=Yes",
    "Priv=Yes",
    "Red=Di",
    # Aspecto (no documentado explícitamente pero posible)
    "Aspect=Perf", "Aspect=Iter", "Aspect=Prosp", "Aspect=Hab",
    # Morfemas (especiales, no UD estándar)
    "Root", "Prefix", "Suffix",
}

# =============================================================================
# FAMILIAS DE ETIQUETAS (para UI agrupada)
# =============================================================================
LABEL_FAMILIES = {
    "📦 Morfemas": {
        "description": "Componentes estructurales",
        "color": "#3b82f6",
        "labels": ["Raíz", "Prefijo", "Sufijo"],
    },
    "👤 Persona": {
        "description": "Person (UD)",
        "color": "#8b5cf6",
        "labels": ["1ra Persona", "2da Persona", "3ra Persona"],
    },
    "🔢 Número": {
        "description": "Number (UD)",
        "color": "#06b6d4",
        "labels": ["Singular", "Plural"],
    },
    "👥 Clusividad": {
        "description": "Clusivity (UD) - 1ra plural",
        "color": "#0ea5e9",
        "labels": ["Inclusivo", "Exclusivo"],
    },
    "📍 Caso": {
        "description": "Case (UD)",
        "color": "#f97316",
        "labels": ["Ablativo", "Alativo", "Locativo", "Dativo", "Referencial"],
    },
    "🔗 Relacional": {
        "description": "Rel (UD) - Específico Tupí-Guaraní",
        "color": "#6366f1",
        "labels": ["Rel. Absoluto", "Rel. Contiguo", "Rel. No-Contiguo", "Correferencial"],
    },
    "⏰ Tiempo": {
        "description": "Tense (UD)",
        "color": "#eab308",
        "labels": ["Pasado", "Futuro", "Futuro-Pasado"],
    },
    "🔄 Aspecto": {
        "description": "Aspect (UD)",
        "color": "#84cc16",
        "labels": ["Completivo", "Iterativo", "Sucesivo", "Habitual"],
    },
    "💭 Modo": {
        "description": "Mood (UD)",
        "color": "#14b8a6",
        "labels": ["Imperativo", "Permisivo"],
    },
    "🗣️ Voz": {
        "description": "Voice (UD)",
        "color": "#ec4899",
        "labels": ["Causativo", "Comitativo"],
    },
    "📝 Forma Verbal": {
        "description": "VerbForm (UD)",
        "color": "#f472b6",
        "labels": ["Gerundio"],
    },
    "🚫 Polaridad": {
        "description": "Polarity (UD)",
        "color": "#ef4444",
        "labels": ["Negación"],
    },
    "🏠 Posesión": {
        "description": "Poss (UD)",
        "color": "#f59e0b",
        "labels": ["Poseedor"],
    },
    "🔧 Nominalizadores": {
        "description": "Nomzr (UD) - Específico Tupí-Guaraní",
        "color": "#a855f7",
        "labels": ["Agentivo (-sar)", "Circunstancial (-saβ)", "Pasivo (-pɨr)", 
                   "C-Circunstancial", "Derivación Pasiva", "Relativo (Nomzr)"],
    },
    "✨ Otros Features": {
        "description": "Otros rasgos morfológicos",
        "color": "#64748b",
        "labels": ["No-Primera Mano", "Enfático", "Intensificador", "Privativo", 
                   "Reduplicación", "Interrogativo", "Correferencia", "Reflexivo"],
    },
    "📝 Categoría (UPOS)": {
        "description": "Universal POS Tags",
        "color": "#dc2626",
        "labels": ["Verbo", "Sustantivo", "Pronombre", "Adverbio", "Posposición",
                   "Determinante", "Numeral", "Partícula", "Interjección", 
                   "Nombre Propio", "Puntuación"],
    },
}

# =============================================================================
# COLORES POR ETIQUETA
# =============================================================================
LABEL_COLORS = {}
for family_name, family_data in LABEL_FAMILIES.items():
    base_color = family_data["color"]
    for label in family_data["labels"]:
        LABEL_COLORS[label] = base_color

# =============================================================================
# FUNCIONES DE MAPEO
# =============================================================================

def map_label(label: str, direction: str = "to_ud") -> str:
    """
    Mapea una etiqueta entre formato amigable y UD.
    
    Args:
        label: La etiqueta a mapear
        direction: "to_ud" o "to_friendly"
    
    Returns:
        La etiqueta mapeada, o "X"/"Otro" si no se encuentra
    """
    if direction == "to_ud":
        # Buscar exacto primero
        if label in FRIENDLY_TO_UD:
            return FRIENDLY_TO_UD[label]
        # Buscar case-insensitive
        label_lower = label.lower()
        for friendly, ud in FRIENDLY_TO_UD.items():
            if friendly.lower() == label_lower:
                return ud
        # Si ya es UD válido, devolverlo
        if label in VALID_UPOS or label in VALID_FEATURES:
            return label
        return "X"
    else:  # to_friendly
        # Buscar exacto primero
        if label in UD_TO_FRIENDLY:
            return UD_TO_FRIENDLY[label]
        # Si ya es amigable, devolverlo
        if label in FRIENDLY_TO_UD:
            return label
        return "Otro"


def map_labels_batch(labels: list, direction: str = "to_ud") -> list:
    """
    Mapea múltiples etiquetas.
    
    Args:
        labels: Lista de etiquetas a mapear
        direction: "to_ud" o "to_friendly"
    
    Returns:
        Lista de etiquetas mapeadas
    """
    return [map_label(label, direction) for label in labels]


def is_valid_ud(label: str) -> bool:
    """Verifica si una etiqueta es un UPOS o Feature válido de UD."""
    return label in VALID_UPOS or label in VALID_FEATURES


def get_all_friendly_labels() -> list:
    """Retorna todas las etiquetas amigables."""
    return list(FRIENDLY_TO_UD.keys())


def get_all_ud_labels() -> list:
    """Retorna todas las etiquetas UD."""
    return list(set(FRIENDLY_TO_UD.values()))


def get_family_labels(family_key: str) -> list:
    """
    Obtiene las etiquetas de una familia por su clave.
    
    Args:
        family_key: Clave corta (ej: "morfema", "persona", "caso")
    
    Returns:
        Lista de etiquetas amigables de esa familia
    """
    # Mapeo de claves cortas a nombres de familia
    _family_keys_map = {
        "morfema": "📦 Morfemas",
        "persona": "👤 Persona",
        "numero": "🔢 Número",
        "clusividad": "👥 Clusividad",
        "caso": "📍 Caso",
        "relacional": "🔗 Relacional",
        "tiempo": "⏰ Tiempo",
        "aspecto": "🔄 Aspecto",
        "modo": "💭 Modo",
        "voz": "🗣️ Voz",
        "forma": "📝 Forma Verbal",
        "polaridad": "🚫 Polaridad",
        "posesion": "🏠 Posesión",
        "nominalizador": "🔧 Nominalizadores",
        "otros": "✨ Otros Features",
        "categoria": "📝 Categoría (UPOS)",
    }
    
    family_key_lower = family_key.lower()
    
    # Buscar en el mapeo de claves
    if family_key_lower in _family_keys_map:
        full_name = _family_keys_map[family_key_lower]
        if full_name in LABEL_FAMILIES:
            return LABEL_FAMILIES[full_name]["labels"]
    
    # Fallback: buscar en nombres de familia
    for name, data in LABEL_FAMILIES.items():
        if family_key_lower in name.lower():
            return data["labels"]
    return []


# =============================================================================
# CLAVES DE FAMILIA PARA CLI
# =============================================================================
FAMILY_KEYS = {
    "morfema": "Morfemas",
    "persona": "Persona",
    "numero": "Número",
    "clusividad": "Clusividad",
    "caso": "Caso",
    "relacional": "Relacional",
    "tiempo": "Tiempo",
    "aspecto": "Aspecto",
    "modo": "Modo",
    "voz": "Voz",
    "forma": "Forma Verbal",
    "polaridad": "Polaridad",
    "posesion": "Posesión",
    "nominalizador": "Nominalizadores",
    "otros": "Otros Features",
    "categoria": "Categoría (UPOS)",
}

# =============================================================================
# GRUPOS ESPECIALIZADOS PARA RECIPES DE ANOTACIÓN
# =============================================================================
# Organizados según Universal Dependencies:
# https://universaldependencies.org/treebanks/gn_oldtudet/index.html
# =============================================================================

SPECIALIZED_GROUPS = {
    # =========================================================================
    # GRUPO PRINCIPAL 1: POS TAGS (UPOS)
    # Categorías gramaticales principales
    # =========================================================================
    "pos-tags": {
        "name": "POS Tags",
        "description": "Categorías gramaticales (Universal POS Tags)",
        "color": "#dc2626",
        "emoji": "🏷️",
        "labels": [
            "Posposición",      # ADP
            "Adverbio",         # ADV
            "Determinante",     # DET
            "Interjección",     # INTJ
            "Sustantivo",       # NOUN
            "Numeral",          # NUM
            "Partícula",        # PART
            "Pronombre",        # PRON
            "Nombre Propio",    # PROPN
            "Puntuación",       # PUNCT
            "Verbo",            # VERB
        ],
        "ud_mapping": {
            "Posposición": "ADP",
            "Adverbio": "ADV",
            "Determinante": "DET",
            "Interjección": "INTJ",
            "Sustantivo": "NOUN",
            "Numeral": "NUM",
            "Partícula": "PART",
            "Pronombre": "PRON",
            "Nombre Propio": "PROPN",
            "Puntuación": "PUNCT",
            "Verbo": "VERB",
        },
    },
    
    # =========================================================================
    # GRUPO PRINCIPAL 2: FEATURES
    # Rasgos morfológicos
    # =========================================================================
    "features": {
        "name": "Features",
        "description": "Rasgos morfológicos (Morphological Features)",
        "color": "#8b5cf6",
        "emoji": "⚙️",
        "labels": [
            # Case
            "Ablativo", "Alativo", "Dativo", "Locativo", "Referencial",
            # Clusivity
            "Inclusivo", "Exclusivo",
            # Corf (Correferentiality)
            "Correferencial",
            # Dev (Derivation) - No hay etiqueta amigable aún
            # Emph
            "Enfático",
            # Evident
            "No-Primera Mano",
            # Int (Interrogative)
            "Interrogativo",
            # Intens
            "Intensificador",
            # Mood
            "Imperativo", "Permisivo",
            # Nomzr
            "Agentivo (-sar)", "Circunstancial (-saβ)", "Pasivo (-pɨr)", 
            "C-Circunstancial", "Derivación Pasiva", "Relativo (Nomzr)",
            # Number
            "Singular", "Plural",
            # Number[psor] - Número del poseedor (se marca con Singular/Plural + contexto)
            # Number[subj] - Número del sujeto (se marca con Singular/Plural + contexto)
            # NumType
            "Cardinal",
            # Person
            "1ra Persona", "2da Persona", "3ra Persona",
            # Person[obj] - Persona del objeto (se marca con 1ra/2da/3ra + contexto)
            # Person[psor] - Persona del poseedor (se marca con 1ra/2da/3ra + contexto)
            # Person[subj] - Persona del sujeto (se marca con 1ra/2da/3ra + contexto)
            # Polarity
            "Negación",
            # Poss
            "Poseedor",
            # Priv
            "Privativo",
            # PronType
            "Demostrativo", "Indefinido", "Interrogativo (Pron)", "Personal", "Total",
            # Red
            "Reduplicación",
            # Reflex
            "Reflexivo",
            # Rel
            "Rel. Absoluto", "Rel. Contiguo", "Rel. No-Contiguo",
            # Tense
            "Pasado", "Futuro", "Futuro-Pasado",
            # VerbForm
            "Gerundio",
            # Voice
            "Causativo", "Comitativo",
        ],
        "ud_mapping": {
            # Case
            "Ablativo": "Case=Abl",
            "Alativo": "Case=All",
            "Dativo": "Case=Dat",
            "Locativo": "Case=Loc",
            "Referencial": "Case=Ref",
            # Clusivity
            "Inclusivo": "Clusivity=In",
            "Exclusivo": "Clusivity=Ex",
            # Corf
            "Correferencial": "Corf=Yes",
            # Emph
            "Enfático": "Emph=Yes",
            # Evident
            "No-Primera Mano": "Evident=Nfh",
            # Int
            "Interrogativo": "Int=Yes",
            # Intens
            "Intensificador": "Intens=Yes",
            # Mood
            "Imperativo": "Mood=Imp",
            "Permisivo": "Mood=Perm",
            # Nomzr
            "Agentivo (-sar)": "Nomzr=Ag",
            "Circunstancial (-saβ)": "Nomzr=Circ",
            "Pasivo (-pɨr)": "Nomzr=Pas",
            "C-Circunstancial": "Nomzr=CCirc",
            "Derivación Pasiva": "Nomzr=DevPass",
            "Relativo (Nomzr)": "Nomzr=Rel",
            # Number
            "Singular": "Number=Sing",
            "Plural": "Number=Plur",
            # NumType
            "Cardinal": "NumType=Card",
            # Person
            "1ra Persona": "Person=1",
            "2da Persona": "Person=2",
            "3ra Persona": "Person=3",
            # Polarity
            "Negación": "Polarity=Neg",
            # Poss
            "Poseedor": "Poss=Yes",
            # Priv
            "Privativo": "Priv=Yes",
            # PronType
            "Demostrativo": "PronType=Dem",
            "Indefinido": "PronType=Ind",
            "Interrogativo (Pron)": "PronType=Int",
            "Personal": "PronType=Prs",
            "Total": "PronType=Tot",
            # Red
            "Reduplicación": "Red=Di",
            # Reflex
            "Reflexivo": "Reflex=Yes",
            # Rel
            "Rel. Absoluto": "Rel=Abs",
            "Rel. Contiguo": "Rel=Cont",
            "Rel. No-Contiguo": "Rel=NCont",
            # Tense
            "Pasado": "Tense=Past",
            "Futuro": "Tense=Fut",
            "Futuro-Pasado": "Tense=FutPast",
            # VerbForm
            "Gerundio": "VerbForm=Ger",
            # Voice
            "Causativo": "Voice=Cau",
            "Comitativo": "Voice=Com",
        },
    },
    
    # =========================================================================
    # GRUPO PRINCIPAL 3: RELATIONS (Deprel)
    # Relaciones sintácticas - Etiquetas amigables en español
    # https://universaldependencies.org/u/dep/
    # =========================================================================
    "relations": {
        "name": "Relaciones Sintácticas",
        "description": "Relaciones de dependencia (Dependency Relations)",
        "color": "#22c55e",
        "emoji": "🔗",
        "labels": [
            "RAÍZ (Verbo Principal)",
            "SUJETO",
            "OBJETO DIRECTO",
            "OBJETO INDIRECTO",
            "COMPLEMENTO OBLICUO",
            "OBLICUO-OBJETO",
            "OBLICUO-SUJETO",
            "MODIFICADOR ADVERBIAL",
            "CLÁUSULA ADVERBIAL",
            "MODIFICADOR NOMINAL",
            "DETERMINANTE (Rel)",
            "MARCADOR DE CASO",
            "PALABRA COMPUESTA",
            "APOSICIÓN",
            "COMPLEMENTO VERBAL",
            "ELEMENTO DE DISCURSO",
            "PARATAXIS",
            "MODIFICADOR NUMÉRICO",
            "PUNTUACIÓN (Rel)",
            "DEPENDENCIA (General)",
        ],
        "ud_mapping": {
            "RAÍZ (Verbo Principal)": "root",
            "SUJETO": "nsubj",
            "OBJETO DIRECTO": "obj",
            "OBJETO INDIRECTO": "iobj",
            "COMPLEMENTO OBLICUO": "obl",
            "OBLICUO-OBJETO": "obl:obj",
            "OBLICUO-SUJETO": "obl:subj",
            "MODIFICADOR ADVERBIAL": "advmod",
            "CLÁUSULA ADVERBIAL": "advcl",
            "MODIFICADOR NOMINAL": "nmod",
            "DETERMINANTE (Rel)": "det",
            "MARCADOR DE CASO": "case",
            "PALABRA COMPUESTA": "compound",
            "APOSICIÓN": "appos",
            "COMPLEMENTO VERBAL": "xcomp",
            "ELEMENTO DE DISCURSO": "discourse",
            "PARATAXIS": "parataxis",
            "MODIFICADOR NUMÉRICO": "nummod",
            "PUNTUACIÓN (Rel)": "punct",
            "DEPENDENCIA (General)": "dep",
        },
        "colors": {
            "RAÍZ (Verbo Principal)": "#dc2626",
            "SUJETO": "#2563eb",
            "OBJETO DIRECTO": "#16a34a",
            "OBJETO INDIRECTO": "#65a30d",
            "COMPLEMENTO OBLICUO": "#ca8a04",
            "OBLICUO-OBJETO": "#ca8a04",
            "OBLICUO-SUJETO": "#ca8a04",
            "MODIFICADOR ADVERBIAL": "#7c3aed",
            "CLÁUSULA ADVERBIAL": "#a855f7",
            "MODIFICADOR NOMINAL": "#0891b2",
            "DETERMINANTE (Rel)": "#64748b",
            "MARCADOR DE CASO": "#78716c",
            "PALABRA COMPUESTA": "#ea580c",
            "APOSICIÓN": "#db2777",
            "COMPLEMENTO VERBAL": "#059669",
            "ELEMENTO DE DISCURSO": "#94a3b8",
            "PARATAXIS": "#f97316",
            "MODIFICADOR NUMÉRICO": "#0d9488",
            "PUNTUACIÓN (Rel)": "#d4d4d4",
            "DEPENDENCIA (General)": "#a1a1aa",
        },
    },
    
    # =========================================================================
    # GRUPO AUXILIAR: MORFEMAS (para análisis morfológico)
    # No es estándar UD pero útil para segmentación
    # =========================================================================
    "morfemas": {
        "name": "Morfemas",
        "description": "Segmentación morfológica (no estándar UD)",
        "color": "#3b82f6",
        "emoji": "📦",
        "labels": ["Raíz", "Prefijo", "Sufijo"],
        "ud_mapping": {
            "Raíz": "Root",
            "Prefijo": "Prefix",
            "Sufijo": "Suffix",
        },
    },
    
    # =========================================================================
    # SUBGRUPOS DE FEATURES (para anotación por partes)
    # =========================================================================
    "features-persona-numero": {
        "name": "Persona y Número",
        "description": "Person, Number, Clusivity",
        "color": "#8b5cf6",
        "emoji": "👤",
        "labels": [
            "1ra Persona", "2da Persona", "3ra Persona",
            "Singular", "Plural",
            "Inclusivo", "Exclusivo",
        ],
    },
    
    "features-caso": {
        "name": "Caso",
        "description": "Case features",
        "color": "#f97316",
        "emoji": "📍",
        "labels": ["Ablativo", "Alativo", "Dativo", "Locativo", "Referencial"],
    },
    
    "features-tam": {
        "name": "Tiempo, Aspecto, Modo",
        "description": "Tense, Mood, VerbForm, Voice",
        "color": "#eab308",
        "emoji": "⏰",
        "labels": [
            "Pasado", "Futuro", "Futuro-Pasado",
            "Imperativo", "Permisivo",
            "Gerundio",
            "Causativo", "Comitativo",
        ],
    },
    
    "features-relacional": {
        "name": "Relacional",
        "description": "Rel (Tupí-Guaraní specific)",
        "color": "#6366f1",
        "emoji": "🔗",
        "labels": ["Rel. Absoluto", "Rel. Contiguo", "Rel. No-Contiguo"],
    },
    
    "features-nominalizadores": {
        "name": "Nominalizadores",
        "description": "Nomzr (Tupí-Guaraní specific)",
        "color": "#a855f7",
        "emoji": "🔧",
        "labels": [
            "Agentivo (-sar)", "Circunstancial (-saβ)", "Pasivo (-pɨr)", 
            "C-Circunstancial", "Derivación Pasiva", "Relativo (Nomzr)",
        ],
    },
    
    "features-otros": {
        "name": "Otros Features",
        "description": "Polarity, Poss, Priv, etc.",
        "color": "#64748b",
        "emoji": "✨",
        "labels": [
            "Negación", "Poseedor", "Privativo", "Reduplicación",
            "Reflexivo", "Correferencial", "Enfático", "Intensificador",
            "No-Primera Mano", "Interrogativo",
        ],
    },
}

# =============================================================================
# UD_MAIN_GROUPS - Grupos principales de Universal Dependencies
# Alias para facilitar el acceso a los grupos UD principales
# =============================================================================
UD_MAIN_GROUPS = {
    "pos-tags": SPECIALIZED_GROUPS["pos-tags"],
    "features": SPECIALIZED_GROUPS["features"],
    "relations": SPECIALIZED_GROUPS["relations"],
    "morfemas": SPECIALIZED_GROUPS["morfemas"],
}


def get_specialized_group(group_key: str) -> dict:
    """
    Obtiene información de un grupo especializado.
    
    Args:
        group_key: Clave del grupo (ej: "morfemas-basicos", "categorias")
    
    Returns:
        Diccionario con info del grupo o None si no existe
    """
    return SPECIALIZED_GROUPS.get(group_key.lower())


def get_ud_main_group(group_key: str) -> dict:
    """
    Obtiene información de un grupo UD principal.
    
    Args:
        group_key: Clave del grupo (pos-tags, features, relations, morfemas)
    
    Returns:
        Diccionario con info del grupo o None si no existe
    """
    return UD_MAIN_GROUPS.get(group_key.lower())


def get_ud_main_labels(group_key: str) -> list:
    """
    Obtiene las etiquetas de un grupo UD principal.
    
    Args:
        group_key: Clave del grupo UD (pos-tags, features, relations)
    
    Returns:
        Lista de etiquetas de ese grupo
    """
    group = UD_MAIN_GROUPS.get(group_key.lower())
    if group:
        return group.get("labels", [])
    return []


def list_ud_main_groups() -> dict:
    """
    Lista todos los grupos UD principales disponibles.
    
    Returns:
        Dict con {key: name} para cada grupo
    """
    return {key: group["name"] for key, group in UD_MAIN_GROUPS.items()}


def get_all_ud_ordered_labels() -> list:
    """
    Obtiene todas las etiquetas ordenadas por grupo UD.
    Útil para mostrar etiquetas agrupadas en la UI.
    
    Returns:
        Lista ordenada: POS Tags primero, luego Features, luego Morfemas
    """
    ordered = []
    # 1. POS Tags
    pos_group = UD_MAIN_GROUPS.get("pos-tags", {})
    ordered.extend(pos_group.get("labels", []))
    
    # 2. Features
    feat_group = UD_MAIN_GROUPS.get("features", {})
    ordered.extend(feat_group.get("labels", []))
    
    # 3. Morfemas (auxiliar)
    morf_group = UD_MAIN_GROUPS.get("morfemas", {})
    ordered.extend(morf_group.get("labels", []))
    
    return ordered


def get_ud_label_colors() -> dict:
    """
    Genera colores para cada etiqueta según su grupo UD.
    
    Returns:
        Dict de {label: color_hex} para todas las etiquetas UD
    """
    colors = {}
    
    for group_key, group in UD_MAIN_GROUPS.items():
        group_color = group.get("color", "#6b7280")
        for label in group.get("labels", []):
            colors[label] = group_color
    
    return colors


def get_specialized_labels(group_key: str) -> list:
    """
    Obtiene las etiquetas de un grupo especializado.
    
    Args:
        group_key: Clave del grupo (ej: "morfemas-basicos", "categorias")
    
    Returns:
        Lista de etiquetas amigables de ese grupo
    """
    group = SPECIALIZED_GROUPS.get(group_key.lower())
    if group:
        return group["labels"]
    return []


def list_specialized_groups() -> dict:
    """Retorna todos los grupos especializados disponibles."""
    return {key: group["name"] for key, group in SPECIALIZED_GROUPS.items()}

# =============================================================================
# EJEMPLO DE USO
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("UD Guaraní Mapper - Test")
    print("=" * 60)
    
    # Test de mapeo
    test_labels = [
        "Raíz", "Prefijo", "Pronombre", "Verbo",
        "1ra Persona", "Locativo", "Imperativo"
    ]
    
    print("\n📋 Test de mapeo Amigable → UD:")
    for label in test_labels:
        ud = map_label(label, "to_ud")
        print(f"  {label:25} → {ud}")
    
    print("\n📋 Test de mapeo UD → Amigable:")
    for ud in ["VERB", "NOUN", "Person=1", "Case=Loc"]:
        friendly = map_label(ud, "to_friendly")
        print(f"  {ud:25} → {friendly}")
    
    print("\n📋 Familias disponibles:")
    for key, full_name in FAMILY_KEYS.items():
        labels = get_family_labels(key)
        print(f"  {key:15} → {len(labels)} etiquetas")
    
    print("\n✅ Mapper funcionando correctamente!")
