#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para generar lotes de oraciones para anotación.

Genera N lotes de M oraciones cada uno desde el dataset original.
MANTIENE EL ORDEN ORIGINAL del archivo JSONL para preservar el contexto.

Uso:
    python scripts/generate_batches.py --total 3000 --batch-size 50
    python scripts/generate_batches.py --total 3000 --batch-size 50 --shuffle --seed 42
    
Esto genera 60 lotes de 50 oraciones cada uno (3000 total).
"""

import json
import random
import argparse
from pathlib import Path


def load_jsonl(filepath: str) -> list:
    """Carga un archivo JSONL con encoding UTF-8."""
    examples = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(json.loads(line))
    return examples


def save_jsonl(examples: list, filepath: str):
    """Guarda ejemplos a un archivo JSONL."""
    with open(filepath, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")


def generate_batches(
    input_file: str,
    output_dir: str,
    total_sentences: int = 3000,
    batch_size: int = 50,
    seed: int = 42,
    shuffle: bool = False,
):
    """
    Genera lotes de oraciones desde el dataset original.
    
    Args:
        input_file: Ruta al archivo JSONL original
        output_dir: Directorio donde guardar los lotes
        total_sentences: Total de oraciones a seleccionar
        batch_size: Oraciones por lote
        seed: Semilla para reproducibilidad (solo si shuffle=True)
        shuffle: Si es True, mezcla aleatoriamente; si es False, mantiene orden original
    """
    print(f"📂 Cargando datos de: {input_file}")
    all_examples = load_jsonl(input_file)
    print(f"   Total disponible: {len(all_examples)} oraciones")
    
    if total_sentences > len(all_examples):
        print(f"⚠️ Solo hay {len(all_examples)} oraciones, ajustando total.")
        total_sentences = len(all_examples)
    
    # Seleccionar oraciones (en orden o aleatorio)
    if shuffle:
        print(f"🔀 Modo ALEATORIO con semilla {seed}")
        random.seed(seed)
        selected = random.sample(all_examples, total_sentences)
    else:
        print(f"📋 Modo SECUENCIAL - manteniendo orden original del JSONL")
        selected = all_examples[:total_sentences]
    
    # Calcular número de lotes
    num_batches = (total_sentences + batch_size - 1) // batch_size
    
    print(f"\n📊 Configuración:")
    print(f"   Total oraciones: {total_sentences}")
    print(f"   Tamaño de lote: {batch_size}")
    print(f"   Número de lotes: {num_batches}")
    print(f"   Orden: {'aleatorio' if shuffle else 'secuencial (original)'}")
    if shuffle:
        print(f"   Semilla: {seed}")
    
    # Crear directorio de salida
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generar lotes
    print(f"\n📦 Generando lotes en: {output_dir}")
    
    for batch_num in range(1, num_batches + 1):
        start_idx = (batch_num - 1) * batch_size
        end_idx = min(start_idx + batch_size, total_sentences)
        
        batch_examples = selected[start_idx:end_idx]
        
        # Agregar metadata del lote a cada ejemplo
        for i, ex in enumerate(batch_examples):
            ex["meta"]["batch_id"] = batch_num
            ex["meta"]["batch_index"] = i + 1
            ex["meta"]["global_index"] = start_idx + i + 1
        
        # Guardar lote
        batch_file = output_path / f"batch_{batch_num:03d}.jsonl"
        save_jsonl(batch_examples, str(batch_file))
        
        print(f"   ✅ Lote {batch_num:02d}: {len(batch_examples)} oraciones → {batch_file.name}")
    
    # Crear archivo de índice
    index_file = output_path / "batches_index.json"
    index_data = {
        "seed": seed if shuffle else None,
        "shuffle": shuffle,
        "total_sentences": total_sentences,
        "batch_size": batch_size,
        "num_batches": num_batches,
        "source_file": str(input_file),
        "order": "random" if shuffle else "sequential",
        "batches": [
            {
                "batch_id": i,
                "file": f"batch_{i:03d}.jsonl",
                "sentences": min(batch_size, total_sentences - (i-1)*batch_size),
                "global_start": (i-1) * batch_size + 1,
                "global_end": min(i * batch_size, total_sentences),
            }
            for i in range(1, num_batches + 1)
        ]
    }
    
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📋 Índice guardado en: {index_file}")
    print(f"\n✅ ¡Listo! {num_batches} lotes generados.")
    
    return num_batches


def main():
    parser = argparse.ArgumentParser(
        description="Genera lotes de oraciones para anotación"
    )
    parser.add_argument(
        "--input", "-i",
        default="data/export/original_translations.jsonl",
        help="Archivo JSONL de entrada"
    )
    parser.add_argument(
        "--output", "-o",
        default="data/batches",
        help="Directorio de salida para los lotes"
    )
    parser.add_argument(
        "--total", "-t",
        type=int,
        default=3000,
        help="Total de oraciones a seleccionar (default: 3000)"
    )
    parser.add_argument(
        "--batch-size", "-b",
        type=int,
        default=50,
        help="Oraciones por lote (default: 50)"
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=42,
        help="Semilla para reproducibilidad (default: 42, solo si --shuffle)"
    )
    parser.add_argument(
        "--shuffle",
        action="store_true",
        help="Mezclar aleatoriamente (por defecto mantiene orden original)"
    )
    
    args = parser.parse_args()
    
    generate_batches(
        input_file=args.input,
        output_dir=args.output,
        total_sentences=args.total,
        batch_size=args.batch_size,
        seed=args.seed,
        shuffle=args.shuffle,
    )


if __name__ == "__main__":
    main()
