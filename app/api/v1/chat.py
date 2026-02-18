"""Chat-related API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.models.schemas import ChatRequest, ChatResponse, ModelInfo, ChatMessage
from app.services.ai_service import AIService
from app.api.dependencies import get_ai_service
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/completions", response_model=ChatResponse)
async def create_chat_completion(
    request: ChatRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    
    SYSTEM_PROMPT = (
        "You are a decoupled administrative agent. "
        "Your ONLY task is to organize and summarize the clinical notes provided. "
        "DO NOT add external info. DO NOT provide clinical interpretations. "
        "Output MUST be strictly JSON."
    )
    
    # injects the system prompt at the beginning of message list
    system_message = ChatMessage(role="system", content=SYSTEM_PROMPT)
    request.messages.insert(0, system_message)
    
    print(request)
    
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
