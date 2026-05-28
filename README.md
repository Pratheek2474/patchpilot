# PatchPilot Backend

AI-powered GitHub bot that automatically resolves issues by analyzing repositories, generating code fixes, and creating pull requests.

## Quick Start

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the server
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/docs` | GET | OpenAPI documentation |
| `/webhook` | POST | GitHub webhook receiver |
| `/api/jobs` | GET | List all pipeline jobs |
| `/api/jobs/{id}` | GET | Get job details + logs |
| `/api/jobs/{id}/logs` | GET | Get reasoning logs |
| `/api/stats` | GET | Dashboard statistics |
| `/api/trigger` | POST | Manual pipeline trigger |

## Manual Trigger (Testing)

```bash
curl -X POST http://localhost:8000/api/trigger \
  -H "Content-Type: application/json" \
  -d '{"repo": "user/repo", "issue_number": 1}'
```

## Architecture

```
app/
├── main.py              # FastAPI app factory
├── config.py            # Environment config
├── database.py          # SQLAlchemy async setup
├── models/              # Pydantic schemas + ORM models
├── routers/             # API endpoints
├── services/            # Business logic (GitHub, Repo, AI, Patch)
├── pipeline/            # AI orchestration (stages, prompts, orchestrator)
└── utils/               # Security, logging, file utilities
```
