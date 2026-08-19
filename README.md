# XYZ AI — Human-Like AI School Assistant

XYZ AI is the planned AI assistant for a school ERP ecosystem. It will eventually provide role-aware, natural-language assistance for students, parents, teachers, and school management.

## Current status

The project is in **Phase 5: Conversation Context + Persona Layer**. It includes deterministic development identity, RBAC and ownership validation, mock attendance data, and a short-term conversational orchestration layer.

## Phase 1 scope

- FastAPI application and health-check endpoint
- Environment-driven LLM configuration
- Controlled attendance and escalation intent vocabulary
- Validated NLU output for an externally configured LLM provider
- Development-only NLU analysis endpoint
- Development-only trusted identity store
- Deterministic RBAC and ownership checks
- Prompt-injection detection signals and secret-free audit event model
- User-bound, bounded conversation context with follow-up resolution
- Trusted role-based response personas and verified attendance responses

The NLU layer only interprets messages; it cannot access data, call APIs, perform actions, or make authorization decisions. The LLM is never trusted for identity, roles, permissions, ownership, or authorization. Voice, avatar, translation, database integration, mock school APIs, and human escalation workflows are planned for later phases.

## Technology stack

- Python
- FastAPI
- Uvicorn
- Pydantic
- python-dotenv
- HTTPX

## Project structure

```text
xyz-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config/settings.py
│   │   ├── authz/
│   │   ├── security/
│   │   ├── session/
│   │   └── nlu/
│   │       ├── intents.py
│   │       ├── llm_client.py
│   │       ├── router.py
│   │       ├── schemas.py
│   │       └── prompts/nlu_system.txt
│   ├── tests/
│   │   └── test_health.py
│   ├── .env.example
│   └── requirements.txt
├── .gitignore
└── README.md
```

## Setup

From the `backend` directory, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
pip install -r requirements.txt
```

## Run the service

From the `backend` directory:

```powershell
uvicorn app.main:app --reload
```

## Verify the health endpoint

With the server running, open [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) or run:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "XYZ AI"
}
```

## API documentation

With the server running, open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). The OpenAPI schema is available at [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json).

## NLU configuration and test endpoint

Copy `.env.example` to `.env` and set `LLM_PROVIDER` (`deepseek` or `openai_compatible`), `LLM_MODEL`, `LLM_API_KEY`, and `LLM_BASE_URL`. The API key is never logged. Without this configuration, the NLU endpoint returns a controlled `503` error.

Send a request to `POST /api/v1/nlu/analyze`:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/nlu/analyze -Method Post -ContentType 'application/json' -Body '{"message":"What is my attendance?"}'
```

## Development authorization check

`POST /api/v1/authz/check` demonstrates authorization with a controlled development identity store. A caller supplies a `user_id` and an intent, but never a role. This endpoint performs no attendance action.

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/authz/check -Method Post -ContentType 'application/json' -Body '{"user_id":"student-001","intent":"view_own_attendance","target_student_id":"student-001"}'
```

## Assistant chat

`POST /api/v1/assistant/chat` uses the development authentication header
`X-Development-User-Id`; the request body cannot supply a user ID or role.
The configured Phase 2 LLM client provides NLU, while authorization, ownership,
attendance retrieval, and response facts remain application-controlled.

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/assistant/chat -Method Post -ContentType 'application/json' -Headers @{'X-Development-User-Id'='parent-001'} -Body '{"message":"What is my child''s attendance?"}'
```

Pass the returned `conversation_id` in a later request to preserve short-term
context. A conversation ID belonging to another authenticated user is rejected.

## Run tests

From the `backend` directory:

```powershell
python -m unittest discover -s tests
```
