🎯 MEJORAS PARA CALIDAD DE ANOTACIONES GUARANÍ (Multi-anotador)
Basándome en la documentación y tu proyecto actual, te propongo 5 mejoras clave para alimentar tu BD con oraciones anotadas de calidad:

1️⃣ Task Routing con overlap parcial (annotations_per_task)
Qué implementar:

Configurar annotations_per_task: 2 → cada oración la ven 2 anotadores (overlap parcial para calcular inter-annotator agreement).
Agregar task_router que usa hash determinista (_task_hash % len(pool)) para asignar oraciones consistentemente.
Predefinir sesiones con PRODIGY_ALLOWED_SESSIONS=alice,bob,carlos.
Por qué mejora calidad: Te permite detectar desacuerdos entre anotadores y resolver ambigüedades antes de entrenar modelos. Además evita sesgos de un solo anotador.

2️⃣ Validate_answer callback (validación en tiempo real)
Qué implementar:

Callback que valida que cada oración aceptada tenga al menos 1 SUJETO y 1 VERBO.
Si falta, muestra error y pide corrección antes de guardar.
Por qué mejora calidad: Impide guardar anotaciones incompletas o erróneas. El anotador recibe feedback inmediato.

3️⃣ Script de Quality Control (inter-annotator agreement)
Qué implementar:

Script scripts/calculate_iaa.py que:
Exporta anotaciones con _session_id (identifica quién anotó cada ejemplo).
Calcula Cohen's Kappa para pares de anotadores (en spans con mismo _task_hash).
Detecta outliers (anotadores con mucha discrepancia).
Genera reporte markdown con métricas por anotador.
Por qué mejora calidad: Identifica anotadores que necesitan re-entrenamiento o guidelines más claros. También detecta oraciones problemáticas (bajo agreement) que necesitan revisión.

4️⃣ Review workflow (doble-check de anotaciones conflictivas)
Qué implementar:

Script scripts/export_conflicts.py que:
Filtra oraciones donde 2 anotadores difirieron (ej: uno marcó SUJETO diferente).
Exporta a nuevo JSONL (data/export/conflicts.jsonl).
Recipe especial guarani-pos-review que:
Muestra ambas anotaciones lado a lado (HTML custom).
Supervisor elige la correcta o crea versión gold-standard.
Por qué mejora calidad: Las anotaciones con desacuerdo son las más valiosas para entrenamiento (ejemplos difíciles). El review asegura gold-standard.

5️⃣ Sync controlado a PostgreSQL + tracking de calidad
Qué implementar:

Modificar sync_prodigy_to_db.py para:
Solo sincronizar oraciones con answer: accept y que pasaron validación.
Agregar campo quality_score calculado como:
1.0 si 2 anotadores coinciden 100%.
0.5-0.9 si hay discrepancias menores.
0 si requiere review.
Agregar reviewed_by (supervisor que validó conflictos).
Por qué mejora calidad: Tu PostgreSQL solo recibe anotaciones de alta calidad verificadas. Puedes filtrar por quality_score al entrenar modelos.

🚀 Implementación concreta
Voy a crear 4 archivos nuevos:

recipes/guarani_pos_tagging_v2.py — recipe con task_router + validate_answer
scripts/calculate_iaa.py — calcula inter-annotator agreement
scripts/export_conflicts.py — filtra oraciones con desacuerdo
scripts/quality_sync_to_db.py — sync con quality score
¿Quieres que genere estos 4 archivos ahora? (Te mostraré el código completo listo para usar + comandos PowerShell para probarlo)