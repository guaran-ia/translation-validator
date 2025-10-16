# Translation Validator Tool - Reorganized Structure

A web application for validating and enriching a Guaraní-Spanish translation dataset. This tool is designed for research teams to generate high-quality corpus data for training AI translation models.

## 📁 Project Structure

```
translation_validator_tool/
├── api/          # Backend API (FastAPI)
├── ui/           # Frontend (React + Vite)  
├── db_schema/    # Database migrations and schema
└── README.md     # This file
```

## 🚀 Features

- **Bilingual Translation Validation**: Evaluate Guaraní ↔ Spanish translation pairs
- **Multi-criteria Scoring**: Rate translations on correctness, fluency, and accuracy
- **Suggestion System**: Submit improved translations with reasoning
- **Progress Tracking**: Monitor validation progress with detailed statistics
- **User Management**: JWT-based authentication and user sessions
- **Responsive Design**: Clean, accessible interface built with React and Tailwind CSS

## 🏗️ Tech Stack

### Backend (api/)
- **FastAPI 0.104+** - Modern Python web framework
- **SQLAlchemy 2.0** - ORM with Alembic migrations
- **PostgreSQL 14+** - Primary database
- **JWT Authentication** - Secure user sessions
- **Pydantic** - Data validation and serialization

### Frontend (ui/)
- **React 18.x** - UI framework
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client with interceptors
- **React Router** - Client-side routing

### Database (db_schema/)
- **Alembic** - Database migration management
- **PostgreSQL** - Production database

## 📋 Prerequisites

### System Requirements
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Git

### Development Tools
- Code editor
- Terminal/Command prompt
- PostgreSQL client (pgAdmin, DBeaver, etc.)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/translation-validator-tool.git
cd translation-validator-tool
```

### 2. API Setup (Backend)

#### Navigate to api directory
```bash
cd api
```

#### Create and activate virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Install dependencies
```bash
pip install -r requirements.txt
```

#### Configure environment variables
```bash
# Copy example environment file
copy .env.example .env

# Edit .env file with your configuration
# DATABASE_URL=postgresql://your_user:your_password@localhost:5432/translation_validator
# SECRET_KEY=your-super-secret-key-change-this-in-production
```

### 3. Database Setup

#### Create database (using PostgreSQL client)
```bash
createdb translation_validator
```

#### Run migrations from db_schema directory
```bash
cd ../db_schema
alembic upgrade head

# Create admin user (optional)
python -m app.scripts.create_admin --username admin --email admin@example.com --password adminpass

# Load sample data (optional)
python -m app.scripts.load_corpus --sample
```

### 3. Frontend Setup

#### Navigate to frontend directory
```bash
cd ../frontend
```

#### Install dependencies
```bash
npm install
```

#### Configure environment
```bash
# Copy example environment file
copy .env.example .env

# Edit .env file
# VITE_API_URL=http://localhost:8000/api
```

## 🚀 Running the Application

### Start Backend Server
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

### Start Frontend Development Server
```bash
cd frontend
npm run dev
```

The frontend will be available at:
- **Application**: http://localhost:5173

## 📊 Loading Data

### Load Sample Data
```bash
cd backend
python -m app.scripts.load_corpus --sample
```

### Load Custom Dataset
```bash
# Prepare your CSV file with columns: guarani,spanish,source
# Example: corpus.csv
python -m app.scripts.load_corpus --file path/to/your/corpus.csv
```

**Expected CSV format:**
```csv
guarani,spanish,source
"Mba'éichapa reiko?","¿Cómo estás?","jojajovai"
"Che aipota che angirũ","Quiero a mi amigo","custom"
```

## 🔧 Configuration

### Backend Environment Variables (.env)

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/translation_validator

# Security Settings
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS Settings
CORS_ORIGINS=["http://localhost:5173"]

# Application Settings
PROJECT_NAME=Translation Validator
VERSION=1.0.0
```

### Frontend Environment Variables (.env)

```bash
# API Configuration
VITE_API_URL=http://localhost:8000/api
```

## 🗂️ Project Structure

```
translation_validator_tool/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration settings
│   │   ├── database.py          # Database connection
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── translation.py
│   │   │   ├── validation.py
│   │   │   └── suggestion.py
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── user.py
│   │   │   ├── translation.py
│   │   │   ├── validation.py
│   │   │   └── suggestion.py
│   │   ├── api/
│   │   │   ├── deps.py          # Dependencies
│   │   │   └── endpoints/       # API routes
│   │   │       ├── auth.py
│   │   │       ├── translations.py
│   │   │       ├── validations.py
│   │   │       └── suggestions.py
│   │   ├── core/
│   │   │   └── security.py      # Authentication & security
│   │   └── scripts/
│   │       ├── load_corpus.py   # Data loading script
│   │       └── create_admin.py  # Admin user creation
│   ├── alembic/                 # Database migrations
│   ├── requirements.txt
│   ├── .env.example
│   └── alembic.ini
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── auth/
    │   │   │   └── LoginForm.jsx
    │   │   ├── translation/
    │   │   │   ├── TranslationCard.jsx
    │   │   │   ├── CorrectnessButtons.jsx
    │   │   │   ├── ScoreSelector.jsx
    │   │   │   └── NotesTextarea.jsx
    │   │   ├── suggestion/
    │   │   │   └── SuggestionModal.jsx
    │   │   └── common/
    │   │       ├── Navbar.jsx
    │   │       └── StatsBar.jsx
    │   ├── pages/
    │   │   ├── LoginPage.jsx
    │   │   └── ValidatorPage.jsx
    │   ├── services/
    │   │   ├── api.js           # Axios configuration
    │   │   └── auth.js          # Authentication utilities
    │   ├── context/
    │   │   └── AuthContext.jsx  # Authentication context
    │   ├── hooks/
    │   │   └── useAuth.js       # Authentication hook
    │   ├── App.jsx
    │   ├── main.jsx
    │   └── index.css
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    └── .env.example
```

## 📱 Usage Guide

### 1. Login
- Access the application at http://localhost:5173
- Use the admin credentials or register a new account
- Default admin: username `admin`, password `adminpass`

### 2. Validate Translations
1. **Review Translation**: Read the Guaraní and Spanish text pairs
2. **Rate Correctness**: Select Correct, Partial, or Incorrect
3. **Score Quality**: Rate fluency and accuracy (1-5 scale)
4. **Add Notes**: Include optional comments about the translation
5. **Submit**: Save your validation and move to the next translation

### 3. Suggest Improvements
- Click "Suggest New Translation" to propose better alternatives
- Provide improved Guaraní and/or Spanish translations
- Include reasoning for your suggestions

### 4. Track Progress
- View validation statistics in the top bar
- Monitor your progress and team contributions
- See total, validated, and pending translations

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user info

### Translations
- `GET /api/translations/{id}` - Get specific translation
- `GET /api/translations/next` - Get next unvalidated translation
- `GET /api/translations/stats` - Get validation statistics

### Validations
- `POST /api/validations` - Create validation
- `PUT /api/validations/{id}` - Update validation
- `GET /api/validations/my-history` - Get user's validations
- `GET /api/validations/by-translation/{id}` - Get validation for translation

### Suggestions
- `POST /api/suggestions` - Submit translation suggestion
- `GET /api/suggestions` - Get suggestions for translation

## 🧪 Development

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm run test
```

### Code Formatting
```bash
# Backend (Python)
cd backend
black app/
isort app/

# Frontend (JavaScript)
cd frontend
npm run lint
```

## 🚀 Production Deployment

### Backend
1. Set production environment variables
2. Use a production-grade WSGI server (Gunicorn + Uvicorn)
3. Configure reverse proxy (Nginx)
4. Set up SSL certificates
5. Use managed PostgreSQL service

```bash
# Example production command
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend
```bash
# Build for production
npm run build

# Serve with static file server
npx serve -s dist
```

## 🛡️ Security Considerations

- JWT tokens expire after 24 hours (configurable)
- Passwords are hashed using bcrypt
- CORS is configured for specific origins
- Input validation using Pydantic schemas
- SQL injection protection via SQLAlchemy ORM

## 📝 Database Schema

### Core Tables
- **users**: User accounts and authentication
- **translations**: Guaraní-Spanish translation pairs
- **validations**: User evaluations of translations
- **translation_suggestions**: User-submitted improvements

### Key Relationships
- Each user can validate each translation only once
- Multiple suggestions allowed per translation
- Validation history tracked per user

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError)
```
- Verify PostgreSQL is running
- Check DATABASE_URL in .env file
- Ensure database exists

**CORS Error**
```
Access to fetch blocked by CORS policy
```
- Update CORS_ORIGINS in backend .env
- Restart backend server

**JWT Token Error**
```
Could not validate credentials
```
- Check SECRET_KEY configuration
- Clear browser localStorage
- Re-login to get new token

**Frontend Build Error**
```
Module not found
```
- Run `npm install` again
- Check Node.js version (18+ required)
- Clear npm cache: `npm cache clean --force`

### Development Reset
```bash
# Reset database
cd backend
alembic downgrade base
alembic upgrade head
python -m app.scripts.load_corpus --sample

# Reset frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes
4. Add tests for new functionality
5. Run tests: `npm test` and `pytest`
6. Commit changes: `git commit -am 'Add new feature'`
7. Push to branch: `git push origin feature/new-feature`
8. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♀️ Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the API documentation at `/docs`

## 🔗 Related Projects

- [Jojajovai Corpus](https://example.com/jojajovai) - Source dataset
- [Guaraní Language Resources](https://example.com/guarani) - Additional resources
- [Translation Quality Assessment](https://example.com/tqa) - Research background

---

**Translation Validator Tool** - Enhancing Guaraní-Spanish Translation Quality Through Collaborative Validation