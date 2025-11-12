from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from .routes import openai_routes, local_routes
from .exceptions import APIException, NotFoundError

app = FastAPI()

@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    error_response = {
        "error": {
            "code": exc.error_code,
            "message": exc.message,
            "status":exc.status_code,
        }
    }
    if exc.field:
        error_response["error"]["field"] = exc.field
    if exc.details:
        error_response["error"]["details"] = exc.details
    return JSONResponse(status_code=exc.status_code, content=error_response)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    field = ".".join(str(loc) for loc in first_error.get("loc", [])[1:])
    message = first_error.get("msg", "Validation error")
    error_type = first_error.get("type", "validation_error")

    if error_type == "missing":
        error_code = "MISSING_REQUIRED_FIELD"
    elif error_type in ["type_error", "int_parsing", "float_parsing"]:
        error_code = "INVALID_TYPE"
    else:
        error_code = "INVALID_VALUE"
    error_response = {
        "error": {
            "code": error_code,
            "message": message,
            "status": 422,
            "field": field,
            "details": errors,
        }
    }
    return JSONResponse(
        status_code=422,
        content=error_response,
    )

@app.exception_handler(404)
async def not_found_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "NOT_FOUND",
                "message": f"Route {request.url.path} not found",
                "status": 404,
            }
        }# Add CORS middleware to allow cross-origin requests
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    print(f"Unexpected error: {type(exc).__name__}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Internal server error",
                "status": 500,
                "details": str(exc) if app.debug else None,
            }
        }
    )

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

