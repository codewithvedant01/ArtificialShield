import time
import uuid
from typing import Any

from app.audit import log_event
from app.detector import InjectionDetector
from app.normalize import extract_encoded_payloads, segment_text
from config import settings


def evaluate_payload(
    detector: InjectionDetector, text: str, source_label: str, request_id: str = None
) -> dict[str, Any]:
    """
    Evaluates text using the provided detector, segments it, checks base64,
    and applies the threshold policy. Logs if blocked or flagged.
    """
    if request_id is None:
        request_id = f"req-{uuid.uuid4().hex[:8]}"

    segments = segment_text(text, settings.max_segment_chars)

    # Decode and inspect obfuscated base64 substrings
    for encoded in extract_encoded_payloads(text):
        for sub in segment_text(encoded, settings.max_segment_chars):
            if sub not in segments:
                segments.append(f"[decoded base64]: {sub}")

    if not segments:
        return {
            "action": "allowed",
            "request_id": request_id,
            "max_score": 0.0,
            "offending_chunk_index": -1,
            "latency_ms": 0.0,
        }

    start = time.perf_counter()
    scored, max_score = detector.score_segments(segments)
    latency_ms = (time.perf_counter() - start) * 1000

    # Policy decision: Block if ANY chunk >= threshold
    offending_chunk_index = -1
    offending_chunk_text = ""
    
    for i, item in enumerate(scored):
        if item.score == max_score:
            offending_chunk_index = i
            offending_chunk_text = item.text
            break

    if max_score >= settings.threshold:
        action = "blocked"
    elif settings.policy_mode == "flag" and max_score >= settings.threshold - 0.1:
        action = "flagged"
    else:
        action = "allowed"

    if action in {"blocked", "flagged"}:
        log_event(
            request_id=request_id,
            source_label=source_label,
            max_score=round(max_score, 4),
            offending_chunk=offending_chunk_text,
            threshold=settings.threshold,
            action=action,
        )

    return {
        "action": action,
        "request_id": request_id,
        "max_score": round(max_score, 4),
        "offending_chunk_index": offending_chunk_index,
        "latency_ms": round(latency_ms, 2),
        # Include full segments only if allowed, or for internal processing
        "segments": [{"score": round(s.score, 4), "label": s.label} for s in scored],
    }

