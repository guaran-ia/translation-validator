from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path
from app.config import settings
from app.api.endpoints import auth, translations, validations, suggestions, prodigy_auth, annotations

# Add db_schema to path for database initialization
db_schema_path = Path(__file__).parent.parent.parent / "db_schema"
sys.path.insert(0, str(db_schema_path))

try:
    from init_db import initialize_database
except ImportError:
    # Fallback - no auto-initialization if script not found
    def initialize_database():
        logging.warning("Database initialization script not found. Manual setup required.")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    try:
        logging.info("🚀 Starting Translation Validator API...")
        initialize_database()
        logging.info("✅ Application startup completed")
    except Exception as e:
        logging.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logging.info("🛑 Shutting down Translation Validator API...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API for validating and enriching Guarani-Spanish translations",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(prodigy_auth.router, prefix="/api", tags=["prodigy"])
app.include_router(translations.router, prefix="/api/translations", tags=["translations"])
app.include_router(validations.router, prefix="/api/validations", tags=["validations"])
app.include_router(suggestions.router, prefix="/api/suggestions", tags=["suggestions"])
app.include_router(annotations.router, prefix="/api/annotations", tags=["annotations"])


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Translation Validator API",
        "version": settings.VERSION,
        "docs_url": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}