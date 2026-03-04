from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

    
class Summaries(Base):
    __tablename__ = "summaries"

    id: Mapped[int] = mapped_column(primary_key=True)
    summary_data: Mapped[dict] = mapped_column(JSON, nullable=False)
