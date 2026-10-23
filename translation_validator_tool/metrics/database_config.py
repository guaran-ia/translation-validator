"""Database configuration for standalone reporting scripts."""

import os
import re
from pathlib import Path

from dotenv import load_dotenv


def get_database_url():
    """Read the API .env without overriding exported environment variables."""
    load_dotenv(Path(__file__).resolve().parents[1] / "api" / ".env")
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        raise ValueError(
            "DATABASE_URL es obligatoria. Configúrala en el entorno o en api/.env."
        )
    # psycopg2 accepts PostgreSQL URLs, without SQLAlchemy's driver suffix.
    return re.sub(r"^postgresql\+[^:]+://", "postgresql://", database_url)
