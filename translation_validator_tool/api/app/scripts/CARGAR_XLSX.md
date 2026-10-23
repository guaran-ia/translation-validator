# Importing annotations from Excel

## Description

The `app.scripts.load_annotations` script imports annotations from an `.xlsx` file.
This command-line importer expects the fixed layout below. The administrative
interface supports choosing worksheets and mapping columns instead.

## Expected workbook format

### Required worksheet

- **Name:** `train_mgsm_es_to_gn`.

### Expected columns

Use row 1 for headers and start data in row 2.

| Column | Field | Type | Required |
| --- | --- | --- | --- |
| A | ID | Ignored | No |
| B | `question_es` | Text | At least one text field |
| D | `answer_es` | Text | At least one text field |
| F | `answer_number` | Integer | No |
| G | `equation_solution` | Text | No |

At least one of `question_es` or `answer_es` must contain a value. They cannot both be empty.

## Usage

### Option 1: Run as a Python module

From `translation_validator_tool/api/`, with the backend environment active:

```bash
python -m app.scripts.load_annotations --file /path/to/file.xlsx
```

### Option 2: Start from db_schema using the API environment

**Windows — PowerShell:**

```powershell
cd ..\api
..\api\venv\Scripts\python.exe -m app.scripts.load_annotations --file /path/to/file.xlsx
```

**Linux/macOS — Bash:**

```bash
cd ../api
../api/venv/bin/python -m app.scripts.load_annotations --file /path/to/file.xlsx
```

Replace `/path/to/file.xlsx` with the path to your own workbook.

## Example output

The source text in the question and answer remains in Spanish:

```text
Loading annotations from /path/to/file.xlsx...
✅ Found sheet 'train_mgsm_es_to_gn'
✓ Row 2: Created annotation ID 1
   Q: Roger tiene 5 pelotas de tenis...
   A: Respuesta paso a paso: Roger comenzó con 5...
   Equation: 5 + 6 = 11
✓ Row 3: Created annotation ID 2
   ...
✓ Reached end of data at row 11

============================================================
✅ Successfully loaded 9 annotations
⚠️  Skipped 0 rows
============================================================
```

## Error handling

- **File not found:** displays the path it attempted to open.
- **Worksheet not found:** lists the available worksheets.
- **Invalid row:** skips the row and reports why.
- **Duplicate data:** skips the record and reports that it already exists.
- **Insertion error:** reports the database error and continues processing as implemented by the importer.
