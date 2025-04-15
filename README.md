# AI Agent Backend (Python Microservice)

This microservice provides REST endpoints for OpenAI Assistants API and Litellm, enabling agent management and LLM calls from your Next.js platform.

## Setup

1. **Create and activate a virtual environment (optional but recommended):**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables:**
   - For OpenAI: `OPENAI_API_KEY`
   - For Litellm: see [Litellm docs](https://github.com/BerriAI/litellm)

4. **Run the server:**

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

   The service will be available at [http://localhost:8000](http://localhost:8000).


## Docker Build & Deployment

### Build the Docker Image

```bash
docker build -t atlas-agent-backend .
```

### Run the Backend with Docker

```bash
docker run --env-file .env -p 8000:8000 atlas-agent-backend
```

- The backend will be available at [http://localhost:8000](http://localhost:8000)
- Healthcheck endpoint: `/` (returns status OK)
- For production, ensure your `.env` file contains all required secrets (e.g., `OPENAI_API_KEY`)

### Compose/Production (Optional)
If you have a database or other services, consider adding a `docker-compose.yml` file.


## Endpoints

- `POST /openai/assistant` — Create an OpenAI Assistant
- `GET /openai/assistant` — List OpenAI Assistants
- `POST /openai/thread` — Create a thread
- `GET /openai/thread` — List threads
- `POST /openai/message` — Add message to thread
- `POST /openai/run` — Run assistant on thread
- `POST /litellm/chat` — Call LLM via Litellm

All endpoints are currently placeholders. Implementations should be added as needed.

### A2A Protocol Endpoints
- `POST /api/v1/a2a/register` — Register agent (A2A)
- `POST /api/v1/a2a/handshake` — Handshake/authenticate (A2A)
- `POST /api/v1/a2a/send` — Relay message to agent (A2A)
- `POST /api/v1/a2a/receive` — Receive/process message (A2A)
- `GET /api/v1/a2a/status/{agent_id}` — Get agent status (A2A)
- `GET /api/v1/a2a/error` — Protocol-compliant error (A2A)

- Implements [Google Agent2Agent (A2A) protocol](https://google.github.io/A2A/#/documentation) for standardized, secure agent-to-agent communication. See `MODEL_CARD_A2A.md` for details.

---

## CI/CD & Quality

- Automated CI pipeline: see `.github/workflows/ci.yml` (runs Ruff linter, pytest, and uploads coverage)
- Linting: [Ruff](https://docs.astral.sh/ruff/) enforced via `ruff.toml`
- Test suite: Pytest, with smoke and coverage checks

## Profiling

- Profile agent runner performance: `python tools/profile_agent.py`
- Edit `tools/profile_agent.py` to customize profiling scenarios

## Model Cards & Ethics

- See `model_card.md` for agent limitations, intended use, and ethical guidance
- All agents/models must have a model card before deployment


---