from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from openai import OpenAI
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import os, httpx
from dotenv import load_dotenv
from ..exceptions import InvalidInputError, InternalError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from slowapi import Limiter
from slowapi.util import get_remote_address

load_dotenv()

timeout_config = httpx.Timeout(
    connect=10.0,
    read=20.0,
    write=10.0,
    pool=10.0,
)
client = OpenAI(
    timeout=timeout_config,
    max_retries=0
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=1, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def call_openai_api(model, input_messages, temperature, top_p, max_tokens, stream=False):
    return client.responses.create(
        model=model,
        input=input_messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        stream=stream
    )
limiter = Limiter(key_func=get_remote_address)
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
            raise InvalidInputError(
                message="Prompt must be less than 1000 characters",
                field ="prompt",
                details = {"max_length": 1000, "actual_length": len(v)}
            )
        return v
@limiter.limit("10/minute")
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
            try:
                input_messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": request.prompt},
                ]
                
                stream_response = call_openai_api(
                    model="gpt-4o-mini",
                    input_messages=input_messages,
                    temperature=request.temperature,
                    top_p=request.top_p,
                    max_tokens=request.max_tokens,
                    stream=True
                )
                        
                for event in stream_response:
                    if getattr(event, "type", "") == "response.output_text.delta":
                        # yield f"data: {event.delta}\n\n"
                        yield event.delta
            except Exception as e:
                print(f"Streaming error: {str(e)}")
                yield f"\n[ERROR] Failed to generate response: {str(e)}"
        # Standard SSE format
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    else:
        try:
            # Normal output
            input_messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": request.prompt},
            ]
            response = call_openai_api(
                model="gpt-4o-mini",
                input_messages=input_messages,
                temperature=request.temperature,
                top_p=request.top_p,
                max_tokens=request.max_tokens,
                stream=False
            )
            return {"response": response.output[0].content[0].text}
        except Exception as e:
            raise InternalError(
                message="Error generating response from OpenAI API",
                details=str(e)
            )