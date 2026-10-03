import asyncio
from contextlib import asynccontextmanager
import json
import threading
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

from app.audit import init_db
from app.detector import InjectionDetector
from app.normalize import normalize_text
from app.policy import evaluate_payload
from config import settings

detector: InjectionDetector | None = None
warmup_lock = threading.Lock()

def _warmup_model():
    global detector
    with warmup_lock:
        if detector is None:
            init_db()
            detector = InjectionDetector()

def get_detector() -> InjectionDetector:
    global detector
    if detector is None:
        _warmup_model()
    return detector

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # Startup warm-up in a background thread to prevent first-request lag
    threading.Thread(target=_warmup_model, daemon=True).start()
    yield

app = FastAPI(
    title="ArtificialShield Guardrail Proxy",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "gpt-4o-mini"
    messages: list[ChatMessage]
    temperature: float = 0.2
    stream: bool = False

class ScanRequest(BaseModel):
    text: str = Field(..., min_length=1)

def _extract_untrusted_text(payload: ChatCompletionRequest) -> str:
    parts = []
    # Segment trusted vs untrusted text
    trusted_roles = {"system", "developer"}
    for message in payload.messages:
        if message.role not in trusted_roles:
            content = normalize_text(message.content)
            if content:
                parts.append(f"[{message.role}]: {content}")
    return "\n".join(parts)


@app.get("/health")
def health() -> dict[str, str]:
    # Must not trigger model loading
    return {"status": "ok", "model": settings.model_name}

@app.post("/scan")
def scan(request: ScanRequest) -> dict[str, Any]:
    det = get_detector()
    result = evaluate_payload(det, request.text, source_label="/scan")
    return {
        "max_score": result["max_score"],
        "threshold": settings.threshold,
        "decision": result["action"],
        "latency_ms": result["latency_ms"],
        "segments": result["segments"],
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest) -> Any:
    text = _extract_untrusted_text(request)
    if text:
        det = get_detector()
        result = evaluate_payload(det, text, source_label="/v1/chat/completions")
        
        if result["action"] == "blocked":
            return JSONResponse(
                status_code=403,
                content={
                    "error": "prompt_injection_detected",
                    "request_id": result["request_id"],
                    "max_score": result["max_score"],
                    "offending_chunk_index": result["offending_chunk_index"],
                },
            )

        if not settings.backend_url:
        last_user_msg = next((m.content for m in reversed(request.messages) if m.role == "user"), "your query")
        resp_json = {
            "id": "chatcmpl-shield-passthrough",
            "object": "chat.completion",
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": f"ArtificialShield (Mock Backend): Payload passed guardrail inspection. Here is the answer to your query: '{last_user_msg}'",
                    },
                    "finish_reason": "stop",
                }
            ],
        }
        if request.stream:
            async def mock_stream():
                yield f"data: {json.dumps(resp_json)}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(mock_stream(), media_type="text/event-stream")
        return resp_json

    headers = {"Authorization": f"Bearer {settings.backend_api_key}"} if settings.backend_api_key else {}
    
    try:
        if request.stream:
            async def proxy_stream():
                async with httpx.AsyncClient(timeout=60.0) as client:
                    async with client.stream(
                        "POST", 
                        settings.backend_url, 
                        headers=headers, 
                        json=request.model_dump()
                    ) as response:
                        if response.status_code >= 400:
                            err = await response.aread()
                            yield err
                            return
                        async for chunk in response.aiter_bytes():
                            yield chunk
            return StreamingResponse(proxy_stream(), media_type="text/event-stream")
        else:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    settings.backend_url,
                    headers=headers,
                    json=request.model_dump(),
                )
            if response.status_code >= 400:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            return response.json()
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to connect to upstream LLM backend ({settings.backend_url}): {exc}",
        )



