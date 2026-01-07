# 🔑 Flujo de Autenticación

Este documento detalla el flujo completo de autenticación desde el login hasta el acceso a Prodigy.

---

## 1. Visión General

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      FLUJO DE AUTENTICACIÓN                             │
└─────────────────────────────────────────────────────────────────────────┘

  ┌─────────┐   1. Credenciales    ┌──────────┐   2. POST /auth/login
  │ Usuario │ ─────────────────────│ Frontend │ ─────────────────────────┐
  └─────────┘                      │  :5173   │                          │
                                   └──────────┘                          │
                                                                         ▼
                                                                  ┌──────────┐
                                                                  │ Backend  │
                                                                  │  :8000   │
                                                                  └────┬─────┘
                                                                       │
                                   ┌───────────────────────────────────┘
                                   │ 3. JWT Token
                                   ▼
                              ┌──────────┐
                              │ Frontend │
                              │  :5173   │
                              └────┬─────┘
                                   │
                                   │ 4. Redirect con token
                                   ▼
                              ┌──────────┐
                              │JWT Proxy │
                              │  :8085   │
                              └────┬─────┘
                                   │
                                   │ 5. Validar token contra Backend
                                   ▼
                              ┌──────────┐
                              │ Backend  │
                              │  :8000   │
                              └────┬─────┘
                                   │
                                   │ 6. Usuario válido
                                   ▼
                              ┌──────────┐
                              │JWT Proxy │───────────────────┐
                              │  :8085   │                   │
                              └──────────┘                   │
                                                             │ 7. Proxy request
                                                             ▼
                                                       ┌──────────┐
                                                       │ Prodigy  │
                                                       │ :8080-82 │
                                                       └──────────┘
```

---

## 2. Paso 1: Login en Frontend

### Request

El usuario ingresa credenciales en el frontend (http://localhost:5173):

```javascript
// Frontend React
const handleLogin = async (username, password) => {
    const response = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            username: username,
            password: password,
        }),
    });
    
    const data = await response.json();
    // data.access_token contiene el JWT
};
```

### Response del Backend

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400
}
```

---

## 3. Paso 2: Estructura del JWT Token

### Payload del Token

```json
{
    "sub": "alice",
    "email": "alice@example.com",
    "is_superuser": false,
    "is_active": true,
    "exp": 1705401600,
    "iat": 1705315200
}
```

### Decodificar Token (Debug)

```python
import jwt

token = "eyJhbGciOiJIUzI1NiIs..."
decoded = jwt.decode(token, options={"verify_signature": False})
print(decoded)
```

---

## 4. Paso 3: Redirect a Prodigy

El frontend redirige al usuario a Prodigy con el token:

```javascript
// Frontend
const redirectToProdigy = (token, annotationType) => {
    const url = `http://localhost:8085/?token=${token}&service=${annotationType}`;
    window.location.href = url;
};
```

URL resultante:
```
http://localhost:8085/?token=eyJhbGciOiJIUzI1NiIs...&service=pos
```

---

## 5. Paso 4: Validación en JWT Proxy

### Extracción del Token

El proxy busca el token en múltiples ubicaciones:

```python
# prodigy_manager.py
def get_token_from_request(request: Request) -> Optional[str]:
    # 1. Header Authorization
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]
    
    # 2. Cookie
    token = request.cookies.get("prodigy_token")
    if token:
        return token
    
    # 3. Query parameter
    return request.query_params.get("token")
```

### Validación contra Backend

```python
async def validate_jwt_token(token: str) -> Optional[dict]:
    """Valida el token contra el endpoint /users/me del backend."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL}/users/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "username": user_data.get("username"),
                    "email": user_data.get("email"),
                    "is_superuser": user_data.get("is_superuser", False),
                    "is_active": user_data.get("is_active", True),
                }
            
            return None
            
    except Exception as e:
        print(f"[AUTH] Error validando token: {e}")
        return None
```

---

## 6. Paso 5: Seteo de Cookies

Si el token viene en la URL, el proxy lo guarda en cookies para requests futuras:

```python
# En proxy_to_prodigy()
if should_set_cookie and token:
    proxy_response.set_cookie(
        key="prodigy_token",
        value=token,
        httponly=True,
        max_age=86400,  # 24 horas
        samesite="lax",
        path="/"
    )
    
    # También guardar el servicio seleccionado
    service_from_url = request.query_params.get("service")
    if service_from_url:
        proxy_response.set_cookie(
            key="prodigy_service",
            value=service_from_url,
            httponly=True,
            max_age=86400,
            samesite="lax",
            path="/"
        )
```

---

## 7. Paso 6: Proxy a Prodigy

Una vez validado el token, el proxy reenvía la request a Prodigy:

```python
# Proxy a Prodigy interno
target_state = prodigy_services.get(service)
url = f"http://127.0.0.1:{target_state.port}/{path}"

response = await http_client.request(
    method=request.method,
    url=url,
    headers={k: v for k, v in request.headers.items() 
            if k.lower() not in ["host", "connection"]},
    content=body if body else None,
)

return Response(
    content=response.content,
    status_code=response.status_code,
    headers=dict(response.headers)
)
```

---

## 8. Sesiones de Prodigy

### Session ID

Prodigy usa el username como session_id para tracking:

```python
# El session_id se pasa a Prodigy
# Prodigy lo usa para:
# 1. Tracking de anotaciones por usuario
# 2. Exclusión de ejemplos ya anotados
# 3. Cálculo de IAA
```

### Cookies de Sesión

```
prodigy_token   = eyJhbGciOiJIUzI1NiIs...  # JWT token
prodigy_service = pos                       # Tipo de anotación actual
```

---

## 9. Manejo de Errores

### Token Inválido

```python
if not user:
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return HTMLResponse(
            content=get_error_page(
                "Acceso Denegado",
                "Necesitas iniciar sesión para acceder a Prodigy."
            ),
            status_code=401
        )
    raise HTTPException(status_code=401, detail="No autorizado")
```

### Token Expirado

Los tokens expiran después de 24 horas. El usuario debe volver a hacer login.

### Usuario Inactivo

```python
if not user.get("is_active", True):
    raise HTTPException(
        status_code=403, 
        detail="Usuario desactivado"
    )
```

---

## 10. APIs de Autenticación

### POST /auth/login (Backend :8000)

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=secret123"
```

### GET /users/me (Backend :8000)

```bash
curl http://localhost:8000/users/me \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

### Respuesta

```json
{
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "is_superuser": false,
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z"
}
```

---

## 11. Seguridad

### Mejores Prácticas

1. **HTTPS en producción**: Siempre usar HTTPS para proteger tokens
2. **HttpOnly cookies**: Las cookies no son accesibles desde JavaScript
3. **SameSite=Lax**: Protección contra CSRF
4. **Expiración de tokens**: 24 horas por defecto
5. **Validación en cada request**: El proxy valida el token en cada request

### Variables de Entorno

```bash
# Backend
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 horas

# NO commitear estos valores en el repositorio
```

---

## 12. Siguiente Paso

Continúa con [06-RECIPE-BATCH.md](06-RECIPE-BATCH.md) para entender el recipe principal de anotación.
