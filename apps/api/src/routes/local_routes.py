from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
import torch
import threading
from ..exceptions import InvalidInputError, InternalError

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

@router.post("/generate")
async def generate(request: LocalGenerateRequest, stream: bool = False):
    print(f"Generating with prompt: {request.prompt}")
    prompt = request.prompt
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
            for text in streamer:
                yield text
        return StreamingResponse(text_streamer(), media_type="text/event-stream")


    else:
    # Generate with appropriate sampling strategy
        if temperature == 0:
            outputs = model.generate(**inputs, max_new_tokens=max_tokens, do_sample=False)
        else:
            outputs = model.generate(**inputs, max_new_tokens=max_tokens, temperature=temperature, top_p=top_p, do_sample=True)
        
        # Decode only the newly generated tokens
        input_length = inputs["input_ids"].shape[1]
        new_tokens = outputs[0][input_length:]
        response_text = tokenizer.decode(new_tokens, skip_special_tokens=True)

        return {"response": response_text}
