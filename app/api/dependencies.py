"""API dependencies and utilities."""

from fastapi import HTTPException, status
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai_service import ai_service
from app.core.database import AsyncSessionLocal
from app.core.logging import get_logger

logger = get_logger(__name__)


async def get_ai_service():
    """Get AI service instance (lightweight – no health-check on every request)."""
    return ai_service


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session and ensure it is closed after use."""
    async with AsyncSessionLocal() as session:
        yield session
