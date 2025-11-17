"""
Recipe personalizado para demostrar validación de traducciones
Simula el flujo de validación Guaraní-Español usando titulares en inglés
"""

import prodigy
from prodigy.components.loaders import JSONL


@prodigy.recipe(
    "translation-demo",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
)
def translation_demo(dataset, source):
    """
    Demo: Simular validación de traducciones con scoring y categorización
    
    Este recipe muestra cómo crear una interfaz personalizada similar
    a la que necesitamos para validar traducciones Guaraní-Español.
    
    Uso:
        prodigy translation-demo my_dataset data/news_headlines.jsonl.txt -F recipes/translation_demo.py
    """
    
    stream = JSONL(source)
    
    # Agregar HTML personalizado y campos extra
    def add_custom_fields(stream):
        for example in stream:
            source_text = example.get('meta', {}).get('source', 'Unknown')
            
            example["html"] = f"""
            <div style="max-width: 800px; margin: 0 auto; padding: 20px; font-family: 'Segoe UI', Arial, sans-serif;">
                
                <!-- Encabezado -->
                <div style="background: #f0f9ff; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #0284c7;">
                    <h3 style="margin: 0 0 5px 0; color: #0c4a6e;">📰 Headline to Review</h3>
                    <p style="margin: 0; color: #64748b; font-size: 13px;">Simula el flujo de validación de traducción</p>
                </div>
                
                <!-- Texto principal -->
                <div style="background: white; padding: 20px; border-radius: 8px; border: 2px solid #e2e8f0; margin-bottom: 20px;">
                    <p style="font-size: 18px; line-height: 1.6; color: #1e293b; margin: 0;">
                        <strong>English:</strong> {example['text']}
                    </p>
                </div>
                
                <!-- Metadata -->
                <div style="display: flex; gap: 15px; margin-bottom: 20px;">
                    <div style="flex: 1; background: #fef3c7; padding: 10px; border-radius: 6px;">
                        <strong style="color: #92400e;">📝 Source:</strong>
                        <p style="margin: 5px 0 0 0; color: #78350f;">{source_text}</p>
                    </div>
                </div>
                
                <!-- Instrucciones -->
                <div style="background: #f1f5f9; padding: 12px; border-radius: 6px; margin-top: 20px;">
                    <p style="margin: 0; font-size: 13px; color: #475569;">
                        💡 <strong>Instrucciones:</strong> Evalúa la calidad del titular. 
                        En el caso real, aquí verías el texto en Guaraní y su traducción al Español.
                    </p>
                </div>
                
            </div>
            """
            yield example
    
    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": add_custom_fields(stream),
        "config": {
            "blocks": [
                {"view_id": "html"},
                {
                    "view_id": "choice",
                    "text": None,
                    "options": [
                        {"id": "excellent", "text": "⭐⭐⭐⭐⭐ EXCELLENT"},
                        {"id": "good", "text": "⭐⭐⭐⭐ GOOD"},
                        {"id": "fair", "text": "⭐⭐⭐ FAIR"},
                        {"id": "poor", "text": "⭐⭐ POOR"},
                        {"id": "very_poor", "text": "⭐ VERY_POOR"}
                    ]
                }
            ],
            "choice_style": "single",
            "choice_auto_accept": False
        }
    }


@prodigy.recipe(
    "translation-validation",
    dataset=("Dataset to save annotations", "positional", None, str),
    source=("Source data (JSONL file)", "positional", None, str),
)
def translation_validation(dataset, source):
    """
    Recipe avanzado: Validación completa con múltiples criterios
    Más cercano al flujo real de validación Guaraní-Español
    
    Uso:
        prodigy translation-validation my_dataset data/news_headlines.jsonl.txt -F recipes/translation_demo.py
    """
    
    stream = JSONL(source)
    
    def add_validation_interface(stream):
        for example in stream:
            source_text = example.get('meta', {}).get('source', 'Unknown')
            
            example["html"] = f"""
            <div style="max-width: 1000px; margin: 0 auto; padding: 15px; font-family: 'Segoe UI', Arial, sans-serif;">
                
                <!-- Header compacto -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 15px; border-radius: 8px; margin-bottom: 15px;">
                    <h3 style="margin: 0; font-size: 18px;">🌐 Validación de Traducción</h3>
                </div>
                
                <!-- Textos lado a lado -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 12px;">
                    
                    <!-- Guaraní -->
                    <div style="background: #ecfdf5; padding: 15px; border-radius: 8px; border-left: 4px solid #10b981;">
                        <h4 style="margin: 0 0 10px 0; color: #047857; font-size: 14px;">🇵🇾 Guaraní</h4>
                        <p style="font-size: 17px; line-height: 1.6; color: #065f46; margin: 0;">
                            {example['text']}
                        </p>
                    </div>
                    
                    <!-- Español -->
                    <div style="background: #fef3c7; padding: 15px; border-radius: 8px; border-left: 4px solid #f59e0b;">
                        <h4 style="margin: 0 0 10px 0; color: #92400e; font-size: 14px;">🇪🇸 Español</h4>
                        <p style="font-size: 17px; line-height: 1.6; color: #78350f; margin: 0;">
                            <strong>Source:</strong> {source_text}<br>
                            <em>En el caso real, aquí verías la traducción al español</em>
                        </p>
                    </div>
                    
                </div>
                
                <!-- Criterios compactos -->
                <div style="background: #f0f9ff; padding: 10px 15px; border-radius: 6px; font-size: 12px; color: #0c4a6e; margin-bottom: 10px;">
                    <strong>📋 Evalúa:</strong> Correctness (¿significado correcto?) · Fluency (¿natural?) · Accuracy (¿precisa?)
                </div>
                
            </div>
            """
            yield example
    
    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": add_validation_interface(stream),
        "config": {
            "blocks": [
                {"view_id": "html"},
                {
                    "view_id": "choice",
                    "text": "Overall Quality:",
                    "options": [
                        {"id": "correct_fluent", "text": "✅ CORRECT & FLUENT"},
                        {"id": "correct_improvement", "text": "⚠️ CORRECT BUT NEEDS IMPROVEMENT"},
                        {"id": "incorrect", "text": "❌ INCORRECT"},
                        {"id": "needs_review", "text": "🤔 NEEDS REVIEW"}
                    ]
                }
            ],
            "choice_style": "single",
            "choice_auto_accept": False
        }
    }
