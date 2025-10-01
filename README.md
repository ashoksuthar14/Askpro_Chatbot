# AskMe Pro

AskMe Pro is an AI Knowledge Companion running on Flask that uses only Google Gemini `gemini-2.5-flash` for LLM features. It supports chat, document upload with local TF-IDF retrieval, 3-point summarization, conversation memory, Wikipedia source checks, and diagram generation.

## Features
- Chat with modes (short, detailed, el5, deep_dive) and personas (teacher, coder, comedian, coach, auto)
- Upload .txt/.pdf, local TF-IDF retrieval (no external embeddings)
- Article/doc summarization into exactly 3 bullet points
- Conversation memory stored in SQLite via SQLAlchemy
- Wikipedia quick source checks
- Diagram generation (NetworkX/Matplotlib) served as PNG
- Rate limiting per IP/session
- Frontend: HTML/CSS/JS with Web Speech API (input only)

## Quickstart
1. Create `.env` from example and set `GEMINI_API_KEY` (or hardcode in `backend/gemini_client.py`).
```bash
cp .env.example .env
```
2. Install dependencies and run server
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
cd backend
flask --app app run
```

3. Open http://localhost:5000

## Testing
```bash
pytest -q
```
Tests mock Gemini via `GEMINI_MOCK=1`.

## Environment
- `GEMINI_API_KEY`: Google Gemini API key
- `FAST_MODE` (default 1) for lower latency

## Known limitations
- Retrieval uses TF-IDF; semantic nuance is limited vs embeddings

## License
See `LICENSE`.
