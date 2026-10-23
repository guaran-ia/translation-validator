"""
Script para crear usuario administrador.
Uso: python -m app.scripts.create_admin --username admin --email admin@example.com --password adminpass
"""
import argparse
from app.database import SessionLocal, engine
from app.models.user import User
from app.core.security import get_password_hash
from app.database import Base


def create_admin_user(username: str, email: str, password: str, nombre_completo: str = "Administrador"):
    """Create an admin user."""
    db = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            print(f"❌ User with username '{username}' or email '{email}' already exists")
            return
        
        # Create admin user
        hashed_password = get_password_hash(password)
        admin_user = User(
            username=username,
            email=email,
            nombre_completo=nombre_completo,
            hashed_password=hashed_password,
            role="admin",
            is_active=True,
            is_superuser=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"✅ Admin user created successfully:")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   ID: {admin_user.id}")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Create admin user")
    parser.add_argument("--username", type=str, required=True, help="Admin username")
    parser.add_argument("--email", type=str, required=True, help="Admin email")
    parser.add_argument("--password", type=str, required=True, help="Admin password")
    parser.add_argument("--nombre-completo", default="Administrador", help="Nombre completo del administrador")
    
    args = parser.parse_args()
    
    # Create tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Create admin user
    create_admin_user(args.username, args.email, args.password, args.nombre_completo)


if __name__ == "__main__":
    main()
