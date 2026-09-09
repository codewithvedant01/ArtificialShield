# ArtificialShield

Inline ML guardrail proxy for detecting indirect prompt injection before LLM dispatch.

## Quick start

```bash
pip install -r requirements.txt
uvicorn app.gateway:app --host 0.0.0.0 --port 8080
streamlit run dashboard/app.py
```

## Endpoints

- `GET /health` — service status
- `POST /scan` — score arbitrary text
- `POST /v1/chat/completions` — OpenAI-compatible guarded proxy

## Review 2 deliverables

- FastAPI proxy integration
- DeBERTa-v3 injection classifier
- SQLite audit logging
- Streamlit analytics dashboard
- Baseline vulnerable agent and attack harness
