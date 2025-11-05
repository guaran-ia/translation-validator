# Frontend — Translation Validator (README)

React + Vite frontend para la aplicación Translation Validator.

### Quick Start (Windows / Linux)

Windows (PowerShell):
```powershell
cd translation_validator_tool/ui
npm install
copy .env.example .env
# Edita .env y configura VITE_API_URL (ej: http://localhost:8000/api)
npm run dev
```

Linux / macOS (bash):
```bash
cd translation_validator_tool/ui
npm install
cp .env.example .env
# Edita .env y configura VITE_API_URL (ej: http://localhost:8000/api)
npm run dev
```

### Build / Preview

Windows (PowerShell):
```powershell
npm run build
npm run preview
```

Linux / macOS (bash):
```bash
npm run build
npm run preview
```

### Environment variables

- `VITE_API_URL` — Backend API URL (por ejemplo: `http://localhost:8000/api`)

### Scripts disponibles

- `npm run dev` — iniciar servidor de desarrollo
- `npm run build` — generar build de producción
- `npm run preview` — previsualizar build de producción
- `npm run lint` — ejecutar ESLint (si está configurado)

### Estructura de componentes (resumen)

```
src/
├── components/
│   ├── auth/          # Login/auth components
│   ├── common/        # Shared components
│   ├── suggestion/    # Translation suggestions
│   └── translation/   # Main validation interface
├── pages/             # Page components
├── services/          # API services
├── context/           # React context
└── hooks/             # Custom hooks
```