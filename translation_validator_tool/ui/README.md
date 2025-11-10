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

#### Override tooltip texts (optional)

La aplicación usa textos configurables para las descripciones "tooltip" de la clasificación de oraciones en guaraní. Puedes sobrescribir los valores por defecto mediante variables de entorno Vite. Añade estas claves a tu `.env` si quieres personalizar los textos:

- Guaraní puro
	- `VITE_TOOLTIP_GUARANI_PURO_TITLE` — Título corto (p. ej. "Guaraní puro")
	- `VITE_TOOLTIP_GUARANI_PURO_DESC` — Descripción más larga
	- `VITE_TOOLTIP_GUARANI_PURO_EXAMPLE` — Ejemplo opcional

- Jopara
	- `VITE_TOOLTIP_JOPARA_TITLE`
	- `VITE_TOOLTIP_JOPARA_DESC`
	- `VITE_TOOLTIP_JOPARA_EXAMPLE`

- Jehe'a
	- `VITE_TOOLTIP_JEHEA_TITLE`
	- `VITE_TOOLTIP_JEHEA_DESC`
	- `VITE_TOOLTIP_JEHEA_EXAMPLE`

Hemos incluido un `.env.example` con valores de ejemplo. Nota importante: Vite sólo lee las variables en tiempo de arranque, así que después de cambiar `.env` necesitas reiniciar el servidor de desarrollo (`npm run dev`) o reconstruir (`npm run build`) para que los cambios surtan efecto.

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