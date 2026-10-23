"""
Endpoints para autenticación de Prodigy Multi-Usuario
======================================================
Permite que usuarios autenticados obtengan URLs de Prodigy con su token JWT.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.api.deps import get_current_active_user
from app.core.security import create_access_token
from app.config import settings
from datetime import timedelta

router = APIRouter()

# Configuración de Prodigy desde settings
PRODIGY_PORT = settings.PRODIGY_PORT
PRODIGY_HOST = settings.PRODIGY_HOST


class ProdigySessionResponse(BaseModel):
    """Respuesta con información de sesión de Prodigy"""
    username: str
    session_url: str
    role: str
    instructions: str
    token: str  # JWT para acceder a Prodigy


class ProdigyTokenResponse(BaseModel):
    """Respuesta con token para Prodigy"""
    token: str
    prodigy_url: str
    expires_in_minutes: int


@router.get("/prodigy/token", response_model=ProdigyTokenResponse)
async def get_prodigy_token(
    current_user: User = Depends(get_current_active_user)
):
    """
    Genera un token JWT para acceder a Prodigy.
    Este token se usa en la URL: http://localhost:8081/?token=JWT&session=username
    """
    # Crear token con expiración de 24 horas para Prodigy
    expires = timedelta(hours=24)
    token = create_access_token(
        data={"sub": str(current_user.id)},
        expires_delta=expires
    )
    
    prodigy_url = f"http://{PRODIGY_HOST}:{PRODIGY_PORT}/?token={token}&session={current_user.username}"
    
    return ProdigyTokenResponse(
        token=token,
        prodigy_url=prodigy_url,
        expires_in_minutes=24 * 60
    )


@router.get("/prodigy/session", response_model=ProdigySessionResponse)
async def get_prodigy_session(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener URL de Prodigy con token JWT para autenticación segura.
    
    Returns:
        - session_url: URL completa de Prodigy con ?token=JWT&session=username
        - username: Nombre del usuario para la sesión
        - role: Rol del usuario (admin/regular)
        - instructions: Instrucciones básicas de uso
        - token: JWT para autenticación
    """
    # Generar token JWT para Prodigy (24 horas)
    expires = timedelta(hours=24)
    token = create_access_token(
        data={"sub": str(current_user.id)},
        expires_delta=expires
    )
    
    session_url = f"http://{PRODIGY_HOST}:{PRODIGY_PORT}/?token={token}&session={current_user.username}"
    
    return ProdigySessionResponse(
        username=current_user.username,
        session_url=session_url,
        role="admin" if current_user.is_superuser else "annotator",
        token=token,
        instructions=(
            "Haz clic en el enlace para abrir Prodigy. "
            "Tu sesión se asignará automáticamente con autenticación segura. "
        )
    )


@router.get("/prodigy/redirect")
async def redirect_to_prodigy(
    current_user: User = Depends(get_current_active_user)
):
    """Redirigir directamente a Prodigy con token JWT."""
    # Generar token JWT
    expires = timedelta(hours=24)
    token = create_access_token(
        data={"sub": str(current_user.id)},
        expires_delta=expires
    )
    session_url = f"http://{PRODIGY_HOST}:{PRODIGY_PORT}/?token={token}&session={current_user.username}"
    return RedirectResponse(url=session_url, status_code=303)


@router.get("/prodigy/dashboard", response_class=HTMLResponse)
async def prodigy_dashboard(
    current_user: User = Depends(get_current_active_user)
):
    """
    Dashboard HTML simple para acceder a Prodigy (alternativa si no usas React).
    """
    # Generar token JWT
    expires = timedelta(hours=24)
    token = create_access_token(
        data={"sub": str(current_user.id)},
        expires_delta=expires
    )
    session_url = f"http://{PRODIGY_HOST}:{PRODIGY_PORT}/?token={token}&session={current_user.username}"
    role_badge = "Admin" if current_user.is_superuser else "Anotador"
    role_color = "#dc2626" if current_user.is_superuser else "#059669"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard Prodigy - {current_user.username}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }}
            .container {{
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                max-width: 600px;
                width: 100%;
            }}
            h1 {{
                color: #333;
                margin-bottom: 10px;
                font-size: 28px;
            }}
            .user-info {{
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid #f0f0f0;
            }}
            .username {{
                font-size: 18px;
                font-weight: 600;
                color: #555;
            }}
            .role-badge {{
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                background: {role_color};
                color: white;
            }}
            .prodigy-link {{
                display: block;
                padding: 20px;
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
                text-align: center;
                text-decoration: none;
                border-radius: 10px;
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 20px;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            .prodigy-link:hover {{
                transform: translateY(-3px);
                box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3);
            }}
            .info-box {{
                background: #fff9e6;
                border-left: 4px solid #fbbf24;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
            .info-box strong {{
                color: #92400e;
            }}
            .info-box p {{
                margin: 8px 0;
                color: #78350f;
                line-height: 1.6;
            }}
            .stats {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin-top: 20px;
            }}
            .stat-box {{
                background: #f8fafc;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
            }}
            .stat-label {{
                font-size: 12px;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .stat-value {{
                font-size: 24px;
                font-weight: 700;
                color: #1e293b;
                margin-top: 5px;
            }}
            .logout-link {{
                display: block;
                text-align: center;
                margin-top: 20px;
                color: #667eea;
                text-decoration: none;
                font-size: 14px;
            }}
            .logout-link:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏷️ Dashboard Prodigy</h1>
            
            <div class="user-info">
                <span class="username">👤 {current_user.username}</span>
                <span class="role-badge">{role_badge}</span>
            </div>
            
            <a href="{session_url}" class="prodigy-link" target="_blank">
                ▶️ Abrir Prodigy
            </a>
            
            <div class="info-box">
                <strong>📌 Instrucciones:</strong>
                <p>1. Haz clic en el botón verde para abrir Prodigy</p>
                <p>2. Tu sesión ({current_user.username}) se asignará automáticamente</p>
                <p>3. Comienza a anotar oraciones en Guaraní</p>
                <p>4. <strong>Recuerda:</strong> Marca al menos 1 SUJETO y 1 VERBO en cada oración</p>
            </div>
            
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-label">Usuario</div>
                    <div class="stat-value">{current_user.username}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Email</div>
                    <div class="stat-value" style="font-size: 14px;">{current_user.email}</div>
                </div>
            </div>
            
            <a href="/" class="logout-link">← Volver al inicio</a>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@router.get("/prodigy/users")
async def list_prodigy_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Listar todos los usuarios activos que pueden usar Prodigy.
    Útil para ver qué sesiones están disponibles.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden ver la lista completa de usuarios"
        )
    
    users = db.query(User).filter(User.is_active == True).all()
    
    return {
        "total_users": len(users),
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": "admin" if user.is_superuser else "annotator",
                "prodigy_session": f"?session={user.username}"
            }
            for user in users
        ]
    }
