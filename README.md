# Project Sole
AI-Powered Customer Support Agent for Indian D2C Brands — WhatsApp + Voice in every Indian language.

---

## Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) — `brew install uv`
- [ngrok](https://ngrok.com) — `brew install ngrok`
- PostgreSQL (via [Railway](https://railway.app))

---

## Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/pranav245/Project-X.git
cd Project-X
```

### 2. Install dependencies
```bash
cd backend
uv sync
```

### 3. Configure environment variables
```bash
cp .env.example .env
```
Fill in the following keys in `.env`:

| Variable | Where to get it |
|---|---|
| `VAPI_API_KEY` | [vapi.ai](https://vapi.ai) → API Keys → Private Key |
| `SARVAM_API_KEY` | [sarvam.ai](https://sarvam.ai) → API Access |
| `LLM_API_KEY` | OpenAI / Anthropic / Groq dashboard |
| `TELNYX_API_KEY` | [telnyx.com](https://telnyx.com) → API Keys |
| `DATABASE_URL` | Railway → PostgreSQL → Variables → `DATABASE_PUBLIC_URL` (change `postgresql://` to `postgresql+asyncpg://`) |

### 4. Run database migrations
```bash
uv run alembic revision --autogenerate -m "initial"
uv run alembic upgrade head
```

### 5. Start ngrok
In a separate terminal:
```bash
ngrok http 8000
```
Copy the `https://....ngrok-free.dev` URL and set it as `BACKEND_URL` in `.env`.

### 6. Start the server
```bash
uv run uvicorn main:app --reload --port 8000
```
Visit `http://localhost:8000/health` — should return `{"status": "healthy", "database": "connected"}`.

### 7. Create VAPI assistant
```bash
uv run python -c "
import asyncio
from services.vapi_service import vapi_service

async def setup():
    assistant = await vapi_service.create_assistant('Your Brand Name')
    print('Assistant ID:', assistant['id'])

asyncio.run(setup())
"
```
Save the Assistant ID — you'll need it to link your phone number in the VAPI dashboard.

### 8. Link phone number
1. Go to [vapi.ai](https://vapi.ai) → **Phone Numbers** → Import Telnyx
2. Enter your Telnyx number and API key
3. Assign the assistant created in Step 7 under **Inbound Settings**

---

## Switching LLM Provider
Just update these three lines in `.env` — no code changes needed:

```env
# OpenAI
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=sk-...

# Anthropic
LLM_PROVIDER=anthropic
LLM_MODEL=claude-haiku-4-5
LLM_API_KEY=sk-ant-...

# Groq (free + fast)
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
LLM_API_KEY=...
```

---

## Project Structure
```
backend/
├── main.py               # FastAPI app entry point
├── config.py             # Environment variables
├── database.py           # SQLAlchemy async setup
├── models/               # Database models (brands, conversations)
├── routers/              # API routes (health, VAPI webhooks)
├── services/             # VAPI, Sarvam integrations
├── prompts/              # LLM system prompts
└── migrations/           # Alembic migrations
```
