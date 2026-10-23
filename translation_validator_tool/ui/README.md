# Frontend — Translation Validator

React and Vite frontend for the Translation Validator application.

## Quick start

Start at the repository root. Copy the environment template only during initial setup.

**Windows — PowerShell:**

```powershell
cd translation_validator_tool/ui
npm install
copy .env.example .env
# Edit .env and set VITE_API_URL (for example, http://localhost:8000/api).
npm run dev
```

**Linux/macOS — Bash:**

```bash
cd translation_validator_tool/ui
npm install
cp .env.example .env
# Edit .env and set VITE_API_URL (for example, http://localhost:8000/api).
npm run dev
```

## Build and preview

From `translation_validator_tool/ui/`, on either operating system:

```bash
npm run build
npm run preview
```

## Environment variables

- `VITE_API_URL` — Backend API URL, for example `http://localhost:8000/api`.
- `DEV_ALLOWED_HOSTS` — Optional additional hostnames for Vite's development server,
  comma-separated and without a scheme or path, for example
  `demo.example.org,preview.example.org`. Localhost and IP addresses do not need
  to be added. This variable does not configure production hosting. To allow the
  frontend to access the backend, also set `CORS_ORIGINS` in `api/.env`.

### Override tooltip text

The application provides configurable tooltip text for Guarani sentence
classification. Override the defaults with Vite environment variables in `.env`.
The classification names below match the terminology used in the interface.

- Guaraní puro:
  - `VITE_TOOLTIP_GUARANI_PURO_TITLE` — Short title, such as "Guaraní puro".
  - `VITE_TOOLTIP_GUARANI_PURO_DESC` — Longer description.
  - `VITE_TOOLTIP_GUARANI_PURO_EXAMPLE` — Optional example.
- Jopara:
  - `VITE_TOOLTIP_JOPARA_TITLE`
  - `VITE_TOOLTIP_JOPARA_DESC`
  - `VITE_TOOLTIP_JOPARA_EXAMPLE`
- Jehe'a:
  - `VITE_TOOLTIP_JEHEA_TITLE`
  - `VITE_TOOLTIP_JEHEA_DESC`
  - `VITE_TOOLTIP_JEHEA_EXAMPLE`

The `.env.example` file includes sample values. Vite reads environment variables
when it starts: restart `npm run dev` or rebuild with `npm run build` after editing
`.env` for the changes to take effect.

## Available scripts

- `npm run dev` — Start the development server.
- `npm run build` — Build the frontend for production.
- `npm run preview` — Preview the production build locally.
- `npm run lint` — Run ESLint if its configuration is available.

## Help

The application does not require the original institutional logos or videos.
Written translation instructions are shared between the sign-in help modal and
the translation help page through
[`TranslationHelpContent.jsx`](src/components/common/TranslationHelpContent.jsx).
Validation instructions are maintained in
[`ValidatorHelpPage.jsx`](src/pages/ValidatorHelpPage.jsx).
Instance-specific support contacts should be maintained by each installation.

## Component layout

```text
src/
├── components/
│   ├── auth/          # Sign-in and authentication components
│   ├── common/        # Shared components
│   ├── suggestion/    # Translation suggestions
│   └── translation/   # Validation interface
├── pages/             # Page components
├── services/          # API services
├── context/           # React context
└── hooks/             # Custom hooks
```
