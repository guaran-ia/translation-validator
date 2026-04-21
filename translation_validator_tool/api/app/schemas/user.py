from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, ConfigDict


UserRole = Literal["admin", "validador", "traductor"]


# Base schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    nombre_completo: Optional[str] = None
    contacto: Optional[str] = None
    role: UserRole = "traductor"
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    nombre_completo: Optional[str] = None
    contacto: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    hashed_password: str


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    user_id: Optional[int] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class AdminPasswordChange(BaseModel):
    new_password: str