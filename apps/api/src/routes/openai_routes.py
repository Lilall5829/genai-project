from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from openai import OpenAI
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

router = APIRouter()
class ChatRequest(BaseModel):
    prompt: str = Field(..., description="The prompt to send to the chat model")
    temperature: Optional[float] = Field(0.0, description="The temperature of the chat model")
    top_p: Optional[float] = Field(0.9, description="The top_p of the chat model")
    max_tokens: Optional[int] = Field(500, description="The max_tokens of the chat model")
    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v):
        if len(v) > 1000:
            raise ValueError("Prompt must be less than 1000 characters")
        return v

@router.post("/generate")
async def generate(request: ChatRequest, stream: bool = False):
    """
    Unified generation endpoint
    - Returns complete response by default
    - Returns SSE streaming response when stream=true
    """
    if stream:
        # SSE streaming output
        def event_generator():
            stream_response = client.responses.create(
                model="gpt-4o-mini",
                input=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": request.prompt},
                ],
                temperature=request.temperature,
                top_p=request.top_p,
                max_output_tokens=request.max_tokens,
                stream=True
            )
            
            for event in stream_response:
                if getattr(event, "type", "") == "response.output_text.delta":
                    
                    # yield f"data: {event.delta}\n\n"
                    yield event.delta
        # Standard SSE format
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    else:
        # Normal output
        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": request.prompt},
            ],
            temperature=request.temperature,
            top_p=request.top_p,
            max_output_tokens=request.max_tokens
        )
        return {"response": response.output[0].content[0].text}