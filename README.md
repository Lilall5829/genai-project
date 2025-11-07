# GenAI Project

A modern AI-powered API service built with FastAPI, supporting both cloud-based (OpenAI) and local model inference.

## Features

- 🚀 **Fast & Modern**: Built with FastAPI for high performance
- 🤖 **Flexible AI Backend**: Support for OpenAI API and local models
- 📡 **Streaming Support**: Real-time SSE streaming responses
- 🔧 **Easy Configuration**: Environment-based configuration
- 🐳 **Docker Ready**: Containerized deployment support
- 🎯 **Type Safe**: Full type hints with Pydantic validation

## Project Structure

```
genai-project/
├── apps/
│   ├── api/                    # API service
│   │   ├── src/
│   │   │   ├── main.py         # FastAPI application
│   │   │   └── routes/         # API routes
│   │   │       └── openai_routes.py
│   │   ├── Dockerfile          # Docker configuration
│   │   └── requirements.txt    # API dependencies
│   ├── rag/                    # RAG service (future)
│   └── agents/                 # AI agents (future)
├── infra/
│   └── docker-compose.yml      # Docker Compose configuration
├── eval/
│   └── cases/                  # Evaluation test cases
├── reports/                    # Test reports
├── .env.example                # Environment variables template
├── requirements.txt            # Base dependencies
├── requirements-local.txt      # Local model dependencies (optional)
└── README.md                   # This file
```

## Quick Start

### Prerequisites

- Python 3.13+
- pip
- (Optional) Docker & Docker Compose

### Installation

#### 1. Clone the repository

```bash
git clone https://github.com/yourusername/genai-project.git
cd genai-project
```

#### 2. Create virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

#### 3. Install dependencies

**Basic installation (OpenAI API only):**

```bash
pip install -r requirements.txt
```

**With local models (optional):**

```bash
pip install -r requirements-local.txt
```

#### 4. Configure environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
# OPENAI_API_KEY=your_key_here
```

#### 5. Run the application

**Development mode:**

```bash
uvicorn apps.api.src.main:app --reload --host 0.0.0.0 --port 8000
```

**Using build script (Windows):**

```powershell
.\build.ps1 dev-api
```

The API will be available at `http://localhost:8000`

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### Health Check

```bash
GET /health
GET /healthz
```

Response:
```json
{
  "status": "ok"
}
```

### Generate Text

Unified endpoint supporting both streaming and non-streaming responses.

**Endpoint:** `POST /generate`

**Query Parameters:**
- `stream` (boolean, optional): Enable SSE streaming (default: false)

**Request Body:**

```json
{
  "prompt": "Explain artificial intelligence",
  "temperature": 0.7,
  "top_p": 0.9,
  "max_tokens": 500
}
```

**Response (Non-streaming):**

```json
{
  "response": "Artificial intelligence is..."
}
```

**Response (Streaming with `?stream=true`):**

Server-Sent Events (SSE) format:

```
data: Artificial
data: intelligence
data: is
...
```

### Examples

**Non-streaming request:**

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is Python?",
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 500
  }'
```

**Streaming request:**

```bash
curl --no-buffer -X POST "http://localhost:8000/generate?stream=true" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a poem about AI",
    "temperature": 1.2
  }'
```

**Using PowerShell:**

```powershell
$body = @{
    prompt = "Hello, AI!"
    temperature = 0.7
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/generate" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

## Docker Deployment

### Using Docker Compose

```bash
# Start all services
docker compose -f infra/docker-compose.yml up -d --build

# View logs
docker compose -f infra/docker-compose.yml logs -f

# Stop services
docker compose -f infra/docker-compose.yml down
```

### Using build script (Windows)

```powershell
# Start services
.\build.ps1 compose-up

# Stop services
.\build.ps1 compose-down
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here

# Model Configuration
DEFAULT_MODEL=gpt-4o-mini
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=1000

# Application Settings
ENV=development
DEBUG=true
```

### Model Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | string | required | Input text prompt |
| `temperature` | float | 0.0 | Controls randomness (0.0-2.0) |
| `top_p` | float | 0.9 | Nucleus sampling parameter |
| `max_tokens` | integer | 500 | Maximum response length |

## Development

### Project Commands

**Windows (PowerShell):**

```powershell
# Start development services
.\build.ps1 dev-services

# Start API
.\build.ps1 dev-api

# Run tests
.\build.ps1 smoke

# View help
.\build.ps1 help
```

**Linux/Mac (Makefile):**

```bash
# Start Docker services
make compose-up

# Stop Docker services
make compose-down

# Run smoke tests
make smoke
```

### Local Model Setup (Optional)

To use local open-source models (Qwen, LLaMA, etc.):

1. Install additional dependencies:
```bash
pip install -r requirements-local.txt
```

2. Download model files (example with Hugging Face):
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen-7B-Chat")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen-7B-Chat")
```

3. Integrate into your routes (see `apps/api/src/routes/`)

### Adding New Routes

Create new route files in `apps/api/src/routes/`:

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/your-endpoint")
async def your_function():
    return {"message": "Hello"}
```

Register in `main.py`:

```python
from .routes import your_routes

app.include_router(your_routes.router)
```

## Troubleshooting

### Common Issues

**1. ModuleNotFoundError**

Make sure virtual environment is activated:
```bash
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

**2. CORS Errors**

CORS is enabled by default for all origins in development. For production, update `apps/api/src/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specify allowed origins
    ...
)
```

**3. Port Already in Use**

Change the port in the uvicorn command:
```bash
uvicorn apps.api.src.main:app --reload --port 8001
```

## Technologies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server
- **OpenAI**: Cloud-based AI models
- **Transformers**: Local model support (optional)
- **Docker**: Containerization
- **Pydantic**: Data validation

## Roadmap

- [ ] RAG (Retrieval-Augmented Generation) service
- [ ] AI Agents framework
- [ ] Vector database integration
- [ ] Authentication & authorization
- [ ] Rate limiting
- [ ] Caching layer
- [ ] Monitoring & logging
- [ ] Multi-model routing

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.

---

**Made with ❤️ using FastAPI and OpenAI**

