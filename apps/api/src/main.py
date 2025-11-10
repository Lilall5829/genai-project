from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import openai_routes, local_routes

app = FastAPI()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (development environment)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all request headers
)

app.include_router(openai_routes.router)
app.include_router(local_routes.router)
@app.get("/")
def root():
    return {"message": "GenAI API Service", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

