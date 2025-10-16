# Backend README

## Translation Validator Backend

FastAPI-based backend for the Translation Validator application.

### Quick Start

1. **Setup Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Database**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

3. **Run Migrations**
   ```bash
   alembic upgrade head
   ```

4. **Start Server**
   ```bash
   uvicorn app.main:app --reload
   ```

### API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Scripts

**Create Admin User**
```bash
python -m app.scripts.create_admin --username admin --email admin@example.com --password adminpass
```

**Load Sample Data**
```bash
python -m app.scripts.load_corpus --sample
```

**Load Custom Corpus**
```bash
python -m app.scripts.load_corpus --file path/to/corpus.csv
```

### Development

**Generate Migration**
```bash
alembic revision --autogenerate -m "Description of changes"
```

**Apply Migration**
```bash
alembic upgrade head
```

**Rollback Migration**
```bash
alembic downgrade -1
```