# Translation Validator — Application

This directory contains the **Mbo'ehara Digital — GuaranIA** application.
The main guide is maintained in the [repository README](../README.md).

- **Public instance:** [mboehara.guarania.org](https://mboehara.guarania.org).
- **Installation and prerequisites:** [installation](../README.md#installation).
- **Opening an activity:** [configure PROJECT_CLOSED](../README.md#opening-and-closing-an-activity).
- **Importing your own data:** [getting started](../README.md#getting-started).
- **Contributions:** [contributing](../README.md#contributing).
- **Origins and attribution:** [NOTICE](../NOTICE).

## Components

| Directory | Contents | Documentation |
| --- | --- | --- |
| `api/` | FastAPI API, models, and importers. | [Backend](api/README.md) |
| `ui/` | React and Vite interface. | [Frontend](ui/README.md) |
| `db_schema/` | PostgreSQL initialization and migrations. | [Database](db_schema/README.md) |
| `metrics/` | Metrics, reports, and exports. | [Metrics](metrics/README.md) |
| `scripts/` | Corpus extraction utilities. | [JSON/JSONL-to-CSV extractor](scripts/extract_json_to_csv.py) |

Campaign datasets and reports are not distributed with the code. Each installation
must configure its own database and import its own content.
Prodigy is not required for the workflow used by GuaranIA.
