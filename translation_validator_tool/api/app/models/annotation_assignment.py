"""
AnnotationAssignment model for many-to-many relationship between annotations and translators.
An annotation can be assigned to multiple translators for independent translations.
"""
from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class AnnotationAssignment(Base):
    """
    Junction table for many-to-many relationship between Annotation and User.
    Allows an annotation to be assigned to multiple translators.
    """
    __tablename__ = "annotation_assignments"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign keys
    annotation_id: Mapped[int] = mapped_column(ForeignKey("annotations.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    # Timestamp
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    annotation = relationship("Annotation", back_populates="assignments")
    user = relationship("User", back_populates="annotation_assignments")
