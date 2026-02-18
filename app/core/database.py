from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config.settings import settings

# connects with database
engine = create_async_engine(settings.database_url)

# allows async access to the database ️
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# all data models inherit from this parent class
class Base(DeclarativeBase):
    pass