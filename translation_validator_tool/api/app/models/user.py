from datetime import datetime
from typing import List
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


USER_ROLES = ("admin", "validador", "traductor")


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    nombre_completo: Mapped[str] = mapped_column(String(255), nullable=False)
    contacto: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="traductor", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relationships - using string names to avoid circular imports
    validations = relationship("Validation", back_populates="user", cascade="all, delete-orphan")
    suggestions = relationship("TranslationSuggestion", back_populates="user", cascade="all, delete-orphan")
    annotation_validations = relationship("AnnotationValidation", back_populates="user", cascade="all, delete-orphan")
    annotation_suggestions = relationship("AnnotationSuggestion", back_populates="user", cascade="all, delete-orphan")
    
    # Many-to-many relationships with annotations
    annotation_assignments = relationship("AnnotationAssignment", back_populates="user", cascade="all, delete-orphan")
    annotation_translations = relationship("AnnotationTranslation", back_populates="user", cascade="all, delete-orphan")