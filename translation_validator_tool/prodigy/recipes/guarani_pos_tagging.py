"""
Recipe para anotación gramatical (POS Tagging) en textos Guaraní
Permite identificar: Sujetos, Verbos, Objetos, Adjetivos, etc.
"""

import prodigy
from prodigy.components.loaders import JSONL
from prodigy.components.preprocess import add_tokens
from prodigy.util import set_hashes
import spacy

# Cargar modelo de spaCy para tokenización
nlp = spacy.blank("es")  # Modelo vacío español (funciona para Guaraní)


@prodigy.recipe(
    "guarani-pos",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
)
def guarani_pos_tagging(dataset, source):
    """
    Anotar categorías gramaticales en textos Guaraní
    
    Uso:
        prodigy guarani-pos pos_annotations data/export/original_translations.jsonl -F recipes/guarani_pos_tagging.py
    """
    
    stream = JSONL(source)
    
    def prepare_for_pos(stream):
        for example in stream:
            # Usar el texto en Guaraní
            guarani_text = example.get('text', '')
            spanish_text = example.get('meta', {}).get('spanish_text', '')
            
            # Tokenizar el texto
            doc = nlp(guarani_text)
            tokens = [{"text": token.text, "start": token.idx, "end": token.idx + len(token.text), "id": i}
                     for i, token in enumerate(doc)]
            
            example["text"] = guarani_text
            example["tokens"] = tokens
            example = set_hashes(example)
            example["html"] = f"""
            <div style="max-width: 900px; margin: 0 auto; padding: 10px; font-family: 'Segoe UI', Arial, sans-serif;">
                
                <!-- Header muy compacto -->
                <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 8px 12px; border-radius: 6px; margin-bottom: 10px;">
                    <h4 style="margin: 0; font-size: 15px;">🏷️ Anotación Gramatical</h4>
                </div>
                
                <!-- Referencia en Español (compacta) -->
                <div style="background: #fef3c7; padding: 10px 12px; border-radius: 6px; margin-bottom: 10px; border-left: 3px solid #f59e0b;">
                    <strong style="color: #92400e; font-size: 12px;">🇪🇸 Referencia:</strong>
                    <span style="color: #78350f; font-size: 13px; margin-left: 8px;">{spanish_text}</span>
                </div>
                
                <!-- Tip compacto -->
                <div style="background: #f0f9ff; padding: 8px 12px; border-radius: 6px; font-size: 11px; color: #0c4a6e; margin-bottom: 10px;">
                    <strong>💡</strong> Selecciona palabras abajo: SUJETO (quien) · VERBO (acción) · OBJETO (qué/quién)
                </div>
                
            </div>
            """
            yield example
    
    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": prepare_for_pos(stream),
        "config": {
            "blocks": [
                {"view_id": "html"},
                {"view_id": "ner_manual"}
            ],
            "labels": [
                "SUJETO",
                "VERBO", 
                "OBJETO",
                "SUSTANTIVO",
                "ADJETIVO",
                "ADVERBIO",
                "PRONOMBRE",
                "PREPOSICIÓN",
                "ARTÍCULO",
                "CONJUNCIÓN"
            ]
        }
    }


@prodigy.recipe(
    "guarani-syntax",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
)
def guarani_syntax_analysis(dataset, source):
    """
    Análisis sintáctico simplificado para Guaraní
    Identifica componentes principales de la oración
    
    Uso:
        prodigy guarani-syntax syntax_annotations data/export/original_translations.jsonl -F recipes/guarani_pos_tagging.py
    """
    
    stream = JSONL(source)
    
    def prepare_for_syntax(stream):
        for example in stream:
            guarani_text = example.get('text', '')
            spanish_text = example.get('meta', {}).get('spanish_text', '')
            
            # Tokenizar el texto
            doc = nlp(guarani_text)
            tokens = [{"text": token.text, "start": token.idx, "end": token.idx + len(token.text), "id": i}
                     for i, token in enumerate(doc)]
            
            example["text"] = guarani_text
            example["tokens"] = tokens
            example = set_hashes(example)
            example["html"] = f"""
            <div style="max-width: 900px; margin: 0 auto; padding: 10px; font-family: 'Segoe UI', Arial, sans-serif;">
                
                <!-- Header muy compacto -->
                <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 8px 12px; border-radius: 6px; margin-bottom: 10px;">
                    <h4 style="margin: 0; font-size: 15px;">🔍 Análisis Sintáctico</h4>
                </div>
                
                <!-- Referencia en Español (compacta) -->
                <div style="background: #fef3c7; padding: 10px 12px; border-radius: 6px; margin-bottom: 10px; border-left: 3px solid #f59e0b;">
                    <strong style="color: #92400e; font-size: 12px;">🇪🇸 Traducción:</strong>
                    <span style="color: #78350f; font-size: 13px; margin-left: 8px;">{spanish_text}</span>
                </div>
                
                <!-- Tip compacto -->
                <div style="background: #fff7ed; padding: 8px 12px; border-radius: 6px; font-size: 11px; color: #92400e; margin-bottom: 10px;">
                    <strong>🎯</strong> SUJETO (¿quién?) · PREDICADO (verbo+info) · OD (¿qué?) · OI (¿a quién?)
                </div>
                
            </div>
            """
            yield example
    
    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": prepare_for_syntax(stream),
        "config": {
            "blocks": [
                {"view_id": "html"},
                {"view_id": "ner_manual"}
            ],
            "labels": [
                "SUJETO",
                "PREDICADO",
                "OD",
                "OI", 
                "COMPLEMENTO_LUGAR",
                "COMPLEMENTO_TIEMPO",
                "COMPLEMENTO_MODO",
                "COMPLEMENTO_OTRO"
            ]
        }
    }
