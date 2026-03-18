"""
Mapper centralizado: Etiquetas amigables <-> Universal Dependencies (Guarani)

Este archivo es la UNICA FUENTE DE VERDAD para el mapeo de etiquetas.
Todos los recipes y scripts importan de aca.

Referencia UD: https://universaldependencies.org/u/pos/
               https://universaldependencies.org/u/feat/
               https://universaldependencies.org/u/dep/

Como configurar:
    1) POS tags        -> editar POS_TAGS
    2) Features        -> editar FEATURES
    3) Dependencias    -> editar DEPENDENCY_RELATIONS
    4) Morfemas        -> editar MORPHEMES (no es estandar UD)
    5) Colores de UI   -> editar GROUP_COLORS / RELATION_COLORS

Importar en cualquier script:
    from ud_guarani_mapper import FRIENDLY_TO_UD, UD_TO_FRIENDLY, map_label, LABEL_FAMILIES
"""


# =============================================================================
# 1) CATEGORIAS GRAMATICALES / POS TAGS
# =============================================================================
# Ref: https://universaldependencies.org/u/pos/
#
# Formato: (etiqueta_amigable, codigo_UD, activa)
#   - activa=True  -> se usa en anotacion
#   - activa=False -> definida pero no se muestra en Prodigy
# =============================================================================

POS_TAGS = [
    # etiqueta amigable        UD      activa   descripcion
    ("Adjetivo",               "ADJ",   True),  # adjetivo
    ("Posposicion",            "ADP",   True),  # adposicion (preposicion o posposicion)
    ("Adverbio",               "ADV",   True),  # adverbio
    ("Auxiliar",               "AUX",   True),  # verbo auxiliar
    ("Conj. Coordinante",      "CCONJ", True),  # conjuncion coordinante
    ("Determinante",           "DET",   True),  # determinante
    ("Interjeccion",           "INTJ",  True),  # interjeccion
    ("Sustantivo",             "NOUN",  True),  # sustantivo
    ("Numeral",                "NUM",   True),  # numero
    ("Particula",              "PART",  True),  # particula
    ("Pronombre",              "PRON",  True),  # pronombre
    ("Nombre Propio",          "PROPN", True),  # nombre propio
    ("Puntuacion",             "PUNCT", True),  # puntuacion
    ("Conj. Subordinante",     "SCONJ", True),  # conjuncion subordinante
    ("Simbolo",                "SYM",   True),  # simbolo
    ("Verbo",                  "VERB",  True),  # verbo
    ("Otro",                   "X",     True),  # otra categoria no definible
]


# =============================================================================
# 2) RASGOS MORFOLOGICOS / FEATURES
# =============================================================================
# Ref: https://universaldependencies.org/u/feat/
#
# Cada feature es: (etiqueta_amigable, valor_UD, activa)
#
# Para desactivar un feature, poner activa=False.
# Para agregar uno nuevo, agregar una tupla a la lista correspondiente.
#
# NOTA: Los features marcados "no usamos" en el doc del equipo estan
#       con activa=False. Se pueden activar cambiando a True.
# =============================================================================

FEATURES = {
    # --- Abbreviation (Abbr) ---
    "Abbr": [
        ("Abreviacion",          "Abbr=Yes",       True),
    ],

    # --- Aspect ---
    "Aspect": [
        ("Completivo",           "Aspect=Perf",    True),   # perfectivo
        ("Iterativo",            "Aspect=Iter",    True),
        ("Sucesivo",             "Aspect=Prosp",   True),   # prospectivo (aprox.)
        ("Habitual",             "Aspect=Hab",     True),
    ],

    # --- Case ---
    "Case": [
        ("Ablativo",             "Case=Abl",       True),
        ("Alativo",              "Case=All",       True),
        ("Locativo",             "Case=Loc",       True),
        ("Dativo",               "Case=Dat",       True),
        ("Referencial",          "Case=Ref",       True),
        ("Perlativo",            "Case=Per",       False),  # no documentado en Old Guarani
        ("Translativo",          "Case=Tra",       False),  # no documentado en Old Guarani
    ],

    # --- Clusivity (especifico guarani, 1ra persona plural) ---
    "Clusivity": [
        ("Inclusivo",            "Clusivity=In",   True),
        ("Exclusivo",            "Clusivity=Ex",   True),
    ],

    # --- Definite ---
    "Definite": [
        ("Definido",             "Definite=Def",   True),
        ("Indefinido (Def)",     "Definite=Ind",   True),
    ],

    # --- Foreign ---
    "Foreign": [
        ("Extranjerismo",        "Foreign=Yes",    True),
    ],

    # --- Mood ---
    "Mood": [
        ("Imperativo",           "Mood=Imp",       True),
        ("Permisivo",            "Mood=Perm",      True),
    ],

    # --- Nasality (nueva, especifica del proyecto) ---
    "Nasality": [
        ("Nasal",                "Nasality=Yes",   True),
    ],

    # --- Number ---
    "Number": [
        ("Singular",             "Number=Sing",    True),
        ("Plural",               "Number=Plur",    True),
    ],

    # --- Other ---
    "Other": [
        ("Otro (Feat)",          "Other=Yes",      True),
    ],

    # --- Person ---
    "Person": [
        ("1ra Persona",          "Person=1",       True),
        ("2da Persona",          "Person=2",       True),
        ("3ra Persona",          "Person=3",       True),
    ],

    # --- Polarity ---
    "Polarity": [
        ("Negacion",             "Polarity=Neg",   True),
    ],

    # --- Poss ---
    "Poss": [
        ("Poseedor",             "Poss=Yes",       True),
    ],

    # --- PronType ---
    "PronType": [
        ("Demostrativo",         "PronType=Dem",   True),
        ("Indefinido",           "PronType=Ind",   True),
        ("Interrogativo (Pron)", "PronType=Int",   True),
        ("Personal",             "PronType=Prs",   True),
        ("Total",                "PronType=Tot",   True),
    ],

    # --- Reflex --- (no la usamos)
    "Reflex": [
        ("Reflexivo",            "Reflex=Yes",     False),
    ],

    # --- Tense ---
    "Tense": [
        ("Pasado",               "Tense=Past",     True),
        ("Futuro",               "Tense=Fut",      True),
        ("Futuro-Pasado",        "Tense=FutPast",  True),
    ],

    # --- Typo ---
    "Typo": [
        ("Errata",               "Typo=Yes",       True),
    ],

    # --- VerbForm ---
    "VerbForm": [
        ("Gerundio",             "VerbForm=Ger",   True),
    ],

    # --- Voice --- (no la usamos, no hay voz pasiva en guarani)
    "Voice": [
        ("Causativo",            "Voice=Cau",      False),
        ("Comitativo",           "Voice=Com",      False),
    ],

    # -----------------------------------------------------------------
    # Features especificos Tupi-Guarani (no estandar UD universal)
    # -----------------------------------------------------------------

    # --- Rel (Relacional) ---
    "Rel": [
        ("Rel. Absoluto",        "Rel=Abs",        True),
        ("Rel. Contiguo",        "Rel=Cont",       True),
        ("Rel. No-Contiguo",     "Rel=NCont",      True),
    ],

    # --- Nomzr (Nominalizadores) ---
    "Nomzr": [
        ("Agentivo (-sar)",          "Nomzr=Ag",       True),
        ("Circunstancial (-sab)",    "Nomzr=Circ",     True),
        ("Pasivo (-pyr)",            "Nomzr=Pas",      True),
        ("C-Circunstancial",         "Nomzr=CCirc",    True),
        ("Derivacion Pasiva",        "Nomzr=DevPass",  True),
        ("Relativo (Nomzr)",         "Nomzr=Rel",      True),
    ],

    # --- Corf (Correferencia) ---
    "Corf": [
        ("Correferencia",        "Corf=Yes",       True),
    ],

    # --- Evident (Evidencialidad) --- (no la usamos)
    "Evident": [
        ("No-Primera Mano",     "Evident=Nfh",    False),
    ],

    # --- Emph ---
    "Emph": [
        ("Enfatico",             "Emph=Yes",       True),
    ],

    # --- Intens ---
    "Intens": [
        ("Intensificador",       "Intens=Yes",     True),
    ],

    # --- Priv (Privativo) ---
    "Priv": [
        ("Privativo",            "Priv=Yes",       True),
    ],

    # --- Red (Reduplicacion) ---
    "Red": [
        ("Reduplicacion",        "Red=Di",         True),
    ],

    # --- Int (Interrogativo morfologico) ---
    "Int": [
        ("Interrogativo",        "Int=Yes",        True),
    ],
}


# =============================================================================
# 3) ETIQUETAS DE DEPENDENCIA / DEPENDENCY RELATIONS
# =============================================================================
# Ref: https://universaldependencies.org/u/dep/
#
# Formato: (etiqueta_amigable, codigo_UD, activa)
#
# Todas las relaciones definidas por UD estan listadas.
# Las marcadas con (*) son las que usamos en nuestros ejemplos hasta ahora.
# =============================================================================

DEPENDENCY_RELATIONS = [
    # etiqueta amigable              UD            activa
    ("CLAUSULA RELATIVA",            "acl",         True),
    ("CLAUSULA ADVERBIAL",           "advcl",       True),
    ("MODIFICADOR ADVERBIAL",        "advmod",      True),
    ("MODIFICADOR ADJETIVAL",        "amod",        True),   # modificador adjetival
    ("APOSICION",                    "appos",       True),
    ("AUXILIAR (dep)",               "aux",         True),   # auxiliar
    ("MARCADOR DE CASO",             "case",        True),   # (*) usado en ejemplos
    ("CONJUNCION COORDINANTE",       "cc",          True),   # (*) usado en ejemplos
    ("COMPLEMENTO CLAUSAL",          "ccomp",       True),   # (*) usado en ejemplos
    ("CLASIFICADOR",                 "clf",         True),
    ("PALABRA COMPUESTA",            "compound",    True),
    ("CONJUNCION",                   "conj",        True),   # (*) usado en ejemplos
    ("COPULA",                       "cop",         True),
    ("SUJETO CLAUSAL",              "csubj",        True),
    ("DEPENDENCIA (General)",        "dep",         True),
    ("DETERMINANTE (dep)",           "det",         True),   # (*) usado en ejemplos
    ("ELEMENTO DE DISCURSO",         "discourse",   True),
    ("DISLOCADO",                    "dislocated",  True),
    ("EXPLETIVO",                    "expl",        True),
    ("EXPRESION FIJA",               "fixed",       True),
    ("NOMBRE PLANO",                 "flat",        True),
    ("VA-CON",                       "goeswith",    True),
    ("OBJETO INDIRECTO",             "iobj",        True),   # objeto indirecto
    ("LISTA",                        "list",        True),
    ("MARCADOR",                     "mark",        True),
    ("MODIFICADOR NOMINAL",          "nmod",        True),   # (*) usado en ejemplos
    ("SUJETO NOMINAL",              "nsubj",        True),   # (*) sujeto nominal
    ("MODIFICADOR NUMERICO",         "nummod",      True),
    ("OBJETO DIRECTO",               "obj",         True),   # (*) usado en ejemplos
    ("OBLICUO",                      "obl",         True),
    ("HUERFANO",                     "orphan",      True),
    ("PARATAXIS",                    "parataxis",   True),
    ("PUNTUACION (dep)",             "punct",       True),   # (*) usado en ejemplos
    ("REPARANDUM",                   "reparandum",  True),
    ("RAIZ",                         "root",        True),   # raiz de la oracion
    ("VOCATIVO",                     "vocative",    True),   # vocativo
    ("COMPLEMENTO VERBAL",          "xcomp",        True),
]


# =============================================================================
# 4) MORFEMAS (no estandar UD, para analisis morfologico)
# =============================================================================

MORPHEMES = [
    ("Raiz",     "Root",    True),
    ("Prefijo",  "Prefix",  True),
    ("Sufijo",   "Suffix",  True),
]


# =============================================================================
# 5) COLORES PARA UI (por grupo)
# =============================================================================
# Cambiar aca para modificar los colores en Prodigy.

GROUP_COLORS = {
    "pos-tags":     "#dc2626",   # rojo
    "features":     "#8b5cf6",   # violeta
    "relations":    "#22c55e",   # verde
    "morfemas":     "#3b82f6",   # azul

    # Subgrupos de features
    "Abbr":         "#64748b",
    "Aspect":       "#84cc16",
    "Case":         "#f97316",
    "Clusivity":    "#0ea5e9",
    "Definite":     "#64748b",
    "Foreign":      "#64748b",
    "Mood":         "#14b8a6",
    "Nasality":     "#14b8a6",
    "Number":       "#06b6d4",
    "Other":        "#64748b",
    "Person":       "#8b5cf6",
    "Polarity":     "#ef4444",
    "Poss":         "#f59e0b",
    "PronType":     "#64748b",
    "Tense":        "#eab308",
    "Typo":         "#64748b",
    "VerbForm":     "#f472b6",
    "Voice":        "#ec4899",
    "Rel":          "#6366f1",
    "Nomzr":        "#a855f7",
    "Corf":         "#6366f1",
    "Evident":      "#64748b",
    "Emph":         "#64748b",
    "Intens":       "#64748b",
    "Priv":         "#64748b",
    "Red":          "#64748b",
    "Int":          "#64748b",
    "Reflex":       "#6366f1",
}

# Colores individuales para relaciones de dependencia
RELATION_COLORS = {
    "RAIZ":                     "#dc2626",
    "SUJETO NOMINAL":           "#2563eb",
    "OBJETO DIRECTO":           "#16a34a",
    "OBJETO INDIRECTO":         "#65a30d",
    "OBLICUO":                  "#ca8a04",
    "MODIFICADOR ADVERBIAL":    "#7c3aed",
    "CLAUSULA ADVERBIAL":       "#a855f7",
    "MODIFICADOR NOMINAL":      "#0891b2",
    "DETERMINANTE (dep)":       "#64748b",
    "MARCADOR DE CASO":         "#78716c",
    "PALABRA COMPUESTA":        "#ea580c",
    "APOSICION":                "#db2777",
    "COMPLEMENTO VERBAL":       "#059669",
    "ELEMENTO DE DISCURSO":     "#94a3b8",
    "PARATAXIS":                "#f97316",
    "MODIFICADOR NUMERICO":     "#0d9488",
    "PUNTUACION (dep)":         "#d4d4d4",
    "DEPENDENCIA (General)":    "#a1a1aa",
    "CONJUNCION COORDINANTE":   "#78716c",
    "COMPLEMENTO CLAUSAL":      "#059669",
    "CONJUNCION":               "#78716c",
    "AUXILIAR (dep)":           "#7c3aed",
    "MODIFICADOR ADJETIVAL":    "#0891b2",
    "CLAUSULA RELATIVA":        "#a855f7",
    "VOCATIVO":                 "#db2777",
}


# =============================================================================
# =============================================================================
#  A PARTIR DE ACA NO DEBERIA SER NECESARIO EDITAR
#  (se genera todo automaticamente a partir de las tablas de arriba)
# =============================================================================
# =============================================================================


def _build_friendly_to_ud():
    """Construye el diccionario FRIENDLY_TO_UD a partir de las tablas de config."""
    mapping = {}

    # Morfemas
    for friendly, ud, active in MORPHEMES:
        if active:
            mapping[friendly] = ud

    # Features (todos los grupos)
    for _group_name, feat_list in FEATURES.items():
        for friendly, ud, active in feat_list:
            if active:
                mapping[friendly] = ud

    # POS tags
    for friendly, ud, active in POS_TAGS:
        if active:
            mapping[friendly] = ud

    # Relaciones de dependencia
    for friendly, ud, active in DEPENDENCY_RELATIONS:
        if active:
            mapping[friendly] = ud

    return mapping


def _build_ud_to_friendly(fwd):
    """Construye el mapeo inverso UD -> amigable."""
    rev = {}
    for friendly, ud in fwd.items():
        rev[ud] = friendly
    return rev


# --- Diccionarios principales ---
FRIENDLY_TO_UD = _build_friendly_to_ud()
UD_TO_FRIENDLY = _build_ud_to_friendly(FRIENDLY_TO_UD)

# --- Compatibilidad: aliases que pueden existir en datos viejos ---
_ALIASES = {
    # Aliases con tildes/caracteres especiales del mapper anterior
    "Posposicion": "ADP",
    "Posposición": "ADP",
    "Interjeccion": "INTJ",
    "Interjección": "INTJ",
    "Particula": "PART",
    "Partícula": "PART",
    "Puntuacion": "PUNCT",
    "Puntuación": "PUNCT",
    "Simbolo": "SYM",
    "Símbolo": "SYM",
    "Negacion": "Polarity=Neg",
    "Negación": "Polarity=Neg",
    "Enfatico": "Emph=Yes",
    "Enfático": "Emph=Yes",
    "Reduplicacion": "Red=Di",
    "Reduplicación": "Red=Di",
    "Abreviacion": "Abbr=Yes",
    "Abreviación": "Abbr=Yes",
    "Derivacion Pasiva": "Nomzr=DevPass",
    "Derivación Pasiva": "Nomzr=DevPass",
    "Raiz": "Root",
    "Raíz": "Root",
    "Posesivo": "Poss=Yes",
    "Correferencial": "Reflex=Yes",
    "Rel. Humano": "Rel=NCont",
    "Habitual (-βor)": "Aspect=Hab",
    "Circunstancial (-saβ)": "Nomzr=Circ",
    "Pasivo (-pɨr)": "Nomzr=Pas",
    # Relaciones con formato anterior
    "RAÍZ (Verbo Principal)": "root",
    "SUJETO": "nsubj",
    "OBLICUO-OBJETO": "obl:obj",
    "OBLICUO-SUJETO": "obl:subj",
    "CLÁUSULA ADVERBIAL": "advcl",
    "DETERMINANTE (Rel)": "det",
    "APOSICIÓN": "appos",
    "MODIFICADOR NUMÉRICO": "nummod",
    "PUNTUACIÓN (Rel)": "punct",
    "COMPLEMENTO OBLICUO": "obl",
}

# Incorporar aliases al mapeo principal (sin sobreescribir los canonicos)
for _alias, _ud_val in _ALIASES.items():
    if _alias not in FRIENDLY_TO_UD:
        FRIENDLY_TO_UD[_alias] = _ud_val

# Asegurar que el inverso tenga las entradas canonicas
for friendly, ud, active in POS_TAGS:
    if active:
        UD_TO_FRIENDLY[ud] = friendly
for friendly, ud, active in MORPHEMES:
    if active:
        UD_TO_FRIENDLY[ud] = friendly


# =============================================================================
# VALID_UPOS y VALID_FEATURES (conjuntos para verificacion)
# =============================================================================

VALID_UPOS = {ud for _f, ud, active in POS_TAGS if active}

VALID_FEATURES = set()
for _group_name, _feat_list in FEATURES.items():
    for _friendly, ud, active in _feat_list:
        if active:
            VALID_FEATURES.add(ud)
# Agregar morfemas como features especiales
for _friendly, ud, active in MORPHEMES:
    if active:
        VALID_FEATURES.add(ud)


# =============================================================================
# LABEL_FAMILIES (para UI agrupada)
# =============================================================================

def _build_label_families():
    families = {}

    # Morfemas
    active_morphemes = [f for f, _u, a in MORPHEMES if a]
    if active_morphemes:
        families["Morfemas"] = {
            "description": "Componentes estructurales (no estandar UD)",
            "color": GROUP_COLORS.get("morfemas", "#3b82f6"),
            "labels": active_morphemes,
        }

    # Features agrupados por tipo
    _feature_family_names = {
        "Abbr":      "Abreviacion",
        "Aspect":    "Aspecto",
        "Case":      "Caso",
        "Clusivity": "Clusividad",
        "Definite":  "Definitud",
        "Foreign":   "Extranjerismo",
        "Mood":      "Modo",
        "Nasality":  "Nasalidad",
        "Number":    "Numero",
        "Other":     "Otros",
        "Person":    "Persona",
        "Polarity":  "Polaridad",
        "Poss":      "Posesion",
        "PronType":  "Tipo de Pronombre",
        "Tense":     "Tiempo",
        "Typo":      "Erratas",
        "VerbForm":  "Forma Verbal",
        "Voice":     "Voz",
        "Rel":       "Relacional",
        "Nomzr":     "Nominalizadores",
        "Corf":      "Correferencia",
        "Evident":   "Evidencialidad",
        "Emph":      "Enfasis",
        "Intens":    "Intensificador",
        "Priv":      "Privativo",
        "Red":       "Reduplicacion",
        "Int":       "Interrogativo",
        "Reflex":    "Reflexivo",
    }

    for group_key, feat_list in FEATURES.items():
        active = [f for f, _u, a in feat_list if a]
        if active:
            name = _feature_family_names.get(group_key, group_key)
            families[name] = {
                "description": f"{group_key} (UD Feature)",
                "color": GROUP_COLORS.get(group_key, "#64748b"),
                "labels": active,
            }

    # POS tags como familia
    active_pos = [f for f, _u, a in POS_TAGS if a]
    if active_pos:
        families["Categoria (UPOS)"] = {
            "description": "Universal POS Tags",
            "color": GROUP_COLORS.get("pos-tags", "#dc2626"),
            "labels": active_pos,
        }

    return families


LABEL_FAMILIES = _build_label_families()


# =============================================================================
# LABEL_COLORS (color por etiqueta individual)
# =============================================================================

LABEL_COLORS = {}
for _family_name, _family_data in LABEL_FAMILIES.items():
    _base_color = _family_data["color"]
    for _label in _family_data["labels"]:
        LABEL_COLORS[_label] = _base_color

# Colores especificos para relaciones
for _friendly, _ud, _active in DEPENDENCY_RELATIONS:
    if _active and _friendly in RELATION_COLORS:
        LABEL_COLORS[_friendly] = RELATION_COLORS[_friendly]


# =============================================================================
# FAMILY_KEYS (claves cortas para CLI)
# =============================================================================

FAMILY_KEYS = {}
_short_key_map = {
    "Morfemas": "morfema",
    "Persona": "persona",
    "Numero": "numero",
    "Clusividad": "clusividad",
    "Caso": "caso",
    "Relacional": "relacional",
    "Tiempo": "tiempo",
    "Aspecto": "aspecto",
    "Modo": "modo",
    "Voz": "voz",
    "Forma Verbal": "forma",
    "Polaridad": "polaridad",
    "Posesion": "posesion",
    "Nominalizadores": "nominalizador",
    "Categoria (UPOS)": "categoria",
    "Nasalidad": "nasalidad",
    "Abreviacion": "abreviacion",
    "Extranjerismo": "extranjerismo",
    "Erratas": "errata",
    "Correferencia": "correferencia",
    "Evidencialidad": "evidencialidad",
    "Enfasis": "enfasis",
    "Intensificador": "intensificador",
    "Privativo": "privativo",
    "Reduplicacion": "reduplicacion",
    "Interrogativo": "interrogativo",
    "Reflexivo": "reflexivo",
    "Tipo de Pronombre": "prontype",
    "Otros": "otros",
    "Definitud": "definitud",
}

for _family_name in LABEL_FAMILIES:
    _short = _short_key_map.get(_family_name, _family_name.lower().replace(" ", "_"))
    FAMILY_KEYS[_short] = _family_name


# =============================================================================
# SPECIALIZED_GROUPS (para los recipes de Prodigy)
# =============================================================================

def _build_specialized_groups():
    groups = {}

    # Grupo: POS Tags
    active_pos = [(f, u) for f, u, a in POS_TAGS if a]
    groups["pos-tags"] = {
        "name": "POS Tags",
        "description": "Categorias gramaticales (Universal POS Tags)",
        "color": GROUP_COLORS.get("pos-tags", "#dc2626"),
        "labels": [f for f, _u in active_pos],
        "ud_mapping": {f: u for f, u in active_pos},
    }

    # Grupo: Features (todos los activos juntos)
    feat_labels = []
    feat_mapping = {}
    for _gk, feat_list in FEATURES.items():
        for friendly, ud, active in feat_list:
            if active:
                feat_labels.append(friendly)
                feat_mapping[friendly] = ud

    groups["features"] = {
        "name": "Features",
        "description": "Rasgos morfologicos (Morphological Features)",
        "color": GROUP_COLORS.get("features", "#8b5cf6"),
        "labels": feat_labels,
        "ud_mapping": feat_mapping,
    }

    # Grupo: Relations
    active_rels = [(f, u) for f, u, a in DEPENDENCY_RELATIONS if a]
    rel_colors = {}
    for f, _u in active_rels:
        if f in RELATION_COLORS:
            rel_colors[f] = RELATION_COLORS[f]

    groups["relations"] = {
        "name": "Relaciones Sintacticas",
        "description": "Relaciones de dependencia (Dependency Relations)",
        "color": GROUP_COLORS.get("relations", "#22c55e"),
        "labels": [f for f, _u in active_rels],
        "ud_mapping": {f: u for f, u in active_rels},
        "colors": rel_colors,
    }

    # Grupo: Morfemas
    active_morph = [(f, u) for f, u, a in MORPHEMES if a]
    groups["morfemas"] = {
        "name": "Morfemas",
        "description": "Segmentacion morfologica (no estandar UD)",
        "color": GROUP_COLORS.get("morfemas", "#3b82f6"),
        "labels": [f for f, _u in active_morph],
        "ud_mapping": {f: u for f, u in active_morph},
    }

    # Subgrupos de features para anotacion por partes
    _subgroups = {
        "features-persona-numero": {
            "name": "Persona y Numero",
            "description": "Person, Number, Clusivity",
            "color": GROUP_COLORS.get("Person", "#8b5cf6"),
            "feat_keys": ["Person", "Number", "Clusivity"],
        },
        "features-caso": {
            "name": "Caso",
            "description": "Case features",
            "color": GROUP_COLORS.get("Case", "#f97316"),
            "feat_keys": ["Case"],
        },
        "features-tam": {
            "name": "Tiempo, Aspecto, Modo",
            "description": "Tense, Aspect, Mood, VerbForm, Voice",
            "color": GROUP_COLORS.get("Tense", "#eab308"),
            "feat_keys": ["Tense", "Aspect", "Mood", "VerbForm", "Voice"],
        },
        "features-relacional": {
            "name": "Relacional",
            "description": "Rel (Tupi-Guarani especifico)",
            "color": GROUP_COLORS.get("Rel", "#6366f1"),
            "feat_keys": ["Rel"],
        },
        "features-nominalizadores": {
            "name": "Nominalizadores",
            "description": "Nomzr (Tupi-Guarani especifico)",
            "color": GROUP_COLORS.get("Nomzr", "#a855f7"),
            "feat_keys": ["Nomzr"],
        },
        "features-otros": {
            "name": "Otros Features",
            "description": "Polarity, Poss, Priv, etc.",
            "color": GROUP_COLORS.get("Polarity", "#64748b"),
            "feat_keys": [
                "Polarity", "Poss", "Priv", "Red", "Reflex",
                "Corf", "Emph", "Intens", "Evident", "Int",
                "Nasality", "Abbr", "Foreign", "Typo", "Other",
            ],
        },
    }

    for sg_key, sg_conf in _subgroups.items():
        labels = []
        for fk in sg_conf["feat_keys"]:
            if fk in FEATURES:
                labels.extend([f for f, _u, a in FEATURES[fk] if a])
        if labels:
            groups[sg_key] = {
                "name": sg_conf["name"],
                "description": sg_conf["description"],
                "color": sg_conf["color"],
                "labels": labels,
            }

    return groups


SPECIALIZED_GROUPS = _build_specialized_groups()

UD_MAIN_GROUPS = {
    "pos-tags":  SPECIALIZED_GROUPS["pos-tags"],
    "features":  SPECIALIZED_GROUPS["features"],
    "relations": SPECIALIZED_GROUPS["relations"],
    "morfemas":  SPECIALIZED_GROUPS["morfemas"],
}


# =============================================================================
# FUNCIONES PUBLICAS (no modificar firmas, las usan los recipes)
# =============================================================================

def map_label(label: str, direction: str = "to_ud") -> str:
    """Mapea una etiqueta entre formato amigable y UD."""
    if direction == "to_ud":
        if label in FRIENDLY_TO_UD:
            return FRIENDLY_TO_UD[label]
        # Buscar case-insensitive
        label_lower = label.lower()
        for friendly, ud in FRIENDLY_TO_UD.items():
            if friendly.lower() == label_lower:
                return ud
        # Si ya es UD valido, devolverlo tal cual
        if label in VALID_UPOS or label in VALID_FEATURES:
            return label
        return "X"
    else:  # to_friendly
        if label in UD_TO_FRIENDLY:
            return UD_TO_FRIENDLY[label]
        if label in FRIENDLY_TO_UD:
            return label
        return "Otro"


def map_labels_batch(labels: list, direction: str = "to_ud") -> list:
    """Mapea multiples etiquetas."""
    return [map_label(label, direction) for label in labels]


def is_valid_ud(label: str) -> bool:
    """Verifica si una etiqueta es un UPOS o Feature valido."""
    return label in VALID_UPOS or label in VALID_FEATURES


def get_all_friendly_labels() -> list:
    """Retorna todas las etiquetas amigables."""
    return list(FRIENDLY_TO_UD.keys())


def get_all_ud_labels() -> list:
    """Retorna todas las etiquetas UD (sin duplicados)."""
    return list(set(FRIENDLY_TO_UD.values()))


def get_family_labels(family_key: str) -> list:
    """Obtiene las etiquetas de una familia por su clave corta."""
    family_key_lower = family_key.lower()

    # Buscar por clave corta
    if family_key_lower in FAMILY_KEYS:
        full_name = FAMILY_KEYS[family_key_lower]
        if full_name in LABEL_FAMILIES:
            return LABEL_FAMILIES[full_name]["labels"]

    # Fallback: buscar por nombre parcial
    for name, data in LABEL_FAMILIES.items():
        if family_key_lower in name.lower():
            return data["labels"]
    return []


def get_specialized_group(group_key: str) -> dict | None:
    """Obtiene informacion de un grupo especializado."""
    return SPECIALIZED_GROUPS.get(group_key.lower())


def get_ud_main_group(group_key: str) -> dict | None:
    """Obtiene info de un grupo UD principal (pos-tags, features, relations, morfemas)."""
    return UD_MAIN_GROUPS.get(group_key.lower())


def get_ud_main_labels(group_key: str) -> list:
    """Obtiene las etiquetas de un grupo UD principal."""
    group = UD_MAIN_GROUPS.get(group_key.lower())
    if group:
        return group.get("labels", [])
    return []


def list_ud_main_groups() -> dict:
    """Lista todos los grupos UD principales: {key: name}."""
    return {key: group["name"] for key, group in UD_MAIN_GROUPS.items()}


def get_all_ud_ordered_labels() -> list:
    """Obtiene todas las etiquetas ordenadas: POS -> Features -> Morfemas."""
    ordered = []
    for key in ("pos-tags", "features", "morfemas"):
        group = UD_MAIN_GROUPS.get(key, {})
        ordered.extend(group.get("labels", []))
    return ordered


def get_ud_label_colors() -> dict:
    """Genera colores para cada etiqueta segun su grupo UD."""
    colors = {}
    for _key, group in UD_MAIN_GROUPS.items():
        group_color = group.get("color", "#6b7280")
        for label in group.get("labels", []):
            colors[label] = group_color
    return colors


def get_specialized_labels(group_key: str) -> list:
    """Obtiene las etiquetas de un grupo especializado."""
    group = SPECIALIZED_GROUPS.get(group_key.lower())
    if group:
        return group["labels"]
    return []


def list_specialized_groups() -> dict:
    """Retorna todos los grupos especializados: {key: name}."""
    return {key: group["name"] for key, group in SPECIALIZED_GROUPS.items()}


# =============================================================================
# TEST
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("UD Guarani Mapper - Test")
    print("=" * 60)

    test_labels = [
        "Raiz", "Prefijo", "Pronombre", "Verbo",
        "1ra Persona", "Locativo", "Imperativo"
    ]

    print("\nMapeo Amigable -> UD:")
    for label in test_labels:
        ud = map_label(label, "to_ud")
        print(f"  {label:25} -> {ud}")

    print("\nMapeo UD -> Amigable:")
    for ud_tag in ["VERB", "NOUN", "Person=1", "Case=Loc"]:
        friendly = map_label(ud_tag, "to_friendly")
        print(f"  {ud_tag:25} -> {friendly}")

    print("\nFamilias disponibles:")
    for key, full_name in FAMILY_KEYS.items():
        labels = get_family_labels(key)
        print(f"  {key:20} -> {len(labels)} etiquetas")

    print("\nGrupos especializados:")
    for key, name in list_specialized_groups().items():
        labels = get_specialized_labels(key)
        print(f"  {key:30} -> {name} ({len(labels)} etiquetas)")

    print(f"\nTotal POS activos:      {len(VALID_UPOS)}")
    print(f"Total Features activos: {len(VALID_FEATURES)}")
    print(f"Total en FRIENDLY_TO_UD: {len(FRIENDLY_TO_UD)}")
    print("\nMapper OK")
