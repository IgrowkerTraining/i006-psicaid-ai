"""Session-related API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Session, Psychologist
from app.services.ai_service import AIService
from app.api.dependencies import get_ai_service, get_db
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/sessions", tags=["sessions"])

"""
@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_session(
    request: SummarizeRequest,
    ai_service: AIService = Depends(get_ai_service),
    db: AsyncSession = Depends(get_db),
):

    # 1 ── Verificar que el psicólogo existe ──────────────────────
    result = await db.execute(
        select(Psychologist).where(Psychologist.id == request.psychologist_id)
    )
    psychologist = result.scalar_one_or_none()

    if psychologist is None:
        raise HTTPException(
            status_code=404,
            detail=f"Psychologist with id {request.psychologist_id} not found",
        )

    # 2 ── Llamar a la IA para generar el resumen ────────────────
    try:
        summary = await ai_service.summarize_notes(request.raw_notes)
    except Exception as e:
        logger.error(f"AI summarization failed: {e}")
        raise HTTPException(status_code=502, detail="AI service failed to summarize notes")

    # 3 ── Guardar la sesión en la base de datos ─────────────────
    new_session = Session(
        summary_data=summary,
        psychologist_id=request.psychologist_id,
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    logger.info(f"Session {new_session.id} created for psychologist {request.psychologist_id}")

    # 4 ── Devolver la respuesta ─────────────────────────────────
    return SummarizeResponse(
        session_id=new_session.id,
        psychologist_id=request.psychologist_id,
        summary=summary,
    )
"""