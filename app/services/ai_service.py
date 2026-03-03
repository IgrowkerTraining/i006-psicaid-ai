"""AI service for OpenRouter integration."""

import json
import httpx
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.config.settings import settings
from app.models.schemas import ChatRequest, ChatResponse, ModelInfo, ChatMessage
from app.core.logging import get_logger
from app.core.security import mask_api_key

logger = get_logger(__name__)

# ─── System prompt for clinical-note summarization ──────────────
SUMMARIZE_SYSTEM_PROMPT = (
    "You are a decoupled administrative agent. "
    "Your ONLY task is to organize and summarize the clinical notes provided. "
    "DO NOT add external info. DO NOT provide clinical interpretations. "
    "Return a JSON object with the following keys: "
    '"main_concern", "observations", "action_items", "follow_up".'
)


class AIService:
    """Service for interacting with OpenRouter API."""
    
    def __init__(self):
        """Initialize the AI service."""
        self.client = httpx.AsyncClient(
            base_url=settings.openrouter_base_url,
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json"
            },
            timeout=60.0
        )
        logger.info(f"AI Service initialized with API key: {mask_api_key(settings.openrouter_api_key)}")
    
    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        """Create a chat completion using OpenRouter API."""
        
        # Convert ChatMessage objects to dict format
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        payload = {
            "model": request.model,
            "messages": messages,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "response_format": request.response_format, # Forces JSON mode
            "stream": request.stream,
        }
        
        try:
            logger.info(f"Sending chat completion request for model: {request.model}")
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            chat_response = ChatResponse(
                id=data.get("id", str(uuid.uuid4())),
                created=data.get("created", int(datetime.now().timestamp())),
                model=data.get("model", request.model),
                choices=data.get("choices", []),
                usage=data.get("usage")
            )
            
            logger.info(f"Chat completion successful: {chat_response.id}")
            return data
            
        except httpx.HTTPStatusError as e:
            error_msg = f"OpenRouter API error: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Error calling OpenRouter API: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    async def list_models(self) -> List[ModelInfo]:
        """List available models from OpenRouter."""
        try:
            logger.info("Fetching available models from OpenRouter")
            response = await self.client.get("/models")
            response.raise_for_status()
            
            data = response.json()
            models_data = data.get("data", [])
            
            models = [
                ModelInfo(
                    id=model.get("id", ""),
                    name=model.get("name"),
                    description=model.get("description"),
                    pricing=model.get("pricing")
                )
                for model in models_data
            ]
            
            logger.info(f"Retrieved {len(models)} models")
            return data
            
        except httpx.HTTPStatusError as e:
            error_msg = f"OpenRouter API error: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Error fetching models: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    # ── Summarize clinical notes ────────────────────────────────
    async def summarize_notes(self, raw_notes: str) -> Dict[str, Any]:
        """Send raw clinical notes to the AI and return a structured JSON summary."""

        messages = [
            {"role": "system", "content": SUMMARIZE_SYSTEM_PROMPT},
            {"role": "user", "content": raw_notes},
        ]

        payload = {
            "model": "openai/gpt-4o-mini",
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "stream": False,
        }

        try:
            logger.info("Sending summarize request to OpenRouter")
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"]
            summary: Dict[str, Any] = json.loads(content)

            logger.info("Summarization successful")
            return summary

        except (httpx.HTTPStatusError, KeyError, json.JSONDecodeError) as e:
            error_msg = f"Summarize error: {e}"
            logger.error(error_msg)
            raise Exception(error_msg)

    async def health_check(self) -> bool:
        """Check if the AI service is healthy."""
        try:
            # Try to fetch models as a simple health check
            await self.list_models()
            return True
        except Exception as e:
            logger.error(f"AI service health check failed: {str(e)}")
            return False
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info("AI service client closed")


# Global AI service instance
ai_service = AIService()
