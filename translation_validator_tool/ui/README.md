# Frontend README

## Translation Validator Frontend

React + Vite frontend for the Translation Validator application.

### Quick Start

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API URL
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   ```

4. **Build for Production**
   ```bash
   npm run build
   ```

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Environment Variables

- `VITE_API_URL` - Backend API URL (default: http://localhost:8000/api)

### Features

- ✅ JWT Authentication
- ✅ Translation validation interface
- ✅ Progress tracking
- ✅ Suggestion system
- ✅ Responsive design
- ✅ Real-time error handling

### Component Structure

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