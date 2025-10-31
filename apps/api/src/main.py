from fastapi import FastAPI
app = FastAPI()
@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/healthz")
def healthz():
    return {"message": "I'mnotok"}