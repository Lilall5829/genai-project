from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
import torch
import threading
from ..exceptions import InvalidInputError, InternalError
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/local", tags=["local"])

print("Loading TinyLlama model...")
tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0", dtype=torch.float32, device_map="cpu", low_cpu_mem_usage=True)
print("Model loaded successfully")

class LocalGenerateRequest(BaseModel):
    prompt: str = Field(..., description="The prompt to send to the chat model")
    temperature: Optional[float] = Field(0.9, description="The temperature of the chat model (0.0 = deterministic)")
    top_p: Optional[float] = Field(0.9, description="The top_p of the chat model")
    max_tokens: Optional[int] = Field(500, description="The max_tokens of the chat model")
    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v):
        if not v or len(v.strip()) == 0:
            raise InvalidInputError(
                message="Prompt cannot be empty",
                field="prompt"
            )
        if len(v) > 1000:
            raise InvalidInputError(
                message="Prompt must be less than 1000 characters",
                field ="prompt",
                details = {"max_length": 1000, "actual_length": len(v)}
            )
        return v
    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v):
        if v < 0 or v > 2:
            raise InvalidInputError(
                message="Temperature must be between 0 and 2",
                field="temperature",
                details = {"min_value": 0, "max_value": 2, "actual_value": v}
            )
        return v
    @field_validator("max_tokens")
    @classmethod
    def validate_max_tokens(cls, v):
        if v < 1 or v > 2000:
            raise InvalidInputError(
                message="Max tokens must be between 1 and 2000",
                field="max_tokens",
                details = {"min_value": 1, "max_value": 2000, "actual_value": v}
            )
        return v
    @field_validator("top_p")
    @classmethod
    def validate_top_p(cls, v):
        if v < 0 or v > 1:
            raise InvalidInputError(
                message="Top p must be between 0 and 1",
                field="top_p",
                details = {"min_value": 0, "max_value": 1, "actual_value": v}
            )
        return v

@limiter.limit("20/minute")
@router.post("/generate")
async def generate(request: LocalGenerateRequest, stream: bool = False):
    print(f"Generating with prompt: {request.prompt}")

    formatted_prompt = f"""<|system|>
You are a helpful assistant.</s>
<|user|>
{request.prompt}</s>
<|assistant|>
"""
    
    prompt = formatted_prompt
    temperature = request.temperature
    top_p = request.top_p
    max_tokens = request.max_tokens

    inputs = tokenizer(prompt, return_tensors="pt")
    if stream:
        streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
        generation_kwargs = {
            "input_ids": inputs["input_ids"],
            "attention_mask": inputs.get("attention_mask"),
            "max_new_tokens": max_tokens,
            "streamer": streamer,
        }
        if temperature == 0:
            generation_kwargs["do_sample"] = False
        else:
            generation_kwargs["temperature"] = temperature
            generation_kwargs["top_p"] = top_p
            generation_kwargs["do_sample"] = True

        thread = threading.Thread(target=model.generate, kwargs=generation_kwargs)
        thread.start()

        def text_streamer():
            try:
                yield from streamer
                # for text in streamer:
                #     yield text
            except Exception as e:
                print(f"Streaming error: {str(e)}")
                yield f"\n[ERROR] Failed to generate response: {str(e)}"
        return StreamingResponse(text_streamer(), media_type="text/event-stream")


    else:
    # Generate with appropriate sampling strategy
        try:
            if temperature == 0:
                outputs = model.generate(**inputs, max_new_tokens=max_tokens, do_sample=False)
            else:
                outputs = model.generate(**inputs, max_new_tokens=max_tokens, temperature=temperature, top_p=top_p, do_sample=True)
            
            # Decode only the newly generated tokens
            input_length = inputs["input_ids"].shape[1]
            new_tokens = outputs[0][input_length:]
            response_text = tokenizer.decode(new_tokens, skip_special_tokens=True)

            return {"response": response_text}
        except Exception as e:
            raise InternalError(
                message="Error generating response from local model",
                details=str(e)
            )