# Metrics and reports

Install dependencies from this directory with
`python -m pip install -r requirements_metrics.txt` using your usual virtual environment.

The three reporting scripts read `DATABASE_URL` from the environment or
`../api/.env`, regardless of the current working directory. An exported environment
variable takes precedence over the file. These scripts do not require `SECRET_KEY`.
If `DATABASE_URL` is missing, they report a configuration error without connecting.
PostgreSQL URLs and SQLAlchemy URLs with a `+psycopg` or `+psycopg2` suffix are supported.

Examples from this directory:

```bash
python metrics_report.py
python ranking_translations_report.py --help
python generar_problemas_guarani.py
```

Results are saved in `documents/`. The problem generator also requires your local
corpus at `../../data/data.xlsx`, with the worksheets `test_mgsm_es_to_gn` and
`train_mgsm_es_to_gn`. This dataset is not distributed through Git.

## Running on Linux/macOS

```bash
bash run_metrics.sh
```

The script uses `python3` from the active environment. To use a different
interpreter, set `METRICS_PYTHON` to its executable path without additional arguments:

```bash
METRICS_PYTHON=/path/to/venv/bin/python bash run_metrics.sh
```

By default, reports are kept locally. To enable uploads, install and configure
rclone and provide your own destination:

```bash
METRICS_DRIVE_REMOTE='myremote:reports' bash run_metrics.sh
```

`METRICS_PYTHON` and `METRICS_DRIVE_REMOTE` are shell or scheduler environment
variables; they are not read from `api/.env`. Logs are saved in
`logsMetrics/metrics_report.log`. The script does not install dependencies and
does not require a particular pyenv path or Linux username.
