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

## Endpoints

- `POST /openai/assistant` — Create an OpenAI Assistant
- `GET /openai/assistant` — List OpenAI Assistants
- `POST /openai/thread` — Create a thread
- `GET /openai/thread` — List threads
- `POST /openai/message` — Add message to thread
- `POST /openai/run` — Run assistant on thread
- `POST /litellm/chat` — Call LLM via Litellm

All endpoints are currently placeholders. Implementations should be added as needed.

---