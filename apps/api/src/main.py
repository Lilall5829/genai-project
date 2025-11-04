from fastapi import FastAPI
from .routes import openai_routes
app = FastAPI()
app.include_router(openai_routes.router)
@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/healthz")
def healthz():
    return {"message": "I'm ok"}