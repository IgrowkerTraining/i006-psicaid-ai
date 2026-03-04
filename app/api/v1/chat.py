"""Chat-related API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.models.schemas import ChatRequest, ChatResponse, ModelInfo, ChatMessage
from app.services.ai_service import AIService
from app.api.dependencies import get_ai_service
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/summary", response_model=ChatResponse)
async def create_chat_completion(
    request: ChatRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    
    SYSTEM_PROMPT = (
        "Eres un asistente administrativo clínico especializado. "
        "Tu tarea es transformar notas clínicas en una 'Memoria clínica del paciente' estructurada. "
        "Debes extraer la información y devolver estrictamente un objeto JSON con las siguientes claves: "
        "'paciente', 'edad', 'frecuencia_sesiones', 'ultima_sesion', "
        "'motivo_consulta', 'contexto_clinico', 'hipotesis_trabajo', "
        "'intervenciones', 'evolucion', 'objetivos', 'proxima_sesion'. "
        "El contenido debe ser redactado en un tono profesional y clínico en español, "
        "siguiendo fielmente la información proporcionada sin inventar datos."
    )
    
    # injects the system prompt at the beginning of message list
    system_message = ChatMessage(role="system", content=SYSTEM_PROMPT)
    request.messages.insert(0, system_message)
    
    try:
        logger.info(f"Chat completion request for model: {request.model}")
        response = await ai_service.chat_completion(request)
        return response
    except Exception as e:
        logger.error(f"Error in chat completion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=List[ModelInfo])
async def list_models(ai_service: AIService = Depends(get_ai_service)):
    """
    List all available AI models from OpenRouter.
    
    Returns a list of available models with their information.
    """
    try:
        models = await ai_service.list_models()
        return models
    except Exception as e:
        logger.error(f"Error fetching models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
