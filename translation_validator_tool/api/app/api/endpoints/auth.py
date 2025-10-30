from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from email.message import EmailMessage
import smtplib
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token, UserLogin
from app.core.security import verify_password, get_password_hash, create_access_token
from app.api.deps import get_current_active_user, get_current_active_superuser
from app.config import settings

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return access token."""
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    # Check if user exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user (start inactive; admin must approve)
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=False
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # collect admin emails synchronously (avoid passing DB session to background task)
    admin_emails = [e[0] for e in db.query(User.email).filter(User.is_superuser == True).all()]

    # schedule background email notification to admins (if SMTP configured)
    def send_registration_email(to_emails: list[str], new_username: str, new_email: str):
        if not to_emails:
            return
        # require SMTP settings
        if not settings.SMTP_HOST or not settings.SMTP_PORT or not settings.SMTP_FROM:
            return

        msg = EmailMessage()
        msg['Subject'] = f"Nuevo registro: {new_username}"
        msg['From'] = settings.SMTP_FROM
        msg['To'] = ', '.join(to_emails)
        body = f"Se ha registrado un nuevo usuario:\n\nUsuario: {new_username}\nEmail: {new_email}\n\nRevise /admin/users para aprobarlo."
        msg.set_content(body)

        try:
            if settings.SMTP_USE_TLS:
                server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
                server.starttls()
            else:
                server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)

            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            # don't raise; just log to stdout for now
            print("Failed to send registration email:", e)

    # If BackgroundTasks is available in the request context, FastAPI will inject it when declared in the function.
    # But here register isn't declared with BackgroundTasks param; we'll attempt to retrieve from fastapi context by accepting an optional BackgroundTasks param.
    # NOTE: FastAPI requires BackgroundTasks to be a parameter; in case a caller did not provide it, we still try to send synchronously in a non-blocking manner via a thread.
    try:
        # Attempt to add a background task if available in the request scope
        # The function signature below will accept BackgroundTasks if FastAPI injects it (we can't declare it here due to existing signature),
        # so as a safe fallback we will just spawn the task synchronously using BackgroundTasks if the framework provides it.
        pass
    except Exception:
        pass

    # No explicit BackgroundTasks param available in this signature; send in a lightweight background thread to avoid blocking the request.
    # Import threading lazily to avoid heavy imports in the request path.
    import threading
    threading.Thread(target=send_registration_email, args=(admin_emails, db_user.username, db_user.email), daemon=True).start()

    return UserResponse.model_validate(db_user)


@router.get('/pending', response_model=list[UserResponse])
async def get_pending_registrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """Return list of users pending approval (requires superuser)."""
    pending = db.query(User).filter(User.is_active == False).order_by(User.created_at).all()
    return [UserResponse.model_validate(u) for u in pending]


@router.patch('/approve/{user_id}', response_model=UserResponse)
async def approve_registration(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """Approve (activate) a pending user registration. Requires superuser."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    user.is_active = True
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information."""
    return UserResponse.model_validate(current_user)