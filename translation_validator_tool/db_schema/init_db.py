"""
Database initialization utilities.
Manages database creation, table setup, and initial data seeding.
"""
import logging
import sys
import os
from pathlib import Path
import subprocess

# Add API directory to Python path to import app package
project_root = Path(__file__).resolve().parent.parent
api_path = project_root / "api"
sys.path.insert(0, str(api_path))

# Set working directory to API for .env file loading
original_cwd = os.getcwd()
os.chdir(str(api_path))

from sqlalchemy import text, create_engine
from sqlalchemy.exc import OperationalError, ProgrammingError
import urllib.parse

# Import after adding path and setting working directory
try:
    from app.database import engine, Base, SessionLocal
    from app.models.user import User
    from app.core.security import get_password_hash
    from app.config import settings
except ImportError as e:
    print(f"❌ Error importing API modules: {e}")
    print("Make sure you're running this from the correct directory")
    print(f"Current working directory: {os.getcwd()}")
    print(f"API path: {api_path}")
    sys.exit(1)


logger = logging.getLogger(__name__)


def create_database_if_not_exists():
    """Create the database if it doesn't exist."""
    try:
        # Parse the database URL to get database name
        parsed_url = urllib.parse.urlparse(settings.DATABASE_URL)
        database_name = parsed_url.path[1:]  # Remove leading slash
        
        # Create engine without database name to connect to PostgreSQL server
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/postgres"
        base_engine = create_engine(base_url)

        # Check if database exists
        # Use one connection to check existence, then if needed open a fresh
        # connection with AUTOCOMMIT to run CREATE DATABASE (cannot run in a transaction)
        conn = base_engine.connect()
        try:
            result = conn.execute(text(
                "SELECT 1 FROM pg_database WHERE datname = :database_name"
            ), {"database_name": database_name})

            if not result.fetchone():
                logger.info(f"🏗️  Creating database: {database_name}")
                # Close the select connection before opening autocommit connection
                conn.close()
                # Open a new connection configured for autocommit and run CREATE DATABASE
                with base_engine.connect().execution_options(isolation_level="AUTOCOMMIT") as ac:
                    ac.execute(text(f'CREATE DATABASE "{database_name}"'))
                logger.info(f"✅ Database '{database_name}' created successfully")
            else:
                logger.info(f"📊 Database '{database_name}' already exists")
        finally:
            try:
                if not conn.closed:
                    conn.close()
            except Exception:
                pass

        base_engine.dispose()
        
    except Exception as e:
        logger.error(f"❌ Error creating database: {e}")
        raise


def create_tables():
    """Create all database tables."""
    try:
        logger.info("🏗️  Creating database tables...")
        # Prefer using Alembic migrations to create schema instead of create_all.
        # This function is kept for manual use but will not be used in initialize_database
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully (via metadata.create_all)")
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        raise


def create_default_admin():
    """Create default admin user if no users exist."""
    db = SessionLocal()
    try:
        # Check if any users exist
        user_count = db.query(User).count()
        
        if user_count == 0:
            logger.info("👤 No users found. Creating default admin user...")
            
            # Create default admin user
            hashed_password = get_password_hash("4dm!n$Pass")
            admin_user = User(
                username="admin",
                email="admin@translation-validator.com",
                hashed_password=hashed_password,
                role="admin",
                is_active=True,
                is_superuser=True
            )
            
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            logger.info("✅ Default admin user created:")
            logger.info(f"   Username: admin")
            logger.info(f"   Email: admin@translation-validator.com")
            logger.info(f"   Password: 4dm!n$Pass")
            logger.info(f"   ID: {admin_user.id}")
            
        else:
            logger.info(f"👥 Found {user_count} existing users. Skipping admin creation.")
            
    except Exception as e:
        logger.error(f"❌ Error creating default admin: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def test_database_connection():
    """Test database connection."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


def run_alembic_upgrade_head():
    """Run `alembic upgrade head` in the db_schema directory."""
    try:
        alembic_dir = Path(__file__).parent
        logger.info("🔼 Running Alembic migrations (upgrade head)")
        # Try calling alembic directly
        try:
            subprocess.check_call(["alembic", "upgrade", "head"], cwd=str(alembic_dir))
            logger.info("✅ Alembic upgrade completed (alembic CLI)")
            return
        except FileNotFoundError:
            logger.warning("alembic CLI not found; trying python -m alembic")

        # Fallback to python -m alembic using the same interpreter
        python_exe = sys.executable
        subprocess.check_call([python_exe, "-m", "alembic", "upgrade", "head"], cwd=str(alembic_dir))
        logger.info("✅ Alembic upgrade completed (python -m alembic)")

    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Alembic process failed: {e}")
        raise


def drop_all_tables():
    """Drop all tables (useful for testing)."""
    try:
        logger.warning("⚠️  Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ All tables dropped successfully")
    except Exception as e:
        logger.error(f"❌ Error dropping tables: {e}")
        raise


def reset_database():
    """Reset database completely (drop and recreate everything)."""
    logger.warning("🔄 Resetting database completely...")
    drop_all_tables()
    create_tables()
    create_default_admin()
    logger.info("✅ Database reset completed")


def initialize_database():
    """Complete database initialization."""
    logger.info("🚀 Starting database initialization...")
    
    try:
        # Step 1: Create database if not exists
        create_database_if_not_exists()
        
        # Step 2: Test connection
        if not test_database_connection():
            raise Exception("Database connection failed")
        
        # Step 3: Run Alembic migrations to bring schema up-to-date
        try:
            run_alembic_upgrade_head()
        except Exception as e:
            logger.error(f"❌ Alembic upgrade failed: {e}")
            raise
        
        # Step 4: Create default admin user
        create_default_admin()
        
        logger.info("🎉 Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"💥 Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("🗄️  TRANSLATION VALIDATOR - DATABASE MANAGEMENT")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "init":
            initialize_database()
        elif command == "reset":
            reset_database()
        elif command == "drop":
            drop_all_tables()
        elif command == "test":
            test_database_connection()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: init, reset, drop, test")
            sys.exit(1)
    else:
        # Default action
        initialize_database()
    
    print("=" * 60)
    print("✅ Database operation completed!")
    print("=" * 60)
    
    # Restore original working directory
    os.chdir(original_cwd)