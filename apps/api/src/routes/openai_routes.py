from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

router = APIRouter()
@router.post("/chat")
async def chat(prompt: str):
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens =1000
    )
    return {"response":resp.choices[0].message.content}

@router.post("/stream")
async def stream_chat(prompt:str):
    def event_generator():
        with client.responses.stream(
            model = "gpt-4o-mini",
            input =[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ]
        ) as stream:
            for event in stream:
                if getattr(event, "type","") == "response.output_text.delta":
                    yield event.delta
            # final = stream.get_final_response()
            # yield f"\n\n[Done]\n{final.output_text}"
    return StreamingResponse(event_generator(), media_type="text/event-stream")