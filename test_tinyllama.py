from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

print("Loading model...")
print("This may take a few minutes...")

tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")

# Add pad_token if not exists
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0", dtype=torch.float32, device_map="cpu", low_cpu_mem_usage=True)

print("Model loaded successfully")
print(f"Model size: ~{sum(p.numel() for p in model.parameters())/1e9:.2f}B parameters")

print("\n" + "="*50)
print("Testing text generation...")
print("="*50 + "\n")

# Use proper chat format for TinyLlama-Chat
# prompt = """<|system|>
# You are a helpful assistant.</s>
# <|user|>
# What is the best programming language for AI?</s>
# <|assistant|>
# """
prompt = "What is the best programming language for AI?"
print(f"Prompt: {prompt}")

inputs = tokenizer(prompt, return_tensors="pt")

outputs = model.generate(**inputs, max_new_tokens=100, temperature=0.7, top_p=0.9, do_sample=True)

# Decode only new tokens
input_length = inputs["input_ids"].shape[1]
new_tokens = outputs[0][input_length:]
response = tokenizer.decode(new_tokens, skip_special_tokens=True)

print(f"Response: {response}")
print("\n" + "="*50)
print("Text generation completed successfully")