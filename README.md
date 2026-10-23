# Mbo'ehara Digital

A collaborative web platform for translating, validating, and enriching Guarani language resources. It helps organize a community of translators and validators, collect translations, and assess their quality to build corpora for research and language technologies.

**Public instance:** [mboehara.guarania.org](https://mboehara.guarania.org).

## Table of contents

- [Features](#features)
- [Installation](#installation)
  - [Technology stack and architecture](#technology-stack-and-architecture)
  - [Prerequisites](#prerequisites)
  - [1. Clone the repository](#1-clone-the-repository)
  - [2. Set up the backend](#2-set-up-the-backend)
  - [3. Initialize the database](#3-initialize-the-database)
  - [4. Set up the frontend](#4-set-up-the-frontend)
  - [5. Start the frontend](#5-start-the-frontend)
  - [Build the frontend](#build-the-frontend)
- [Getting started](#getting-started)
  - [Default administrator](#default-administrator)
  - [Questions and answers: importing through the interface](#questions-and-answers-importing-through-the-interface)
  - [Sentence corpus: CSV import](#sentence-corpus-csv-import)
  - [Metrics and further documentation](#metrics-and-further-documentation)
- [Configuration](#configuration)
  - [Environment variables](#environment-variables)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [Opening and closing an activity](#opening-and-closing-an-activity)
- [Screenshots](#screenshots)
  - [Signing in](#signing-in)
  - [Selecting tasks and translating](#selecting-tasks-and-translating)
  - [Validating translations](#validating-translations)
  - [Leaderboards](#leaderboards)
- [Project origins and GuaranIA modifications](#project-origins-and-guarania-modifications)
- [Contributing](#contributing)
- [License and attribution](#license-and-attribution)

## Features

| Area | Capabilities |
| --- | --- |
| Collaborative translation | Choose pending tasks, assign them to yourself, and translate questions and answers from Spanish into Guarani. Includes buttons for inserting Guarani characters. |
| Multiple contributions | Collect up to three translations from different users for each annotation. |
| Validation | Compare the original text and its translation; rate it as correct, fair, or incorrect, and score fluency and accuracy from 1 to 5. The workflow supports three validations per translation. |
| Suggestions | Propose alternative translations, explain assessments, and add notes. |
| Administration | Manage users, roles, and tasks; create content and import Excel files with worksheet selection and column mapping. |
| Participation | View your tasks, history, and weekly and all-time translation and validation leaderboards. |
| Help | Access written guides for translators and validators. |
| Reports | Generate metrics and export Word, Excel, CSV, and JSON files using additional scripts. |
| Activity closure | Display a closing page with a participation summary. |

Contributors have the `ambos` role and can switch between translation and validation. Administrators manage users and content.

## Installation

### Technology stack and architecture

| Component | Technologies |
| --- | --- |
| Interface | React 18, Vite 5, React Router 6, Tailwind CSS 3, Axios, and React Toastify. |
| API | Python, FastAPI, Uvicorn, and Pydantic 2. |
| Persistence | PostgreSQL, SQLAlchemy 2, and Alembic. |
| Authentication | JWT with python-jose; password hashing with Passlib and bcrypt. |
| Imports | pandas and openpyxl for CSV and Excel files. |
| Metrics | Python scripts using python-docx, openpyxl, and matplotlib. |

```text
translation-validator/
├── README.md
├── LICENSE
├── NOTICE
├── screenshots/                  Platform screenshots
└── translation_validator_tool/
    ├── api/                      API, models, and importers
    ├── ui/                       React interface
    ├── db_schema/                Initialization and migrations
    ├── metrics/                  Reports and exports
    └── scripts/                  Corpus extraction utilities
```

### Prerequisites

- Git.
- Python and pip. Use Python 3.12 as the reference version for setting up your environment.
- Node.js and npm. Use Node.js 22 as the reference version for the frontend.
- A running PostgreSQL server and a connection with permission to create and migrate tables. The initializer also connects to the `postgres` database and can create the application database if the user has the `CREATEDB` privilege.

### 1. Clone the repository

```bash
git clone https://github.com/guaran-ia/translation-validator.git
cd translation-validator
```

### 2. Set up the backend

Starting at the repository root, choose the commands for your operating system.

**Windows — PowerShell:**

```powershell
cd translation_validator_tool/api
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

**Linux/macOS — Bash:**

```bash
cd translation_validator_tool/api
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Before initializing the database, fill in `api/.env` following the [backend configuration](#backend). Copy the template only during initial setup.

### 3. Initialize the database

In the same terminal, with the virtual environment active and your working directory set to `api/`:

```bash
cd ../db_schema
python init_database.py init
```

The initializer creates the database if necessary, runs Alembic migrations, and creates the default administrator if no users exist. Then start the API:

```bash
cd ../api
python -m uvicorn app.main:app --reload --port 8000
```

The API also runs initialization at startup. It requires access to PostgreSQL and permission to apply migrations.

- Interactive API documentation: [localhost:8000/docs](http://localhost:8000/docs).
- ReDoc documentation: [localhost:8000/redoc](http://localhost:8000/redoc).
- API health endpoint: [localhost:8000/health](http://localhost:8000/health).

### 4. Set up the frontend

Open **another terminal at the repository root**.

**Windows — PowerShell:**

```powershell
cd translation_validator_tool/ui
npm install
Copy-Item .env.example .env
```

**Linux/macOS — Bash:**

```bash
cd translation_validator_tool/ui
npm install
cp .env.example .env
```

Set up `ui/.env` following the [frontend configuration](#frontend). To accept contributions, also review [opening and closing an activity](#opening-and-closing-an-activity).

### 5. Start the frontend

From `ui/`, start the development server:

```bash
npm run dev
```

Open [localhost:5173](http://localhost:5173). Keep both terminals open to use the interface and API.

### Build the frontend

From `translation_validator_tool/ui/`:

```bash
npm run build
```

The output is generated in `ui/dist/`. Run `npm run preview` to inspect it locally. Changes to frontend environment variables or `PROJECT_CLOSED` require rebuilding the frontend.

## Getting started

### Default administrator

If no users exist, the initializer creates the following account:

| Field | Value |
| --- | --- |
| Username | `admin` |
| Initial password | `4dm!n$Pass` |
| Full name | `Administrador` |

The initial password is shared across new installations. Change it through user administration before making your instance publicly accessible.

To create another administrator, run the following from `translation_validator_tool/api/`, with the virtual environment active and the database initialized:

```bash
python -m app.scripts.create_admin --username otro-admin --email admin@example.org --password "tu-clave-propia" --nombre-completo "Nombre del administrador"
```

`--nombre-completo` sets the administrator's full name. Replace the example username, email, password, and full name with your own values.

### Questions and answers: importing through the interface

1. Sign in as an administrator and open **Anotaciones** (Annotations, `/admin/annotations`).
2. Create an annotation manually or upload your `.xlsx` file.
3. For Excel files, select the worksheet, inspect the preview, and map its columns to the platform's fields.
4. Import the content. Users can then select tasks, translate them, and validate translations.

| Import field | Content |
| --- | --- |
| `question_es` | Question or prompt in Spanish. |
| `answer_es` | Answer in Spanish, when applicable. |
| `answer_number` | Numeric answer for mathematical problems; optional. |
| `equation_solution` | Mathematical expression or solution; optional. |
| `md5` | Content identifier; optional. |

The interface lets you choose your own column mapping. The alternative `app.scripts.load_annotations` script expects a specific worksheet and column layout.

### Sentence corpus: CSV import

Use a UTF-8 CSV file for the sentence-corpus workflow:

```csv
guarani,spanish,source
Mba'éichapa reiko?,¿Cómo estás?,ejemplo
```

Save it locally, for example as `data/mi_corpus.csv` at the repository root, creating the directory if needed. From `api/`, with the virtual environment active:

```bash
python -m app.scripts.load_corpus --file ../../data/mi_corpus.csv
```

### Metrics and further documentation

Metrics scripts use your `DATABASE_URL` and generate local reports. Uploading through rclone is optional and requires a destination that you configure.

- [Backend: configuration and importers](translation_validator_tool/api/README.md).
- [Frontend: scripts and configurable help text](translation_validator_tool/ui/README.md).
- [Database: initialization, migrations, and backups](translation_validator_tool/db_schema/README.md).
- [Metrics, exports, and scheduled execution](translation_validator_tool/metrics/README.md).

## Configuration

### Environment variables

| File | Variable | Purpose |
| --- | --- | --- |
| `api/.env` | `DATABASE_URL` | Required. PostgreSQL connection URL. |
| `api/.env` | `SECRET_KEY` | Required. JWT signing key. |
| `api/.env` | `CORS_ORIGINS` | Allowed frontend origins as a JSON array. |
| `api/.env` | `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime; default: `1440`. |
| `api/.env` | `PROJECT_NAME`, `VERSION` | Application name and version published by the API. |
| `api/.env` | `SMTP_*` | Optional. Notify administrators of new registrations. |
| `ui/.env` | `VITE_API_URL` | API URL, including `/api`. |
| `ui/.env` | `DEV_ALLOWED_HOSTS` | Optional. Additional development hostnames, comma-separated, without a scheme or path. |
| `ui/.env` | `VITE_TOOLTIP_*` | Optional. Help text for Guarani classification. |

### Backend

Copy the template only during initial setup. Edit `api/.env` with your PostgreSQL connection URL and your own token-signing key:

```dotenv
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/translation_validator
SECRET_KEY=reemplaza-este-valor-por-una-clave-aleatoria
CORS_ORIGINS=["http://localhost:5173"]
```

Generate a key with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Replace the sample values, including `SECRET_KEY`. Reserved URL characters in the PostgreSQL password must be URL-encoded in `DATABASE_URL`.

### Frontend

In `ui/.env`, set the API URL, including the `/api` suffix:

```dotenv
VITE_API_URL=http://localhost:8000/api
```

### Opening and closing an activity

The repository retains the closed-activity setting used by GuaranIA. To enable sign-in and registration on your instance, edit [`ui/src/config/projectStatus.js`](translation_validator_tool/ui/src/config/projectStatus.js):

```js
export const PROJECT_CLOSED = false;
```

When set to `true`, the home page displays the activity's closing summary, and the login and registration routes redirect there. This is a frontend setting; it does not disable API endpoints. After changing it, rebuild the frontend if you are using a production installation.

## Screenshots

These historical screenshots show the platform during translation and validation
activities and retain the original campaign branding. New installations use the
generic logo described above.

### Signing in

![Mbo'ehara Digital sign-in page](screenshots/auth.png)

### Selecting tasks and translating

![List of available translation tasks](screenshots/translate1.png)

![Translation editor with Guarani character buttons](screenshots/translate2.png)

### Validating translations

![Original text and translation with quality assessment](screenshots/validate.png)

![Explanation of a fair translation assessment](screenshots/validate1.png)

![Fluency and accuracy scores](screenshots/validate2.png)

![Translation improvement form](screenshots/validate3.png)

### Leaderboards

![Weekly participation leaderboard](screenshots/leaderboard.png)

## Project origins and GuaranIA modifications

This platform is based on the tool used by the **Universidad Nacional de Itapúa (UNI)** for its **Lacuna Fund** translation hackathon:

- **Original repository:** [aalvarez-fiuni/guarani-corpus-lacuna-uni](https://github.com/aalvarez-fiuni/guarani-corpus-lacuna-uni).
- **Original UNI instance:** [guarani.uni.edu.py](https://guarani.uni.edu.py/login).

GuaranIA used that repository as a starting point and maintains a modified version for its translation and validation activities. Work to make this version reusable includes environment-based configuration, administrator creation adjustments, disabling hackathon promotion, and separating instance data, reports, and unused legacy modules.

We acknowledge the work of the original authors. See [NOTICE](NOTICE) for attribution details and the scope of GuaranIA's contributions.

## Contributing

Contributions are welcome, including bug fixes, accessibility improvements, documentation, importers, and workflow improvements.

1. Check existing [issues](https://github.com/guaran-ia/translation-validator/issues). For a substantial change, open an issue describing the problem and your proposed behavior first.
2. Fork the repository, clone your fork, and create a branch:

   ```bash
   git switch -c feature/description
   ```

3. Set up your local environment, make a focused change, and update the documentation where appropriate.
4. Check the frontend build with `npm run build` from `ui/`. If you change the API, verify the affected workflow using a development database. For schema changes, add an Alembic migration following the [database guide](translation_validator_tool/db_schema/README.md).
5. Open a pull request against `main`, describing the problem, your changes, and how you verified them. Include screenshots for interface changes.

Do not commit `.env` files, credentials, personal data, instance datasets, or generated reports. Use fictional data when reproducing issues.

When reporting a bug, include reproduction steps, expected and actual behavior, and relevant versions, without secrets or personal data. Feature requests can also be submitted as issues.

## License and attribution

GuaranIA's own contributions are offered under the [Apache License 2.0](LICENSE). See [NOTICE](NOTICE) for the project's origins, modifications, and the scope of this statement. Dependencies and third-party materials retain their respective rights and terms.
