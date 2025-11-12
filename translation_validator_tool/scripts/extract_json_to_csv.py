#!/usr/bin/env python3
"""
extract_json_to_csv.py

Improved script to support newline-delimited JSON (.jsonl) and plain JSON.

Behavior summary:
 - Reads base CSV (defaults to `data/translations.csv`). It will not overwrite the base CSV.
 - Reads an input JSON or JSONL file (you must keep that file local and do not commit it).
 - For each item (each JSON object) it extracts sentences ending with a single '.' while ignoring ellipses ('...' and '…').
 - Keeps sentences of at most N words (default 30, words = tokens separated by spaces).
 - Samples up to M sentences per item (default 50), no duplicates per item.
 - Writes a new CSV (default `data/jojajovai_with_json_rows.csv`) containing the original rows plus appended rows with extra metadata
   columns: `corpus`, `corpus_file`, `url`, `language`.

Usage examples:
  python extract_json_to_csv.py --input data/coreguapa_identified_gn.jsonl
  python extract_json_to_csv.py --input data/coreguapa_identified_gn.jsonl --out data/trans_with_coreguapa.csv --max-sentences 50

"""

import argparse
import csv
import json
import os
import random
import re
import shutil
import sys
from typing import List, Iterable


def extract_sentences(text: str) -> List[str]:
    """Extract candidate sentences ending with a single '.' while ignoring ellipses.

    Approach:
    - Normalize newlines to spaces.
    - Replace '...' and '…' with a placeholder token so they don't split sentences.
    - Find fragments that end with a '.' (single dot).
    - Restore ellipsis placeholder and strip whitespace.
    """
    if not text:
        return []
    txt = text.replace('\n', ' ').replace('\r', ' ')
    ELLIP = '<ELLIPSIS>'
    txt = txt.replace('...', ELLIP).replace('…', ELLIP)
    fragments = re.findall(r"[^.]*\.", txt)
    sentences = []
    for frag in fragments:
        s = frag.strip()
        if not s:
            continue
        s = s.replace(ELLIP, '…')
        sentences.append(s)
    return sentences


def valid_sentence_by_wordcount(s: str, max_words: int = 30) -> bool:
    tokens = [t for t in s.strip().split(' ') if t]
    return 0 < len(tokens) <= max_words


def normalize_whitespace(s: str) -> str:
    return ' '.join(s.split())


def read_existing_csv(csv_path: str):
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        orig_fieldnames = reader.fieldnames or []
    return rows, orig_fieldnames


def write_new_csv(output_path: str, orig_rows, orig_fieldnames, appended_rows, new_fieldnames):
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames, extrasaction='ignore')
        writer.writeheader()
        for r in orig_rows:
            out = {k: r.get(k, '') for k in orig_fieldnames}
            for nf in new_fieldnames:
                if nf not in out:
                    out[nf] = ''
            writer.writerow(out)
        for r in appended_rows:
            writer.writerow(r)


def iter_jsonl(path: str) -> Iterable[dict]:
    with open(path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                print(f"[warn] skipping invalid json on line {i+1}")


def process_items(items: Iterable[dict], max_sentences_per_item=50, max_words=30):
    appended = []
    for idx, item in enumerate(items):
        text = item.get('text') or item.get('txt') or ''
        corpus = item.get('corpus', '')
        corpus_file = item.get('corpus_file', '')
        src = item.get('source', '')
        url = item.get('url', '')
        language = item.get('language', '')

        sentences = extract_sentences(text)
        filtered = [normalize_whitespace(s) for s in sentences if valid_sentence_by_wordcount(s, max_words)]
        seen = set()
        unique = []
        for s in filtered:
            if s not in seen:
                seen.add(s)
                unique.append(s)
        if not unique:
            print(f"[info] item {idx}: no sentences <= {max_words} words, skipping")
            continue
        if len(unique) > max_sentences_per_item:
            sampled = random.sample(unique, max_sentences_per_item)
        else:
            sampled = unique
        for s in sampled:
            row = {
                'split': 'train',
                'source': src or corpus or 'jsonl',
                'gn': s,
                'es': '',
                'tokens_gn': s,
                'tokens_es': '',
                'corpus': corpus,
                'corpus_file': corpus_file,
                'url': url,
                'language': language,
            }
            appended.append(row)
        print(f"[info] item {idx}: extracted {len(sampled)} sentences (candidates {len(unique)})")
    return appended


def main():
    ap = argparse.ArgumentParser(description='Extract sentences from JSON/JSONL and append to CSV')
    ap.add_argument('--input', required=True, help='Path to input JSON or JSONL file (DO NOT COMMIT)')
    ap.add_argument('--csv', default='data/translations.csv', help='Path to original CSV')
    ap.add_argument('--out', default='data/coreguapa_appended_only.csv', help='Output CSV path (new file)')
    ap.add_argument('--include-original', action='store_true', help='Include original rows from base CSV in the output (default: do NOT include originals)')
    ap.add_argument('--max-sentences', type=int, default=50, help='Max sentences per item')
    ap.add_argument('--max-words', type=int, default=30, help='Max words per sentence')
    ap.add_argument('--force', action='store_true', help='Overwrite output if exists (default: create .bak)')
    args = ap.parse_args()

    if not os.path.exists(args.input):
        print(f"ERROR: input file not found: {args.input}")
        sys.exit(2)
    if not os.path.exists(args.csv):
        print(f"ERROR: base CSV not found: {args.csv}")
        sys.exit(2)

    print(f"[info] reading base CSV: {args.csv}")
    orig_rows, orig_fieldnames = read_existing_csv(args.csv)

    print(f"[info] parsing input: {args.input}")
    # decide json vs jsonl by extension or by trying to load
    items_iter = None
    lower = args.input.lower()
    if lower.endswith('.jsonl') or lower.endswith('.ndjson'):
        items_iter = iter_jsonl(args.input)
    else:
        # try plain json load
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, dict):
            items_iter = iter([data])
        elif isinstance(data, list):
            items_iter = iter(data)
        else:
            print('ERROR: unexpected JSON structure (object or list expected)')
            sys.exit(2)

    new_fieldnames = list(orig_fieldnames) + ['corpus', 'corpus_file', 'url', 'language']

    appended_rows = process_items(items_iter, max_sentences_per_item=args.max_sentences, max_words=args.max_words)

    # Prevent accidental overwrite of the base CSV
    if os.path.abspath(args.out) == os.path.abspath(args.csv) and not args.force:
        print(f"ERROR: output path (--out) must not be the same as the base CSV (--csv). To overwrite, pass --force.")
        sys.exit(2)

    if os.path.exists(args.out):
        if args.force:
            print(f"[info] Overwriting existing {args.out} because --force is set")
        else:
            bak = args.out + '.bak'
            print(f"[info] output {args.out} exists, creating backup {bak}")
            shutil.copy2(args.out, bak)

    appended_only = not args.include_original

    if appended_only:
        # Default behavior: write only appended rows (do not duplicate original CSV)
        print(f"[info] Writing only appended rows to {args.out} (default behavior)")
        os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
        with open(args.out, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=new_fieldnames, extrasaction='ignore')
            writer.writeheader()
            for r in appended_rows:
                writer.writerow(r)
        print(f"Done. Wrote {len(appended_rows)} appended rows to {args.out}")
    else:
        # include original rows in the output (opt-in)
        write_new_csv(args.out, orig_rows, orig_fieldnames, appended_rows, new_fieldnames)
        print(f"Done. Wrote {len(orig_rows)} original rows + {len(appended_rows)} appended rows to {args.out}")


if __name__ == '__main__':
    main()
