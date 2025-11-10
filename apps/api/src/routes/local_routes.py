from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

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
async def generate(request: LocalGenerateRequest):
    print(f"Generating with prompt: {request.prompt}")
    prompt = request.prompt
    temperature = request.temperature
    top_p = request.top_p
    max_tokens = request.max_tokens

    inputs = tokenizer(prompt, return_tensors="pt")
    
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
