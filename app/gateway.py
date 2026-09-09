import json
import time
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.audit import init_db, log_event
from app.detector import InjectionDetector
from app.normalize import normalize_text, segment_text
from config import settings

app = FastAPI(title="ArtificialShield Guardrail Proxy", version="0.2.0")
detector: InjectionDetector | None = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "gpt-4o-mini"
    messages: list[ChatMessage]
    temperature: float = 0.2


class ScanRequest(BaseModel):
    text: str = Field(..., min_length=1)


class ScanResponse(BaseModel):
    max_score: float
    threshold: float
    decision: str
    latency_ms: float
    segments: list[dict[str, Any]]


@app.on_event("startup")
def startup() -> None:
    global detector
    init_db()
    detector = InjectionDetector()


def _extract_text(payload: ChatCompletionRequest) -> str:
    parts = [normalize_text(message.content) for message in payload.messages if message.content]
    return "\n".join(part for part in parts if part)


def _evaluate_text(text: str) -> tuple[float, list[dict[str, Any]], float]:
    if detector is None:
        raise HTTPException(status_code=503, detail="Detector not initialized")
    segments = segment_text(text, settings.max_segment_chars)
    start = time.perf_counter()
    scored, max_score = detector.score_segments(segments)
    latency_ms = (time.perf_counter() - start) * 1000
    segment_payload = [
        {"text": item.text, "score": round(item.score, 4), "label": item.label}
        for item in scored
    ]
    return max_score, segment_payload, latency_ms


def _decision(max_score: float) -> str:
    if max_score >= settings.threshold:
        return "blocked"
    if settings.policy_mode == "flag" and max_score >= settings.threshold - 0.1:
        return "flagged"
    return "allowed"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "model": settings.model_name}


@app.post("/scan", response_model=ScanResponse)
def scan(request: ScanRequest) -> ScanResponse:
    max_score, segments, latency_ms = _evaluate_text(request.text)
    decision = _decision(max_score)
    if decision in {"blocked", "flagged"}:
        log_event(
            endpoint="/scan",
            max_score=max_score,
            threshold=settings.threshold,
            latency_ms=latency_ms,
            payload=request.text[:4000],
            decision=decision,
        )
    return ScanResponse(
        max_score=round(max_score, 4),
        threshold=settings.threshold,
        decision=decision,
        latency_ms=round(latency_ms, 2),
        segments=segments,
    )


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest) -> dict[str, Any]:
    text = _extract_text(request)
    max_score, segments, latency_ms = _evaluate_text(text)
    decision = _decision(max_score)

    if decision == "blocked":
        log_event(
            endpoint="/v1/chat/completions",
            max_score=max_score,
            threshold=settings.threshold,
            latency_ms=latency_ms,
            payload=text[:4000],
            decision=decision,
        )
        raise HTTPException(
            status_code=403,
            detail={
                "error": "prompt_injection_detected",
                "message": "Request blocked by ArtificialShield guardrail.",
                "max_score": round(max_score, 4),
                "threshold": settings.threshold,
                "latency_ms": round(latency_ms, 2),
                "segments": segments,
            },
        )

    if decision == "flagged":
        log_event(
            endpoint="/v1/chat/completions",
            max_score=max_score,
            threshold=settings.threshold,
            latency_ms=latency_ms,
            payload=text[:4000],
            decision=decision,
        )

    headers = {"Authorization": f"Bearer {settings.backend_api_key}"} if settings.backend_api_key else {}
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            settings.backend_url,
            headers=headers,
            json=request.model_dump(),
        )
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()
