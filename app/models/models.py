from typing import List
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Psychologist(Base):
    __tablename__ = "psychologists"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    license: Mapped[str] = mapped_column(String(100))
    
    sessions: Mapped[List["Session"]] = relationship(back_populates="psychologist")
    
    
class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    summary_data: Mapped[dict] = mapped_column(JSON)
    psychologist_id: Mapped[int] = mapped_column(ForeignKey("psychologists.id"))
    
    psychologist: Mapped["Psychologist"] = relationship(back_populates="sessions")