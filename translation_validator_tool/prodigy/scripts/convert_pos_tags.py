"""
Script para convertir anotaciones entre etiquetas internas y UPOS

Convierte archivos JSONL/JSON entre etiquetas internas (español) y 
Universal Dependencies (UPOS), manteniendo toda la metadata y estructura.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

# Importar el módulo de mapeo
from pos_tag_mapper import (
    convert_spans_to_upos,
    convert_spans_to_internal,
    INTERNAL_TO_UPOS,
    UPOS_TO_INTERNAL
)


def convert_jsonl_to_upos(input_file: str, output_file: str, verbose: bool = False):
    """
    Convierte archivo JSONL con etiquetas internas a UPOS.
    
    Args:
        input_file: Ruta al archivo JSONL de entrada
        output_file: Ruta al archivo JSONL de salida
        verbose: Mostrar detalles de conversión
    """
    converted_count = 0
    span_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as f_in, \
         open(output_file, 'w', encoding='utf-8') as f_out:
        
        for line_num, line in enumerate(f_in, 1):
            try:
                example = json.loads(line)
                
                # Convertir spans si existen
                if 'spans' in example and example['spans']:
                    original_spans = example['spans']
                    converted_spans = convert_spans_to_upos(original_spans)
                    example['spans'] = converted_spans
                    
                    span_count += len(converted_spans)
                    converted_count += 1
                    
                    if verbose:
                        print(f"Línea {line_num}: {len(original_spans)} spans convertidos")
                        for span in converted_spans:
                            orig = span.get('original_label', '')
                            upos = span.get('upos', '')
                            text = span.get('text', '')
                            print(f"  • '{text}': {orig} → {upos}")
                
                # Agregar metadata de conversión
                if 'meta' not in example:
                    example['meta'] = {}
                example['meta']['converted_to_upos'] = True
                example['meta']['conversion_source'] = 'internal_spanish'
                
                # Escribir línea convertida
                f_out.write(json.dumps(example, ensure_ascii=False) + '\n')
                
            except json.JSONDecodeError as e:
                print(f"Error en línea {line_num}: {e}", file=sys.stderr)
                continue
            except Exception as e:
                print(f"Error procesando línea {line_num}: {e}", file=sys.stderr)
                continue
    
    print(f"\n✓ Conversión completada:")
    print(f"  • Ejemplos convertidos: {converted_count}")
    print(f"  • Total spans: {span_count}")
    print(f"  • Archivo de salida: {output_file}")


def convert_jsonl_to_internal(input_file: str, output_file: str, verbose: bool = False):
    """
    Convierte archivo JSONL con etiquetas UPOS a internas (español).
    
    Args:
        input_file: Ruta al archivo JSONL de entrada
        output_file: Ruta al archivo JSONL de salida
        verbose: Mostrar detalles de conversión
    """
    converted_count = 0
    span_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as f_in, \
         open(output_file, 'w', encoding='utf-8') as f_out:
        
        for line_num, line in enumerate(f_in, 1):
            try:
                example = json.loads(line)
                
                # Convertir spans si existen
                if 'spans' in example and example['spans']:
                    original_spans = example['spans']
                    converted_spans = convert_spans_to_internal(original_spans)
                    example['spans'] = converted_spans
                    
                    span_count += len(converted_spans)
                    converted_count += 1
                    
                    if verbose:
                        print(f"Línea {line_num}: {len(original_spans)} spans convertidos")
                        for span in converted_spans:
                            upos = span.get('upos', '')
                            internal = span.get('internal_label', '')
                            text = span.get('text', '')
                            print(f"  • '{text}': {upos} → {internal}")
                
                # Agregar metadata de conversión
                if 'meta' not in example:
                    example['meta'] = {}
                example['meta']['converted_to_internal'] = True
                example['meta']['conversion_source'] = 'upos'
                
                # Escribir línea convertida
                f_out.write(json.dumps(example, ensure_ascii=False) + '\n')
                
            except json.JSONDecodeError as e:
                print(f"Error en línea {line_num}: {e}", file=sys.stderr)
                continue
            except Exception as e:
                print(f"Error procesando línea {line_num}: {e}", file=sys.stderr)
                continue
    
    print(f"\n✓ Conversión completada:")
    print(f"  • Ejemplos convertidos: {converted_count}")
    print(f"  • Total spans: {span_count}")
    print(f"  • Archivo de salida: {output_file}")


def convert_json_report(input_file: str, output_file: str, direction: str = "to_upos", verbose: bool = False):
    """
    Convierte archivo JSON (reporte con metadata) entre formatos.
    
    Args:
        input_file: Ruta al archivo JSON de entrada
        output_file: Ruta al archivo JSON de salida
        direction: 'to_upos' o 'to_internal'
        verbose: Mostrar detalles de conversión
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    converted_count = 0
    span_count = 0
    
    # Convertir ejemplos
    if 'examples' in report:
        for example in report['examples']:
            if 'spans' in example and example['spans']:
                if direction == "to_upos":
                    example['spans'] = convert_spans_to_upos(example['spans'])
                else:
                    example['spans'] = convert_spans_to_internal(example['spans'])
                
                span_count += len(example['spans'])
                converted_count += 1
    
    # Actualizar metadata
    if 'metadata' not in report:
        report['metadata'] = {}
    
    report['metadata']['label_format'] = 'upos' if direction == "to_upos" else 'internal_spanish'
    report['metadata']['conversion_direction'] = direction
    
    # Guardar archivo convertido
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Conversión de reporte completada:")
    print(f"  • Ejemplos convertidos: {converted_count}")
    print(f"  • Total spans: {span_count}")
    print(f"  • Formato: {report['metadata']['label_format']}")
    print(f"  • Archivo de salida: {output_file}")


def show_statistics(file_path: str):
    """
    Muestra estadísticas de las etiquetas en un archivo.
    
    Args:
        file_path: Ruta al archivo JSONL o JSON
    """
    from collections import Counter
    
    label_counts = Counter()
    total_examples = 0
    total_spans = 0
    
    file_ext = Path(file_path).suffix.lower()
    
    try:
        if file_ext == '.jsonl':
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    example = json.loads(line)
                    total_examples += 1
                    if 'spans' in example:
                        for span in example['spans']:
                            label = span.get('label', 'UNKNOWN')
                            label_counts[label] += 1
                            total_spans += 1
        
        elif file_ext == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'examples' in data:
                    for example in data['examples']:
                        total_examples += 1
                        if 'spans' in example:
                            for span in example['spans']:
                                label = span.get('label', 'UNKNOWN')
                                label_counts[label] += 1
                                total_spans += 1
        
        print(f"\n{'='*60}")
        print(f"ESTADÍSTICAS: {Path(file_path).name}")
        print(f"{'='*60}")
        print(f"Total ejemplos: {total_examples}")
        print(f"Total spans: {total_spans}")
        print(f"\nDistribución de etiquetas:")
        print(f"{'-'*60}")
        print(f"{'ETIQUETA':<30} {'CANTIDAD':<15} {'%'}")
        print(f"{'-'*60}")
        
        for label, count in label_counts.most_common():
            percentage = (count / total_spans * 100) if total_spans > 0 else 0
            print(f"{label:<30} {count:<15} {percentage:>5.1f}%")
        
        print(f"{'='*60}\n")
        
        # Detectar formato
        sample_labels = set(label_counts.keys())
        is_upos = any(label in ['VERB', 'NOUN', 'ADJ', 'ADV', 'PRON'] for label in sample_labels)
        is_internal = any(label in ['VERBO', 'SUSTANTIVO', 'SUJETO', 'OBJETO'] for label in sample_labels)
        
        if is_upos:
            print("✓ Formato detectado: UPOS (Universal Dependencies)")
        elif is_internal:
            print("✓ Formato detectado: INTERNO (Español)")
        else:
            print("⚠ Formato no detectado claramente")
    
    except Exception as e:
        print(f"Error analizando archivo: {e}", file=sys.stderr)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Convertir anotaciones entre etiquetas internas (español) y UPOS"
    )
    
    parser.add_argument(
        "input",
        help="Archivo de entrada (.jsonl o .json)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Archivo de salida (por defecto: input_converted.ext)"
    )
    
    parser.add_argument(
        "--direction", "-d",
        choices=["to_upos", "to_internal"],
        default="to_upos",
        help="Dirección de conversión (por defecto: to_upos)"
    )
    
    parser.add_argument(
        "--stats", "-s",
        action="store_true",
        help="Mostrar estadísticas del archivo sin convertir"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Mostrar detalles de conversión"
    )
    
    args = parser.parse_args()
    
    # Determinar archivo de salida
    if not args.output:
        input_path = Path(args.input)
        suffix = "_upos" if args.direction == "to_upos" else "_internal"
        args.output = str(input_path.parent / f"{input_path.stem}{suffix}{input_path.suffix}")
    
    # Mostrar estadísticas si se solicita
    if args.stats:
        show_statistics(args.input)
        if not args.output:
            sys.exit(0)
    
    # Convertir archivo
    file_ext = Path(args.input).suffix.lower()
    
    try:
        if file_ext == '.jsonl':
            if args.direction == "to_upos":
                convert_jsonl_to_upos(args.input, args.output, args.verbose)
            else:
                convert_jsonl_to_internal(args.input, args.output, args.verbose)
        
        elif file_ext == '.json':
            convert_json_report(args.input, args.output, args.direction, args.verbose)
        
        else:
            print(f"Error: Formato de archivo no soportado: {file_ext}", file=sys.stderr)
            print("Formatos soportados: .jsonl, .json", file=sys.stderr)
            sys.exit(1)
        
        # Mostrar estadísticas del archivo convertido
        if not args.stats:
            print("\nEstadísticas del archivo convertido:")
            show_statistics(args.output)
    
    except FileNotFoundError:
        print(f"Error: Archivo no encontrado: {args.input}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error durante la conversión: {e}", file=sys.stderr)
        sys.exit(1)
